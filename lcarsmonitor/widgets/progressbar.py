import math
import libasvat.imgui.type_editor as types
from lcarsmonitor.widgets.base import LeafWidget, WidgetColors
from lcarsmonitor.widgets.rect import RectCorners
from lcarsmonitor.widgets.label import TextMixin
from lcarsmonitor.widgets.style import VisualStyle
from libasvat.imgui.colors import Colors, Color
from libasvat.imgui.math import Vector2, Rectangle
from libasvat.imgui.nodes import input_property
from imgui_bundle import imgui
from typing import Iterator
from enum import Enum


class BarType(Enum):
    """Type of Progress Bar."""
    HORIZONTAL = "Bar is a rect, filled in the horizontal (left -> right) direction."
    INVERTED_HORIZONTAL = "Bar is a rect, filled in the inverted horizontal (right -> left) direction."
    VERTICAL = "Bar is a rect, filled in the vertical (top -> bottom) direction."
    INVERTED_VERTICAL = "Bar is a rect, filled in the inverted vertical (bottom -> top) direction."
    CIRCLE = "Bar is a circle, filled in a clockwise direction."
    ANTI_CIRCLE = "Bar is a circle, filled in a anti-clockwise direction."


class BarObject:
    """Low-level progress-bar rendering object in LCARSMonitor's Widgets system.

    This holds all the necessary data and is capable of drawing a progress-bar with IMGUI in the Widgets System.
    However, this class is completely independent of a widget.

    Our purpose is to be used in a widget by association, not inheritance: a widget might hold several BarObjects at the
    same time, in order to easily render multiple bars with different properties.

    For a specific simple bar widget see ``ProgressBar``.
    """

    def __init__(self):
        self.area = Rectangle()
        """Position and size of area in which this bar will be drawn."""
        self.color: Color = Colors.grey
        """Color of bar background."""
        self.rounding: float = 0.0
        """Amount of rounding in the corners. Value in [0, 1] range, with 0 being "no rounding" and 1 being "maximum rounding".
        Use ``self.corners`` attribute to select which corners will be rounded off. Applies when using rectangle-type bars."""
        self.corners: RectCorners = RectCorners.NONE
        """Which corners apply rounding. Applies when using rectangle-type bars."""
        self.bar_color = Colors.yellow
        """Bar fill color."""
        self.frame_color = Colors.white
        """Bar frame color."""
        self.frame_thickness = 5.0
        """Thickness of bar frame, in absolute pixels. If <=0, no frame is shown."""
        self.bar_type: BarType = BarType.HORIZONTAL
        """Which kind of bar to use."""
        self.value = 0.0
        """Value of the bar, in a [0, 1] range."""
        self.inner_hole_ratio = 0.0
        """Ratio of inner-radius, as a [0, 1] value.
        When using circle-bars, this value defines the inner radius as a percentage of the full circle radius. The inner-radius
        defines a smaller, empty circle inside the bar-circle, thus transforming it into a "donut".
        """

    @property
    def actual_rounding(self):
        """Actual value of corner roundness, used for drawing the rectangle.
        This converts our ``self.rounding`` scaling factor to the actual range of pixel values for the rounding. [GET]"""
        return self.area.size.min_component() * 0.5 * self.rounding

    def draw(self):
        """Draws this bar object to IMGUI.

        The progress bar is drawn using IMGUI's DrawLists and our absolute area coords.
        Bar-type, area, color and other parameters that alter how the bar is rendered are all defined as public attributes
        of this object, so change them at will.
        """
        if "circle" in self.bar_type.name.lower():
            self._draw_circle_bar()
        else:
            self._draw_rect_bar()

    def _draw_rect_bar(self):
        """Draws the rectangle-type bars."""
        is_horizontal = "horizontal" in self.bar_type.name.lower()
        is_inverted = "inverted" in self.bar_type.name.lower()

        draw = imgui.get_window_draw_list()
        pos = self.area.position
        bottom_right = self.area.bottom_right_pos
        corner_flags = self.corners.get_flags()
        # Draw background
        draw.add_rect_filled(pos, bottom_right, self.color.u32, self.actual_rounding, corner_flags)

        # Draw bar fill.
        hor_fraction = self.value if is_horizontal else 1.0
        ver_fraction = self.value if (not is_horizontal) else 1.0
        if is_inverted:  # TESTING with 'not'
            bar_start_pos = pos + self.area.size * (1-hor_fraction, 1-ver_fraction)
            bar_end_pos = bottom_right
        else:
            bar_start_pos = pos
            bar_end_pos = pos + self.area.size * (hor_fraction, ver_fraction)
        draw.push_clip_rect(bar_start_pos - (0.5, 0.5), bar_end_pos)
        draw.add_rect_filled(pos, bottom_right, self.bar_color.u32, self.actual_rounding, corner_flags)
        draw.pop_clip_rect()

        # Draw bar frame.
        if self.frame_thickness > 0:
            draw.add_rect(pos, bottom_right, self.frame_color.u32, self.actual_rounding, corner_flags, self.frame_thickness)

    def _draw_circle_bar(self):
        """Draws the circle-type bars."""
        is_clockwise = self.bar_type == BarType.CIRCLE

        draw = imgui.get_window_draw_list()
        center = self.area.center
        radius = self.area.size.min_component() * 0.5

        draw.add_circle_filled(center, radius, self.color.u32)

        first_half = min(0.5, self.value) / 0.5
        secnd_half = max(0, self.value - 0.5) / 0.5

        if is_clockwise:
            draw.path_line_to(center - (0, radius))
            draw.path_arc_to(center, radius, math.pi*1.5, math.pi*1.5 + first_half * math.pi)
        else:
            angle = math.pi*1.5 - math.pi * first_half
            draw.path_line_to(center + Vector2.from_angle(angle) * radius)
            draw.path_arc_to(center, radius, angle, math.pi*1.5)
        draw.path_line_to(center)
        draw.path_fill_convex(self.bar_color.u32)

        if secnd_half > 0:
            if is_clockwise:
                draw.path_line_to(center + (0, radius))
                draw.path_arc_to(center, radius, math.pi*0.5, (0.5 + secnd_half) * math.pi)
            else:
                angle = math.pi * 0.5 - secnd_half * math.pi
                draw.path_line_to(center + Vector2.from_angle(angle) * radius)
                draw.path_arc_to(center, radius, angle, math.pi*0.5)
            draw.path_line_to(center)
            draw.path_fill_convex(self.bar_color.u32)

        if self.inner_hole_ratio > 0:
            draw.add_circle_filled(center, radius*self.inner_hole_ratio, Colors.background.u32)
            draw.add_circle(center, radius*self.inner_hole_ratio, self.frame_color.u32, thickness=self.frame_thickness)
        draw.add_circle(center, radius, self.frame_color.u32, thickness=self.frame_thickness)


class ChainedBarObject:
    """Specialized BarObject that is composed of several internal "sub" BarObjects.

    These sub-bars are "chained" together: each can have its own independent config and area (position/size).
    However, the value of each sub-bar depends on the value of this "parent" ChainedBarObject. The value (in 0-1)
    of this parent bar is translated into all sub-bars, depending on their order: all sub-bars together form the
    "whole" (value=1).

    For example: if we have sub-bars A, B, C and D, and a value of 0.5, then A and B would be totally filled (their
    individual values = 1). A parent value of 0.625 would mean A and B filled, while C is half-filled.

    The area of each sub-bar is defined as a ratio (or percentage) of the full area of this ChainedBarObject control.
    Thus if the parent bar is moved/sized/scaled in any way, the sub-bars will maintain their relative position and
    size between themselves and to the parent bar.
    """

    def __init__(self):
        self.area = Rectangle()
        """Position and size of area in which this bar will be drawn."""
        self._bars: list[BarObject] = []
        self._bar_areas: list[Rectangle] = []
        self._value = 0.0

    @property
    def value(self):
        """Value of the total chained bar, in a [0, 1] range.
        When drawing, the value of each individual bar is updated according to this, so that all inner bars together
        match this value.
        """
        return self._value

    @value.setter
    def value(self, v: float):
        self._value = min(1, max(0, v))

    @property
    def num_bars(self):
        """Gets the number of inner bars that are chained in this object"""
        return len(self._bars)

    def add_bar(self, bar_area: Rectangle = None, copy_config=False, copy_index=-1):
        """Adds a new BarObject to the end of this ChainedBar.

        Args:
            bar_area (Rectangle, optional): The area in which to draw this new sub-bar, as a ratio of the ChainedBar's area (the "parent" area).
            This rect's position and size ratios to the parent area (in the range [0,1]), and thus the sub-bar's final absolute position
            is ``parent_position + bar_area.position * parent_size`` and the sub-bar's size is ``parent_size * bar_area.size``.
            If None, defaults to a rect with ``position=(0,0)`` and ``size=(1,1)`` which means the same area as the ChainedBar.
            copy_config (bool, optional): If true, the new BarObject will have its attributes set with the same value as the sub-bar
            in the ``copy_index`` index. See ``self.copy_bar_config()``.
            copy_index (int, optional): Index of the source sub-BarObject of this ChainedBar that will provide the values for this
            new sub-bar's attributes. See ``self.get_bar()``.

        Returns:
            BarObject: the newly created BarObject.
        """
        bar = BarObject()
        if bar_area is None:
            bar_area = Rectangle(size=(1, 1))
        if copy_config and self.num_bars > 0:
            self.copy_bar_config(bar, self.get_bar(copy_index)[0])
        self._bars.append(bar)
        self._bar_areas.append(bar_area)
        return bar

    def copy_bar_config(self, target_bar: BarObject, source_bar: BarObject):
        """Copies all attributes from the source BarObject to the target BarObject.

        Args:
            target_bar (BarObject): Bar to set attribute values to.
            source_bar (BarObject): Bar to copy attribute values from.
        """
        if target_bar is None or source_bar is None:
            return
        target_bar.color = source_bar.color.copy()
        target_bar.rounding = source_bar.rounding
        target_bar.corners = source_bar.corners
        target_bar.bar_color = source_bar.bar_color.copy()
        target_bar.frame_color = source_bar.frame_color.copy()
        target_bar.frame_thickness = source_bar.frame_thickness
        target_bar.bar_type = source_bar.bar_type
        target_bar.inner_hole_ratio = source_bar.inner_hole_ratio

    def get_bar(self, index: int):
        """Gets the sub BarObject and its area ratio of this ChainedBar in the given index.

        Args:
            index (int): index of the bar to get. Accepts indexes just like any regular python list.

        Returns:
            tuple[BarObject, Rectangle]: the BarObject at the given index, and its area ratio rect.
        """
        # index = min(self.num_bars - 1, max(-self.num_bars, index))
        return self._bars[index], self._bar_areas[index]

    def remove_bar(self, index: int):
        """Removes a sub BarObject from this ChainedBar.

        Args:
            index (int): index of the bar to remove. Accepts indexes just like any regular python list.
        """
        self._bars.pop(index)
        self._bar_areas.pop(index)

    def draw(self):
        """Draws this chained bar using IMGUI.

        This draws all our sub-BarObjects, while updating the ``area`` and ``value`` of each one of them.
        """
        total_value = self.value * len(self._bars)
        pos = self.area.position
        size = self.area.size
        for bar, area_ratio in self:
            bar.area.position = pos + size * area_ratio.position
            bar.area.size = size * area_ratio.size
            bar.value = min(total_value, 1)
            total_value -= bar.value
            bar.draw()

    def set_all_fill_color(self, color: Color):
        """Sets the fill color of all sub-bars to the given color.

        Args:
            color (Color): Color to use as fill color in all bars.
        """
        for bar, area in self:
            bar.bar_color = color

    def __iter__(self) -> Iterator[tuple[BarObject, Rectangle]]:
        return iter(zip(self._bars, self._bar_areas))


# TODO: circle bars fica com uma pequena fresta entre as duas metades da barra...
class ProgressBar(TextMixin, LeafWidget):
    """A Progress Bar widget.

    Shows a shape (according to bar config) that can be filled according to a %-value in order to show progress or amount of something.

    This widget has Rect and Label properties as well:
    * Rect color is used as the bar's background color (seen when bar is empty), in any bar type.
    * Most other Rect properties are only used when the bar type is a rect-based type.
    * Label allows the bar to show a label on top of the bar itself. The label's ``text`` property will allow a ``{value}`` tag
    that may be used to insert the current bar value (*100, so in a [0,100] range) in the label.
    """

    def __init__(self):
        LeafWidget.__init__(self)
        TextMixin.__init__(self)
        self.node_header_color = WidgetColors.Interactible
        self._inner_bar = BarObject()

    # Editable Properties
    @input_property()
    def style(self) -> VisualStyle:
        """Visual style of this label. [GET/SET]"""
        st = VisualStyle()
        st.normal_color = Colors.grey
        return st

    @types.float_property(min=0, max=1, is_slider=True, flags=imgui.SliderFlags_.always_clamp)
    def rounding(self):
        """Corner rounding value, used when any corner is rounded.

        This is a scaling value, from 0 (no rounding) to 1 (max rounding). The maximum rounding value is half of the minimum
        rect dimension. When using max rounding and both corners of a side of the rect are rounded, that side will form a perfect
        half-circle between the corners.

        Only used with rectangular type bars. [GET/SET]"""
        return self._inner_bar.rounding

    @rounding.setter
    def rounding(self, value: float):
        self._inner_bar.rounding = value

    @types.enum_property()
    def corners(self) -> RectCorners:
        """Which corners to round on this bar (only when rectangular type bar is used). [GET/SET]"""
        return self._inner_bar.corners

    @corners.setter
    def corners(self, value: RectCorners):
        self._inner_bar.corners = value

    @input_property()
    def bar_color(self) -> Color:
        """The color of the bar fill. [GET/SET]"""
        return Colors.yellow

    @input_property()
    def frame_color(self) -> Color:
        """The color of the bar frame outline. [GET/SET]"""
        return Colors.white

    @types.float_property()
    def frame_thickness(self) -> float:
        """The thickness, in pixels, of the bar's frame outline. [GET/SET]"""
        return self._inner_bar.frame_thickness

    @frame_thickness.setter
    def frame_thickness(self, value: float):
        self._inner_bar.frame_thickness = value

    @types.enum_property()
    def bar_type(self) -> BarType:
        """The type of this progress bar. [GET/SET]"""
        return self._inner_bar.bar_type

    @bar_type.setter
    def bar_type(self, value: BarType):
        self._inner_bar.bar_type = value

    @input_property(max=1.0, is_slider=True, flags=imgui.SliderFlags_.always_clamp)
    def value(self) -> float:
        """The current value of the bar, in the range [0,1] [GET/SET]"""
        return 0.0  # this is essentially the default value.

    @types.float_property(max=1.0, is_slider=True, flags=imgui.SliderFlags_.always_clamp)
    def inner_hole_ratio(self) -> float:
        """The ratio of the circle radius that will be a hole. [GET/SET]

        This is only used when the Bar Type is any of the circle types. When this is > 0, the rendered bar will resemble a donut:
        a circle bar with a empty hole in the middle. This value is the percentage of the circle radius that will be the hole radius.
        """
        return self._inner_bar.inner_hole_ratio

    @inner_hole_ratio.setter
    def inner_hole_ratio(self, value: float):
        self._inner_bar.inner_hole_ratio = value

    # Method Overrides
    def render(self):
        self._handle_interaction()
        self._inner_bar.color = self.style.get_current_color(self)
        self._inner_bar.bar_color = self.bar_color
        self._inner_bar.frame_color = self.frame_color
        self._inner_bar.value = self.value
        self._inner_bar.area = self.area
        self._inner_bar.draw()
        self._draw_text(self.style.text_color)

    def _format_text(self, text: str):
        tags = {"value": self.value * 100}
        try:
            return text.format(**tags)
        except Exception:
            return str(text)
