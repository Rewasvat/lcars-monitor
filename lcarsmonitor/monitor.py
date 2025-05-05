import click
import lcarsmonitor.sensors.sensors as sensors
import libasvat.command_utils as cmd_utils
import libasvat.utils as utils
import libasvat.imgui.windows as windows
import libasvat.imgui.general as imgui_utils
import libasvat.imgui.type_editor as types
from libasvat.imgui.popups import button_with_confirmation, TextInputPopup
from libasvat.imgui.colors import Colors
from libasvat.data import DataCache
from imgui_bundle import imgui, imgui_ctx


class MonitorAppData:
    """Struct containing data and other user settings for the Monitor App window."""

    def __init__(self):
        self.in_edit_mode: bool = True
        """If the Monitor is in Edit mode or in Display mode."""
        self.selected_system: str = None
        """Name of the selected UISystem to display."""
        self._update_time: float = 1.0
        self._use_borderless_display: bool = False
        self._idle_fps: int = 1

    @property
    def update_time(self) -> float:
        """Time between sensor updates (in seconds).

        Every this amount of time, the sensors will be polled for new data, updating their values.

        Lower values will make the sensors update more often, but will also increase CPU usage.
        Default is 1 second.
        """
        return self._update_time

    @update_time.setter
    def update_time(self, value: float):
        self._update_time = value
        computer = sensors.ComputerSystem()
        computer.update_time = self._update_time

    @types.int_property(min=1, max=60, is_slider=True)
    def sensor_polling_rate(self) -> int:
        """Number of times per second the sensors will be polled for new data, updating their values.

        Higher values will make the sensors update more often, but will also increase CPU usage.
        Default is 1 update per second.
        """
        return 1.0 / self.update_time

    @sensor_polling_rate.setter
    def sensor_polling_rate(self, value: int):
        self.update_time = 1.0 / max(1, value)

    @types.bool_property()
    def use_borderless_display(self) -> bool:
        """If the DISPLAY mode window should be borderless.

        Borderless windows have larger areas since they have no borders or title bars, but can still be moved aroundm resized and closed as usual.

        The window has a "dummy" title bar that appears when the mouse hovers over the top-region of the window. Clicking and dragging it allows
        moving the window, and clicking the "X" button closes it. When the lower-right corner is hovered, a "resize" widget appears, allowing
        clicking&dragging to resize the window.

        The downside is that the window can't be maximized as usual, and its selected size/position in your desktop isn't always properly saved
        at the moment.
        """
        return self._use_borderless_display

    @use_borderless_display.setter
    def use_borderless_display(self, value: bool):
        self._use_borderless_display = value

    @types.int_property(min=1, max=30, is_slider=True)
    def idle_fps(self) -> int:
        """FPS at which the window will run when the app is idle.

        The app is considered idle when no user interaction is detected for a few seconds.
        When idling the FPS is capped to this value, which will reduce the CPU usage of the app.

        If any user interaction is detected, the FPS cap will be removed and the app will run at the
        maximum FPS possible, until it idles again.

        Note that this is just the "target" FPS cap. The actual FPS when idling may be lower depending on the system performance.

        FPS Idling can be toggled on/off in the app's menu or status bar when in EDIT mode.
        """
        return self._idle_fps

    @idle_fps.setter
    def idle_fps(self, value: int):
        self._idle_fps = value

    def save(self):
        """Saves the MonitorAppData to LCARSMonitor's DataCache for persistence."""
        cache = DataCache()
        data = vars(self)
        cache.set_data("monitor_data", data)

    @classmethod
    def load(cls):
        """Loads a persisted MonitorAppData instance from LCARSMonitor's DataCache."""
        cache = DataCache()
        data = cache.get_data("monitor_data", {})
        obj = cls()
        obj.__dict__.update(data)
        return obj


# TODO: refatorar MonitorApp pra ter 2 modos de display: EDIT e DISPLAY (names pending)
#   * DISPLAY:
#       - right-click menu:
#           - QUIT
#           - trocar pro EDIT (se for possível) (atalho de teclado pra isso)
#           - opções pra mudar os settings (como no edit)? essas talvez tenham que reiniciar o app (reabrir a janela)...
#   * EDIT:
#       - poder configurar settings:
#           - se DISPLAY mode vai ser borderless-window ou não
#           - se DISPLAY mode vai ser fullscreen ou não
class SystemMonitorApp(windows.AppWindow):
    """System Monitor App.

    This is the main System Monitor App, opened by the ``monitor open`` or ``monitor edit`` commands, which allows
    the use of UI Systems. A UI System is a user-configurable GUI system that can display widgets, sensor data (from
    the local machine), supports interactions, and more.

    Which actual window is opened along with this App depends if `edit_mode`  is selected or not. According to it, the opened window is:
    * The EDIT Window: allows user to create, edit, visualize and delete UI Systems, as well as select the `main` system.
    This is a regular window, that supports viewports and docking nodes to allow user to see/edit multiple systems at once
    across several monitors.
    * The DISPLAY Window: only allows user to visualize (and interact with) the selected `main` system. This is a borderless
    window.

    NOTE: for now, while the edit_mode flag is persisted, it must be used manually by passing it as arg to the constructor,
    forcing to use one mode or the other. The two different commands (``open``/``edit``) do this. Its because trying to change
    the mode (and window) programatically during the same LCARSMonitor session caused several issues... So for now this way it works.
    """

    def __init__(self, force_edit_mode=None, forced_system_name: str = None):
        data = MonitorAppData.load()
        if force_edit_mode is not None:
            data.in_edit_mode = force_edit_mode
        title_suffix = "Edit" if data.in_edit_mode else "Display"
        super().__init__(f"System Monitor {title_suffix}", windows.RunnableAppMode.DOCK)
        self.data = data
        self.do_restart = False
        self._forced_system_name = forced_system_name
        from lcarsmonitor.system.system import UISystem, UIManager
        self.system_manager = UIManager()
        self.opened_systems: dict[str, UISystem] = {}
        self._reset_window_attrs()

    @property
    def selected_system(self) -> str:
        """Name of the selected UISystem to display.

        This is a read-only property that also considers if the Monitor was opened with a forced system name.
        To get/set the actual persisted main system name, use `self.data.selected_system` instead.
        """
        if self._forced_system_name is not None:
            return self._forced_system_name
        return self.data.selected_system

    @property
    def _in_edit_mode(self):
        """If the Monitor app is in Edit mode (or in Display mode)."""
        return self.data.in_edit_mode

    @_in_edit_mode.setter
    def _in_edit_mode(self, value: bool):
        self.data.in_edit_mode = value

    def _reset_window_attrs(self):
        """Sets Basic/AppWindow attributes we inherit."""
        self.mode = windows.RunnableAppMode.DOCK if self._in_edit_mode else windows.RunnableAppMode.SIMPLE
        self.show_app_menu = self._in_edit_mode
        self.show_menu_bar = self._in_edit_mode
        self.show_status_bar = self._in_edit_mode
        self.enable_viewports = self._in_edit_mode
        self.use_borderless = (not self._in_edit_mode) and (self.data.use_borderless_display)
        self.debug_menu_enabled = True

    def render(self):
        if imgui.is_key_chord_pressed(imgui.Key.mod_ctrl | imgui.Key.mod_shift | imgui.Key.q):
            self.close()
        if imgui.is_key_chord_pressed(imgui.Key.mod_ctrl | imgui.Key.end):
            self.change_mode()

        delta_t = imgui.get_io().delta_time
        sensors.ComputerSystem().timed_update(delta_t)

        if self._in_edit_mode:
            self._render_edit_mode()
        else:
            self._render_display_mode()

    def _render_edit_mode(self):
        """Renders contents of this window when in EDIT mode."""
        self.update_closed_systems()

    def _render_display_mode(self):
        """Renders contents of this window when in DISPLAY mode."""
        system = self.opened_systems.get(self.selected_system)
        if system:
            window_flags = imgui.WindowFlags_.no_scrollbar | imgui.WindowFlags_.no_scroll_with_mouse
            with imgui_ctx.begin_child("SystemDisplay", window_flags=window_flags):
                system.render()
        elif self.selected_system is not None:
            imgui.text_colored(Colors.red, f"Invalid UISystem name '{self.selected_system}'\nOpen monitor in EDIT mode to select a system.")
        else:
            imgui.text_colored(Colors.red, "No UISystem selected.\nOpen monitor in EDIT mode to select a system.")

    def on_init(self):
        super().on_init()
        computer = sensors.ComputerSystem()
        computer.open()
        computer.update_time = self.data.update_time
        self.children.clear()
        self.update_closed_systems()
        if self._in_edit_mode:
            self.add_child_window(MonitorMainWindow(self))
        else:
            self.update_opened_system(self.selected_system)

    def on_before_exit(self):
        for system in self.opened_systems.values():
            system.save_config()
        self.system_manager.save()
        # TODO: persistir systems abertos pra edicao/display?
        self.data.save()
        super().on_before_exit()

    def change_mode(self):
        """Changes the GUI mode of the Monitor App between EDIT and DISPLAY.

        This updates the wanted mode and closes the app, which will save all opened systems and configs, and persist
        all data to disk. Then, the app will be restarted in the newly selected mode.

        Restarting the app is required since DISPLAY and EDIT modes are essentially different main app-windows.
        """
        self._in_edit_mode = not self._in_edit_mode
        self.do_restart = True
        self.close()

    def create_new_system(self, name: str):
        """Creates a new UISystem config with the given NAME, if available.

        This will also instantiate the (empty) system, and open its Display and Edit windows.
        """
        if self.system_manager.has_config(name):
            click.secho(f"Can't create new system named '{name}'", fg="red")
            return False
        from lcarsmonitor.system.system import UISystem
        system = UISystem(name)
        self.opened_systems[name] = system
        self.system_manager.update_system(system)
        this_dock_id = imgui.get_window_dock_id()
        self.open_system_display(name).force_dock_id = this_dock_id
        self.open_system_edit(name).force_dock_id = this_dock_id
        click.secho(f"Created new system {name}!", fg="green")
        return True

    def delete_system(self, name: str):
        """Deletes the UISystem with the given NAME.

        The system's config is deleted and removed from the UIManager and persisted configs.
        If the system was opened, it is stopped/deleted, and if its Display or Edit window were opened,
        they are closed as well.
        """
        # Delete instantiated system
        system = self.opened_systems.pop(name, None)
        if system is not None:
            system.clear()
        # Delete system config from manager
        self.system_manager.remove_config(name)
        # Remove system windows, if opened
        display_window = self.get_display_window(name)
        if display_window:
            display_window.hide()
        edit_window = self.get_edit_window(name)
        if edit_window:
            edit_window.hide()
        # If system was the selected one, clear that
        if self.data.selected_system == name:
            self.data.selected_system = None
        click.secho(f"Deleted system {name}", fg="green")

    def open_system_display(self, name: str):
        """Opens a System Display window for the system with the given NAME.
        This allows visualization and interaction with the UI System.

        Only works if the window isn't already opened (see `has_display_window`).
        Will use the same opened system instance if available, otherwise will instantiate the system
        and store it."""
        if self.update_opened_system(name) and not self.has_display_window(name):
            window = MonitorDisplaySystemWindow(name, self)
            self.add_child_window(window)
            return window

    def get_display_window(self, name: str):
        """Gets a System Display window for the given system NAME, if opened."""
        for window in self.children:
            if isinstance(window, MonitorDisplaySystemWindow):
                if window.system_name == name:
                    return window

    def has_display_window(self, name: str):
        """Checks if a System Display window for the given system name is already opened."""
        return self.get_display_window(name) is not None

    def open_system_edit(self, name: str):
        """Opens a System Edit window for the system with the given NAME.
        This allow editing of the UISystem.

        If the System Display window is also opened for this same system, then the changes can be seen in real-time.

        Only works if the window isn't already opened (see `has_edit_window`).
        Will use the same opened system instance if available, otherwise will instantiate the system
        and store it.
        """
        if self.update_opened_system(name) and not self.has_edit_window(name):
            window = MonitorEditSystemWindow(name, self)
            self.add_child_window(window)
            return window

    def get_edit_window(self, name: str):
        """Gets a System Edit window for the given system NAME, if opened."""
        for window in self.children:
            if isinstance(window, MonitorEditSystemWindow):
                if window.system_name == name:
                    return window

    def has_edit_window(self, name: str):
        """Checks if a System Edit window for the given system name is already opened."""
        return self.get_edit_window(name) is not None

    def update_opened_system(self, name: str):
        """Checks if the UISystem with the given name is opened (instantiated).

        If it isn't, then the system will be instantiated and stored for use by the Display or Edit windows.

        Args:
            name (str): name of the UISystem to check

        Returns:
            bool: if the system exists (or was successfully instantiated). False if system isn't opened and couldn't
            be instantiated.
        """
        if name in self.opened_systems:
            return True
        config = self.system_manager.get_config(name)
        if config is not None:
            system = config.instantiate()
            self.opened_systems[name] = system
            return True
        return False

    def update_closed_systems(self):
        """Checks for and closes any opened systems that are no longer being used."""
        for name in list(self.opened_systems.keys()):
            if (not self.has_display_window(name)) and (not self.has_edit_window(name)):
                if system := self.opened_systems.pop(name, None):
                    system.save_config()
                    system.clear()


class MonitorMainWindow(windows.BasicWindow):
    """Main sub-window of `MonitorApp`.

    Used mainly when the Monitor is opened in EDIT mode, this allows setting app options, handling available UISystems, and more.
    """

    def __init__(self, parent: SystemMonitorApp):
        super().__init__("Monitor Main")
        self.parent = parent
        self.system_manager = parent.system_manager
        self.can_be_closed = False
        self.new_system_popup = TextInputPopup(
            "Create New System",
            "New UI System Popup",
            "Choose the name for this new UI System.",
            validator=self.validate_new_system_name
        )

    def render(self):
        if imgui.shortcut(imgui.Key.mod_ctrl | imgui.Key.q):
            self.parent.close()

        new_system_name = self.new_system_popup.render()
        if new_system_name is not None:
            self.parent.create_new_system(new_system_name)
            self.new_system_popup.value = ""

        imgui.separator()
        imgui.text("UI Systems:")
        flags = imgui.TableFlags_.row_bg | imgui.TableFlags_.borders_h | imgui.TableFlags_.resizable
        flags |= imgui.TableFlags_.hideable | imgui.TableFlags_.sortable
        if imgui.begin_table("SystemConfigs", 7, flags):
            imgui.table_setup_scroll_freeze(1, 1)
            imgui.table_setup_column("Name")
            imgui.table_setup_column("Num Nodes")
            imgui.table_setup_column("Main")
            imgui.table_setup_column("Display")
            imgui.table_setup_column("Edit")
            imgui.table_setup_column("Initialized")
            imgui.table_setup_column("Delete")

            imgui.table_headers_row()

            for config in self.system_manager.get_all_configs():
                imgui.push_id(f"table_row_{repr(config)}")
                imgui.table_next_row(0, 1)

                imgui.table_next_column()
                imgui.text(config.name)

                imgui.table_next_column()
                imgui.text(str(config.num_nodes))

                imgui.table_next_column()
                if imgui.radio_button("##", self.parent.data.selected_system == config.name):
                    self.parent.data.selected_system = config.name
                imgui.set_item_tooltip("\n".join([
                    "Selects the 'main' UI System.",
                    "",
                    "The main system is the one used by default by the Monitor app when running in DISPLAY mode.",
                ]))

                imgui.table_next_column()
                if self.parent.has_display_window(config.name):
                    imgui.text_colored(Colors.green, "<DISPLAYED>")
                else:
                    if imgui.button("Open Display"):
                        self.parent.open_system_display(config.name)

                imgui.table_next_column()
                if self.parent.has_edit_window(config.name):
                    imgui.text_colored(Colors.green, "<EDITING>")
                else:
                    if imgui.button("Open Edit"):
                        self.parent.open_system_edit(config.name)

                imgui.table_next_column()
                if config.name in self.parent.opened_systems:
                    imgui.text_colored(Colors.green, "running")
                else:
                    imgui.text("-")

                imgui.table_next_column()
                title = f"Confirm {config.name} System Delete"
                if button_with_confirmation("Delete", title, "Are you sure you want to delete this UISystem config?"):
                    self.parent.delete_system(config.name)

                imgui.pop_id()

            imgui.end_table()

    def validate_new_system_name(self, value: str) -> tuple[bool, str]:
        """Checks if the given value is valid for a new system name.

        Args:
            value (str): possible new UISystem name to check

        Returns:
            tuple[bool, str]: a (valid, reason) tuple, which indicates if the given name is valid
            and the reason why it's invalid.
        """
        if value is None or len(value) <= 0:
            return False, "empty name."
        if self.parent.system_manager.has_config(value):
            return False, f"A System with name '{value}' already exists."
        return True, "valid"


class MonitorDisplaySystemWindow(windows.BasicWindow):
    """Sub-window used by `MonitorApp` to render a UISystem."""

    def __init__(self, system_name: str, parent: SystemMonitorApp):
        super().__init__(f"Display: {system_name}")
        self.user_closable = True
        self.parent = parent
        self.system_name = system_name

    def render(self):
        region_id = repr(self)
        window_flags = imgui.WindowFlags_.no_scrollbar | imgui.WindowFlags_.no_scroll_with_mouse
        imgui.begin_child(region_id, window_flags=window_flags)
        imgui.push_id(region_id)
        if imgui.shortcut(imgui.Key.mod_ctrl | imgui.Key.q):
            self.is_visible = False
        system = self.parent.opened_systems.get(self.system_name)
        if system:
            system.render()
        else:
            imgui.text_colored(Colors.red, "SYSTEM NOT INITIALIZED")
        imgui.pop_id()
        imgui.end_child()


class MonitorEditSystemWindow(windows.BasicWindow):
    """Sub-window used by `MonitorApp` to render a UISystem's EDIT contents (graph, etc)."""

    def __init__(self, system_name: str, parent: SystemMonitorApp):
        super().__init__(f"Edit: {system_name}")
        self.user_closable = True
        self.parent = parent
        self.system_name = system_name
        self._perform_fit = 3

    def render(self):
        region_id = repr(self)
        imgui.begin_child(region_id)
        imgui.push_id(region_id)
        if imgui.shortcut(imgui.Key.mod_ctrl | imgui.Key.q):
            self.is_visible = False
        system = self.parent.opened_systems.get(self.system_name)
        if system:
            system.render_system()
            if self._perform_fit > 0:
                # This is being done for 3 frames since using a boolean to trigger this in a single frame wasn't working on the first time
                # this window was opened in a session.
                system.fit_to_window()
                self._perform_fit -= 1
        else:
            imgui.text_colored(Colors.red, "SYSTEM NOT INITIALIZED")
        imgui.pop_id()
        imgui.end_child()
