import libasvat.imgui.type_editor as types
from lcarsmonitor.widgets.base import LeafWidget, WidgetColors
from lcarsmonitor.widgets.progressbar import ChainedBarObject, BarType, RectCorners
from lcarsmonitor.widgets.lcars.alerts import XAMLPath
from libasvat.imgui.nodes import input_property
from libasvat.imgui.colors import Color, Colors
from libasvat.imgui.math import Vector2, Rectangle
from imgui_bundle import imgui


class WavesBar(LeafWidget):
    """A LCARS "Waves" Bar widget.

    The Waves bar is a widget seen in Star Trek's LCARS screens, usually in Federation starships.
    It is composed of several segmented circles, which together form an interactible progress
    bar in the screens.

    The left and right "bars" of the widget function as separate progress bars,
    allowing the user to set each side to its own value, thus displaying 2 bar-values in the same widget.
    """

    def __init__(self):
        super().__init__()
        self.node_header_color = WidgetColors.Interactible
        self._xaml_scale = Vector2(1/79.44, 1/445.77)  # NOTE: min X,Y = 0.5,0.5
        self._lines_color = Colors.background
        self._block_color = Color.from_hex("ffeff7ff", use_argb=True)
        self._is_vertical = True
        self._is_inverted = False
        self._build()

    def _build(self):
        """Sets up the fixed values of internal attributes used later when rendering this widget.

        This uses some of the properties of this widget in order to setup the values, so this method
        can be used to "update" the contents of the widget after changing some property."""
        bar_size = Vector2(32.78, 46.06) * self._xaml_scale
        initial_left_pos = Vector2(0.5, 378.62) * self._xaml_scale
        initial_right_pos = Vector2(46.52, 378.63) * self._xaml_scale
        bar_offset = bar_size + (0, 5.02 * self._xaml_scale.y)
        bar_offset.x = 0

        center_line_width = initial_right_pos.x - (initial_left_pos.x + bar_size.x)
        # In order to fix corner rounding size in the bars, the bar_size's Y axis needs to be smaller than its X axis.
        # so we extend the bar into the center line, and afterwards draw a black line on top of it to hide the bars.
        offset = center_line_width * 0.75
        bar_size.x += offset
        initial_right_pos.x -= offset

        if not self._is_vertical:
            bar_size.swap_axis()
            initial_left_pos.swap_axis()
            initial_right_pos.swap_axis()
            initial_left_pos, initial_right_pos = initial_right_pos, initial_left_pos  # this way, LEFT will be BOTTOM
            bar_offset.swap_axis()

        position_offsets = [bar_offset * i for i in range(8)]

        if self._is_inverted and self._is_vertical:
            bar_type = BarType.VERTICAL
            position_offsets.reverse()
        elif self._is_inverted and (not self._is_vertical):
            bar_type = BarType.INVERTED_HORIZONTAL
        elif (not self._is_inverted) and self._is_vertical:
            bar_type = BarType.INVERTED_VERTICAL
        elif (not self._is_inverted) and (not self._is_vertical):
            bar_type = BarType.HORIZONTAL
            position_offsets.reverse()

        self.left_bar = ChainedBarObject()
        blob_bar = self.left_bar.add_bar(Rectangle(initial_left_pos - position_offsets[0], bar_size))
        blob_bar.rounding = 1
        blob_bar.bar_type = bar_type
        blob_bar.corners = RectCorners.LEFT if self._is_vertical else RectCorners.BOTTOM
        blob_bar.frame_thickness = 0
        blob_bar.color = Colors.grey
        for offset in position_offsets[1:]:
            self.left_bar.add_bar(Rectangle(initial_left_pos - offset, bar_size), True)

        self.right_bar = ChainedBarObject()
        blob_bar = self.right_bar.add_bar(Rectangle(initial_right_pos - position_offsets[0], bar_size))
        blob_bar.rounding = 1
        blob_bar.bar_type = bar_type
        blob_bar.corners = RectCorners.RIGHT if self._is_vertical else RectCorners.TOP
        blob_bar.frame_thickness = 0
        blob_bar.color = Colors.grey
        for offset in position_offsets[1:]:
            self.right_bar.add_bar(Rectangle(initial_right_pos - offset, bar_size), True)

        # Lines (visual details) that cross the bars
        self.lines_info = [
            # left line
            [center_line_width * 0.16, (27.5, 20.0), (27.5, 426.0)],
            # right line
            [center_line_width * 0.16, (52.42, 20.0), (52.42, 426.0)],
        ]
        mid_top = Vector2()
        mid_bottom = Vector2()
        for line in self.lines_info:
            line[1] = Vector2(*line[1]) * self._xaml_scale
            line[2] = Vector2(*line[2]) * self._xaml_scale
            if not self._is_vertical:
                line[1].swap_axis()
                line[2].swap_axis()
            mid_top += line[1]
            mid_bottom += line[2]
        # append center line
        self.lines_info.append([center_line_width, mid_top * 0.5, mid_bottom * 0.5])

        # Top/Bottom Blocks
        top_block_p1 = Vector2(16.420, 0.500) * self._xaml_scale
        top_block_p2 = Vector2(63.530, 16.570) * self._xaml_scale
        bottom_block_p1 = Vector2(16.410, 429.690) * self._xaml_scale
        bottom_block_p2 = Vector2(63.520, 445.760) * self._xaml_scale
        if not self._is_vertical:
            top_block_p1.swap_axis()
            top_block_p2.swap_axis()
            bottom_block_p1.swap_axis()
            bottom_block_p2.swap_axis()
        self.blocks = [
            (top_block_p1, top_block_p2),
            (bottom_block_p1, bottom_block_p2),
        ]

    def _draw_waves(self):
        """Draws the LCARS waves bar widget using imgui"""
        if self.is_vertical:
            ratio = self._xaml_scale.aspect_ratio()
        else:
            ratio = self._xaml_scale.swapped_axis().aspect_ratio()
        ratio = 1.0 / ratio
        waves_area = self.area.get_inner_rect(ratio)

        self.left_bar.area = waves_area
        self.left_bar.value = self.left_value
        self.left_bar.set_all_fill_color(self.left_fill_color)
        self.left_bar.draw()
        self.right_bar.area = waves_area
        self.right_bar.value = self.right_value
        self.right_bar.set_all_fill_color(self.right_fill_color)
        self.right_bar.draw()

        pos = waves_area.position
        size = waves_area.size
        draw = imgui.get_window_draw_list()
        for thickness, off1, off2 in self.lines_info:
            p1 = pos + off1 * size
            p2 = pos + off2 * size
            draw.add_line(p1, p2, self._lines_color.u32, thickness * size.min_component())

        for off1, off2 in self.blocks:
            p1 = pos + off1 * size
            p2 = pos + off2 * size
            draw.add_rect_filled(p1, p2, self._block_color.u32)

    def render(self):
        self._draw_waves()
        self._handle_interaction()

    @input_property(max=1.0, is_slider=True, flags=imgui.SliderFlags_.always_clamp)
    def left_value(self) -> float:
        """The current value of the left bar, in the range [0,1] [GET/SET]"""
        return 0.0  # this is essentially the default value.

    @input_property(max=1.0, is_slider=True, flags=imgui.SliderFlags_.always_clamp)
    def right_value(self) -> float:
        """The current value of the right bar, in the range [0,1] [GET/SET]"""
        return 0.0  # this is essentially the default value.

    @input_property()
    def left_fill_color(self) -> Color:
        """The color of the bottom bar fill. [GET/SET]"""
        return Color.from_hex("FFADD8E6", use_argb=True)

    @input_property()
    def right_fill_color(self) -> Color:
        """The color of the top bar fill. [GET/SET]"""
        return Color.from_hex("FFADD8E6", use_argb=True)

    @types.bool_property()
    def is_vertical(self):
        """Is this waves bar is oriented vertically or not (thus, horizontally).

        When horizontal, the LEFT bar will be the BOTTOM bar, while the RIGHT will
        be the TOP bar.
        """
        return self._is_vertical

    @is_vertical.setter
    def is_vertical(self, value: bool):
        self._is_vertical = value
        self._build()

    @types.bool_property()
    def is_inverted(self):
        """Is this waves bar is filled inverted or not.

        Vertical bars fill bottom->up, while horizontal bars are left->right.

        If this is true, vertical bars will fill up->bottom, while horizontal bars will fill right->left.
        """
        return self._is_inverted

    @is_inverted.setter
    def is_inverted(self, value: bool):
        self._is_inverted = value
        self._build()
