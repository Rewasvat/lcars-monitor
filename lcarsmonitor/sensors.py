import math
import click
import itertools
import libasvat.command_utils as cmd_utils
import libasvat.imgui.type_editor as types
from enum import Enum
from dataclasses import dataclass
from typing import Iterator, TYPE_CHECKING
from imgui_bundle import imgui
from libasvat.data import DataCache
from lcarsmonitor.native_api import SensorType, ISensor, Computer
from lcarsmonitor.test_sensor import TestIHardware, TestIComputer
from libasvat.imgui.math import Vector2
from libasvat.imgui.colors import Color, Colors
from libasvat.imgui.general import drop_down


if TYPE_CHECKING:
    from lcarsmonitor.sensor_node import Sensor


# Local implementation of classes wrapping C# types.
# This is to allow us some documentation (intellisense) and some custom logic/API of ours.

# TODO: update dos hardware era feito de forma async (no C#)
class ComputerSystem(metaclass=cmd_utils.Singleton):
    """Singleton class that represents the Computer System we're running from.

    This is the main class from which to access hardware and sensor data from the computer.

    Wraps and builds upon ``LibreHardwareMonitorLib.Hardware.Computer`` class.
    """

    def __init__(self):
        self._pc: Computer = None
        self.hardwares: list[Hardware] = []
        self.all_sensors: dict[str, InternalSensor] = {}
        self.elapsed_time: float = 0
        """Internal counter of elapsed time, used for ``timed_update()`` (in seconds)."""
        self.update_time: float = 1.0
        """Amount of time that must pass for a ``timed_update()`` call to trigger an actual ``update()`` (in seconds)."""

    def open(self, dummy_test=False):
        """Starts the computer object, allowing us to query its hardware, sensors and more.

        Args:
            dummy_test (bool, optional): If true, will use a dummy internal Computer object, with dummy sensors that simulate actual
            sensors with changing values, for testing sensor-related code without needing to load sensors properly. Defaults to False.
        """
        if len(self.all_sensors) > 0:
            # Was already opened
            return
        if dummy_test:
            self._pc = TestIComputer()
        else:
            self._pc = Computer()
        self._pc.IsCpuEnabled = True
        self._pc.IsGpuEnabled = True
        self._pc.IsMemoryEnabled = True
        self._pc.IsMotherboardEnabled = True
        self._pc.IsStorageEnabled = True
        self._pc.IsNetworkEnabled = True
        # IsControllerEnabled  NOTE: tried this one, apparently was crashing due to missing assembly
        # IsBatteryEnabled
        # IsControllerEnabled
        self._pc.Open()

        for hw in self._pc.Hardware:
            self.hardwares.append(Hardware(hw))
        if not dummy_test:
            self.hardwares.append(Hardware(TestIHardware()))

        self.all_sensors = {sensor.id: sensor for sensor in self.get_all_isensors()}
        click.secho("Initialized Computer", fg="magenta")
        cache = DataCache()
        cache.add_shutdown_listener(self.close)

    def close(self):
        """Stops the computer object, releasing resources.

        This is automatically called on shutdown of LCARSMonitor."""
        if len(self.all_sensors) <= 0:
            # Was already closed
            return
        self._pc.Close()
        click.secho("Closed Computer", fg="magenta")
        self.hardwares.clear()
        self.all_sensors.clear()

    def update(self):
        """Updates our hardware, to update all of our sensors."""
        for hardware in self.hardwares:
            hardware.update()

    def timed_update(self, delta_time: float):
        """Updates our hardware (calls ``self.update()``), but only after a set of time has elapsed.

        This instance stores how much time has elapsed, and updates it with the given ``delta_time``.
        When elapsed time passes the threshold of ``self.update_time``, then ``update()`` is triggered.

        Args:
            delta_time (float): Amount of time passed since the previous call to this method. In seconds.
        """
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.update_time:
            self.update()
            self.elapsed_time = 0

    def get_all_isensors(self) -> list['InternalSensor']:
        """Gets a list of all internal sensors of this system.

        Returns:
            list[InternalSensor]: list of sensors
        """
        if self._pc is None:
            return []

        sensors = []
        for hardware in self.hardwares:
            sensors += list(hardware.get_all_isensors())
        return sensors

    def get_isensor_by_id(self, id_obj: str | ISensor):
        """Gets the sensor with the given ID.

        Args:
            id_obj (str | ISensor): the ID of the sensor to get. Can be an ID str to check, or a native ISensor
            object, in which case we'll use its ID.

        Returns:
            InternalSensor: the InternalSensor object, or None if no sensor exists with the given ID.
        """
        if isinstance(id_obj, str):
            id = id_obj
        elif id_obj is not None:
            id = str(id_obj.Identifier)
        return self.all_sensors.get(id)

    def __iter__(self) -> Iterator['Hardware']:
        return iter(self.hardwares)


# TODO: transformar isso num node? ou melhor: ter action pra pegar os dados de um hardware, ai poderia pegar coisas do HW vindo de um sensor.
class Hardware:
    """Represents a Hardware device on the system.

    Hardware are the "building blocks" of the system: your CPU, GPU, Memory, etc.
    Amongst other things, a hardware may contain Sensors and other "children" sub-Hardware (which are other Hardware objects).

    Wraps and builds upon ``LibreHardwareMonitorLib.Hardware.IHardware`` interface."""

    def __init__(self, hw, parent: 'Hardware' = None):
        self._parent = parent
        self._hw = hw
        """Internal IHardware object from native C#"""
        self._isensors: list[InternalSensor] = [InternalSensor(s, self) for s in hw.Sensors]
        """Sensors of this hardware. Note that sub-hardware may have other sensors as well."""
        self.children: list[Hardware] = [Hardware(subhw, self) for subhw in hw.SubHardware]
        """Sub-hardwares of this device."""

    @property
    def id(self):
        """Gets the unique identifier of this hardware"""
        return str(self._hw.Identifier)

    @property
    def type(self):
        """Gets the type of this hardware"""
        return str(self._hw.HardwareType)

    @property
    def root_type(self) -> str:
        """Gets the type of our 'root' parent hardware, which is the parent of our parent and so on, until reaching the parent with no parent."""
        if self._parent is not None:
            return self._parent.root_type
        return self.type

    @property
    def name(self):
        """Gets the name of this hardware"""
        return str(self._hw.Name)

    @property
    def full_name(self):
        """Gets the full name of this hardware, which is ``parent_name / our_name``, recursively
        checking all parent hardware up to the root."""
        if self._parent is not None:
            return f"{self._parent.full_name} / {self.name}"
        return self.name

    @property
    def parent(self):
        """Gets the parent hardware of this device. May be None if we don't have a parent (root hardware)."""
        return self._parent

    @property
    def enabled(self):
        """Checks if this hardware is enabled. That is, if at least one of its sensors (recursively through sub-hardware)
        is enabled"""
        for sensor in self:
            if sensor.enabled:
                return True
        return False

    @enabled.setter
    def enabled(self, value: bool):
        """Sets the 'enabled' flag on all of our sensors to the given value.

        Args:
            value (bool): if sensors will be enabled or not
        """
        for sensor in self:
            sensor.enabled = value

    @property
    def sensors(self):
        """Gets a list of all existing Sensor objects that use a InternalSensor from this hardware."""
        return sum((isen.sensors for isen in self._isensors), [])

    @property
    def isensors(self):
        """Gets a list of the InternalSensors of this hardware.
        Doesn't include sensors from sub-hardware, see ``self.get_all_isensors()`` for that."""
        return self._isensors.copy()

    def update(self):
        """Updates this hardware, updating all of our sensors."""
        if self.enabled:
            self._hw.Update()
            for sensor in self.sensors:
                sensor.update()
            for child in self.children:
                child.update()

    def __iter__(self) -> Iterator['Sensor']:
        return itertools.chain(iter(self.sensors), *(iter(child) for child in self.children))

    def get_all_isensors(self) -> Iterator['InternalSensor']:
        """Returns an iterator of all InternalSensors of this hardware and recursively of all sub-hardware we have."""
        return itertools.chain(iter(self._isensors), *(child.get_all_isensors() for child in self.children))

    def get_sensors_by_type(self, stype: str, recursive=False):
        """Gets all of our sensors of the given type.

        Args:
            stype (str): Type of sensors to acquire.
            recursive (bool, optional): If true, will also check sensors of all sub-hardware recursively. Defaults to False.

        Returns:
            list[Sensor]: the sensors of the given type.
        """
        if recursive:
            return [s for s in self if s.type == stype]
        return [s for s in self.sensors if s.type == stype]

    def __str__(self):
        return f"{self.type} {self.full_name}"


class SensorLimitsType(str, Enum):
    """Methods to acquire the min/max limits of a sensor.
    * CRITICAL: limits from sensor's device critical limits (if they exist).
    * LIMITS: limits from sensor's device limits (if they exist).
    * MINMAX: limits are the same as the sensor's measured min/max values (always available).
    * MINMAX_EVER: limits are the same as the sensor's measured min/max values ever, across all times this has been run.
    * FIXED: limits are those set by the user. Defaults to values based on the sensor's unit (always available).
    * AUTO: limits are acquired automatically. Tries getting from the following methods, using the first that is
    available: CRITICAL > LIMITS > FIXED.
    """
    # NOTE: duplicated value's docs in the Enum class doc since at moment in python, we can't programmatically get these docstrings.
    #   How then, you may ask, does VSCode gets them? Magic I tell you!
    CRITICAL = "CRITICAL"
    """Limits from the sensor's ICriticalSensorLimits interface (not all sensors implement this)."""
    LIMITS = "LIMITS"
    """Limits from the sensor's ISensorLimits interface (not all sensors implement this)."""
    MINMAX = "MINMAX"
    """Limits are the same as the sensor's measured min/max values."""
    MINMAX_EVER = "MINMAX_EVER"
    """Limits are the same as the sensor's measured min/max values ever - across all times this sensor was updated and saved."""
    FIXED = "FIXED"
    """Limits are hardcoded in the sensor object. Can be changed by user. Default values are based on the sensor's unit."""
    AUTO = "AUTO"
    """Limits are acquired automatically. The options are checked for availability following a specific order (CRITICAL > LIMITS > FIXED),
    and the first option that is valid will be used. This is the default limits type used."""


@dataclass
class SensorUnitData:
    id: str
    limits: Vector2
    types: set[SensorType]
    value_format: str


class SensorUnit(SensorUnitData, Enum):
    """Enum of all possible Sensor Units.

    Each item also associates its unit to the internal sensor types. A few sensor types share the same unit, while a few
    sensor types have the same unit but on different orders of magnitude (such as Hz and MHz). When possible the unit is from SI.

    Each unit also contains a few other attributes related to it, such as default min/max limits and more.
    """
    VOLTAGE = ("V", Vector2(1, 1.5), {SensorType.Voltage}, "{:.3f}")
    CURRENT = ("A", Vector2(5, 90), {SensorType.Current}, "{:.3f}")
    CLOCK = ("MHz", Vector2(1000, 6000), {SensorType.Clock}, "{:.1f}")
    PERCENT = ("%", Vector2(0, 100), {SensorType.Load, SensorType.Level, SensorType.Control}, "{:.1f}")
    TEMPERATURE = ("°C", Vector2(20, 90), {SensorType.Temperature}, "{:.1f}")
    FAN = ("RPM", Vector2(0, 10000), {SensorType.Fan}, "{:.0f}")
    FLOW = ("L/h", Vector2(), {SensorType.Flow}, "{:.1f}")
    POWER = ("W", Vector2(10, 200), {SensorType.Power}, "{:.1f}")
    DATA = ("GB", Vector2(0, math.inf), {SensorType.Data}, "{:.1f}")
    SMALLDATA = ("MB", Vector2(0, math.inf), {SensorType.SmallData}, "{:.1f}")
    FACTOR = (".", Vector2(-math.inf, math.inf), {SensorType.Factor}, "{:.3f}")
    FREQUENCY = ("Hz", Vector2(0, 4000), {SensorType.Frequency}, "{:.1f}")
    THROUGHPUT = ("B/s", Vector2(0, 1e9), {SensorType.Throughput}, "{:.1f}")
    # TODO: TIMESPAN VALUE FORMAT: no C#, era `{0:g}` que eh "general-short" format do elemento. Aparentemente isso muda de acordo com o tipo.
    # Se for numero normal, seria a mesma coisa. Mas se o valor for um time-span mesmo, ai o resultado eh "[-][d:]h:mm:ss[.FFFFFFF]"
    # Precisa arrumar isso aqui
    TIMESPAN = ("s", Vector2(-math.inf, math.inf), {SensorType.TimeSpan}, "{}")
    ENERGY = ("mWh", Vector2(), {SensorType.Energy}, "{:.0f}")
    UNKNOWN = ("<WAT>", Vector2(), {}, "{}")

    def __str__(self):
        return self.id

    @classmethod
    def from_type(self, stype: str):
        for unit in self:
            if stype in [str(t) for t in unit.types]:
                return unit
        return self.UNKNOWN


class InternalSensor:
    """Represents a single ISensor object from C# for a hardware device.

    This is a simple wrapper of ``LibreHardwareMonitorLib.Hardware.ISensor`` interface, providing some basic identification values.

    A ComputerSystem will always create all of its InternalSensors objects upon loading. Since we contain native C# objects, this class
    can't be pickled.

    A InternalSensor contains refs to all ``Sensor`` objects that use it. The ``Sensor`` class is the proper API to access/use sensor
    data, and it uses its InternalSensor object internally to access the underlying data.
    """

    def __init__(self, internal_sensor: ISensor, parent_hw: Hardware):
        # FIXED SENSOR-RELATED ATTRIBUTES
        self.isensor = internal_sensor  # LibreHardwareMonitor.Hardware.ISensor
        """Internal, fixed, ISensor object from LibreHardwareMonitor to access sensor data."""
        self.parent = parent_hw
        """Parent hardware of this sensor."""
        self.unit: SensorUnit = SensorUnit.from_type(self.type)
        """Unit of this sensor, based on its type (usually SI units)."""
        self._sensors: list[Sensor] = []

    @property
    def id(self) -> 'SensorID':
        """Gets the sensor ID. This uniquely identifies this sensor (and is reasonably human-readable)."""
        return SensorID(self.isensor.Identifier)

    @property
    def name(self) -> str:
        """Gets the sensor name. Some different sensors may have the same name."""
        return str(self.isensor.Name)

    @property
    def type(self) -> str:
        """Gets the type of this sensor. This specifies which kind of data it measures/returns, such
        as Temperature, Power, Frequency, Load, etc"""
        # TODO: trocar isso pra uma enum? ou usar a própria enum do C#? Como funcionaria?
        return str(self.isensor.SensorType)

    @property
    def critical_limits(self):
        """Tries to get the sensor's limits from the ICriticalSensorLimits interface."""
        low = getattr(self.isensor, "CriticalLowLimit", None)
        high = getattr(self.isensor, "CriticalHighLimit", None)
        if low is not None and high is not None:
            # TODO: in C#, we used to cast the ISensor object to ICriticalSensorLimits to see if we could access these attributes.
            #   maybe should've done something like that here? Not sure if this `hasattr` method works...
            #   On the other hand, apparently no sensors implement the Limits interfaces anyway...
            return Vector2(low, high)

    @property
    def basic_limits(self):
        """Tries to get the sensor's limits from the ISensorLimits interface."""
        low = getattr(self.isensor, "LowLimit", None)
        high = getattr(self.isensor, "HighLimit", None)
        if low is not None and high is not None:
            return Vector2(low, high)

    @property
    def info(self):
        """Gets a short multi-line description of this sensor (name, type, unit, parent hardware, etc)"""
        lines = [
            f"Sensor: {self.name} ({self.id})",
            f"Type/unit: {self.type} ({self.unit})",
            f"Hardware: {self.parent.full_name} ({self.parent.type})",
        ]
        return "\n".join(lines)

    @property
    def sensors(self):
        """Gets the Sensor nodes associated with this InternalSensor/ID.

        A Sensor node is the proper API for accessing/changing sensor data, while this InternalSensor is only a bare
        ISensor wrapper providing minimal identification values.

        See ``self.create()`` to create and associate a Sensor to this InternalSensor.
        """
        return self._sensors

    def create(self):
        """Creates a Sensor object associated with this InternalSensor/ID.

        Returns:
            Sensor: newly created Sensor object.
        """
        from lcarsmonitor.sensor_node import Sensor
        sensor = Sensor(self.id)
        self._add(sensor)
        return sensor

    def _add(self, sensor: 'Sensor'):
        """Adds the given Sensor object to our list of sensors, if we haven't already.
        This is used internally when ``self.create()``ing a new sensor object.
        """
        if sensor not in self._sensors:
            self._sensors.append(sensor)

    def _remove(self, sensor: 'Sensor'):
        """Clears our associated Sensor object, if any.
        This is used internally by the Sensor when it is destroyed.
        """
        if sensor in self._sensors:
            self._sensors.remove(sensor)


class SensorID(str):
    """Represents the unique identification value of a InternalSensor.

    This is just a `string`. But by using this sub-class, we can better document (by typing) the
    places that should/are using a Sensor ID, and we can easily allow a custom editing of this
    value in IMGUI with our TypeEditors to only allow selecting valid sensor IDs as value.

    The editing part is particularly useful when the sensors are used as nodes in a UISystem graph.
    """


@types.TypeDatabase.register_editor_for_type(SensorID)
class InternalSensorEditor(types.TypeEditor):
    """Imgui TypeEditor for selecting a SensorID value."""

    def __init__(self, config: dict):
        super().__init__(config)
        self._options: list[SensorID] = []
        self._docs: list[str] = []
        self.add_tooltip_after_value = False
        self.color = Colors.yellow
        self.extra_accepted_input_types = str
        self.convert_value_to_type = True

    @property
    def sensor_options(self):
        """Gets the sensor options available for selection."""
        if len(self._options) == 0:
            self._populate_options()
        return self._options

    @property
    def sensor_docs(self):
        """Gets the docstrings for the sensor options."""
        if len(self._docs) == 0:
            self._populate_options()
        return self._docs

    def draw_value_editor(self, value: SensorID):
        flags = imgui.SelectableFlags_.no_auto_close_popups
        return drop_down(value, self.sensor_options, self.sensor_docs, default_doc=self.attr_doc, item_flags=flags)

    def _populate_options(self):
        """Populates the available sensor IDs and infos (used as doc) data stored by this object.
        This data is then used when rendering the editor to properly display the available options and their docs."""
        isensors = ComputerSystem().get_all_isensors()
        for isen in isensors:
            self._options.append(isen.id)
            self._docs.append(isen.info)
