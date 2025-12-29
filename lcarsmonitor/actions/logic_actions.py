import libasvat.imgui.editors.primitives as primitives
from lcarsmonitor.actions.actions import Action, ActionFlow, ActionColors
from libasvat.imgui.nodes import PinKind, input_property, output_property, SelectableTypeMixin, DataPin, DataPinState
from libasvat.imgui.general import not_user_creatable
from libasvat.imgui.editors.primitives import StringEditor
from imgui_bundle import imgui


@not_user_creatable
class LogicAction(Action):
    """Base class for logic flow related actions."""

    def __init__(self, include_default_flow_pins=True, create_data_pins=True):
        super().__init__(include_default_flow_pins, create_data_pins)
        self.node_header_color = ActionColors.Logic


class ActionBranch(LogicAction):
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
        """Boolean value for the condition check."""

    def execute(self):
        if self.condition:
            self.trigger_flow("True")
        else:
            self.trigger_flow("False")


class DataBranch(SelectableTypeMixin, LogicAction):
    """Data values IF branching"""

    def __init__(self):
        super().__init__(False)

    @input_property()
    def condition(self) -> bool:
        """Boolean value for the condition check."""

    @input_property()
    def truthy(self):
        """Value returned by this action if ``condition`` is truthy."""

    @input_property()
    def falsy(self):
        """Value returned by this action if ``condition`` is falsy."""

    @output_property(use_prop_value=True)
    def result(self):
        """The result of this data branch. Value is the same as either our ``truthy`` or ``falsy`` input, according to our ``condition``."""
        if self.condition:
            return self.truthy
        return self.falsy


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


class DataSwitch(SelectableTypeMixin, LogicAction):
    """Enables switching between different input data (of the same type).

    User can setup multiple named input-pins to receive data, and select which input is "used" by its name.
    The node outputs the data from the selected input.
    """

    def __init__(self):
        self._subpins: dict[str, DataPin] = {}
        self._input_options: str = "A,B"
        super().__init__(False, False)
        self.create_data_pins_from_properties()

    @primitives.string_property(imgui.InputTextFlags_.enter_returns_true)
    def options(self) -> str:
        """List of input options for this switch, defined as a comma-separated list of input names.

        For example, defining this property as ``A,B,C`` will create 3 inputs for the switch: A, B and C.
        """
        return self._input_options

    @options.setter
    def options(self, value: str):
        self._input_options = value
        self.update_input_pins()

    @input_property()
    def selection(self) -> str:
        """The name of the input data to pass as the output of this switch."""

    @output_property(use_prop_value=True)
    def output(self):
        """The output of this switch. Value is the same as our input-pin whose name matches the ``selection`` name.
        If no name matches, we'll default to output the data from the first input-pin.
        """
        if self.selection in self._subpins:
            pin = self._subpins[self.selection]
            return pin.get_value()
        if len(self._subpins) > 0:
            return self._subpins[self.input_names[0]].get_value()
        return self.value_type()

    @property
    def input_names(self):
        """Names of our input pins, taken from the ``options`` property."""
        return self.options.split(",")

    def update_input_pins(self):
        """Updates our dynamic switch input pins, creating or deleting them as needed so that our pins
        matches the expected input options defined in ``self.options``."""
        new_keys = set(self.input_names)
        cur_keys = set(self._subpins.keys())
        missing = new_keys - cur_keys
        for name in missing:
            self.create_subpin(name)
        removed = cur_keys - new_keys
        for name in removed:
            pin = self._subpins.pop(name)
            pin.delete()

    def create_subpin(self, name: str):
        """Creates a new input sub-pin in this node with the given name.
        These subpins are meant to represent the possible inputs for the switch, based on the given ``options``.

        Args:
            name (str): sub-pin name.
        """
        tooltip = f"Input value for the switch's '{name}' option."
        state = DataPinState(name, PinKind.input, tooltip, self.value_type)
        pin = DataPin(self, state)
        self.add_pin(pin)
        self._subpins[name] = pin

    def render_edit_details(self):
        imgui.text("DataSwitch Properties:")
        type(self).options.render_editor(self)
        imgui.separator()
        return super().render_edit_details()

    def _update_selection_editor(self, editor: StringEditor):
        """Callback to update TypeEditor object from our ``selection`` property."""
        editor.options = self.input_names
