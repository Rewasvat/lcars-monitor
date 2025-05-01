import libasvat.imgui.type_editor as types
from lcarsmonitor.widgets.lcars import LCARSWidget
from lcarsmonitor.widgets.base import WidgetColors
from lcarsmonitor.widgets.progressbar import ChainedBarObject, BarType, RectCorners
from lcarsmonitor.widgets.lcars.alerts import XAMLPath
from libasvat.imgui.nodes import input_property
from libasvat.imgui.colors import Color, Colors
from libasvat.imgui.math import Vector2, Rectangle
from imgui_bundle import imgui


class ReactorBar(LCARSWidget):
    """A LCARS Reactor Bar widget.

    Visually, this widget is the reactor display seen in Star Trek's LCARS screens, usually in
    Federation starships.

    The top and bottom "bars" of the reactor (from the center outwards) function as separate progress bars,
    allowing the user to set each side to its own value, thus displaying 2 bar-values in the same widget.
    """

    def __init__(self):
        super().__init__()
        self.node_header_color = WidgetColors.Interactible
        self._xaml_scale = Vector2(1/179.21, 1/581.12)  # NOTE: min X,Y = 0.75,0.75
        self._bar_cross_line_color = Colors.background
        self._is_vertical = True
        self._build()

    def _build(self):
        """Sets up the fixed values of internal attributes used later when rendering this widget.

        This uses some of the properties of this widget in order to setup the values, so this method
        can be used to "update" the contents of the widget after changing some property."""
        bar_size = Vector2(138.76, 32.07) * self._xaml_scale
        initial_bottom_pos = Vector2(20.59, 331.120) * self._xaml_scale
        initial_top_pos = Vector2(20.59, 218.670) * self._xaml_scale
        bar_offset = bar_size + (0, 5.41 * self._xaml_scale.y)
        bar_offset.x = 0

        if not self._is_vertical:
            bar_size.swap_axis()
            initial_bottom_pos.swap_axis()
            initial_top_pos.swap_axis()
            bar_offset.swap_axis()

        self.bottom_bar = ChainedBarObject()
        reactor_blob_bar = self.bottom_bar.add_bar(Rectangle(initial_bottom_pos, bar_size))
        reactor_blob_bar.rounding = 1
        reactor_blob_bar.bar_type = BarType.VERTICAL if self._is_vertical else BarType.HORIZONTAL
        reactor_blob_bar.corners = RectCorners.ALL
        reactor_blob_bar.frame_thickness = 0
        reactor_blob_bar.color = Colors.grey
        for i in range(4):
            self.bottom_bar.add_bar(Rectangle(initial_bottom_pos + bar_offset * (i + 1), bar_size), True)

        self.top_bar = ChainedBarObject()
        reactor_blob_bar = self.top_bar.add_bar(Rectangle(initial_top_pos, bar_size))
        reactor_blob_bar.rounding = 1
        reactor_blob_bar.bar_type = BarType.INVERTED_VERTICAL if self._is_vertical else BarType.INVERTED_HORIZONTAL
        reactor_blob_bar.corners = RectCorners.ALL
        reactor_blob_bar.frame_thickness = 0
        reactor_blob_bar.color = Colors.grey
        for i in range(4):
            self.top_bar.add_bar(Rectangle(initial_top_pos - bar_offset * (i + 1), bar_size), True)

        self.bar_cross_thickness = 0.018
        bar_cross_pos = Vector2(77.60, 68.74) * self._xaml_scale
        bar_cross_size = Vector2(23.40, 444.47) * self._xaml_scale
        if not self._is_vertical:
            bar_cross_pos.swap_axis()
            bar_cross_size.swap_axis()
            bar_cross_pos -= (0.01, 0)
            bar_cross_size += (0.01, 0)
        self.bar_cross_lines = Rectangle(bar_cross_pos, bar_cross_size)

        splitter_lines_color = Color.from_hex("ff7f7f7f", use_argb=True)
        reactor_color = Color.from_hex("ffa6a6a6", use_argb=True)
        bg_color = Colors.background

        bottom_blocks_info = [
            # Bottom Lines/Trapeze
            (1.5, bg_color, reactor_color, "M 150.820,521.560 L 28.750,521.560 L 2.920,556.610 C 1.510,558.530 0.750,560.840 0.750,563.220 \
             L 0.750,564.020 C 0.750,567.100 3.250,569.590 6.320,569.590 L 173.100,569.590 C 176.180,569.590 178.670,567.090 178.670,564.020 \
             L 178.670,563.170 C 178.670,560.840 177.930,558.580 176.560,556.700 L 150.820,521.550 L 150.820,521.560 Z"),
            # Bottom bar (at the border)
            (1.5, bg_color, reactor_color, "M 74.790,571.080 L 104.810,571.080 C 107.582,571.080 109.830,573.328 109.830,576.100 \
             L 109.830,576.100 C 109.830,578.872 107.582,581.120 104.810,581.120 L 74.790,581.120 C 72.018,581.120 69.770,578.872 69.770,576.100 \
             L 69.770,576.100 C 69.770,573.328 72.018,571.080 74.790,571.080 Z"),
        ]
        self.bottom_blocks: list[XAMLPath] = []
        for thickness, stroke_color, fill_color, path in bottom_blocks_info:
            self.bottom_blocks.append(XAMLPath(path, self._xaml_scale, fill_color, stroke_color, thickness))
            if not self._is_vertical:
                self.bottom_blocks[-1].swap_axis()

        top_blocks_info = [
            # Top Lines/Trapeze
            (1.5, bg_color, reactor_color, "M 29.140,60.310 L 151.210,60.310 L 177.040,25.260 C 178.450,23.340 179.210,21.030 179.210,18.650 \
                L 179.210,17.850 C 179.210,14.770 176.710,12.280 173.640,12.280 L 6.860,12.280 C 3.780,12.280 1.290,14.780 1.290,17.850 \
                L 1.290,18.700 C 1.290,21.030 2.030,23.290 3.400,25.170 L 29.140,60.320 L 29.140,60.310 Z"),
            # Top bar (at the border)
            (1.5, bg_color, reactor_color, "M 105.170,10.790 L 75.150,10.790 C 72.378,10.790 70.130,8.542 70.130,5.770 L 70.130,5.770 \
                C 70.130,2.998 72.378,0.750 75.150,0.750 L 105.170,0.750 C 107.942,0.750 110.190,2.998 110.190,5.770 L 110.190,5.770 \
                C 110.190,8.542 107.942,10.790 105.170,10.790 Z"),
        ]
        self.top_blocks: list[XAMLPath] = []
        for thickness, stroke_color, fill_color, path in top_blocks_info:
            self.top_blocks.append(XAMLPath(path, self._xaml_scale, fill_color, stroke_color, thickness))
            if not self._is_vertical:
                self.top_blocks[-1].swap_axis()

        center_blocks_info = [
            # Center Piece/ Bottom bar
            (1.0, bg_color, reactor_color, "M 17.380,308.120 L 164.300,308.120 L 164.300,309.430 C 164.300,318.590 156.860,326.030 \
             147.700,326.030 L 33.970,326.030 C 24.810,326.030 17.380,318.600 17.380,309.440 L 17.380,308.110 L 17.380,308.110 L 17.380,308.120 Z"),
            # Center Piece/ Top bar
            (1.0, bg_color, reactor_color, "M 164.300,274.310 L 17.380,274.310 L 17.380,273.000 C 17.380,263.840 24.820,256.400 33.980,256.400 \
             L 147.710,256.400 C 156.870,256.400 164.300,263.830 164.300,272.990 L 164.300,274.320 L 164.300,274.320 L 164.300,274.310 Z"),
            # Center Piece/ Middle bar
            (1.0, bg_color, reactor_color, "M 21.230,274.310 L 159.270,274.310 L 159.270,308.120 L 21.230,308.120 L 21.230,274.310 Z"),
            # Center Piece/ center circle
            (6.0, bg_color, reactor_color, "M 90.250,265.840 C 104.261,265.840 115.620,277.199 115.620,291.210 C 115.620,305.221 104.261,316.580 \
             90.250,316.580 C 76.239,316.580 64.880,305.221 64.880,291.210 C 64.880,277.199 76.239,265.840 90.250,265.840 \
             C 104.261,265.840 115.620,277.199 115.620,291.210 Z"),
        ]
        self.center_blocks: list[XAMLPath] = []
        for thickness, stroke_color, fill_color, path in center_blocks_info:
            self.center_blocks.append(XAMLPath(path, self._xaml_scale, fill_color, stroke_color, thickness))
            if not self._is_vertical:
                self.center_blocks[-1].swap_axis()

        self.lines_info = [
            # bottom thin-splitter left line
            (0.5, splitter_lines_color, (38.680, 518.530), (80.010, 518.530)),
            # bottom thin-splitter middle line
            (0.5, splitter_lines_color, (82.820, 518.530), (97.860, 518.530)),
            # bottom thin-splitter right line
            (0.5, splitter_lines_color, (99.790, 518.530), (141.940, 518.530)),
            # top thin-splitter right line
            (0.5, splitter_lines_color, (141.290, 63.340), (99.950, 63.340)),
            # top thin-splitter middle line
            (0.5, splitter_lines_color, (97.140, 63.340), (82.100, 63.340)),
            # top thin-splitter left line
            (0.5, splitter_lines_color, (80.180, 63.340), (38.030, 63.340)),
            # Bottom Trapeze/ outer splitter line
            (1.5, bg_color, (3.870, 555.330), (175.400, 555.330)),
            #  Bottom Trapeze/ third splitter line
            (2.0, bg_color, (13.980, 541.610), (165.680, 541.610)),
            # Bottom Trapeze/ second splitter line
            (1.0, bg_color, (18.930, 534.890), (160.550, 534.890)),
            # Bottom Trapeze/ inner splitter line
            (0.5, bg_color, (22.320, 530.280), (157.270, 530.280)),
            # Top Trapeze/ outer splitter line
            (1.5, bg_color, (176.090, 26.540), (4.570, 26.540)),
            # Top Trapeze/ third splitter line
            (2.0, bg_color, (165.990, 40.260), (14.280, 40.260)),
            # Top Trapeze/ second splitter line
            (1.0, bg_color, (161.030, 46.980), (19.410, 46.980)),
            # Top Trapeze/ inner splitter line
            (0.5, bg_color, (157.640, 51.590), (22.690, 51.590)),
            # CenterPiece/ vert-line 1
            (0.5, bg_color, (29.860, 274.310), (29.860, 308.120)),
            # CenterPiece/ vert-line 2
            (1.0, bg_color, (35.490, 274.310), (35.490, 308.120)),
            # CenterPiece/ vert-line 3
            (0.5, bg_color, (40.820, 274.310), (40.820, 308.120)),
            # CenterPiece/ vert-line 4
            (0.5, bg_color, (140.970, 274.310), (140.970, 308.120)),
            # CenterPiece/ vert-line 5
            (1.0, bg_color, (146.160, 274.310), (146.160, 308.120)),
            # CenterPiece/ vert-line 6
            (0.5, bg_color, (151.340, 274.310), (151.340, 308.120)),
        ]

    def _draw_reactor(self):
        """Draws the LCARS reactor bar widget using imgui"""
        if self.is_vertical:
            ratio = self._xaml_scale.aspect_ratio()
        else:
            ratio = self._xaml_scale.swapped_axis().aspect_ratio()
        ratio = 1.0 / ratio
        reactor_area = self.area.get_inner_rect(ratio)

        draw = imgui.get_window_draw_list()
        self.bottom_bar.area = reactor_area
        self.bottom_bar.value = self.bottom_value
        self.bottom_bar.set_all_fill_color(self.bottom_fill_color)
        self.bottom_bar.draw()
        self.top_bar.area = reactor_area
        self.top_bar.value = self.top_value
        self.top_bar.set_all_fill_color(self.top_fill_color)
        self.top_bar.draw()

        pos = reactor_area.position
        size = reactor_area.size
        left_top = pos + self.bar_cross_lines.position * size
        left_bot = pos + self.bar_cross_lines.bottom_left_pos * size
        right_top = pos + self.bar_cross_lines.top_right_pos * size
        right_bot = pos + self.bar_cross_lines.bottom_right_pos * size
        line_thickness = self.bar_cross_thickness * size.min_component()
        line_color = self._bar_cross_line_color.u32
        if self.is_vertical:
            draw.add_line(left_top, left_bot, line_color, line_thickness)
            draw.add_line(right_top, right_bot, line_color, line_thickness)
        else:
            draw.add_line(left_top, right_top, line_color, line_thickness)
            draw.add_line(left_bot, right_bot, line_color, line_thickness)

        for bottom_block in self.bottom_blocks:
            bottom_block.render(pos, size)
        for top_block in self.top_blocks:
            top_block.render(pos, size)
        for center_block in self.center_blocks:
            center_block.render(pos, size)

        for thickness, color, off1, off2 in self.lines_info:
            scaled_off1 = self._xaml_scale * off1
            scaled_off2 = self._xaml_scale * off2
            if not self.is_vertical:
                scaled_off1.swap_axis()
                scaled_off2.swap_axis()
            p1 = pos + scaled_off1 * size
            p2 = pos + scaled_off2 * size
            draw.add_line(p1, p2, color.u32, thickness * self._xaml_scale.min_component() * size.min_component() * 4)

    def render(self):
        self._draw_reactor()
        self._handle_interaction()

    @input_property(max=1.0, is_slider=True, flags=imgui.SliderFlags_.always_clamp)
    def top_value(self) -> float:
        """The current value of the top bar, in the range [0,1] [GET/SET]"""
        return 0.0  # this is essentially the default value.

    @input_property(max=1.0, is_slider=True, flags=imgui.SliderFlags_.always_clamp)
    def bottom_value(self) -> float:
        """The current value of the bottom bar, in the range [0,1] [GET/SET]"""
        return 0.0  # this is essentially the default value.

    @input_property()
    def top_fill_color(self) -> Color:
        """The color of the top bar fill. [GET/SET]"""
        return Color.from_hex("FFADD8E6", use_argb=True)

    @input_property()
    def bottom_fill_color(self) -> Color:
        """The color of the bottom bar fill. [GET/SET]"""
        return Color.from_hex("FFADD8E6", use_argb=True)

    @types.bool_property()
    def is_vertical(self):
        """Is this Reactor bar is oriented vertically or not (thus, horizontally).

        When horizontal, the TOP bar will be the LEFT bar, while the BOTTOM will
        be the RIGHT bar.
        """
        return self._is_vertical

    @is_vertical.setter
    def is_vertical(self, value: bool):
        self._is_vertical = value
        self._build()
