import libasvat.imgui.editors.primitives as primitives
from libasvat.imgui.colors import Color, Colors
from libasvat.imgui.nodes import input_property, output_property
from libasvat.imgui.editors.database import TypeDatabase
from libasvat.imgui.editors.container import ObjectEditor
from lcarsmonitor.actions.conversion_actions import ConversionAction
from lcarsmonitor.widgets.base import BaseWidget


@TypeDatabase.register_editor_class_for_this(ObjectEditor)
class VisualStyle:
    """Represents the visual style (or "theme") of a widget.

    This defines several generic visual properties (such as colors) that can be used to customize the
    appearance of a widget. How these properties are used depends on the widget itself.

    Usually, this is used by interactible widgets or widgets that changes states according to user input somehow.
    """

    def __init__(self):
        self._normal_color: Color = Colors.white
        self._hovered_color: Color = Colors.white
        self._pressed_color: Color = Colors.white
        self._disabled_color: Color = Colors.grey
        self._text_color: Color = Colors.white

    @primitives.color_property()
    def normal_color(self) -> Color:
        """Normal color of this style. Used by default in the widget, when it doesn't match any other state."""
        return self._normal_color

    @normal_color.setter
    def normal_color(self, value: Color):
        self._normal_color = value

    @primitives.color_property()
    def hovered_color(self) -> Color:
        """Hovered color of this style. Used when the widget is hovered by the mouse."""
        return self._hovered_color

    @hovered_color.setter
    def hovered_color(self, value: Color):
        self._hovered_color = value

    @primitives.color_property()
    def pressed_color(self) -> Color:
        """Pressed color of this style. Used when the widget is pressed by the mouse."""
        return self._pressed_color

    @pressed_color.setter
    def pressed_color(self, value: Color):
        self._pressed_color = value

    @primitives.color_property()
    def disabled_color(self) -> Color:
        """Disabled color of this style. Used when the widget is disabled."""
        return self._disabled_color

    @disabled_color.setter
    def disabled_color(self, value: Color):
        self._disabled_color = value

    @primitives.color_property()
    def text_color(self) -> Color:
        """Text color of this style. Used by the widget when it draws text."""
        return self._text_color

    @text_color.setter
    def text_color(self, value: Color):
        self._text_color = value

    def get_current_color(self, widget: BaseWidget):
        """Gets the current color that should be used by the given widget based on its state."""
        if not widget.interactive:
            return self.disabled_color

        if widget.is_clicked:
            return self.pressed_color
        if widget.is_hovered:
            return self.hovered_color
        return self.normal_color


class BreakStyle(ConversionAction):
    """Splits a VisualStyle object into its properties."""

    @input_property()
    def style(self) -> VisualStyle:
        """Visual style of this rect. [GET/SET]"""
        return VisualStyle()

    @output_property(use_prop_value=True)
    def normal_color(self) -> Color:
        """The style's normal color."""
        return self.style.normal_color

    @output_property(use_prop_value=True)
    def hovered_color(self) -> Color:
        """The style's hovered color."""
        return self.style.hovered_color

    @output_property(use_prop_value=True)
    def pressed_color(self) -> Color:
        """The style's pressed color."""
        return self.style.pressed_color

    @output_property(use_prop_value=True)
    def disabled_color(self) -> Color:
        """The style's disabled color."""
        return self.style.disabled_color

    @output_property(use_prop_value=True)
    def text_color(self) -> Color:
        """The style's text color."""
        return self.style.text_color


class AssembleStyle(ConversionAction):
    """Creates a new VisualStyle object from its properties."""

    @input_property()
    def normal_color(self) -> Color:
        """The style's normal color."""
        return Colors.white

    @input_property()
    def hovered_color(self) -> Color:
        """The style's hovered color."""
        return Colors.white

    @input_property()
    def pressed_color(self) -> Color:
        """The style's pressed color."""
        return Colors.white

    @input_property()
    def disabled_color(self) -> Color:
        """The style's disabled color."""
        return Colors.white

    @input_property()
    def text_color(self) -> Color:
        """The style's text color."""
        return Colors.white

    @output_property(use_prop_value=True)
    def style(self) -> VisualStyle:
        """Visual style of this rect. [GET/SET]"""
        st = VisualStyle()
        st.normal_color = self.normal_color
        st.hovered_color = self.hovered_color
        st.pressed_color = self.pressed_color
        st.disabled_color = self.disabled_color
        st.text_color = self.text_color
        return st
