import re
import math
import click
from libasvat.imgui.math import Vector2, multiple_lerp_with_weigths
from libasvat.imgui.colors import Colors, Color
from libasvat.imgui.nodes import PinKind, Node, input_property, output_property
from lcarsmonitor.sensors import InternalSensor, SensorLimitsType, Hardware, SensorUnit, SensorID, ComputerSystem


class Sensor(Node):
    """Represents a single Sensor for a hardware device.

    A Sensor measures a single numeric value of some kind about the hardware, such as: temperature, power usage, fan speed,
    usage (%), and so on.
    The hardware itself and its drivers provide these values. LibreHardwareMonitorLib uses native APIs to query these values,
    and we can see and use here those that the lib (and your hardware) supports.

    Wraps and builds upon ``LibreHardwareMonitorLib.Hardware.ISensor`` interface.

    This class uses an InternalSensor for accessing the C# ISensor interface for the sensor with its given ID.
    As such, multiple Sensor nodes can be used with the same InternalSensor object. This is particularly useful since
    InternalSensor objects are unique for a given sensor, and are maintained by the singleton `ComputerSystem`.
    """

    def __init__(self, id: SensorID = None):
        super().__init__()
        # FIXED SENSOR-RELATED ATTRIBUTES
        self._isensor: InternalSensor = None
        self.id = id
        # NODE-RELATED ATTRIBUTES
        self.node_header_color = Color(0.3, 0, 0, 0.6)
        self.node_bg_color = Color(0.2, 0.12, 0.12, 0.75)
        from lcarsmonitor.actions import ActionFlow
        self._on_update_pin = ActionFlow(self, PinKind.output, "On Update")
        self._on_update_pin.pin_tooltip = "Triggered when this Sensor is updated, getting a new value from the hardware."
        self.add_pin(self._on_update_pin)
        self.create_data_pins_from_properties()

    # ======= MAIN PROPERTIES
    @property
    def isensor(self) -> InternalSensor:
        """The InternalSensor object of this Sensor node.

        This changes according to ``self.id``.
        """
        self._update_isensor(self.id)
        return self._isensor

    @input_property()
    def id(self) -> SensorID:
        """Gets/sets the sensor ID. This uniquely identifies this sensor (and is reasonably human-readable).

        This ID dictates from which PC sensor we'll get data. Thus, changing this will
        change the value of nearly all of our properties.
        """
        return SensorID()

    @id.setter
    def id(self, value: SensorID):
        self._update_isensor(value)
        if self.isensor is None:
            self.node_title = "Sensor\n<empty>"
        else:
            self.node_title = f"{self.hardware.full_name}\n{self.name} {self.type}"

    # ======= INPUT PROPERTIES (User settings)
    @input_property()
    def enabled(self) -> bool:
        """If this sensor is enabled. [GET/SET]

        When enabled, we can be shown in any GUI, and our parent hardware will be updated in order to update this sensor
        when the Sensor System is updated. This defaults to True.
        """
        return True  # data-pin from input_property holds our value. This is the default/initial value.

    @input_property()
    def limits_type(self) -> SensorLimitsType:
        """How to define this sensor's min/max limits. [GET/SET]

        * CRITICAL: limits from sensor's device critical limits (if they exist).
        * LIMITS: limits from sensor's device limits (if they exist).
        * MINMAX: limits are the same as the sensor's measured min/max values (always available).
        * MINMAX_EVER: limits are the same as the sensor's measured min/max values ever, across all times this has been run.
        * FIXED: limits are those set by the user. Defaults to values based on the sensor's unit (always available).
        * AUTO: limits are acquired automatically. Tries getting from the following methods, using the first that is available:
          CRITICAL > LIMITS > FIXED.  (This is the default).
        """
        return SensorLimitsType.AUTO

    @input_property()
    def custom_limits(self) -> Vector2:
        """Custom sensor limits range. [GET/SET]

        Used when ``self.limits_type`` is ``FIXED``. If None, a default limit range, based on the sensor's unit will be used.
        """
        return Vector2()

    # ======= OUTPUT PROPERTIES (Sensor data)
    @output_property(use_prop_value=True)
    def name(self) -> str:
        """Gets the sensor name. Some different sensors may have the same name."""
        return self.isensor and self.isensor.name

    @output_property(use_prop_value=True)
    def hardware(self) -> Hardware:
        """Gets the parent hardware of this sensor."""
        return self.isensor and self.isensor.parent

    @output_property(use_prop_value=True)
    def percent_value(self) -> float:
        """Gets the sensor value as a percent (in [0,1]) between the sensor's min/max limits.
        Return is clamped to [0,1] range.

        Always 0 if we have no limits (``self.limits`` is None) or if the difference between the maximum and minimum limits is 0."""
        return self.get_percent_of_value(self.value)

    @output_property(use_prop_value=True)
    def value(self) -> float:
        """The current value of this sensor."""
        return self.isensor and self.isensor.isensor.Value

    @output_property(use_prop_value=True)
    def formatted_value(self) -> str:
        """Gets the sensor's value, but formatted to the common value-format for this sensor's type."""
        try:
            if self.value is not None:
                return self.unit.value_format.format(self.value)
            return "None"
        except Exception:
            click.secho(f"FVALUE CRASH: value='{self.value}' realType='{type(self.value)}' format='{self.unit.value_format}'", fg="red")
            raise

    @output_property(use_prop_value=True)
    def minimum(self) -> float:
        """The minimum value this sensor has reached since measurements started."""
        return self.isensor and self.isensor.isensor.Min or math.inf

    @output_property(use_prop_value=True)
    def maximum(self) -> float:
        """The maximum value this sensor has reached since measurements started."""
        return self.isensor and self.isensor.isensor.Max or -math.inf

    @property
    def value_range(self):
        """Gets the minimum/maximum sensor values as a (min, max) vector2.

        These are the min/max values recorded by the sensor since the start of this our measurement."""
        return Vector2(self.minimum, self.maximum)

    @output_property(use_prop_value=True)
    def type(self) -> str:
        """Gets the type of this sensor. This specifies which kind of data it measures/returns, such
        as Temperature, Power, Frequency, Load, etc"""
        return self.isensor and self.isensor.type

    @output_property(use_prop_value=True)
    def unit(self) -> SensorUnit:
        """The sensor's unit (usually SI units)."""
        return self.isensor and self.isensor.unit

    @output_property(use_prop_value=True)
    def min_limit(self) -> float:
        """Gets the sensor's minimum limit.

        This is the "theoretical" minimum value of this sensor. If the sensor's value is lower than this, most likely
        the sensor is broken or something is (or will be) really wrong in your computer.

        The limit depends on the Limits Type of this sensor. See ``self.limits_type``.

        For example, percent values shouldn't pass the limit of 0."""
        return self.limits.x

    @output_property(use_prop_value=True)
    def max_limit(self) -> float:
        """Gets the sensor's maximum limit.

        This is the "theoretical" maximum value of this sensor. If the sensor's value is larger than this, most likely
        the sensor is broken or something is (or will be) really wrong in your computer.

        The limit depends on the Limits Type of this sensor. See `self.limits_type`.

        For example, percent values shouldn't pass the limit of 100. Temperatures shouldn't pass the device's set limits
        in order to prevent thermal throttling."""
        return self.limits.y

    @property
    def limits(self):
        """Gets the sensor limits as a (min, max) limit vector2.

        These are the "theoretical" limits of this sensor. If the sensor's value is outside this range, most likely
        the sensor is broken or something is (or will be) really wrong in your computer.

        The limit depends on the Limits Type of this sensor. See ``self.limits_type``.

        For example, percent values shouldn't pass the limit of 100. Temperatures shouldn't pass the device's set limits
        in order to prevent thermal throttling.
        """
        limit_type = self.limits_type
        if limit_type == SensorLimitsType.CRITICAL:
            return self._get_critical_limits()
        elif limit_type == SensorLimitsType.LIMITS:
            return self._get_basic_limits()
        elif limit_type == SensorLimitsType.MINMAX:
            return self.value_range
        elif limit_type == SensorLimitsType.MINMAX_EVER:
            return self.minmax_ever
        elif limit_type == SensorLimitsType.FIXED:
            return self._get_custom_limits()
        # else is only AUTO
        return self._get_critical_limits() or self._get_basic_limits() or self._get_custom_limits()

    @property
    def limits_diff(self):
        """Gets the difference between our minimum and maximum limits.
        Returns 0 if ``self.limits`` is None."""
        if self.limits is None:
            return 0.0
        return self.max_limit - self.min_limit

    @output_property(use_prop_value=True)
    def state_color(self) -> Color:
        """Gets the imgui color of this sensor, based on its current value and limits.

        This uses a few color ranges according to our unit, to interpolate from using ``self.percent_value``
        and generate the final color. Not all units supports this, in which case color defaults to white.
        """
        return self.get_color_for_value(self.value)

    @output_property()
    def minmax_ever(self) -> Vector2:
        """Gets the minimum/maximum sensor values ever recorded as a (min, max) vector2.

        These are the min/max values ever recorded by this sensor, across all times this app was executed.
        """
        # Without the use_prop_value=True flag that nearly all other output-properties here have, this property's value
        # will be persisted by NodeConfig.
        return Vector2(math.inf, -math.inf)  # default minmax ever

    # ======= METHODS
    def get_attribute(self, key: str):
        """Gets the property of this sensor whose name matches the given key"""
        conversions = {
            "min": "minimum",
            "max": "maximum",
            "identifier": "id",
            "fvalue": "formatted_value"
        }
        key = key.lower()
        key = conversions.get(key, key)
        if hasattr(self, key):
            return getattr(self, key)

    # TODO: virar action
    def format(self, format: str):
        """Utility to generate a string of formatted data from this sensor.

        Args:
            format (str): Format of string to generate. ``{key}`` tags in the string are substituted for
            the value of the sensor property ``key``. Any property from this Sensor class can be used.
            The tag can include python format specifiers. For example, to get the sensor's value with 3
            decimal plates: ``{value:.3f}``.

        Returns:
            str: the generated formatted string.
        """
        def replace(m: re.Match):
            pack: str = m.group(1)
            parts = pack.split(":")
            var_name = parts[0]
            if len(parts) <= 1:
                entry_format = "{}"
            else:
                entry_format = f"{{:{parts[1]}}}"
            return entry_format.format(self.get_attribute(var_name))

        return re.sub(r"{([^}]+)}", replace, format)

    def _get_critical_limits(self):
        """Internal method to try to get the sensor's limits from the ICriticalSensorLimits interface."""
        return self.isensor and self.isensor.critical_limits

    def _get_basic_limits(self):
        """Internal method to try to get the sensor's limits from the ISensorLimits interface."""
        return self.isensor and self.isensor.basic_limits

    def _get_custom_limits(self):
        """Internal method to get the sensor's custom (FIXED) limits."""
        user_limit = self.custom_limits
        if user_limit is None or user_limit.is_zero():
            return self.unit and self.unit.limits or Vector2()
        return user_limit

    # TODO: virar action
    def get_percent_of_value(self, value: float):
        """Gets the percent of the given value between the sensor's min/max limits.

        Args:
            value (float): any float value to calculate percent. Preferably, a past or expected
            value of the sensor.

        Returns:
            float: the percent value, in the range [0,1]  (clamped).
            Always 0 if we have no limits (``self.limits`` is None) or if the difference between the maximum and minimum limits is 0.
        """
        range = self.limits_diff
        if range == 0.0 or (value is None):
            return 0.0
        factor = (value - self.min_limit) / range
        return min(1.0, max(0.0, factor))

    # TODO: virar action
    def get_color_for_value(self, value: float) -> Color:
        """Gets the imgui color of this sensor, based on the given value and limits.

        This uses a few color ranges according to our unit, to interpolate from using ``self.get_percent_of_value(value)``
        and generate the final color. Not all units supports this, in which case color defaults to white.

        Args:
            value (float): any float value to calculate percent. Preferably, a past or expected
            value of the sensor.

        Returns:
            ImVec4: sensor color based on the value.
        """
        targets = None
        if self.unit in (SensorUnit.PERCENT, SensorUnit.FAN):
            targets = [
                (Colors.magenta, 0),
                (Colors.green, 0.0001),
                (Colors.yellow, 0.75),
                (Colors.red, 1),
            ]
        elif self.unit in (SensorUnit.TEMPERATURE, ):
            targets = [
                (Colors.red, 0),
                (Colors.green, 0.001),
                (Colors.yellow, 0.75),
                (Colors.red, 1),
            ]
        elif self.unit in (SensorUnit.POWER, SensorUnit.VOLTAGE, SensorUnit.CURRENT):
            targets = [
                (Colors.green, 0),
                (Colors.yellow, 0.75),
                (Colors.red, 1),
            ]
        elif self.unit in (SensorUnit.THROUGHPUT, SensorUnit.CLOCK):
            targets = [
                (Colors.white, 0),
                (Colors.white, 0.5),
                (Colors.yellow, 0.75),
                (Colors.red, 1),
            ]

        if targets is not None:
            return multiple_lerp_with_weigths(targets, self.get_percent_of_value(value))
        return Colors.white

    def update(self):
        """Updates this Sensor object.

        Called by our parent Hardware when he is updated.
        Does nothing if this sensor is not enabled.
        """
        if not self.enabled:
            return
        # Update minmax_ever value
        prev_minmax = self.minmax_ever
        self.minmax_ever = Vector2(min(self.minimum, prev_minmax.x), max(self.maximum, prev_minmax.y))
        # Trigger Update flow pin
        self._on_update_pin.trigger()

    def delete(self):
        super().delete()
        if self.isensor:
            self.isensor._remove(self)

    def _update_isensor(self, id: SensorID):
        """Updates our private InternalSensor object to be the one with given ID.

        Only updates if ID is valid and different from our current isensor.

        Args:
            id (SensorID): ID of isensor to use.
        """
        valid_id = id is not None and len(id) > 0
        need_update = (self._isensor is None) or (self._isensor.id != id)
        if valid_id and need_update:
            if self._isensor is not None:
                self._isensor._remove(self)
            self._isensor = ComputerSystem().get_isensor_by_id(id)
            if self._isensor is not None:
                self._isensor._add(self)
