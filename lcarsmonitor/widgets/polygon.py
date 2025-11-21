import click
import lcarsmonitor.actions as actions
import libasvat.imgui.editors.primitives as primitives
from libasvat.imgui.math import Vector2, Rectangle
from libasvat.imgui.colors import Color, Colors
from libasvat.imgui.assets import ImageInfo, AssetPath
from libasvat.imgui.nodes import input_property, PinKind
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


# NOTE: Important: filled shapes must always use clockwise winding order! The anti-aliasing fringe depends on it.
#       Counter-clockwise shapes will have "inward" anti-aliasing.
###
# TODO: botao pra abrir algum tipo de UI pra desenhar os pontos in-game pra config local (em vez de setar pontos na lista manualmente).
class Polygon(LeafWidget):
    """Generic polygon drawing widget.

    Allows the definition and drawing of a polygonal shape from a list of points in relative-coords.

    For more advanced generic shape drawing, see the `Shape` widget.
    """

    def __init__(self):
        super().__init__()
        self.node_header_color = WidgetColors.Primitives
        self._fill_mode: PolygonFillMode = PolygonFillMode.STROKE
        self._out_margin = 5
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

    def _draw_polygon(self, color: Color):
        """Draws this polygon using simple imgui draw-list add-poly commands."""
        if len(self.points) < 3:
            return

        draw = imgui.get_window_draw_list()
        color_val = color.u32
        if self.use_area_ratio:
            ratio = self.area.size.aspect_ratio()
        else:
            ratio = self.ratio
        inner_area = self.area.get_inner_rect(ratio, self.out_margin)

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


class Shape:
    """Path-based generic shape drawing widget.

    Allows the definition of a path, built using lines and curves, in order to create a generic shape.
    """
    # draw.path_fill_concave(color)
    # draw.path_fill_convex(color)
    # draw.path_stroke(color, thickness=thick)
    # #
    # draw.path_arc_to(center, radius, angleMin, angleMax)
    # draw.path_arc_to_fast(center, radius, angleMinOf12, angleMaxOf12)
    # draw.path_elliptical_arc_to(center, radius, rotation, angleMin, angleMax)

    # draw.path_bezier_cubic_curve_to(c1, c2, end)
    # draw.path_bezier_quadratic_curve_to(c1?, end?)  [eh: p2,p3]

    # draw.path_line_to(position)
    # draw.path_line_to_merge_duplicate(position)
    # draw.path_rect(rectMin, rectMax, rounding, drawFlags)

    # draw.path_clear()
