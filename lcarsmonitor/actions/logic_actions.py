from lcarsmonitor.actions.actions import Action, ActionFlow, ActionColors
from libasvat.imgui.nodes import PinKind, input_property, output_property
from libasvat.imgui.general import not_user_creatable


@not_user_creatable
class LogicAction(Action):
    """Base class for logic flow related actions."""

    def __init__(self):
        super().__init__()
        self.node_header_color = ActionColors.Logic


class Branch(LogicAction):
    """Action Flow IF branching"""

    def __init__(self):
        super().__init__()
        default_trigger = self.get_output_pin("Trigger")
        default_trigger.pin_name = "True"
        default_trigger.pin_tooltip = "Triggered when the condition is True (truthy)."
        false_trigger = ActionFlow(self, PinKind.output, "False")
        false_trigger.pin_tooltip = "Triggered when the condition is False (falsy)."
        self.add_pin(false_trigger)

    @input_property()
    def condition(self) -> bool:
        """Boolean value for the condition."""

    def execute(self):
        if self.condition:
            self.trigger_flow("True")
        else:
            self.trigger_flow("False")


class ForRangeLoop(LogicAction):
    """Simple FOR Range Loop.

    Basically the same as Python's ``for i in range(start, end, step)``.
    Produces integers from ``start`` (inclusive) to ``end`` (exclusive) by ``step``.
    """

    def __init__(self):
        super().__init__()
        default_trigger = self.get_output_pin("Trigger")
        default_trigger.pin_name = "On Iteration"
        default_trigger.pin_tooltip = "Triggered on each loop iteration."
        finish_trigger = ActionFlow(self, PinKind.output, "Finished")
        finish_trigger.pin_tooltip = "Triggered when the loop ends"
        self.add_pin(finish_trigger)

    @input_property()
    def start(self) -> int:
        """The starting index of the range loop. Defaults to 0."""
        return 0

    @input_property()
    def end(self) -> int:
        """The final index of the range loop. When start-index is 0 (the default), this is equal to the
        number of iterations the loop will perform."""
        return 0

    @input_property()
    def step(self) -> int:
        """The step (or increment/decrement) of the loop: the current index will be updated by this amount on each iteration."""
        return 1

    @output_property()
    def index(self) -> int:
        """The current index of the loop. Should be used along with ``On Iteration`` triggers."""

    def execute(self):
        for i in range(self.start, self.end, self.step):
            self.index = i
            self.trigger_flow("On Iteration")
        self.trigger_flow("Finished")
