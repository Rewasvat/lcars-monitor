import lcarsmonitor.actions as actions
import libasvat.imgui.nodes as nodes
from libasvat.imgui.nodes import input_property
from lcarsmonitor.widgets.base import LeafWidget, WidgetColors
from lcarsmonitor.widgets.rect import RectMixin
from lcarsmonitor.widgets.label import TextMixin
from lcarsmonitor.widgets.style import VisualStyle


class Button(RectMixin, TextMixin, LeafWidget):
    """A simple button widget.

    Visually, its a ``Rect`` + ``Label`` widget.
    Allows to set a command that will be executed when clicked.
    """

    def __init__(self):
        LeafWidget.__init__(self)
        RectMixin.__init__(self)
        TextMixin.__init__(self)
        self.node_header_color = WidgetColors.Interactible
        self._on_clicked = actions.ActionFlow(self, nodes.PinKind.output, "On Click")
        self.add_pin(self._on_clicked)

    @input_property()
    def style(self) -> VisualStyle:
        """Visual style of this button. [GET/SET]"""
        return VisualStyle()

    def render(self):
        if self._handle_interaction():
            self._on_clicked.trigger()
        self._draw_rect(self.style.get_current_color(self))
        self._draw_text(self.style.text_color)
