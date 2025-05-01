import lcarsmonitor.actions as actions
import libasvat.imgui.nodes as nodes
from libasvat.imgui.nodes import input_property
from lcarsmonitor.widgets.lcars import LCARSWidget
from lcarsmonitor.widgets.lcars.lcars_style import LCARSStyle
from lcarsmonitor.widgets.base import WidgetColors
from lcarsmonitor.widgets.rect import RectMixin
from lcarsmonitor.widgets.label import TextMixin

# In here we implement "LCARS" version of common leaf-widgets.
# Main difference between them and the original widgets is that they use LCARS styles.


class LCARSRect(RectMixin, LCARSWidget):
    """Simple colored Rectangle widget."""

    def __init__(self):
        LCARSWidget.__init__(self)
        RectMixin.__init__(self)
        self.node_header_color = WidgetColors.Primitives

    @input_property()
    def style(self) -> LCARSStyle:
        """Visual style of this rect. [GET/SET]"""
        return LCARSStyle.COMMON

    def render(self):
        self._handle_interaction()
        self._draw_rect(self.style.get_style().get_current_color(self))


class LCARSLabel(TextMixin, LCARSWidget):
    """Simple text widget."""

    def __init__(self, text: str = ""):
        LCARSWidget.__init__(self)
        TextMixin.__init__(self, text)
        self.node_header_color = WidgetColors.Primitives

    @input_property()
    def style(self) -> LCARSStyle:
        """Visual style of this label. [GET/SET]"""
        return LCARSStyle.EXTERNAL_LABEL

    def render(self):
        self._draw_text(self.style.get_style().text_color)
        self._handle_interaction()


class LCARSButton(RectMixin, TextMixin, LCARSWidget):
    """A simple button widget.

    Visually, its a ``LCARSRect`` + ``LCARSLabel`` widget.
    Allows to set a command that will be executed when clicked.
    """

    def __init__(self):
        LCARSWidget.__init__(self)
        RectMixin.__init__(self)
        TextMixin.__init__(self)
        self.node_header_color = WidgetColors.Interactible
        self._on_clicked = actions.ActionFlow(self, nodes.PinKind.output, "On Click")
        self.add_pin(self._on_clicked)

    @input_property()
    def style(self) -> LCARSStyle:
        """Visual style of this button. [GET/SET]"""
        return LCARSStyle.COMMON

    def render(self):
        if self._handle_interaction():
            self._on_clicked.trigger()
        vistyle = self.style.get_style()
        self._draw_rect(vistyle.get_current_color(self))
        self._draw_text(vistyle.text_color)
