##################################
# Dummy Sensor API implementation
###
# This dummy SensorSource and related Hardware/InternalSensor implementations create dummy sensors
# which can be used to test the whole LCARS system with minimal performance loss.
#
# The main ComputerSystem class may exceptionally use this SensorSource directly in order to always
# provide the dummy sensors, regardless of the selected source.
##################################
import math
import random
from libasvat.imgui.math import Vector2
from libasvat.imgui.general import not_user_creatable
from lcarsmonitor.sensors.sensors_api import SensorSource, SensorID, HardwareType, SensorType, Hardware, InternalSensor


@not_user_creatable
class DummySensors(SensorSource):
    """Dummy SensorSource. Provides dummy/mocked hardware/sensors for testing.

    Purpose of this is to create local dummy sensors for testing sensor-related code/features, without
    needing to load and use actual sensors from the computer. These test classes are used internally by
    the Sensor System, enabling code to use these test sensors as any other (real) sensor.
    """

    def __init__(self):
        super().__init__()
        self._hardwares: list[DummyHardware] = []

    def initialize(self):
        self._hardwares.append(DummyHardware())

    def shutdown(self):
        self._hardwares.clear()

    def get_all_hardware(self):
        return self._hardwares


class DummyHardware(Hardware):

    def __init__(self, parent: 'DummyHardware' = None):
        isensors = [DummySensor(self, False), DummySensor(self, True)]
        super().__init__(parent, isensors, [])

    @property
    def id(self):
        return "/test"

    @property
    def name(self):
        return "Dummy"

    @property
    def type(self):
        return HardwareType.CPU


class DummySensor(InternalSensor):

    def __init__(self, parent_hw, is_random: bool):
        super().__init__(parent_hw)
        self._is_random = is_random
        self._value = 0.0
        self._min = None
        self._max = None

    @property
    def id(self):
        return SensorID(f"/test/load/{self.name.lower()}/0")

    @property
    def name(self):
        if self._is_random:
            return "Random"
        return "Tester"

    @property
    def type(self):
        return SensorType.Load

    @property
    def limits(self):
        return None

    @property
    def value(self):
        return self._value

    @property
    def value_range(self):
        return Vector2(self._min or math.inf, self._max or -math.inf)

    def update(self):
        if self._is_random:
            self._value = random.random() * 100
        else:
            self._update_test_increment_value(0, 100, random.random() + 1)
        self._update_test_minmax()
        super().update()

    def _update_test_increment_value(self, min_value: float, max_value: float, increment=1):
        """Updates our value by incrementing it by a fixed amount. If value passes the max bound, will be
        reset to the min bound.

        Args:
            min_value (float): Minimum value possible.
            max_value (float): Maximum value possible.
            increment (float, optional): Amount to increment by. Defaults to 0.1.
        """
        self._value += increment
        if self._value > max_value:
            self._value = min_value

    def _update_test_minmax(self):
        """Updates this TestISensor's min/max values based on our current value."""
        self._min = min(self._value, self._min or math.inf)
        self._max = max(self._value, self._max or -math.inf)
