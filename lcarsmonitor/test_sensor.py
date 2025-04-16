import math
import random


class TestIHardware:
    """A Python implementation of the ``LibreHardwareMonitorLib.Hardware.IHardware`` interface.

    This doesn't actually inherit/implement/etc the C# interface, we only implement all attributes that
    this python lib expects the interface to have.

    Purpose of this is to create local dummy hardware for testing sensor-related code/features, without
    needing to load and use actual sensors from the computer. These test classes are used internally by
    the Sensor System, enabling code to use these test hardwares as any other (real) hardware.
    """

    def __init__(self):
        self._id = "/test"
        self._type = "Test"
        self._name = "Dummy"
        self._sensors = [TestISensor(self._id), RandomTestISensor(self._id)]
        self._subhardware: list[TestIHardware] = []

    @property
    def Identifier(self) -> str:
        return self._id

    @property
    def HardwareType(self) -> str:
        return self._type

    @property
    def Name(self) -> str:
        return self._name

    @property
    def Sensors(self) -> list:
        return self._sensors

    @property
    def SubHardware(self) -> list:
        return self._subhardware

    def Update(self):
        for sensor in self._sensors:
            sensor.update_test_sensor()


class TestISensor:
    """A Python implementation of the ``LibreHardwareMonitorLib.Hardware.ISensor`` interface.

    This doesn't actually inherit/implement/etc the C# interface, we only implement all attributes that
    this python lib expects the interface to have.

    Purpose of this is to create local dummy sensors for testing sensor-related code/features, without
    needing to load and use actual sensors from the computer. These test classes are used internally by
    the Sensor System, enabling code to use these test sensors as any other (real) sensor.

    This base TestISensor implementation simply cycles through 0-100 values, as a Load-type sensor.
    """

    def __init__(self, parent_id):
        self._name = "Tester"
        self._type = "Load"  # One of the possible `SensorType`s. Load is basic % unit, has default 0-100 limit.
        self._parent_id = parent_id
        self._value = 0
        self._min = None
        self._max = None
        self._crit_low_limit = None
        self._crit_high_limit = None
        self._low_limit = None
        self._high_limit = None

    @property
    def Identifier(self) -> str:
        return f"{self._parent_id}/{self._type.lower()}/{self._name.lower()}/0"

    @property
    def Name(self) -> str:
        return self._name

    @property
    def Value(self) -> float:
        return self._value

    @property
    def Min(self) -> float:
        return self._min

    @property
    def Max(self) -> float:
        return self._max

    @property
    def SensorType(self) -> str:
        return self._type

    @property
    def CriticalLowLimit(self) -> float | None:
        return self._crit_low_limit

    @property
    def CriticalHighLimit(self) -> float | None:
        return self._crit_high_limit

    @property
    def LowLimit(self) -> float | None:
        return self._low_limit

    @property
    def HighLimit(self) -> float | None:
        return self._high_limit

    def update_test_sensor(self):
        """Updates this TestISensor's values in order to simulate an actual sensor with its changing values.

        Base implementation calls ``self._update_test_increment_value(0, 100, random in [1,2])`` and ``self._update_test_minmax()``.
        """
        self._update_test_increment_value(0, 100, random.random() + 1)
        self._update_test_minmax()

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


class RandomTestISensor(TestISensor):
    """Another dummy ISensor class for testing. This reports random values."""

    def __init__(self, parent_id):
        super().__init__(parent_id)
        self._name = "Random"

    def update_test_sensor(self):
        self._value = random.random() * 100
        self._update_test_minmax()


class TestIComputer:
    """A Python implementation of the ``LibreHardwareMonitorLib.Hardware.Computer`` class.

    This doesn't actually inherit/implement/etc the C# class, we only implement all attributes that
    this python lib expects the interface to have.

    Purpose of this is to create local dummy sensors for testing sensor-related code/features, without
    needing to load and use actual sensors from the computer. These test classes are used internally by
    the Sensor System, enabling code to use these test sensors as any other (real) sensor.
    """

    def __init__(self):
        self.IsCpuEnabled: bool = False
        self.IsGpuEnabled: bool = False
        self.IsMemoryEnabled: bool = False
        self.IsMotherboardEnabled: bool = False
        self.IsStorageEnabled: bool = False
        self.IsNetworkEnabled: bool = False
        self._hardware: list[TestIHardware] = [TestIHardware()]

    @property
    def Hardware(self):
        return self._hardware

    def Open(self):
        pass

    def Close(self):
        pass
