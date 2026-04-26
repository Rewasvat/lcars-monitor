##################################
# Sensor API implementation for LIBRE HARDWARE MONITOR LIB!
# See https://github.com/LibreHardwareMonitor/LibreHardwareMonitor
###
# This expects the user to have the LHM app/Lib in their systems, and point LCARS Monitor
# to find and use it.
##################################
import os
import clr
import math
import click
import libasvat.imgui.editors.primitives as primitives
from imgui_bundle import imgui
from libasvat.imgui.math import Vector2
from lcarsmonitor.sensors.sensors_api import SensorSource, SensorID, HardwareType, SensorType, Hardware, InternalSensor


# TODO: baixar ZIP do ultimo release de LHM pra atualizar a install atual (ou até permitir instalar do zero)
#   copilot deve ajudar com isso.
#   - interessante tb mostrar o changelog, se possivel desde a versão sendo usada até a atual
class LibreComputer(SensorSource):
    """LCARSMonitor Sensor Source implementation using Libre Hardware Monitor.

    LibreHardwareMonitor (LHM for short), from https://github.com/LibreHardwareMonitor/LibreHardwareMonitor, is free
    software that can monitor the temperature sensors, fan speeds, voltages, load and clock speeds of your computer.

    LHM itself is a simple UI program on top of the Libre Hardware Monitor Lib (LHML), which is the actual library that
    allows monitoring computer sensors. This SensorSource uses the LHML from a local install of LHM in your machine to
    provide hardware/sensor data to LCARSMonitor.
    """

    def __init__(self):
        super().__init__()
        self._pretty_name = "Libre Hardware Monitor"
        self._pc = None
        self._lhm_path: str = None
        self._lhm_loaded = False
        self._last_message: str = "Please set the `library_path` property to a valid value"

    @primitives.string_property(is_folder=True)
    def library_path(self) -> str:
        """Path to LibreHardwareMonitor folder [GET/SET].

        The LibreHardwareMonitor (LHM) folder should contain the LibreHardwareMonitorLib.dll file which we'll load
        to access sensor data. As such, this property needs to be correctly set in order for this Sensor Source to work.

        To load the dll, other related DLLs should be in the same folder, so we need to point to the LHM folder directly.
        Usually when downloading the LHM release from GitHub, the ZIP contains a folder with all DLLs and more.

        When this property is set (in imgui - through select-folder dialog), we'll check the given path and try to load the LHMLib
        DLL. Any errors will be shown in the UI.

        However, if loading is successful, changing this property, for example to change which version of LHM you're using,
        WILL NOT CHANGE THE DLL THAT IS LOADED. The .NET framework does not allow unloading assemblies. The path will still
        be changed (and persisted!), but you'll need to restart this application entirely in order to "re-load" a different
        LHM DLL.
        """
        return self._lhm_path

    @library_path.setter
    def library_path(self, value: str):
        # NOTE: SensorSource base class handles loading/saving data from imgui-properties like this one.
        if value != self._lhm_path:
            self._lhm_path = value
            if not self._lhm_loaded:
                self._load_lhm()
            else:
                self._last_message = "Restart app to re-load DLL after path change (see tooltip). Previous DLL is loaded."

    def check_availability(self):
        return self._lhm_loaded, self._last_message

    def _load_lhm(self):
        """Loads the LibreHardwareMonitorLib.dll from C#/.NET using the `clr` module.

        Appropriately updates our loaded/message attributes according to the result of loading the DLL.
        """
        if self._lhm_loaded:
            click.secho("[LibreSensors] Tried to re-load LHML DLL. Restart the app to be able to load a different DLL", fg="yellow")
            return

        dll_name = "LibreHardwareMonitorLib.dll"
        dll_path = os.path.join(self.library_path, dll_name)
        if not os.path.isfile(dll_path):
            self._last_message = f"{dll_name} not found. Path '{self.library_path}' doesn't point to a valid LHM install"
            return

        try:
            # Load LibreHardwareMonitorLib (LHML) from C# .NET
            from System.Reflection import Assembly  # type: ignore
            Assembly.UnsafeLoadFrom(dll_path)
        except Exception as e:
            self._last_message = f"Error while loading {dll_name}: {e}"
            return

        self._lhm_loaded = True
        self._last_message = f"{dll_name} successfully loaded"

    def initialize(self):
        if not self._lhm_loaded:
            raise RuntimeError("Can't initialize LibreHardwareMonitor sensors without loading the LHM Lib.")

        from LibreHardwareMonitor.Hardware import Computer  # type: ignore

        # Initialize LHML Computer object
        self._pc = Computer()
        self._pc.IsCpuEnabled = True
        self._pc.IsGpuEnabled = True
        self._pc.IsMemoryEnabled = True
        self._pc.IsMotherboardEnabled = True
        self._pc.IsStorageEnabled = True
        self._pc.IsNetworkEnabled = True
        self._pc.IsBatteryEnabled = True
        self._pc.IsControllerEnabled = True
        self._pc.IsPsuEnabled = True
        self._pc.Open()

        for hw in self._pc.Hardware:
            self._hardwares.append(LibreHardware(hw))

    def shutdown(self):
        if self._pc is not None:
            self._pc.Close()
        super().shutdown()


class LibreHardware(Hardware):
    # Wraps and builds upon ``LibreHardwareMonitorLib.Hardware.IHardware`` interface.

    def __init__(self, hw, parent: 'LibreHardware' = None):
        """hw should be LHML's IHardware object"""
        isensors = [LibreSensor(self, s) for s in hw.Sensors]
        children = [LibreHardware(subhw, self) for subhw in hw.SubHardware]

        super().__init__(parent, isensors, children)
        self._hw = hw
        """Internal IHardware object from native C#"""
        self._type: HardwareType = None

    @property
    def id(self):
        return str(self._hw.Identifier)

    @property
    def name(self):
        return str(self._hw.Name)

    @property
    def type(self):
        if self._type is None:
            self._type = HardwareType.from_obj(self._hw.HardwareType)
        return self._type

    def update(self):
        if self.enabled:
            self._hw.Update()
            return super().update()


class LibreSensor(InternalSensor):
    """Represents a single ISensor object from C# for a hardware device.

    This is a simple wrapper of ``LibreHardwareMonitorLib.Hardware.ISensor`` interface, providing some basic identification values.

    A LibreComputer will always create all of its InternalSensors objects upon loading. Since we contain native C# objects, this class
    can't be pickled.

    A InternalSensor contains refs to all ``Sensor`` objects that use it. The ``Sensor`` class is the proper API to access/use sensor
    data, and it uses its InternalSensor object internally to access the underlying data.
    """

    def __init__(self, parent_hw, internal_sensor):
        """internal_sensor should be LHML's ISensor object"""
        super().__init__(parent_hw)
        self.isensor = internal_sensor  # LibreHardwareMonitor.Hardware.ISensor
        """Internal, fixed, ISensor object from LibreHardwareMonitor to access sensor data."""
        self._type: SensorType = None

    @property
    def id(self):
        return SensorID(self.isensor.Identifier)

    @property
    def name(self):
        return str(self.isensor.Name)

    @property
    def type(self):
        if self._type is None:
            self._type = SensorType.from_obj(self.isensor.SensorType)
        return self._type

    @property
    def limits(self):
        low = getattr(self.isensor, "LowLimit", None)
        high = getattr(self.isensor, "HighLimit", None)
        if low is not None and high is not None:
            return Vector2(low, high)

    @property
    def value(self):
        if self.isensor.Value:
            return float(self.isensor.Value)

    @property
    def value_range(self):
        minimum = self.isensor.Min or math.inf
        maximum = self.isensor.Max or -math.inf
        return Vector2(minimum, maximum)
