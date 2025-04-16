import click
from lcarsmonitor.actions.actions import Action, ActionColors
from libasvat.imgui.nodes import input_property
from libasvat.imgui.general import not_user_creatable


@not_user_creatable
class DebugAction(Action):
    """Base class for debug-related actions."""

    def __init__(self):
        super().__init__()
        self.node_header_color = ActionColors.Debug


class Print(DebugAction):
    """Prints a value to the terminal."""

    @input_property()
    def text(self) -> str:
        """Text to print."""

    def execute(self):
        click.secho(self.text)
        self.trigger_flow()
