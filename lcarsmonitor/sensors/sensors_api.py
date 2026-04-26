import re
import math
import itertools
from enum import Enum
from dataclasses import dataclass
from typing import Iterator, TYPE_CHECKING
from libasvat.imgui.math import Vector2
from libasvat.imgui.general import is_user_creatable
from libasvat.imgui.editors.controller import render_all_properties, get_all_prop_values_for_storage, restore_prop_values_to_object

if TYPE_CHECKING:
    from lcarsmonitor.sensors.sensor_node import Sensor


class SensorSource:
    """Represents a source of hardware/sensor data for the computer.

    This abstract class is the base from which to integrate PC Sensors/Monitor APIs (such as LibreHardwareMonitorm HWInfo, and others)
    into the LCARS Monitor system. Using these APIs, implementations of this class should provide ``Hardware`` and ``InternalSensor``
    objects that provide the hardware/sensor data from the computer.

    Our ``ComputerSystem`` singleton handles the available SensorSources, letting the user choose between any user-creatable (see
    ``libasvat.imgui.general.is_user_creatable()``) implementations (subclasses) of this base-class to use as the active sensor
    data source.

    While SensorSource implementations may be singletons themselves, the ComputerSystem will only instantiate a single instance
    of any implementations during a session.

    NOTE: this base class has a single abstract method - the ``initialize()`` method - that need to be overriden by subclasses
    in order to properly implement the class to their sensor source. Besides that, subclasses may choose to override some other
    methods (such as ``check_availability()``) to implement or add their own logic to the base logic.
    """

    def __init__(self):
        self._hardwares: list[Hardware] = []
        # Insert spaces before capital letters (except the first one)
        self._pretty_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', type(self).__name__)
        """Value returned by the ``.pretty_name`` property. Default value is a prettified class name."""

    def check_availability(self) -> tuple[bool, str]:
        """Checks the availability of this Sensor Source: if it can be used (initialized) or not.

        The availability of a SensorSource may depend on external variables, such as a user-set property
        on the SensorSource or existence of some external library. This method can be used to check these
        conditions to make sure the SensorSource is ready to be used.

        Base implementation in SensorSource always returns `True, ""`. Subclasses should override this to
        implement their own logic. Note that this method may be called several times at the same frame,
        so it's best to be performant.

        Returns:
            tuple[bool, str]: a `ok, message` tuple, with:
            * `ok` being a boolean value indicating if the SensorSource is valid and can be initialized.
            * `message` being a string indicating the status of the SensorSource: why it can be initialized or not.
        """
        return True, "Always Available"

    def initialize(self):
        """Initializes this SensorSource, acquiring any needed resources to create our Hardware objects.

        Subclasses should override this method to implement their own initialization logic. Add any created
        Hardware objects to our ``._hardwares`` list.
        """
        raise NotImplementedError()

    def shutdown(self):
        """Shuts down this SensorSource, releasing any stored resources and Hardware objects.

        Base implementation in `SensorSource` only clears our `_hardwares` list. Subclasses may override
        this to add their own specific shutdown logic.
        """
        self._hardwares.clear()

    def get_all_hardware(self) -> list['Hardware']:
        """Gets a list of Hardware objects provided by this SensorSource.
        This should return an empty list if the SensorSource is not initialized.
        """
        return self._hardwares

    @property
    def pretty_name(self) -> str:
        """Gets a pretty representation of this SensorSource's name.

        The default ``.pretty_name`` property implementation in SensorSource returns the prettified
        class name (inserting spaces before capital letters). Subclasses may just change ``self._pretty_name``
        to set the name to another value.
        """
        return self._pretty_name

    def update(self):
        """Updates our hardware, to update all of our sensors.

        The base implementation in SensorSource calls `update()` in all our hardware objects.

        This is expected to be a costly call, performance wise. Usually the ComputerSystem singleton
        will call this asynchronously.
        """
        for hw in self.get_all_hardware():
            hw.update()

    def render_editor(self):
        """Renders IMGUI controls to edit settings of this SensorSource instance.

        Base implementation in SensorSource uses ``render_all_properties(self)`` to render
        all of the instance's imgui-properties.
        """
        render_all_properties(self)

    def load_data(self, data: dict):
        """Loads persisted data from the given dict into this SensorSource instance.

        Base implementation in SensorSource uses ``restore_prop_values_to_object()`` to load
        data into all of our imgui-properties.

        The data received here should've been previously acquired via ``self.get_data()``.
        """
        restore_prop_values_to_object(self, data)

    def get_data(self) -> dict:
        """Gets data (as a pickable dict) from this instance to persist.

        Base implementation in SensorSource uses ``get_all_prop_values_for_storage()`` to get
        all data from our imgui-properties as a dict.

        The data returned by this will be eventually used by ``self.load_data(data)`` to update
        the instance.
        """
        return get_all_prop_values_for_storage(self)

    @classmethod
    def get_all_subclasses(cls):
        """Recursively gets all subclasses of this class, and organizes them into a `{name: class}` dict.

        Only user-creatable subclasses are included in the result (see ``libasvat.imgui.general.is_user_creatable()``).

        Returns:
            dict[str,type[SensorSource]]: a `{name: class}` dict of all subclasses of this class, and their sub-subclasses
            recursively.
        """
        subclasses: dict[str, type[SensorSource]] = {}
        for subcls in cls.__subclasses__():
            if is_user_creatable(subcls):
                subclasses[subcls.__name__] = subcls
            subclasses.update(subcls.get_all_subclasses())
        return subclasses


class HardwareType(Enum):
    """Enumeration of possible Hardware types."""
    Motherboard = "Motherboard"
    SuperIO = "SuperIO"
    CPU = "CPU"
    GPU = "GPU"
    Memory = "Memory"
    Storage = "Storage"
    Network = "Network"
    Cooler = "Cooler"
    EmbeddedController = "EmbeddedController"
    PSU = "PSU"
    Battery = "Battery"
    PowerMonitor = "PowerMonitor"
    Unknown = "Unknown"

    @classmethod
    def from_obj(cls, obj):
        """Gets the HardwareType enum value that matches the given object's string-representation.
        The comparison/matching is case-insensitive."""
        obj_txt = str(obj).lower()
        for hwtype in cls:
            if hwtype.value.lower() == obj_txt:
                return hwtype
        return cls.Unknown

    def __str__(self):
        return self.value


class SensorType(Enum):
    """Enumeration of possible Sensor types, usually representing what the sensor measures."""
    Voltage = "Voltage"
    Current = "Current"
    Power = "Power"
    Clock = "Clock"
    Temperature = "Temperature"
    Load = "Load"
    """Load in percentage usage."""
    Frequency = "Frequency"
    Fan = "Fan"
    Flow = "Flow"
    Control = "Control"
    Level = "Level"
    Factor = "Factor"
    Data = "Data"
    SmallData = "SmallData"
    Throughput = "Throughput"
    TimeSpan = "TimeSpan"
    Timing = "Timing"
    Energy = "Energy"
    Noise = "Noise"
    Conductivity = "Conductivity"
    Humidity = "Humidity"
    Unknown = "Unknown"

    @classmethod
    def from_obj(cls, obj):
        """Gets the SensorType enum value that matches the given object's string-representation.
        The comparison/matching is case-insensitive."""
        obj_txt = str(obj).lower()
        for hwtype in cls:
            if hwtype.value.lower() == obj_txt:
                return hwtype
        return cls.Unknown

    def __str__(self):
        return self.value


class Hardware:
    """Represents a Hardware device on the system.

    Hardware are the "building blocks" of the system: your CPU, GPU, Memory, etc.
    Amongst other things, a hardware may contain ``InternalSensor``s and other "children" sub-Hardware (which are other Hardware objects).

    NOTE: this base class has abstract properties that need to be overriden by subclasses in order to properly implement the
    class to their sensor source. These are: `id`, `name` and `type`.
    """

    def __init__(self, parent: 'Hardware', isensors: list['InternalSensor'], children: list['Hardware']):
        self._parent = parent
        self._isensors: list[InternalSensor] = isensors
        self._children: list[Hardware] = children

    @property
    def id(self) -> str:
        """Gets the unique identifier of this hardware"""
        raise NotImplementedError()

    @property
    def name(self) -> str:
        """Gets the name of this hardware"""
        raise NotImplementedError()

    @property
    def type(self) -> HardwareType:
        """Gets the type of this hardware"""
        raise NotImplementedError()

    ###############

    @property
    def children(self) -> list['Hardware']:
        """Gets the list of children of this hardware.
        These are the direct children, there is no recursion to also get the sub-children and so on.
        """
        return self._children.copy()

    @property
    def isensors(self) -> list['InternalSensor']:
        """Gets a list of the InternalSensors of this hardware.
        Doesn't include sensors from sub-hardware, see ``self.get_all_isensors()`` for that."""
        return self._isensors.copy()

    @property
    def root_type(self) -> HardwareType:
        """Gets the type of our 'root' parent hardware, which is the parent of our parent and so on, until reaching the parent with no parent."""
        if self._parent is not None:
            return self._parent.root_type
        return self.type

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
        """Gets a list of all existing Sensor objects that use a InternalSensor from this hardware
        (does not include sensors from children hardware).
        """
        return sum((isen.sensors for isen in self.isensors), [])

    def update(self):
        """Updates this hardware, updating all of our sensors if we're enabled.

        Subclasses might need to override this method to perform their own hardware update logic.
        Remember to call this base method to also update our InternalSensors and children hardware.
        """
        if self.enabled:
            for isensor in self.isensors:
                isensor.update()
            for child in self.children:
                child.update()

    def __iter__(self) -> Iterator['Sensor']:
        return itertools.chain(iter(self.sensors), *(iter(child) for child in self.children))

    def get_all_isensors(self) -> Iterator['InternalSensor']:
        """Returns an iterator of all InternalSensors of this hardware and recursively of all sub-hardware we have."""
        return itertools.chain(iter(self.isensors), *(child.get_all_isensors() for child in self.children))

    def get_sensors_by_type(self, stype: SensorType, recursive=False):
        """Gets all of our current sensors of the given type.

        Args:
            stype (SensorType): Type of sensors to acquire.
            recursive (bool, optional): If true, will also check sensors of all sub-hardware recursively. Defaults to False.

        Returns:
            list[Sensor]: the sensors of the given type.
        """
        if recursive:
            return [s for s in self if s.type is stype]
        return [s for s in self.sensors if s.type is stype]

    def __str__(self):
        return self.full_name


class SensorID(str):
    """Represents the unique identification value of a InternalSensor.

    This is just a `string`. But by using this sub-class, we can better document (by typing) the
    places that should/are using a Sensor ID, and we can easily allow a custom editing of this
    value in IMGUI with our TypeEditors to only allow selecting valid sensor IDs as value.

    The editing part is particularly useful when the sensors are used as nodes in a UISystem graph.
    """


@dataclass
class SensorUnitData:
    id: str
    """Unit identifier (usually SI)."""
    limits: Vector2
    """Default min/max limits of this unit."""
    types: set[SensorType]
    """SensorTypes that use this Unit."""
    value_format: str
    """Format-string to convert a numeric value of this unit to human-readable text."""


class SensorUnit(SensorUnitData, Enum):
    """Enum of all possible Sensor Units.

    Each item also associates its unit to the internal sensor types. A few sensor types share the same unit, while a few
    sensor types have the same unit but on different orders of magnitude (such as Hz and MHz). When possible the unit is from SI.

    Each unit also contains a few other attributes related to it, such as default min/max limits and more.
    """
    VOLTAGE = ("V", Vector2(1, 1.5), {SensorType.Voltage}, "{:.3f}")
    CURRENT = ("A", Vector2(5, 90), {SensorType.Current}, "{:.3f}")
    CLOCK = ("MHz", Vector2(1000, 6000), {SensorType.Clock}, "{:.1f}")
    PERCENT = ("%", Vector2(0, 100), {SensorType.Load, SensorType.Level, SensorType.Control, SensorType.Humidity}, "{:.1f}")
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
    TIMING = ("ns", Vector2(), {SensorType.Timing}, "{:.3f}")
    NOISE = ("dBA", Vector2(), {SensorType.Noise}, "{:.0f}")
    CONDUCTIVITY = ("µS/cm", Vector2(), {SensorType.Conductivity}, "{:.1f}")
    UNKNOWN = ("<WAT>", Vector2(), {SensorType.Unknown}, "{}")

    def __str__(self):
        return self.id

    @classmethod
    def from_type(self, stype: SensorType):
        """Gets the SensorUnit that is used for the given sensor type.

        Args:
            stype (SensorType): SensorType to get default unit for.

        Returns:
            SensorUnit: the default unit for the given type.
        """
        for unit in self:
            if stype in unit.types:
                return unit
        return self.UNKNOWN


class InternalSensor:
    """Represents a single sensor from a hardware device.

    This class is responsible for communication with the underlying lib/API that is the source of sensor data, providing the
    data for a single sensor identified by an unique ID. It's expected that for a given ID, only a single InternalSensor instance
    will exist within all `Hardware` objects and their root `SensorSource` object.

    A ``SensorSource`` should always create all of its ``InternalSensor``s objects upon initialization. Since implementations
    of this class may contain native objects, it is expected that this class won't be pickable. However, the sensor's ID (a
    `SensorID` object, which is a string) can be pickled to identify the sensor in persistence scenarios.

    A ``InternalSensor`` contains refs to all ``Sensor`` nodes that use it. The ``Sensor`` class is the proper API to access/use sensor
    data, and it uses its ``InternalSensor`` object internally to access the underlying data.

    NOTE: this base class has abstract properties that need to be overriden by subclasses in order to properly implement the
    class to their sensor source. These are: `id`, `name`, `type`, `limits`, `value` and `value_range`.
    """

    def __init__(self, parent_hw: Hardware):
        # FIXED SENSOR-RELATED ATTRIBUTES
        self._sensors: list[Sensor] = []
        self.parent = parent_hw
        """Parent hardware of this sensor."""
        self._unit: SensorUnit = None

    @property
    def id(self) -> SensorID:
        """Gets the sensor ID. This uniquely identifies this sensor (and is reasonably human-readable).

        NOTE: This should be overriden by subclasses for implementation.
        """
        raise NotImplementedError()

    @property
    def name(self) -> str:
        """Gets the sensor name. Some different sensors may have the same name.

        NOTE: This should be overriden by subclasses for implementation.
        """
        raise NotImplementedError()

    @property
    def type(self) -> SensorType:
        """Gets the type of this sensor. This specifies which kind of data it measures/returns, such as Temperature, Power, Frequency, Load, etc.

        While this `type` indicates the kind of data this sensor measures, our `unit` property indicates the unit used by the sensor.

        NOTE: This should be overriden by subclasses for implementation.
        """
        raise NotImplementedError()

    @property
    def limits(self) -> Vector2 | None:
        """Gets the sensor limits as a (min, max) Vector2 object.

        These are the sensor provided limits to the data it measures. As such, it might be None.

        For example, for temperature sensors in CPUs or GPUs, the sensor may provide this limit as the temperature value for that
        hardware in which thermal throttling occurs.

        NOTE: This should be overriden by subclasses for implementation.
        """
        raise NotImplementedError()

    @property
    def value(self) -> float:
        """Gets the current value of this sensor.

        NOTE: This should be overriden by subclasses for implementation.
        """
        raise NotImplementedError()

    @property
    def value_range(self) -> Vector2:
        """Gets the minimum/maximum recorded sensor values as a (min, max) Vector2 object.

        NOTE: This should be overriden by subclasses for implementation.
        """
        raise NotImplementedError()

    ###############

    @property
    def unit(self) -> SensorUnit:
        """Unit of this sensor, based on our type (usually in SI units).

        The default implementation of this property simply returns the unit stored internally
        at ``self._unit``. If that attribute is None, we'll get the unit from our `type`
        and store it.

        Subclasses may override this if needed to specify a unit differently, or simply directly set
        the ``self._unit`` value.
        """
        if self._unit is None:
            self._unit = SensorUnit.from_type(self.type)
        return self._unit

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
        """Gets the Sensor nodes associated with this InternalSensor/SensorID.

        A Sensor node is the proper API for accessing/changing sensor data within the LCARSMonitor,
        while this InternalSensor is only mostly a wrapper to the native sensor data source.

        See ``self.create()`` to create and associate a Sensor to this InternalSensor.
        """
        return self._sensors

    def create(self):
        """Creates a Sensor object associated with this InternalSensor/ID.

        Returns:
            Sensor: newly created Sensor object.
        """
        from lcarsmonitor.sensors.sensor_node import Sensor
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

    def update(self):
        """Updates this InternalSensor, calling update() on all our existing Sensor nodes."""
        for sensor in self.sensors:
            sensor.update()
