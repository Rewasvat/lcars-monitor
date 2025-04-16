from imgui_bundle import imgui
from lcarsmonitor.actions.actions import Action, ActionColors
from libasvat.imgui.nodes import input_property, output_property
from libasvat.imgui.general import not_user_creatable
from libasvat.imgui.colors import Color, Colors
from libasvat.imgui.math import Vector2, Rectangle
from libasvat.imgui.type_editor import TypeDatabase


@not_user_creatable
class ConversionAction(Action):
    """Base class for debug-related actions."""

    def __init__(self):
        super().__init__(False)
        self.node_header_color = ActionColors.Conversion


for cls in TypeDatabase().get_creatable_types():
    @output_property(value_type=cls)
    def value(self):
        """User-created value."""

    create_action_cls = type(f"Create{cls.__name__.capitalize()}", (ConversionAction,), {"value": value})
    create_action_cls.__doc__ = f"Allows user creation of a {cls.__name__}"

    globals()[create_action_cls.__name__] = create_action_cls


class BreakVector2(ConversionAction):
    """Splits a Vector2 value in its constituent components (X and Y)."""

    @input_property()
    def vector(self) -> Vector2:
        """Vector2 to get components."""
        return Vector2()

    @output_property(use_prop_value=True)
    def x(self) -> float:
        """The vector's X component."""
        return self.vector.x

    @output_property(use_prop_value=True)
    def y(self) -> float:
        """The vector's Y component."""
        return self.vector.y


class AssembleVector2(ConversionAction):
    """Creates a new Vector2 value from X and Y values."""

    @input_property()
    def x(self) -> float:
        """The vector's X component."""
        return 0.0

    @input_property()
    def y(self) -> float:
        """The vector's Y component."""
        return 0.0

    @output_property(use_prop_value=True)
    def vector(self) -> Vector2:
        """The (X, Y) vector."""
        return Vector2(self.x, self.y)


class BreakRectangle(ConversionAction):
    """Splits a Rectangle value in its constituent components."""

    @input_property()
    def rect(self) -> Rectangle:
        """Rectangle to get components."""
        return Rectangle()

    @output_property(use_prop_value=True)
    def size(self) -> Vector2:
        """The rectangle's size."""
        return self.rect.size

    @output_property(use_prop_value=True)
    def position(self) -> Vector2:
        """The rectangle's position (top left corner)."""
        return self.rect.position

    @output_property(use_prop_value=True)
    def top_right_pos(self) -> Vector2:
        """The rectangle's top right corner vector"""
        return self.rect.top_right_pos

    @output_property(use_prop_value=True)
    def bottom_left_pos(self) -> Vector2:
        """The rectangle's bottom left corner vector"""
        return self.rect.bottom_left_pos

    @output_property(use_prop_value=True)
    def bottom_right_pos(self) -> Vector2:
        """The rectangle's bottom right corner vector"""
        return self.rect.bottom_right_pos

    @output_property(use_prop_value=True)
    def center(self) -> Vector2:
        """The rectangle's center vector"""
        return self.rect.center


class AssembleRectangle(ConversionAction):
    """Creates a new Rectangle value from a position and size."""

    @input_property()
    def position(self) -> Vector2:
        """The rectangle's position (top left corner)."""
        return Vector2()

    @input_property()
    def size(self) -> Vector2:
        """The rectangle's size."""
        return Vector2()

    @output_property(use_prop_value=True)
    def rect(self) -> Rectangle:
        """Rectangle with the given position and size."""
        return Rectangle(self.position, self.size)


class BreakColor(ConversionAction):
    """Splits a Color value in its constituent components (R, G, B, A)."""

    @input_property()
    def color(self) -> Color:
        """Color to get components."""
        return Colors.white

    @output_property(use_prop_value=True)
    def r(self) -> float:
        """The color's R (red) component, in the range [0, 1]."""
        return self.color.x

    @output_property(use_prop_value=True)
    def g(self) -> float:
        """The color's G (green) component, in the range [0, 1]."""
        return self.color.y

    @output_property(use_prop_value=True)
    def b(self) -> float:
        """The color's B (blue) component, in the range [0, 1]."""
        return self.color.z

    @output_property(use_prop_value=True)
    def a(self) -> float:
        """The color's A (alpha) component, in the range [0, 1]."""
        return self.color.w


class AssembleColor(ConversionAction):
    """Creates a new Color value from its R, G, B, A components."""

    @input_property(min=0, max=1, is_slider=True, flags=imgui.SliderFlags_.always_clamp)
    def r(self) -> float:
        """The color's R (red) component, in the range [0, 1]."""
        return 1

    @input_property(min=0, max=1, is_slider=True, flags=imgui.SliderFlags_.always_clamp)
    def g(self) -> float:
        """The color's G (green) component, in the range [0, 1]."""
        return 1

    @input_property(min=0, max=1, is_slider=True, flags=imgui.SliderFlags_.always_clamp)
    def b(self) -> float:
        """The color's B (blue) component, in the range [0, 1]."""
        return 1

    @input_property(min=0, max=1, is_slider=True, flags=imgui.SliderFlags_.always_clamp)
    def a(self) -> float:
        """The color's A (alpha) component, in the range [0, 1]."""
        return 1

    @output_property(use_prop_value=True)
    def color(self) -> Color:
        """RGBA Color"""
        return Color(self.r, self.g, self.b, self.a)
