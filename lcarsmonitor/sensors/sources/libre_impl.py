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
from libasvat.imgui.math import Vector2
from lcarsmonitor.sensors.sensors_api import SensorSource, SensorID, HardwareType, SensorType, Hardware, InternalSensor


class LibreComputer(SensorSource):

    def __init__(self):
        super().__init__()
        self._pc = None
        self._hardwares: list[LibreHardware] = []

    def initialize(self):
        # Load LibreHardwareMonitorLib (LHML) from C# .NET
        from System.Reflection import Assembly  # type: ignore

        dll_name = "LibreHardwareMonitorLib.dll"
        dll_path = os.path.join(os.path.expanduser("~"), "Downloads", "LibreHardwareMonitor v0.9.5 BETA", dll_name)
        Assembly.UnsafeLoadFrom(dll_path)

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
        self._pc.Close()
        self._hardwares.clear()

    def get_all_hardware(self):
        return self._hardwares


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
