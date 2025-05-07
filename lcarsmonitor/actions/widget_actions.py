from lcarsmonitor.actions.actions import Action, ActionColors
from libasvat.imgui.editors.primitives import StringEditor
from libasvat.imgui.nodes import input_property, output_property
from libasvat.imgui.general import not_user_creatable
from lcarsmonitor.widgets.board import Board


@not_user_creatable
class WidgetAction(Action):
    """Base class for Widget-related actions."""

    def __init__(self):
        super().__init__()
        self.node_header_color = ActionColors.Widget


class SetBoard(WidgetAction):
    """Changes the selected child slot in a Board widget to the given name."""

    @input_property()
    def board(self) -> Board:
        """Board to change selected slot."""

    @input_property()
    def slot_name(self) -> str:
        """Name of slot to select in the board."""

    @output_property()
    def success(self) -> bool:
        """If changing selected slot on the board was successful."""

    def execute(self):
        self.success = False
        if self.board and self.slot_name:
            if self.slot_name in self.board.boards:
                self.board.selected_name = self.slot_name
                self.success = True
        self.trigger_flow()

    def _update_slot_name_editor(self, editor: StringEditor):
        """Callback to update TypeEditor object from our ``name`` property."""
        if self.board:
            if editor.options is None:
                # Node has just received a Board link.
                if self.slot_name not in self.board.boards:
                    self.slot_name = self.board.selected_name
            editor.options = self.board.boards
        else:
            editor.options = None
