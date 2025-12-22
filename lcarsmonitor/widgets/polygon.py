import math
import click
import lcarsmonitor.actions as actions
import libasvat.imgui.editors.primitives as primitives
import libasvat.imgui.editors.container as containers
import libasvat.imgui.nodes.node_config as node_config
from libasvat.imgui.math import Vector2, Rectangle
from libasvat.imgui.colors import Color, Colors
from libasvat.imgui.assets import ImageInfo, AssetPath
from libasvat.imgui.nodes import input_property, PinKind
from libasvat.imgui.general import not_user_creatable
from libasvat.imgui.editors.database import TypeDatabase
from lcarsmonitor.widgets.base import LeafWidget, WidgetColors
from lcarsmonitor.widgets.rect import RectMixin
from lcarsmonitor.widgets.label import TextMixin, Alignment
from lcarsmonitor.widgets.style import VisualStyle
from imgui_bundle import imgui
from enum import Enum


class PolygonFillMode(Enum):
    """How to fill (or finish) a polygon drawing."""
    CONVEX_FILL = "CONVEX_FILL"
    """The CONVEX polygon will be drawn filled with the given color.

    Convex shapes are easy to draw and should work perfectly. Thus they are recommended to use (for filling)
    if you know the polygon is convex. Self-intersections or holes are not supported.
    """
    CONCAVE_FILL = "CONCAVE_FILL"
    """The CONCAVE polygon will be drawn filled with the given color.

    Concave shapes are more expensive (O(N^2)) to draw than convex ones. This works by trying to "split" the
    concave polygon into several convex ones, and drawing them together. This is provided by the library as
    a convenience for the user, and as such might have some drawing issues in some cases - use with care.
    Self-intersections or holes are still not supported.
    """
    STROKE = "STROKE"
    """The polygon will be drawn as a stroke: only the polygon lines (borders) are drawn,
    with the given color and thickness."""


class BasePolygonAttributes:
    """Mixin of common attributes/properties for polygon-related widgets."""

    def __init__(self):
        self._fill_mode: PolygonFillMode = PolygonFillMode.STROKE
        self._out_margin = 5

    @primitives.enum_property()
    def fill_mode(self):
        """How the polygon is drawn/filled [GET/SET]"""
        return self._fill_mode

    @fill_mode.setter
    def fill_mode(self, value: PolygonFillMode):
        self._fill_mode = value

    @input_property()
    def use_area_ratio(self) -> bool:
        """If we should use our slot area's aspect-ratio for the inner polygon area. [GET/SET]

        If false, we'll use our `ratio` attribute as our fixed aspect-ratio.
        Otherwise, we'll use our slot's area aspect-ratio, in which case the polygon's area and ratio will
        change along with our area.
        """
        return True

    @input_property(min=0, speed=0.1)
    def ratio(self) -> float:
        """The aspect-ratio of our inner polygon area. [GET/SET]

        The "inner polygon area" is the rect area where the polygon will be drawn. This is the maximum possible rect
        with this `ratio` contained within our slot's area.
        """
        return 1.0

    @primitives.float_property(speed=0.1)
    def out_margin(self) -> float:
        """The margin of the inner polygon area to the edges of our slot's available area."""
        return self._out_margin

    @out_margin.setter
    def out_margin(self, value: float):
        self._out_margin = value

    @input_property()
    def style(self) -> VisualStyle:
        """Visual style of this polygon. [GET/SET]"""
        return VisualStyle()

    @input_property(min=0)
    def thickness(self) -> float:
        """Thickness of this polygon's lines, when using fill-mode STROKE. [GET/SET]"""
        return 5

    def get_inner_area(self, area: Rectangle):
        """Gets the inner area to draw this polygon inside the given area rectangle,
        respecting our aspect-ratio and margin properties.

        Args:
            area (Rectangle): parent area in which the polygon will be drawn.

        Returns:
            Rectangle: inner area inside the parent area to draw to polygon in.
        """
        if self.use_area_ratio:
            ratio = area.size.aspect_ratio()
        else:
            ratio = self.ratio
        return area.get_inner_rect(ratio, self.out_margin)


# NOTE: Important: filled shapes must always use clockwise winding order! The anti-aliasing fringe depends on it.
#       Counter-clockwise shapes will have "inward" anti-aliasing.
###
# TODO: botao pra abrir algum tipo de UI pra desenhar os pontos in-game pra config local (em vez de setar pontos na lista manualmente).
class Polygon(BasePolygonAttributes, LeafWidget):
    """Generic polygon drawing widget.

    Allows the definition and drawing of a polygonal shape from a list of points in relative-coords.
    The points in this list should be in clockwise winding order for the polygon to be properly drawn.

    For more advanced generic shape drawing, see the `Shape` widget.
    """

    def __init__(self):
        LeafWidget.__init__(self)
        BasePolygonAttributes.__init__(self)
        self.node_header_color = WidgetColors.Primitives
        self._on_clicked = actions.ActionFlow(self, PinKind.output, "On Click")
        self.add_pin(self._on_clicked)

    @input_property(dynamic_input_pins=True, item_config={"x_range": (0, 1), "y_range": (0, 1)})
    def points(self) -> list[Vector2]:
        """The list of points (vertices) of the polygon.

        Each point is a relative position inside our "inner polygon area", with (0,0) being top-left and
        (1,1) being bottom-right of the area, and the minimum/maximum points.

        The "inner polygon area" is the rect area where the polygon will be drawn. This is the maximum possible rect
        with our `ratio` contained within our slot's area. The `ratio` is the aspect-ratio of this inner area rect.
        See the `ratio` and `use_area_ratio` attributes.

        At least 3 points are required to draw a polygon. The points in this list should be in clockwise winding order
        for the polygon to be properly drawn.
        """
        return []

    def _draw_polygon(self, color: Color):
        """Draws this polygon using simple imgui draw-list add-poly commands."""
        if len(self.points) < 3:
            return

        draw = imgui.get_window_draw_list()
        color_val = color.u32
        inner_area = self.get_inner_area(self.area)

        absolute_points = []
        for point in self.points:
            inner = inner_area.get_inner_point(point)
            absolute_points.append(imgui.ImVec2(inner.x, inner.y))

        if self.fill_mode is PolygonFillMode.CONCAVE_FILL:
            draw.add_concave_poly_filled(absolute_points, color_val)
        elif self.fill_mode is PolygonFillMode.CONVEX_FILL:
            draw.add_convex_poly_filled(absolute_points, color_val)
        elif self.fill_mode is PolygonFillMode.STROKE:
            # draw.add_polyline(absolute_points, color_val, thickness=self.thickness)
            # NOTE: add_polyline isn't working - it doesn't accept a list of Vector2 (or ImVec2, or (x,y) tuples...)
            for point in absolute_points:
                draw.path_line_to(point)
            draw.path_line_to(absolute_points[0])
            draw.path_stroke(color_val, thickness=self.thickness)
        else:
            click.secho(f"Polygon: invalid fill-mode '{self.fill_mode}' for drawing", fg="red")

    def render(self):
        if self._handle_interaction():
            self._on_clicked.trigger()
        self._draw_polygon(self.style.get_current_color(self))


@not_user_creatable
@TypeDatabase.register_editor_class_for_this(containers.ObjectEditor)
class ShapeSegment:
    """Base segment class to define the path-segments in a Shape widget.

    Subclasses of this represent the possible segments to use in a shape.
    """

    def __init__(self):
        self._area: Rectangle = None
        self._starting_point: Vector2 = None

    @property
    def area(self):
        """The area in which the shape, and thus this segment, is being drawn.

        It is recommended that Segment subclasses always work with relative positions (points in [0,1])
        and use `area.get_inner_point(p)` to get the appropriate absolute point in the draw area for drawing.

        This value is updated each frame by our parent Shape object, before calling `draw()`.
        """
        return self._area

    @property
    def starting_point(self):
        """The starting-point of this segment, in relative coords.

        This is never set directly by this segment - it matches the end-point (see `get_endpoint()`) of
        the previous segment. As such this is updated each frame by our parent Shape object, before calling `draw()`.

        While this value is thus always available for the segment implementations to use, it is mostly here to allow
        segments to use it for internal calculations that require knowledge of the starting point. All imgui drawlists
        path-methods use the starting point internally based on previous path calls.
        """
        return self._starting_point

    def update(self, area: Rectangle, prev_point: Vector2):
        """Updates our internal area and starting-point attributes to the given values."""
        self._area = area
        self._starting_point = prev_point

    def draw(self):
        """Draws this shape segment using IMGUI DrawLists path_* methods, according
        to the segment's logic.

        Note this is a abstract method: ShapeSegment subclasses should override this with their logic.
        """
        raise NotImplementedError(f"ShapeSegment subclass '{type(self).__name__}' missing `draw()` implementation.")

    def get_endpoint(self) -> Vector2:
        """Gets this segment's endpoint, in area relative coords.

        This point is used as the starting point for the next segment in the shape.

        Note this is a abstract method: ShapeSegment subclasses should override this with the logic.

        Returns:
            Vector2: the segment's endpoint, in relative coords.
        """
        raise NotImplementedError(f"ShapeSegment subclass '{type(self).__name__}' missing `get_endpoint()` implementation.")

    def __str__(self):
        return type(self).__name__.replace("Shape", "")


class ShapeLineSegment(ShapeSegment):
    """Line segment for a Shape.

    Draws a line from the previous end-point to a point specified in this segment.
    """

    @input_property(x_range=(0, 1), y_range=(0, 1))
    def end_point(self) -> Vector2:
        """The endpoint of this line segment.

        The line drawn by this segment will be from the previous end-point to this point.
        This point will then be the end-point for the next segment in the shape.

        The point is a relative position inside our shape's area, with (0,0) being top-left and
        (1,1) being bottom-right of the area, and the minimum/maximum points.
        """
        return Vector2()

    def draw(self):
        draw = imgui.get_window_draw_list()
        draw.path_line_to(self.area.get_inner_point(self.end_point))
        # draw.path_line_to_merge_duplicate(position)

    def get_endpoint(self):
        return self.end_point


class ShapeArcSegment(ShapeSegment):
    """Arc segment for a shape.

    Draws a circle arc from the previous end-point and starting angle to a ending angle, which
    will be the arc's endpoint.
    """

    @input_property(min=0, max=1, is_slider=True)
    def radius(self) -> float:
        """The radius of the arc's curve from its center point.

        This value (in [0,1] range) is normalized to the minimum component/axis of the area we're being drawn to.
        Which means when at max radius (value=1), the curve will go from one side of the area to the other.
        """
        return 0.05

    @property
    def actual_radius(self):
        """The actual radius of this arc, based on our relative radius (`self.radius`) and our inner area."""
        return self.radius * self.area.size.min_component()

    @input_property(min=0, max=360, is_slider=True)
    def angle_start(self) -> float:
        """The starting angle of the arc, in degrees.

        0 degrees points to the right (+X axis).

        This angle, along with the previous end-point, are used to determine the Arc's center-point.
        """
        return 270.0

    @input_property(min=0, max=360, is_slider=True)
    def angle_end(self) -> float:
        """The ending angle of the arc, in degrees.

        0 degrees points to the right (+X axis).

        The arc is drawn from `angle_start` to `angle_end` in a clockwise direction.
        The point in the the arc defined by this angle is this arc's end-point for the next segment.
        """
        return 270.0

    @property
    def center(self):
        """Gets the center point of this arc, based on the segment's starting-point and the arc's
        starting angle."""
        # offset = vector from center to starting point
        angle_rads = math.radians(self.angle_start)
        offset = Vector2.from_angle(angle_rads) * self.radius
        return self.starting_point - offset

    def draw(self):
        draw = imgui.get_window_draw_list()
        angle_min = math.radians(self.angle_start)
        angle_max = math.radians(self.angle_end)
        actual_center = self.area.get_inner_point(self.center)
        # TODO: arrumar isso. angleMin ~= 270 faz coisas estranhas acontecerem... Parece que o center se move pra um lugar que não devia,
        #   ai o starting-point não bate com o endpoint anterior.
        draw.path_arc_to(actual_center, self.actual_radius, angle_min, angle_min + angle_max)
        # draw.path_arc_to_fast(center, radius, angleMinOf12, angleMaxOf12)
        # draw.path_elliptical_arc_to(center, radius, rotation, angleMin, angleMax)

    def get_endpoint(self):
        angle_rads = math.radians(self.angle_end)
        # offset is vector from center to endpoint.
        offset = Vector2.from_angle(angle_rads) * self.radius
        return self.center + offset


class ShapeCurveSegment(ShapeSegment):
    """Bezier-curve segment for a Shape.

    Draws a bezier-curve from the previous end-point to a point specified in this segment.
    """

    @input_property(x_range=(0, 1), y_range=(0, 1))
    def control_point1(self) -> Vector2:
        """The first control-point for this bezier-curve.

        The point is a relative position inside our shape's area, with (0,0) being top-left and
        (1,1) being bottom-right of the area, and the minimum/maximum points.
        """
        return Vector2()

    @input_property(x_range=(0, 1), y_range=(0, 1))
    def control_point2(self) -> Vector2:
        """The second control-point for this bezier-curve.

        This is only used if this is a cubic bezier-curve (see `use_cubic_curve` property).

        The point is a relative position inside our shape's area, with (0,0) being top-left and
        (1,1) being bottom-right of the area, and the minimum/maximum points.
        """
        return Vector2()

    @input_property(x_range=(0, 1), y_range=(0, 1))
    def end_point(self) -> Vector2:
        """The endpoint of this curve segment.

        The curve drawn by this segment will be from the previous end-point to this point,
        bending according to our control points.
        This point will then be the end-point for the next segment in the shape.

        The point is a relative position inside our shape's area, with (0,0) being top-left and
        (1,1) being bottom-right of the area, and the minimum/maximum points.
        """
        return Vector2()

    @input_property()
    def use_cubic_curve(self) -> bool:
        """If this segment will use a CUBIC bezier-curve instead of the default QUADRATIC curve."""
        return False

    def draw(self):
        draw = imgui.get_window_draw_list()
        c1 = self.area.get_inner_point(self.control_point1)
        endpoint = self.area.get_inner_point(self.end_point)
        if self.use_cubic_curve:
            c2 = self.area.get_inner_point(self.control_point2)
            draw.path_bezier_cubic_curve_to(c1, c2, endpoint)
        else:
            draw.path_bezier_quadratic_curve_to(c1, endpoint)

    def get_endpoint(self):
        return self.end_point


class Shape(BasePolygonAttributes, LeafWidget):
    """Path-based generic shape drawing widget.

    Allows the definition of a path, built using lines and curves, in order to create a generic shape.

    The points/segments in the path should be in clockwise winding order for the shape to be properly drawn.
    """

    def __init__(self):
        LeafWidget.__init__(self)
        BasePolygonAttributes.__init__(self)
        self.node_header_color = WidgetColors.Primitives
        self._on_clicked = actions.ActionFlow(self, PinKind.output, "On Click")
        self.add_pin(self._on_clicked)
        self._segments: list[ShapeSegment] = []

    @input_property(x_range=(0, 1), y_range=(0, 1))
    def starting_point(self) -> Vector2:
        """The starting (or initial) point of the path to draw this shape.

        The point is a relative position inside our "inner polygon area", with (0,0) being top-left and
        (1,1) being bottom-right of the area, and the minimum/maximum points.

        The "inner polygon area" is the rect area where the polygon will be drawn. This is the maximum possible rect
        with our `ratio` contained within our slot's area. The `ratio` is the aspect-ratio of this inner area rect.
        See the `ratio` and `use_area_ratio` attributes.

        The path segments are then drawn in order from this point in order to complete the shape.
        This acts as the root/initial "previous end-point" to which the following segments use.
        """
        return Vector2()

    @containers.list_property(use_item_subclasses=True)
    def segments(self) -> list[ShapeSegment]:
        """Ordered list of path-segments that make up this shape. [GET/SET]"""
        return self._segments

    @segments.setter
    def segments(self, value: list[ShapeSegment]):
        self._segments = value

    def _draw_shape(self, color: Color):
        """Draws this path-based shape, by orderly drawing all our path segments."""
        draw = imgui.get_window_draw_list()
        inner_area = self.get_inner_area(self.area)

        # Start drawing shape by its initial point.
        if len(self.segments) < 1:
            # no point trying to draw shape without any segments.
            return
        draw.path_line_to(inner_area.get_inner_point(self.starting_point))

        # Then draw each segment in order.
        prev_point = self.starting_point
        for segment in self.segments:
            segment.update(inner_area, prev_point)
            segment.draw()
            prev_point = segment.get_endpoint()

        # Finish the shape with fill or stroke color.
        if self.fill_mode is PolygonFillMode.CONCAVE_FILL:
            draw.path_fill_concave(color.u32)
        elif self.fill_mode is PolygonFillMode.CONVEX_FILL:
            draw.path_fill_convex(color.u32)
        else:
            draw.path_line_to(inner_area.get_inner_point(self.starting_point))
            draw.path_stroke(color.u32, thickness=self.thickness)

    def render(self):
        if self._handle_interaction():
            self._on_clicked.trigger()
        self._draw_shape(self.style.get_current_color(self))

    def get_custom_config_data(self):
        data = super().get_custom_config_data()
        data["segments"] = [node_config.get_all_prop_values_for_storage(segment) for segment in self.segments]
        return data

    def setup_from_config_post_props(self, data):
        # Our segments property isn't automatically saved properly since its a list of complex objects.
        # Each segment is saved, but not its properties. So we do that ourselves here.
        # TODO: seria bom arrumar isso, pro get_all/restore_prop_values funcionar recursivamente com containers de objetos complexos.
        #   Talvez afete a necessidade desses setup_from_config nos Nodes.
        for i, segment_data in enumerate(data.get("segments", [])):
            node_config.restore_prop_values_to_object(self.segments[i], segment_data)
        return super().setup_from_config_post_props(data)
