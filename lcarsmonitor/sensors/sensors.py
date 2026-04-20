import click
import threading
import libasvat.command_utils as cmd_utils
from typing import Callable
from typing import Iterator, TYPE_CHECKING
from imgui_bundle import imgui
from libasvat.data import DataCache
from libasvat.imgui.colors import Colors
from libasvat.imgui.general import adv_button
from libasvat.imgui.editors import TypeDatabase, TypeEditor
from lcarsmonitor.sensors.sensors_api import SensorSource, Hardware, InternalSensor, SensorID
from lcarsmonitor.sensors.sources.dummy_impl import DummySensors


if TYPE_CHECKING:
    from lcarsmonitor.sensors.sensor_node import Sensor


class ComputerSystem(metaclass=cmd_utils.Singleton):
    """Singleton class that represents the Computer System we're running from.

    This is the main class from which to access hardware and sensor data from the computer.

    Wraps and builds upon ``LibreHardwareMonitorLib.Hardware.Computer`` class.
    """

    def __init__(self):
        self.all_sensors: dict[str, InternalSensor] = {}
        self.update_time: float = 1.0
        """Amount of time that must pass for our async-update-thread to trigger an actual ``update()`` (in seconds)."""
        # Async update thread support
        self._update_thread: threading.Thread = None
        self._stop_event: threading.Event = None
        self._lock: threading.Lock = None

        cache = DataCache()
        cache.add_shutdown_listener(self.close)

        self._available_sources = {name: source() for name, source in SensorSource.get_all_subclasses().items()}
        self._selected_source: str = "LibreComputer"
        # TODO: load and save selected-source from cache
        self._dummy_source = DummySensors()

    @property
    def current_source(self):
        """Gets the currently selected SensorSource instance."""
        return self._available_sources.get(self._selected_source)

    def open(self, dummy_test=False):
        """Starts the computer object, allowing us to query its hardware, sensors and more.

        Args:
            dummy_test (bool, optional): If true, will use a dummy internal Computer object, with dummy sensors that simulate actual
                sensors with changing values, for testing sensor-related code without needing to load sensors properly. Defaults to False.
        """
        if len(self.all_sensors) > 0:
            click.secho("ComputerSystem: tried to open() while already opened.", fg="yellow")
            return
        # TODO: a flag de dummy-test é pra desabilitar usar qualquer SensorSource, portanto rodando só com os DummySensors
        if self.current_source:
            self.current_source.initialize()
        self._dummy_source.initialize()
        self.all_sensors = {sensor.id: sensor for sensor in self.get_all_isensors()}
        click.secho("ComputerSystem: Initialized!", fg="magenta")
        self.start_async_update()

    def close(self):
        """Stops the computer object, releasing resources.

        This is automatically called on shutdown of LCARSMonitor."""
        if len(self.all_sensors) <= 0:
            click.secho("ComputerSystem: tried to close() while already closed.", fg="yellow")
            return
        self.stop_async_update()
        self.all_sensors.clear()
        if self.current_source:
            self.current_source.shutdown()
        self._dummy_source.shutdown()
        click.secho("ComputerSystem: Closed Computer.", fg="magenta")

    def update(self):
        """Updates our hardware, to update all of our sensors.

        NOTE: this is a costly call! Updating the native sensors takes time. So its preferable to call
        this asynchronously, using ``self.start_async_update()``.
        """
        if self.current_source:
            self.current_source.update()
        self._dummy_source.update()

    def start_async_update(self):
        """Starts a background thread to periodically call ``update()`` on hardware sensors.
        Uses ``self.update_time`` as the interval between updates (can be changed at runtime).

        This is started by default when ``self.open()`` is called.
        """
        if self._update_thread and self._update_thread.is_alive():
            return  # Already running
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        def _async_update_loop():
            while not self._stop_event.is_set():
                with self._lock:
                    self.update()
                # Use the current value of self.update_time for each wait
                self._stop_event.wait(self.update_time)
        self._update_thread = threading.Thread(target=_async_update_loop, daemon=True)
        # NOTE: if we need to get a thread-safe something, use:
        #   if lock:
        #       with lock:
        #           get/copy stuff
        #   else:
        #       get/copy stuff
        self._update_thread.start()

    def stop_async_update(self):
        """Stops the background update thread, if its running.
        This is automatically called by ``self.close()``."""
        if self._stop_event:
            self._stop_event.set()
        if self._update_thread:
            self._update_thread.join()
        self._update_thread = None
        self._stop_event = None
        self._lock = None

    def get_all_isensors(self):
        """Gets a list of all internal sensors of this system.

        Returns:
            list[InternalSensor]: list of sensors
        """
        sensors: list[InternalSensor] = []
        for hardware in self:
            sensors += list(hardware.get_all_isensors())
        return sensors

    def get_isensor_by_id(self, id_obj: str):
        """Gets the sensor with the given ID.

        Args:
            id_obj (str): the ID of the sensor to get.

        Returns:
            InternalSensor: the InternalSensor object, or None if no sensor exists with the given ID.
        """
        return self.all_sensors.get(id_obj)

    def __iter__(self) -> Iterator[Hardware]:
        all_hw = []
        if self.current_source:
            all_hw.extend(self.current_source.get_all_hardware())
        all_hw.extend(self._dummy_source.get_all_hardware())
        return iter(all_hw)


@TypeDatabase.register_editor_for_type(SensorID)
class InternalSensorEditor(TypeEditor):
    """Imgui TypeEditor for selecting a SensorID value."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.add_tooltip_after_value = False
        self.color = Colors.yellow
        self.extra_accepted_input_types = str
        self.convert_value_to_type = True

    def draw_value_editor(self, value: SensorID):
        changed = False
        new_value = value
        system = ComputerSystem()
        isen = system.get_isensor_by_id(value)
        if imgui.begin_combo("##", f"{isen.parent.full_name} / {isen.name}"):
            new_sensor = render_create_sensor_menu()
            if new_sensor:
                changed = True
                new_value = new_sensor.id
            imgui.end_combo()
        return changed, new_value


def render_create_sensor_menu(sensor_tooltip_suffix: str = "", filter: Callable[[InternalSensor], bool] = None) -> InternalSensor | None:
    """Renders the contents for a menu that allows the user to select a computer sensor.

    Args:
        sensor_tooltip_suffix (str, optional): Extra text to display at the end of the tooltip for each sensor. Defaults to "".
        filter (Callable[[InternalSensor], bool], optional): optional callable that receives a InternalSensor and returns a boolean
            indicating if the sensor can be displayed for the user to select. This only applies to the sensor itself -
            subclasses of the sensor/hardware are checked separately. If None (the default), all sensors are allowed.

    Returns:
        InternalSensor: the InternalSensor object from the ComputerSystem singleton. The object is only returned in the frame the user
        clicked to select that sensor. All other times this will return None.
    """
    def check_hw(hw: Hardware) -> bool:
        """Checks if any sensor in the given hardware (or its children hardware) can be displayed."""
        for sub_hw in hw.children:
            if check_hw(sub_hw):
                return True
        for isensor in hw.isensors:
            if filter is None or filter(isensor.name):
                return True
        return False

    def render_hw(hw: Hardware) -> InternalSensor | None:
        ret = None
        if not check_hw(hw):
            return ret
        opened = imgui.begin_menu(hw.name)
        imgui.set_item_tooltip(f"ID: {hw.id}\nTYPE: {hw.type}\n\n{hw.__doc__}")
        if opened:
            for sub_hw in hw.children:
                sub_ret = render_hw(sub_hw)
                if sub_ret:
                    ret = sub_ret
            for isensor in hw.isensors:
                if filter is None or filter(isensor.name):
                    imgui.push_id(repr(isensor))
                    if adv_button(f"{isensor.name} ({isensor.type}: {isensor.unit})", f"{isensor.info}\n\n{sensor_tooltip_suffix}", in_menu=True):
                        ret = isensor
                    imgui.pop_id()
            imgui.end_menu()
        return ret

    new_sensor = None
    # Check which of the root hardware objects of the Computer can be displayed
    checked_hardware: list[Hardware] = []
    for hardware in ComputerSystem():
        if check_hw(hardware):
            checked_hardware.append(hardware)
    if len(checked_hardware) > 0:
        # Only display the Sensor menu if we have at least one hardware to display.
        opened = imgui.begin_menu("Sensors:")
        imgui.set_item_tooltip("Select a sensor to create.\n\nA 'empty' sensor or one already set can be created directly.")
        if opened:
            for hardware in checked_hardware:
                ret = render_hw(hardware)
                if ret:
                    new_sensor = ret
            imgui.end_menu()
    return new_sensor
