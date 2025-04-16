import lcarsmonitor.actions as actions
import libasvat.imgui.nodes as nodes
from lcarsmonitor.widgets.base import LeafWidget, WidgetColors
from lcarsmonitor.widgets.rect import RectMixin
from lcarsmonitor.widgets.label import TextMixin


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

    def render(self):
        self._draw_rect()
        self._draw_text()
        if self._handle_interaction():
            self._on_clicked.trigger()
