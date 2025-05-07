import re
import libasvat.imgui.editors.primitives as primitives
from lcarsmonitor.widgets.lcars import LCARSWidget
from lcarsmonitor.widgets.base import WidgetColors
from lcarsmonitor.widgets.label import TextObject, LCARSFont, TextAlignment
from libasvat.imgui.colors import Color, Colors
from libasvat.imgui.nodes import input_property
from libasvat.imgui.math import Vector2, multiple_lerp_with_weigths
from imgui_bundle import imgui
from enum import Enum


class AlertType(Enum):
    """Type of Alert to display"""
    RED = "RED"
    YELLOW = "YELLOW"


class Alert(LCARSWidget):
    """Purely visual animated LCARS Alert widget.

    The type of the alert (Red, Yellow, etc) is selectable via property, and will update the alert visual representation
    accordingly.

    The alert graphics itself has a fixed aspect-ratio to preserve its proportions, and will try to fit to the slot's area.
    So depending on slot size, some empty space may be left on the left/right or top/bottom sides.
    """

    def __init__(self):
        super().__init__()
        self.node_header_color = WidgetColors.Animated
        self._out_margin = 10
        self.color: Color = None
        self._large_text = TextObject("ALERT")
        self._large_text.scale = 2.0
        self._large_text.font = LCARSFont.LCARS_WIDE
        self._large_text.align = TextAlignment.TOP
        self._small_text = TextObject("CONDITION: WHAT")
        self._small_text.scale = 2.0
        self._small_text.font = LCARSFont.LCARS_WIDE
        self._small_text.align = TextAlignment.BOTTOM
        self._xaml_scale = Vector2(1/734.305, 1/582.540)
        self.bar_data: list[tuple[Color, Animation]] = []
        self._setup_fixed_paths()
        self.alert_type = AlertType.RED  # this will update colors, text and setup_bar_data().

    @primitives.float_property()
    def out_margin(self) -> float:
        """The margin of the borders/corners to the edges of our slot's available area."""
        return self._out_margin

    @out_margin.setter
    def out_margin(self, value: float):
        self._out_margin = value

    @primitives.enum_property()
    def alert_type(self):
        """Type of this alert [GET/SET]"""
        return self._alert_type

    @alert_type.setter
    def alert_type(self, value: AlertType):
        self._alert_type = value
        self._update_alert_type()

    def _draw_alert(self):
        """Internal utility to render our rectangle."""
        ratio = 1.0 / self._xaml_scale.aspect_ratio()
        alert_area = self.area.get_inner_rect(ratio, self.out_margin)
        pos = alert_area.position
        size = alert_area.size

        # draw = imgui.get_window_draw_list()
        # draw.add_rect(base_pos, base_pos+base_size, Colors.blue.u32)
        # draw.add_rect(pos, pos+size, Colors.red.u32)

        self.draw_bars(pos, size)

        # TODO: talvez dê pra fazer o XAMLPath/Shape calcular internamente um bounding-rect baseado nos pontos passados pros segmentos.
        #   e ai usar esse bounding-rect aqui pra pegar esses pontos dinamicamente
        p1 = pos + Vector2(121.485, 227.990) * self._xaml_scale * size  # top-right corner of left-block, position fixed to slot
        p2 = pos + Vector2(609.455, 354.320) * self._xaml_scale * size  # bottom-left corner of right-block, position fixed to slot
        # draw.add_rect(p1, p2, Colors.magenta.u32)

        large_pos = p1.copy()
        large_area = p2 - large_pos
        self._large_text.area.position = large_pos
        self._large_text.area.size = large_area
        self._large_text.draw()
        self.text_animation.update(self._large_text.color)

        small_pos = self._large_text.text_area.bottom_left_pos
        small_area = p2 - small_pos
        self._small_text.area.position = small_pos
        self._small_text.area.size = small_area
        self._small_text.draw()

        for path in self.fixed_paths:
            path.render(pos, size)

    def draw_bars(self, pos: Vector2, size: Vector2):
        """Internal method to draw the animated top and bottom bars of the alert."""
        draw = imgui.get_window_draw_list()
        top_inner_pos = pos + size * (0.299, 0.274)
        bottom_inner_pos = pos + size * (0.299, 0.705)
        bar_size = size * (0.3987, 0.021)
        rounding = bar_size.y * 0.3

        color = Colors.blue
        for i, (color, anim) in enumerate(self.bar_data):
            anim.update(color)
            offset = bar_size * (0, 1.235) * i
            top_pos = top_inner_pos - offset
            bottom_pos = bottom_inner_pos + offset
            draw.add_rect_filled(top_pos, top_pos+bar_size, color.u32, rounding, imgui.ImDrawFlags_.round_corners_all)
            draw.add_rect_filled(bottom_pos, bottom_pos+bar_size, color.u32, rounding, imgui.ImDrawFlags_.round_corners_all)

    def _setup_fixed_paths(self):
        """Sets up this instance's ``fixed_paths`` attribute. These are the fixed polygons in the Alert UI.
        They aren't animated or changed in any way."""
        fixed_paths = [
            # LEFT BLOCK
            "F1 M 6.075,354.320 L 99.265,354.320 L 99.265,227.990 L 6.075,227.990 C -2.025,270.100 -2.025,312.210 6.075,354.320 Z",
            # RIGHT BLOCK
            "F1 M 726.205,227.990 L 633.015,227.990 L 633.015,354.320 L 726.205,354.320 C 734.305,312.210 734.305,270.100 726.205,227.990 \
                L 726.205,227.990 Z",
            # BOTTOM BAR HOLDER
            "F1 M 516.235,582.520 L 516.265,415.910 C 516.265,410.770 512.175,406.770 507.045,406.760 L 224.845,406.720 C 219.685,406.720 \
                216.465,410.420 216.465,415.580 L 216.645,582.530 C 162.835,562.310 101.495,518.310 70.925,479.630 L 173.545,389.870 \
                C 302.165,389.870 430.715,389.800 559.335,389.800 L 662.045,479.610 C 647.095,496.550 626.955,516.380 600.825,535.540 \
                C 569.605,558.430 539.765,573.080 516.245,582.520 L 516.235,582.520 Z",
            # TOP BAR HOLDER
            "F1 M 216.725,0.010 L 216.695,166.620 C 216.695,171.760 220.785,175.760 225.915,175.770 L 508.115,175.810 C 513.275,175.810 \
                516.495,172.110 516.495,166.950 L 516.315,0.000 C 570.125,20.220 631.465,64.220 662.035,102.900 L 559.415,192.660 \
                C 430.795,192.660 302.245,192.730 173.625,192.730 L 70.915,102.920 C 85.865,85.980 106.005,66.150 132.135,46.990 \
                C 163.355,24.100 193.195,9.450 216.725,0.010 Z",
        ]
        self.fixed_paths: list[XAMLPath] = []
        for path in fixed_paths:
            self.fixed_paths.append(XAMLPath(path, self._xaml_scale, self.color))

    def _setup_bar_data(self):
        """Sets up this instance's ``bar_data`` and the related ``text_animation`` attributes,
        if they aren't initialized yet."""
        if len(self.bar_data) > 0:
            return
        s = 0.2  # time step
        duration = s*8
        self.bar_data = [
            (self.color.alpha_copy(1), Animation("a", duration)),
            (self.color.alpha_copy(0.8), Animation("a", duration)),
            (self.color.alpha_copy(0.6), Animation("a", duration)),
            (self.color.alpha_copy(0.4), Animation("a", duration)),
            (self.color.alpha_copy(0.2), Animation("a", duration)),
            (self.color.alpha_copy(0.2), Animation("a", duration)),
            (self.color.alpha_copy(0.2), Animation("a", duration)),
            (self.color.alpha_copy(0.2), Animation("a", duration)),
        ]
        bars_keyframes: list[list[tuple[float, float]]] = [
            [
                (0.0, 1),
                (s*1, 0.8),
                (s*2, 0.6),
                (s*3, 0.4),
                (s*4, 0.2),
                (s*5, 0.2),
                (s*6, 0.3),
                (s*7, 0.5),
            ],
            [
                (0.0, 0.8),
                (s*1, 0.6),
                (s*2, 0.4),
                (s*3, 0.2),
                (s*4, 0.2),
                (s*5, 0.3),
                (s*6, 0.5),
                (s*7, 1),
            ],
            [
                (0.0, 0.6),
                (s*1, 0.4),
                (s*2, 0.2),
                (s*3, 0.2),
                (s*4, 0.3),
                (s*5, 0.5),
                (s*6, 1),
                (s*7, 0.8),
            ],
            [
                (0.0, 0.4),
                (s*1, 0.2),
                (s*2, 0.2),
                (s*3, 0.3),
                (s*4, 0.5),
                (s*5, 1),
                (s*6, 0.8),
                (s*7, 0.6),
            ],
            [
                (0.0, 0.2),
                (s*1, 0.2),
                (s*2, 0.3),
                (s*3, 0.5),
                (s*4, 1),
                (s*5, 0.8),
                (s*6, 0.6),
                (s*7, 0.4),
            ],
            [
                (0.0, 0.2),
                (s*1, 0.3),
                (s*2, 0.5),
                (s*3, 1),
                (s*4, 0.8),
                (s*5, 0.6),
                (s*6, 0.4),
                (s*7, 0.2),
            ],
            [
                (0.0, 0.3),
                (s*1, 0.5),
                (s*2, 1),
                (s*3, 0.8),
                (s*4, 0.6),
                (s*5, 0.4),
                (s*6, 0.2),
                (s*7, 0.2),
            ],
            [
                (0.0, 0.5),
                (s*1, 1),
                (s*2, 0.8),
                (s*3, 0.6),
                (s*4, 0.4),
                (s*5, 0.2),
                (s*6, 0.2),
                (s*7, 0.3),
            ],
        ]
        for data, frames_info in zip(self.bar_data, bars_keyframes):
            for t, v in frames_info:
                data[1].add_keyframe(t, v)
            data[1].add_looping_keyframe()

        self.text_animation = Animation("a", duration)
        self.text_animation.add_keyframe(0.0, 1)
        self.text_animation.add_keyframe(s*1, 1)
        self.text_animation.add_keyframe(s*2, 0.6)
        self.text_animation.add_keyframe(s*3, 0.4)
        self.text_animation.add_keyframe(s*4, 0.2)
        self.text_animation.add_keyframe(s*5, 0.5)
        self.text_animation.add_keyframe(s*6, 1)
        self.text_animation.add_keyframe(s*7, 1)
        self.text_animation.add_looping_keyframe()

    def render(self):
        self._draw_alert()
        self._handle_interaction()

    def reset_animations(self):
        """Resets all alert animation objects"""
        self.text_animation.reset()
        for color, anim in self.bar_data:
            anim.reset()

    def _update_alert_type(self):
        """Updates this alert based on its type."""
        if self.alert_type is AlertType.RED:
            self._small_text.text = "CONDITION: RED"
            self.color = Color(236/255, 27/255, 35/255, 1)
        elif self.alert_type is AlertType.YELLOW:
            self._small_text.text = "CONDITION: YELLOW"
            self.color = Color(1.0, 241/255, 0, 1)
        self._large_text.color = self.color.copy()
        self._small_text.color = self._large_text.color
        for path in self.fixed_paths:
            path.fill_color = self.color
        self.bar_data.clear()
        self._setup_bar_data()


class XAMLPath:
    """IMGUI Control to render the generic polygon from the Path directive of a C#'s XAML file.

    The XAML Path string data may define several shapes (polygons), which are represented here with the
    ``XAMLShape`` class we'll build based on the path-data.

    Note that when drawing shapes with fill color, those shapes are assumed by default to be concave (imgui's ``path_fill_concave`` is used),
    and thus some visual artifacts may appear in some cases. Most notably, internal holes are not supported inside concave shapes in imgui's
    simple concave rendering algorithm.
    """

    def __init__(self, path: str, scale: Vector2, fill_color: Color, stroke_color: Color = None, stroke_thickness: float = 0, is_convex=False):
        self.path = path
        self.scale = scale
        self.fill_color = fill_color
        self.stroke_color = stroke_color
        # NOTE: this `*4` was found by trial and error to put stroke thickness apparently right. However, this was tried out only with the
        #   reactor bar line paths. This might need refactoring to set different scale factor for other Paths.
        self.stroke_thickness = stroke_thickness * scale.min_component() * 4
        self.is_convex = is_convex
        self.shapes: list[XAMLShape] = []
        self._build()

    def _build(self):
        """Builds the internal XAMLShapes object that make up this path, based on our xaml
        string path data.

        This is called automatically on the constructor.
        """
        segments: list[str] = re.findall(r"([A-Z][^A-Z]*)", self.path)
        segments = [s.strip() for s in segments]
        shape: XAMLShape | None = None
        self.shapes = []
        for segment in segments:
            # XAML PATH
            # M x,y  => starting point (absolute)
            # L x,y  => line to (absolute)
            # C (x,y) (x,y) (x,y) ==> controlPoint1 controlPoint2 endPoint ==> Cubic bezier curve do last-point pro endpoint, com tais controls
            # Z => close figure (line from last point to initial point)
            args = segment.split()
            code = args[0]
            if code == "M" and shape is None:
                p = self._convert_point(args[1])
                shape = XAMLShape(p)
            elif code == "L":
                p = self._convert_point(args[1])
                shape.add_line(p)
            elif code == "C":
                c1 = self._convert_point(args[1])
                c2 = self._convert_point(args[2])
                end = self._convert_point(args[3])
                shape.add_curve(c1, c2, end)
            elif code == "Z":
                self.shapes.append(shape)
                shape = None

    def _convert_point(self, point_text: str):
        """Converts the textual representation of a point in the XAML's Path data-string
        to a Vector2 in our relative coordinate system."""
        return Vector2(*[float(c) for c in point_text.split(",")]) * self.scale

    def render(self, pos: Vector2, size: Vector2):
        """Renders this XAML Path polygon using IMGUI.

        The path's points (the polygon vertices) are internally represented in a relative area.
        So to properly draw the polygon, we need the area in imgui where we'll draw the polygon
        in order to properly scale the polygon to its rendering area.

        Args:
            pos (Vector2): The top-left position of the area to draw this path at.
            size (Vector2): The size of the area to draw this path.
        """
        draw = imgui.get_window_draw_list()
        for shape in self.shapes:
            if self.fill_color is not None:
                shape.render(pos, size)
                if self.is_convex:
                    draw.path_fill_convex(self.fill_color.u32)
                else:
                    draw.path_fill_concave(self.fill_color.u32)
            if self.stroke_color is not None and self.stroke_thickness > 0:
                shape.render(pos, size)
                draw.path_stroke(self.stroke_color.u32, thickness=self.stroke_thickness * size.min_component())

    def reverse(self):
        """Reverses the drawing order of all shapes contained in this path.

        When drawing primitive polygons with imgui, the vertices need to be drawn in clockwise order, otherwise
        the resulting drawn polygone will just be wrong. Using this method allows you to easily change
        the drawing order and thus fix this issue, in case the path was defined with anticlockwise points/segments.
        """
        for shape in self.shapes:
            shape.reverse()

    def swap_axis(self):
        """Swaps the X and Y components between each other in all points of all our shapes.

        This essentially "inverts", or rotates, the shapes 90 degrees.
        """
        for shape in self.shapes:
            shape.swap_axis()


class XAMLShape:
    """Represents a single shape/polygon from a XAML path-data string.

    A shape is a fully closed polygon, starting from a point, adding several "segments"
    (line/curves) based on the commands in the path-data, and finishing back at the starting point.
    """

    def __init__(self, initial_point: Vector2):
        self.initial_point = initial_point
        self.segments: list[XAMLLine | XAMLCurve] = []

    def add_line(self, point: Vector2):
        """Adds a ``XAMLLine`` segment in this shape, from the finishing point of the previous
        segment to the given ``point``. If no previous segment exist, the previous point is
        the shape's initial-point.

        Args:
            point (Vector2): point to draw a line to. In relative coords.
        """
        self.segments.append(XAMLLine(point))

    def add_curve(self, control1: Vector2, control2: Vector2, end: Vector2):
        """Adds a ``XAMLCurve`` segment in this shape, from the finishing point of the previous
        segment to the given ``end`` point. If no previous segment exists, the previous point is
        the shape's initial-point.

        Args:
            control1 (Vector2): First control point to pass to the XAMLCurve.
            control2 (Vector2): Second control point to pass to the XAMLCurve.
            end (Vector2): End point, in relative coords, where the curve will end (the starting point for the next segment).
        """
        self.segments.append(XAMLCurve(control1, control2, end))

    def render(self, pos: Vector2, size: Vector2):
        """Renders this shape using IMGUI.

        Note that while this draws all segments of this shape, it doesn't "finish" the shape render with
        either draw-filling or draw-stroking it. Calling ``path_fill_*`` or ``path_stroke`` is the responsibility
        of whoever uses this.

        Args:
            pos (Vector2): Top-left position of the area to draw this shape into.
            size (Vector2): Size of the area to draw this shape into.
        """
        draw = imgui.get_window_draw_list()
        draw.path_line_to(pos + size * self.initial_point)
        for segment in self.segments:
            segment.render(pos, size)

    def reverse(self):
        """Reverses the drawing order of this polygon's vertices, by reverting all our segments.

        When drawing primitive polygons with imgui, the vertices need to be drawn in clockwise order, otherwise
        the resulting drawn polygone will just be wrong. Using this method allows you to easily change
        the drawing order and thus fix this issue, in case the path was defined with anticlockwise points/segments.
        """
        self.segments.reverse()
        prev_point = self.initial_point
        for seg in reversed(self.segments):
            prev_point = seg.reverse(prev_point)
        self.initial_point = prev_point

    def swap_axis(self):
        """Swaps the X and Y components between each other in all points of all our segments.

        This essentially "inverts", or rotates, this shape 90 degrees.
        """
        self.initial_point.swap_axis()
        for segment in self.segments:
            segment.swap_axis()


class XAMLLine:
    """A single line segment for a ``XAMLShape`` object.

    This represents a line, from the previous point, to one defined by this segment, forming a line.
    """

    def __init__(self, point: Vector2):
        self.point = point

    def render(self, pos: Vector2, size: Vector2):
        """Renders this segment using IMGUI.

        This method should be called with the same args as passed to ``XAMLShape.render()``.

        Args:
            pos (Vector2): Top-left position of the area where our shape is being drawn.
            size (Vector2): Size of the area where our shape is being drawn.
        """
        draw = imgui.get_window_draw_list()
        p = pos + size * self.point
        draw.path_line_to(p)

    def reverse(self, prev_starting: Vector2):
        """Reverts the drawing order of this polygon segment.

        When drawing primitive polygons with imgui, the vertices need to be drawn in clockwise order, otherwise
        the resulting drawn polygone will just be wrong. Using this method allows you to easily change
        the drawing order and thus fix this issue, in case the path was defined with anticlockwise points/segments.

        Args:
            prev_starting (Vector2): the starting (or previous) point of this segment in the Shape it belongs to,
            before reversing.

        Returns:
            Vector2: our old ending point. This point should now be the starting point of this segment.
        """
        old_point = self.point
        self.point = prev_starting
        return old_point

    def swap_axis(self):
        """Swaps the X and Y components between each other in all points of this segment.

        This essentially "inverts", or rotates, this segment 90 degrees.
        """
        self.point.swap_axis()


class XAMLCurve:
    """A single curve segment for a ``XAMLShape`` object.

    This represents a cubic bezier curve, from the previous point to our end point,
    using 2 control-points for controlling the curve.
    """

    def __init__(self, control1: Vector2, control2: Vector2, end: Vector2):
        self.control1 = control1
        self.control2 = control2
        self.end = end

    def render(self, pos: Vector2, size: Vector2):
        """Renders this segment using IMGUI.

        This method should be called with the same args as passed to ``XAMLShape.render()``.

        Args:
            pos (Vector2): Top-left position of the area where our shape is being drawn.
            size (Vector2): Size of the area where our shape is being drawn.
        """
        draw = imgui.get_window_draw_list()
        c1 = pos + size * self.control1
        c2 = pos + size * self.control2
        end = pos + size * self.end
        draw.path_bezier_cubic_curve_to(c1, c2, end)

    def reverse(self, prev_starting: Vector2):
        """Reverts the drawing order of this polygon segment.

        When drawing primitive polygons with imgui, the vertices need to be drawn in clockwise order, otherwise
        the resulting drawn polygone will just be wrong. Using this method allows you to easily change
        the drawing order and thus fix this issue, in case the path was defined with anticlockwise points/segments.

        Args:
            prev_starting (Vector2): the starting (or previous) point of this segment in the Shape it belongs to,
            before reversing.

        Returns:
            Vector2: our old ending point. This point should now be the starting point of this segment.
        """
        self.control1, self.control2 = self.control2, self.control1
        old_end = self.end
        self.end = prev_starting
        return old_end

    def swap_axis(self):
        """Swaps the X and Y components between each other in all points of this segment.

        This essentially "inverts", or rotates, this segment 90 degrees.
        """
        self.control1.swap_axis()
        self.control2.swap_axis()
        self.end.swap_axis()


class Animation:
    """A simple tween object for animating a interpolable attribute in a generic object."""

    def __init__(self, target_attribute_key: str, duration: float = None):
        """
        Args:
            target_attribute_key (str): The key/name of the attribute we'll update in the given object (see ``update()``).
            The attribute doesn't need to exist - we'll directly set it.
            duration (float, optional): Duration of the animation. If not given (None), this'll default to the maximum time frame of the animation.
        """
        self.target_attribute_key = target_attribute_key
        self.elapsed_time = 0.0
        self.keyframes: list[tuple[any, float]] = []
        self._duration = duration

    def add_keyframe(self, time: float, value):
        """Adds a keyframe in this animation.

        Keyframes dictate the value of the animated attribute at a specific point in time.


        Args:
            time (float): Point in time to set this keyframe in. This should be unique amongst all keyframes, but the keyframes
            themselves don't need to be added in order (we'll order them based on ``time``).
            value (int|float|Vector2|Color): the value associated with this keyframe, to set as the attribute's value when the animation
            is at this point in time. Needs to be a interpolable numeric value.
        """
        self.keyframes.append((value, time))

    def add_looping_keyframe(self):
        """Adds a "looping" keyframe in this animation.

        This is a utility method that adds a keyframe with time equal the duration of this animation, and value equal to the
        first keyframe that was added (time=0). This keyframe can be added manually (with ``self.add_keyframe``) by whoever is building
        this, or using this method to facilitate it.

        Having the first (time=0) and last (time=duration) keyframes with the same value is usually needed so the animation seems
        to loop properly.
        """
        self.add_keyframe(self.duration, self.keyframes[0][0])

    @property
    def duration(self):
        """The duration of the animation, in seconds.

        When this amount of time elapses, the animation restarts (repeats).
        """
        return self._duration or max([kf[1] for kf in self.keyframes])

    def update(self, object):
        """Advances this animation based on IMGUI's delta-time between frames, and updates the value of the object's
        attribute we're animating.

        Basically does ``object.KEY = interpolate(self.keyframes, self.elapsed_time)``, where ``KEY`` is ``self.target_attribute_key``.

        Args:
            object (any): The object to update the attribute in.
        """
        value = multiple_lerp_with_weigths(self.keyframes, self.elapsed_time)
        if value is not None:
            setattr(object, self.target_attribute_key, value)

        delta_t = imgui.get_io().delta_time
        self.elapsed_time += delta_t
        if self.elapsed_time > self.duration:
            self.elapsed_time = 0

    def reset(self):
        """Resets this animation to its starting point (0 time elapsed)."""
        self.elapsed_time = 0.0
