import libasvat.imgui.type_editor as types
from lcarsmonitor.widgets.base import ContainerWidget, Slot
from lcarsmonitor.widgets.corner import Corner, CornerType
from lcarsmonitor.widgets.rect import Rect
from lcarsmonitor.widgets.style import VisualStyle
from libasvat.imgui.math import Vector2
from libasvat.imgui.general import menu_item
from libasvat.imgui.nodes import input_property
from imgui_bundle import imgui
from enum import Flag, auto


class PanelBorders(Flag):
    """Possible border settings for the Panel. Defines which border will be shown in a Panel.

    This is a FLAG enumeration, so multiple values can be aggregated with ``|``.
    """
    TOP = auto()
    RIGHT = auto()
    BOTTOM = auto()
    LEFT = auto()
    ALL = TOP | RIGHT | BOTTOM | LEFT


# TODO: arrumar bordas só poderem ter Leafs ou AxisLists com só Leafs
# TODO: border ratios com absolute=False tão bizarros
class Panel(ContainerWidget):
    """A container widget with a single child and optional margin and borders around it.

    The borders are slots themselves, that only accept Leaf widgets. So the panel accepts a single main child widget in its center,
    and up to four leaf-childs representing the borders. For example, a single Rect as a border would make it a filled solid color border.
    """

    def __init__(self):
        super().__init__()
        self.accepts_new_slots = False
        base_names = ["CornerTopLeft", "CornerTopRight", "CornerBottomLeft", "CornerBottomRight"]

        self._borders_type: PanelBorders = PanelBorders.ALL
        self._out_margin: float = 5.0
        self._border_width_ratio = 0.3
        self._border_height_ratio = 0.1
        self._corner_inner_radius_ratio = 0.15  # based on width
        self._use_absolute_values = False

        self._fixed_slots = [Slot(self, name) for name in base_names]
        self.corners = [
            Corner(CornerType.TOP_LEFT),
            Corner(CornerType.TOP_RIGHT),
            Corner(CornerType.BOTTOM_LEFT),
            Corner(CornerType.BOTTOM_RIGHT),
        ]
        self.borders = {
            PanelBorders.TOP: Slot(self, "Top Border"),
            PanelBorders.BOTTOM: Slot(self, "Bottom Border"),
            PanelBorders.LEFT: Slot(self, "Left Border"),
            PanelBorders.RIGHT: Slot(self, "Right Border"),
        }

        self._child_slot = Slot(self, "Content")
        self._child_slot.can_be_deleted = False
        self._slots.append(self._child_slot)

        for i, corner in enumerate(self.corners):
            self._fixed_slots[i].child = corner
            c = corner.type.name.lower()
            c = "".join([p.capitalize() for p in c.split("_")])
            corner.name = f"{self.id}-{c}Corner"
            corner.editable = False
        for border in self.borders.values():
            border.can_be_deleted = False
            self._slots.append(border)

    # Editable Properties
    @types.enum_property()
    def borders_type(self) -> PanelBorders:
        """Which borders to enable on this panel. [GET/SET]"""
        return self._borders_type

    @borders_type.setter
    def borders_type(self, value: PanelBorders):
        self._borders_type = value

    @types.float_property()
    def out_margin(self) -> float:
        """The margin of the borders/corners to the edges of our slot's available area."""
        return self._out_margin

    @out_margin.setter
    def out_margin(self, value: float):
        self._out_margin = value

    @types.float_property(max=1.0, is_slider=True, flags=imgui.SliderFlags_.always_clamp)
    def border_width_ratio(self):
        """The ratio of our available horizontal space that is used as the width for each of the LEFT/RIGHT borders. [GET/SET]

        This is the ratio (in [0,1]) of our area width that will be our column width. If ``self.use_absolute_values``
        is True, then this value will be our column width directly.
        """
        return self._border_width_ratio

    @border_width_ratio.setter
    def border_width_ratio(self, value: float):
        self._border_width_ratio = value

    @types.float_property(max=1.0, is_slider=True, flags=imgui.SliderFlags_.always_clamp)
    def border_height_ratio(self):
        """The ratio of our available vertical space that is used as the height for each of the TOP/BOTTOM borders. [GET/SET]

        This is the ratio (in [0,1]) of our area height that will be our bar height. If ``self.use_absolute_values``
        is True, then this value will be our bar height directly.
        """
        return self._border_height_ratio

    @border_height_ratio.setter
    def border_height_ratio(self, value: float):
        self._border_height_ratio = value

    @types.float_property(max=1.0, is_slider=True, flags=imgui.SliderFlags_.always_clamp)
    def corner_inner_radius_ratio(self) -> float:
        return self._corner_inner_radius_ratio

    @corner_inner_radius_ratio.setter
    def corner_inner_radius_ratio(self, value: float):
        self._corner_inner_radius_ratio = value

    @types.bool_property()
    def use_absolute_values(self):
        """If our border width/height ratios are absolute values instead of ratios to our area size. [GET/SET]"""
        return self._use_absolute_values

    @use_absolute_values.setter
    def use_absolute_values(self, value: bool):
        self._use_absolute_values = value

    @input_property()
    def border_style(self) -> VisualStyle:
        """The color of the borders and corners. [GET/SET]"""
        return VisualStyle()

    @types.bool_property()
    def outline_borders(self) -> bool:
        """If a thin outline will be rendered, showing the area of the borders. [GET/SET]"""
        return self.borders[PanelBorders.TOP].draw_area_outline

    @outline_borders.setter
    def outline_borders(self, value: bool):
        for border in self.borders.values():
            border.draw_area_outline = value

    # Regular Properties
    @property
    def border_size(self):
        """Base real size of borders, from our settings [GET]"""
        size = Vector2(self._border_width_ratio, self._border_height_ratio)
        if not self._use_absolute_values:
            size *= self.area.size
        return size

    @property
    def corner_size(self):
        """Real size of all corners [GET]"""
        size = self.border_size
        small = self._corner_inner_radius_ratio
        if not self._use_absolute_values:
            small *= size.x
        return Corner.get_min_area(size.x, size.y, small)

    @property
    def child_pos(self):
        """The position for drawing our selected child. This depends on the corner/borders config. [GET]"""
        top_left_corner = self.corners[0]  # top left corner
        pos = top_left_corner.inner_curve_center_pos + top_left_corner.corner_direction * top_left_corner.inner_curve_radius * 0.5
        if PanelBorders.TOP not in self._borders_type:
            pos.y = self.area.position.y + self._out_margin
        if PanelBorders.LEFT not in self._borders_type:
            pos.x = self.area.position.x + self._out_margin
        return pos

    @property
    def child_size(self):
        """The slot size for drawing our selected child. This depends on the corner/borders config. [GET]"""
        bottom_right_corner = self.corners[3]  # bottom right corner
        end_pos = bottom_right_corner.inner_curve_center_pos + bottom_right_corner.corner_direction * bottom_right_corner.inner_curve_radius * 0.5
        if PanelBorders.BOTTOM not in self._borders_type:
            end_pos.y = bottom_right_corner.area.bottom_right_pos.y
        if PanelBorders.RIGHT not in self._borders_type:
            end_pos.x = bottom_right_corner.area.bottom_right_pos.x
        return end_pos - self.child_pos

    @property
    def content(self):
        """The content slot of this Panel."""
        return self._child_slot

    # Methods
    def update_all_borders(self):
        """Updates all of our corner and border slots."""
        for corner in self.corners:
            self._update_corner(corner)

        for side, border in self.borders.items():
            self._update_border(border, side)

    def _update_corner(self, corner: Corner):
        """Updates our given child corner."""
        margin_vec = Vector2(self._out_margin, self._out_margin)
        size = self.corner_size
        pos = self.area.position
        if corner.type == CornerType.TOP_RIGHT:
            enabled = PanelBorders.TOP in self._borders_type and PanelBorders.RIGHT in self._borders_type
            pos += (self.area.size.x - size.x - margin_vec.x, margin_vec.y)
        elif corner.type == CornerType.TOP_LEFT:
            enabled = PanelBorders.TOP in self._borders_type and PanelBorders.LEFT in self._borders_type
            pos += margin_vec
        elif corner.type == CornerType.BOTTOM_RIGHT:
            enabled = PanelBorders.BOTTOM in self._borders_type and PanelBorders.RIGHT in self._borders_type
            pos = self.area.bottom_right_pos - size - margin_vec
        elif corner.type == CornerType.BOTTOM_LEFT:
            enabled = PanelBorders.BOTTOM in self._borders_type and PanelBorders.LEFT in self._borders_type
            pos += (margin_vec.x, self.area.size.y - size.y - margin_vec.y)

        corner.use_absolute_values = self._use_absolute_values
        corner.width_ratio = self._border_width_ratio
        corner.height_ratio = self._border_height_ratio
        corner.enabled = enabled
        corner.slot.enabled = True
        corner.slot.area.position = pos
        corner.slot.area.size = size
        corner.style = self.border_style

    def _update_border(self, border: Slot, side: PanelBorders):
        """Updates our given border slot as being at the given SIDE."""
        enabled = side in self._borders_type
        border.enabled = enabled
        if not enabled:
            return

        # This is a {border->corner indexes} table that associates a border with its "start"/"end" corners,
        # according to the corner's index in our self.corners array.
        # NOTE: this is hardcoded here and depends on how our hardcoded corners array was built!
        corners_indexes = {
            PanelBorders.TOP: (0, 1),
            PanelBorders.BOTTOM: (2, 3),
            PanelBorders.LEFT: (0, 2),
            PanelBorders.RIGHT: (1, 3),
        }
        start_corner: Corner = self.corners[corners_indexes[side][0]]
        end_corner: Corner = self.corners[corners_indexes[side][1]]

        if side in (PanelBorders.TOP | PanelBorders.BOTTOM):
            p1 = start_corner.top_bar_pos
            if not start_corner.enabled:
                p1 -= (start_corner.area.size.x, 0)
            p2 = end_corner.bottom_bar_pos
            if not end_corner.enabled:
                p2 += (end_corner.area.size.x, 0)
        else:
            p1 = start_corner.left_column_pos
            if not start_corner.enabled:
                p1 -= (0, start_corner.area.size.y)
            p2 = end_corner.right_column_pos
            if not end_corner.enabled:
                p2 += (0, end_corner.area.size.y)

        actual_border_size = p2 - p1
        border.area.position = p1
        border.area.size = actual_border_size
        border.area_outline_color = self.border_style.normal_color

    def fill_borders_with_rects(self):
        """Fills our borders with rects, by adding a new Rect widget to any empty slot in our borders.

        These rects will have our border style.
        """
        for side, border in self.borders.items():
            if border.child is None:
                r = Rect()
                self.system.add_node(r)
                r.style = self.border_style
                r.name = f"{self.id}-{side.name.capitalize()}Rect"
                border.child = r

    # Method Overrides
    def update_slots(self):
        self.update_all_borders()
        self._child_slot.area.position = self.child_pos
        self._child_slot.area.size = self.child_size

    def render(self):
        self._handle_interaction()
        self.update_slots()
        for slot in self._fixed_slots:
            slot.render()
        for slot in self._slots:
            slot.render()

    def render_edit_details(self):
        super().render_edit_details()
        imgui.spacing()
        imgui.separator_text("Commands")
        imgui.spacing()
        if menu_item("Fill Borders with Rects"):
            self.fill_borders_with_rects()
        imgui.set_item_tooltip(self.fill_borders_with_rects.__doc__)

    # Dynamic Editor Updaters
    def _update_border_width_ratio_editor(self, editor: types.FloatEditor):
        """Method automatically called by our ``border_width_ratio`` float-property editor in order to dynamically
        update its settings before editing."""
        if self._use_absolute_values:
            editor.max = self.area.size.x
        else:
            editor.max = 1.0

    def _update_border_height_ratio_editor(self, editor: types.FloatEditor):
        """Method automatically called by our ``border_height_ratio`` float-property editor in order to dynamically
        update its settings before editing."""
        if self._use_absolute_values:
            editor.max = self.area.size.y
        else:
            editor.max = 1.0

    def _update_corner_inner_radius_ratio_editor(self, editor: types.FloatEditor):
        """Method automatically called by our ``corner_inner_radius_ratio`` float-property editor in order to dynamically
        update its settings before editing."""
        if self._use_absolute_values:
            editor.max = self.border_size.x
        else:
            editor.max = 1.0
