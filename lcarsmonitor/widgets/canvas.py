import libasvat.imgui.editors.primitives as primitives
from lcarsmonitor.widgets.base import ContainerWidget, Slot
from libasvat.imgui.math import Vector2, Rectangle
from libasvat.imgui.colors import Colors
from imgui_bundle import imgui


class CanvasSlot(Slot):
    """Slot for a Canvas Container.

    Allows user-selection of the slot's position, size and few other attributes.
    """

    def __init__(self, parent: ContainerWidget, name: str):
        super().__init__(parent, name)
        self.pos_ratio: Vector2 = Vector2()
        self.size_ratio: Vector2 = Vector2(0.5, 0.5)
        self._move_offset: Vector2 = None
        self._resize_offset: Vector2 = None
        self._handling_enabled = True

    @primitives.string_property(imgui.InputTextFlags_.enter_returns_true)
    def name(self) -> str:
        """Name of this slot. User can change this, but it should be unique amongst all slots of this container. [GET/SET]"""
        return self.pin_name

    @name.setter
    def name(self, value):
        self.pin_name = value

    @primitives.vector2_property(x_range=(0, 1), y_range=(0, 1), flags=imgui.SliderFlags_.always_clamp)
    def position(self) -> Vector2:
        """The position of the slot, as a ratio of the canvas's size. [GET/SET]"""
        return self.pos_ratio

    @position.setter
    def position(self, value: Vector2):
        self.pos_ratio = value

    @primitives.vector2_property(x_range=(0, 1), y_range=(0, 1), flags=imgui.SliderFlags_.always_clamp)
    def size(self) -> Vector2:
        """The size of the slot, as a ratio of the canvas's size. [GET/SET]"""
        return self.size_ratio

    @size.setter
    def size(self, value: Vector2):
        self.size_ratio = value

    @primitives.bool_property()
    def is_handling_enabled(self) -> bool:
        """If enabled, allows the user to move and resize this slot via clicking-and-dragging the slot itself
        in its display.
        * Moving: a small circle widget is displayed at the center of the slot's area. Click & drag anywhere in the
        "inside" (away from the borders) will move the slot with the mouse.
        * Resizing: a small triangular widget is displayed at the bottom-right corner of the slot's area.
        Click & dragging it will resize the slot accordingly.

        Note that the same limits to position and size still apply.
        """
        return self._handling_enabled

    @is_handling_enabled.setter
    def is_handling_enabled(self, value: bool):
        self._handling_enabled = value

    def render(self):
        super().render()
        mouse_pos = imgui.get_mouse_pos()
        if (mouse_pos in self.area) and self.can_be_handled:
            draw = imgui.get_window_draw_list()
            widget_size = Vector2(10, 10)

            draw.add_circle_filled(self.area.center, widget_size.min_component() * 0.5, Colors.cyan.u32)
            move_area = self.area.copy()
            move_area.expand(-widget_size.min_component())
            if imgui.is_mouse_hovering_rect(move_area.position, move_area.bottom_right_pos) and imgui.is_mouse_clicked(imgui.MouseButton_.left):
                self._move_offset = self.area.position - mouse_pos

            resize_area = Rectangle(self.area.bottom_right_pos - widget_size, widget_size)
            p1 = resize_area.bottom_right_pos
            p2 = resize_area.bottom_left_pos
            p3 = resize_area.top_right_pos
            draw.add_triangle_filled(p1, p2, p3, Colors.cyan.u32)
            if imgui.is_mouse_hovering_rect(resize_area.position, resize_area.bottom_right_pos) and imgui.is_mouse_clicked(imgui.MouseButton_.left):
                self._resize_offset = p1 - mouse_pos

        if self._move_offset is not None:
            if imgui.is_mouse_down(imgui.MouseButton_.left):
                new_abs_pos = self._move_offset + mouse_pos
                new_rel_pos = (new_abs_pos - self.parent_node.area.position) / self.parent_node.area.size
                new_rel_pos.clamp(0.0, Vector2(1, 1) - self.size)
                self.position = new_rel_pos
            else:
                self._move_offset = None

        if self._resize_offset is not None:
            if imgui.is_mouse_down(imgui.MouseButton_.left):
                # Get "current" (or new) bottom-right pos based on current mouse-pos
                bottom_right = self._resize_offset + mouse_pos
                # Clamp bottom-right pos to be inside our parent's area (max size possible).
                bottom_right = bottom_right.min(self.parent_node.area.bottom_right_pos)
                # Calculate new relative size based on new bottom-right pos
                new_abs_size = bottom_right - self.area.position
                new_rel_size = new_abs_size / self.parent_node.area.size
                self.size = new_rel_size.max(Vector2(0.01, 0.01))
            else:
                self._resize_offset = None

    @property
    def is_being_handled(self):
        """Indicates if this CanvasSlot is currently being moved or resized by the user through the UI widgets.
        See ``self.can_be_handled``.
        """
        return self._move_offset is not None or self._resize_offset is not None

    @property
    def can_be_handled(self):
        """Indicates if this CanvasSlot can be moved or resized by the user through the UI widgets.

        A CanvasSlot can be handled by the user if no other slot from its parent Canvas is being handled.
        This feature is also only available in EDIT mode.
        """
        from lcarsmonitor.monitor_data import MonitorAppData
        data = MonitorAppData()
        if (not self.is_handling_enabled) or (not data.in_edit_mode):
            return False
        if self.is_being_handled:
            return True
        ok = True
        for slot in self.parent_node.slots:
            if issubclass(type(slot), CanvasSlot) and slot.is_being_handled:
                ok = False
                break
        return ok


class Canvas(ContainerWidget):
    """A Canvas widget container.

    User can control position and size of each slot individually, the container has no logic automatically setting
    the slot's area. Also allows arbitrary number of slots.
    """

    def __init__(self):
        super().__init__()
        self._slot_class = CanvasSlot

    def update_slots(self):
        for slot in self._slots:
            slot.area.position = self.area.position + self.area.size * slot.pos_ratio
            slot.area.size = self.area.size * slot.size_ratio
