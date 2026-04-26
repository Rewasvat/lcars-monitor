import libasvat.command_utils as cmd_utils
import libasvat.imgui.editors.primitives as primitives
from libasvat.data import DataCache


class MonitorAppData(metaclass=cmd_utils.Singleton):
    """Struct containing data and other user settings for the Monitor App window."""

    def __init__(self):
        # Setup default attributes
        self.in_edit_mode: bool = True
        """If the Monitor is in Edit mode or in Display mode."""
        self.selected_system: str = None
        """Name of the selected UISystem to display."""
        self._use_borderless_display: bool = False
        self._idle_fps: int = 1
        self._window_fps: int = 60
        # Load persisted values from DataCache
        cache = DataCache()
        data = cache.get_data("monitor_data", {})
        self.__dict__.update(data)

    @primitives.bool_property()
    def use_borderless_display(self) -> bool:
        """If the DISPLAY mode window should be borderless.

        Borderless windows have larger areas since they have no borders or title bars, but can still be moved around, resized and closed as usual.

        The borderless window has a "dummy" title bar that appears when the mouse hovers over the top-region of the window. Clicking & dragging
        it allows moving the window, and clicking the "X" button closes it. When the lower-right corner is hovered, a "resize" widget appears,
        allowing click & drag to resize the window.

        The downside is that the window can't be maximized as usual, and its selected size/position in your desktop isn't always properly saved
        at the moment.
        """
        return self._use_borderless_display

    @use_borderless_display.setter
    def use_borderless_display(self, value: bool):
        self._use_borderless_display = value

    @primitives.int_property(min=1, max=30, is_slider=True)
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

    @primitives.int_property(min=0, max=240, is_slider=True)
    def window_fps(self) -> int:
        """FPS at which the window will run when the app is NOT IDLE.

        The app is considered not-idle when user interaction is detected, or if idling is disabled.
        When running (non-idling), the window tries to run at the maximum FPS the system performance allows it.
        This setting can then cap the maximum FPS of the window to this value. If this value is 0, the FPS will be uncapped.

        If idling is enabled and no user interaction is detected after a little while, the window will change into the idle mode,
        using the ``idle_fps`` cap.

        Note that this is just the "target" FPS cap. The actual FPS when running may be lower depending on the system performance,
        and even without a FPS cap, the monitor's refresh rate might be the window's upper limit for frame rate.

        It is recommended to set this to a value that allows smooth interactions with the GUI, like something between 30 and 60 FPS,
        even if your PC can run it higher like 120 or more. That's because running the Monitor GUI in a higher refresh rate will have
        little visual/UX benefit, while consuming more CPU/GPU resources.
        And while gaming, for example, the monitor will most likely be in a IDLE state anyway.
        """
        return self._window_fps

    @window_fps.setter
    def window_fps(self, value: int):
        self._window_fps = value

    def save(self):
        """Saves the MonitorAppData to LCARSMonitor's DataCache for persistence."""
        cache = DataCache()
        data = vars(self)
        cache.set_data("monitor_data", data)
