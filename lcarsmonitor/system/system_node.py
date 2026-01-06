import click
import libasvat.imgui.editors.primitives as primitives
from libasvat.imgui.colors import Color
from libasvat.imgui.general import not_user_creatable
from libasvat.imgui.nodes import PinKind, input_property, output_property
from libasvat.imgui.nodes.nodes_data import DataPin, DataPinState, SyncedDataPropertyState
from libasvat.imgui.editors.database import TypeDatabase
from lcarsmonitor.system.system import UIManager, UISystem, SystemConfig
from lcarsmonitor.widgets.base import LeafWidget, ContainerWidget, WidgetColors, Slot
from lcarsmonitor.actions.actions import Action, ActionFlow
from imgui_bundle import imgui


###########################################
# MAIN USE SYSTEM NODE
###########################################
class UseSystem(ContainerWidget):
    """Executes a UISystem.

    This allows to execute one of the saved UISystem configs as a single node in another graph.
    The system's input/output properties (data values, widget connections, etc) are connected to equivalent
    pins in this node, thus allowing to pass/receive data, actions and widgets from the contained UISystem.

    Allowing re-use of a UISystem in other systems may simplify a lot of work to create complex graphs.
    """

    def __init__(self):
        super().__init__()
        self.accepts_new_slots = False
        self._slot_class = SystemSlot
        self.node_bg_color = Color(0.1, 0.25, 0.15, 0.75)
        self.node_header_color = WidgetColors.External
        self._uisystem: UISystem = None
        self._system_pins: list[ActionFlow | DataPin] = []

    @primitives.string_property()
    def system_name(self) -> str:
        """Name of UISystem Config to use."""
        return self._uisystem.name if self._uisystem is not None else ""

    @system_name.setter
    def system_name(self, value: str):
        if self._uisystem is not None:
            if self._uisystem.name == value:
                return
            self._clear_system()
        manager = UIManager()
        config = manager.get_config(value)
        if config:
            self._set_system(config)

    @property
    def uisystem(self):
        """Gets our internal UISystem being used.

        This depends on our ``system_name`` property.
        """
        return self._uisystem

    def render(self):
        self._handle_interaction()
        # No need to call `self.update_slots()` here, since we have no logic to update them.
        # Our 'SystemSlots' areas are actually directly updated by the ExternalWidgets that they render,
        # from the internal sub-UISystem.
        if self._uisystem is not None:
            self._uisystem.render()

    def delete(self):
        if self._uisystem is not None:
            self._clear_system()
        return super().delete()

    def get_custom_config_data(self):
        data = super().get_custom_config_data()
        data["system_name"] = self.system_name
        for pin in self._system_pins:
            if pin.pin_kind is PinKind.output or isinstance(pin, ActionFlow):
                # No need to store output data nor store anything for the action pins.
                continue
            data[f"Input_{pin.pin_name}"] = pin.get_value()
        return data

    def setup_from_config(self, data):
        system_name = data.get("system_name", None)
        if system_name is None:
            # Stored data is incomplete, probably was saved before this implementation.
            return
        # NodeConfig logic would set the system-name value automatically, since `self.system_name` is a Data Property.
        # However, that would happend AFTER this method, and we need it at this point in order to instantiate the UISystem now,
        # so we can properly restore its input values.
        # TODO: deve dar pra arrumar isso agora usando self.setup_from_config_post_props()
        self.system_name = system_name

        # Load the subsystem's input data.
        prefix = "Input_"
        for name, value in data.items():
            if not name.startswith(prefix):
                continue
            pin_name = name[len(prefix):]
            pin: DataPin = self.get_input_pin(pin_name)
            if pin:
                pin.set_value(value)
            else:
                click.secho(f"Setup {self}: Couldn't find input-pin '{pin_name}' to restore.", fg="yellow")
        super().setup_from_config(data)

    def _update_system_name_editor(self, editor: primitives.StringEditor):
        """Method automatically called by our ``system_name`` enum-property editor in order to dynamically
        update its settings before editing."""
        manager = UIManager()
        editor.options = manager.get_all_config_names()

    def _clear_system(self):
        """Clears and removes our instantiated UISystem and all other related objects (such as Pins, etc)."""
        if self._uisystem is None:
            return
        # Remove all slots
        for slot in self.slots:
            slot.delete()
        # Remove dynamic pins from the system
        for pin in self._system_pins:
            pin.delete()
        self._system_pins.clear()
        # Clear the system itself
        self._uisystem.clear()
        self._uisystem = None

    def _set_system(self, config: SystemConfig):
        """Instantiates the UISystem from the given config and sets it up as our system, updating our pins, etc to match the system."""
        self._uisystem = config.instantiate()
        # Create input-pin (for us) synced to the value output-pin of the sub-system's Input nodes.
        for innode in self._uisystem.input_nodes:
            if isinstance(innode, SystemActionInput):
                pin = ActionFlow(self, PinKind.input, innode.name)
                pin.pin_tooltip = innode.description
                pin.synced_to_flow = innode.flow_pin
            else:
                state = SyncedToState(innode)
                pin = DataPin(self, state)
            self.add_pin(pin)
            self._system_pins.append(pin)
        # Create output-pin (for us) synced to the value input-pin of the sub-system's Output nodes.
        for outnode in self._uisystem.output_nodes:
            if isinstance(outnode, ExternalWidget):
                slot = SystemSlot(self, outnode)
                self.add_new_slot(slot)
                continue
            elif isinstance(outnode, SystemActionOutput):
                pin = ActionFlow(self, PinKind.output, outnode.name)
                pin.pin_tooltip = outnode.description
                outnode.flow_pin.synced_to_flow = pin
            else:
                state = SyncedToState(outnode)
                pin = DataPin(self, state)
            self.add_pin(pin)
            self._system_pins.append(pin)


###########################################
# Related Nodes to connect action-flows
###########################################
@not_user_creatable
class SystemAction(Action):
    """Base class for UISystem input/output actions."""

    def __init__(self):
        super().__init__(False)
        self.node_bg_color = Color(0.1, 0.25, 0.15, 0.75)
        self.node_header_color = WidgetColors.External

    @input_property()
    def name(self) -> str:
        """Name to identify this System Input/Output parameter when using this UISystem elsewhere."""
        return "param"

    @input_property()
    def description(self) -> str:
        """Description of this System Input/Output property. Used as a tooltip for the pin in a UseSystem
        node that is connected to this Input/Output node."""


# SystemAction subclasses for action-flow input/output
class SystemActionInput(SystemAction):
    """Allows receiving a ActionFlow execution trigger from outside this UISystem, when it is used as a subsystem
    by another UISystem."""

    def __init__(self):
        super().__init__()
        self.flow_pin = ActionFlow(self, PinKind.output, "External Trigger")
        self.add_pin(self.flow_pin)

    def execute(self, trigger_pin: ActionFlow):
        pass


class SystemActionOutput(SystemAction):
    """Allows sending a ActionFlow execution trigger to outside this UISystem, when it is used as a subsystem
    by another UISystem."""

    def __init__(self):
        super().__init__()
        # esse flow-pin input precisa ser syncado com o pin equivalente no UseSystem. O UseSystem vai cuidar disso.
        self.flow_pin = ActionFlow(self, PinKind.input, "Execute External")
        self.add_pin(self.flow_pin)

    def execute(self, trigger_pin: ActionFlow):
        pass


###########################################
# Related classes to connect data-pins
###########################################
# Create SystemAction subclasses for data input/output
for cls in TypeDatabase().get_creatable_types():
    # Create SystemInput<T> node
    @output_property(value_type=cls, allow_sync=True)
    def value(self):
        """Input value for this UISystem."""

    sysinput_action_cls = type(f"SystemInput-{cls.__name__.capitalize()}", (SystemAction,), {"value": value})
    sysinput_action_cls.__doc__ = f"Allows receiving a {cls.__name__} value from outside, as input to this system.\n\
        Other UISystems using this system with a UseSystem node can pass data to its input, which will be available to this system via this node."

    globals()[sysinput_action_cls.__name__] = sysinput_action_cls

    # Create SystemOutput<T> node
    @input_property(value_type=cls, allow_sync=True)
    def value(self):
        """Value to output from this UISystem."""

    sysoutput_action_cls = type(f"SystemOutput-{cls.__name__.capitalize()}", (SystemAction,), {"value": value})
    sysoutput_action_cls.__doc__ = f"Outputs a {cls.__name__} value to other UISystems using this system with a UseSystem node. "

    globals()[sysoutput_action_cls.__name__] = sysoutput_action_cls


class SyncedToState(DataPinState):
    """Specialized DataPin state for the dynamic input/output pins of a UseSystem node.

    This state connects to a SystemAction in the internal subsystem of a UseSystem node,
    thus syncing input-pins from the UseSystem node with system output-pins in the subsystem, and vice-versa.
    """

    def __init__(self, target_node: SystemAction):
        value_pin: DataPin = target_node.get_input_pin("value")
        if value_pin is None:
            value_pin: DataPin = target_node.get_output_pin("value")

        if value_pin.pin_kind is PinKind.output:
            kind = PinKind.input
            desc = "Input data for the internal UISystem being executed by this node."
        else:
            kind = PinKind.output
            desc = "Output data from the internal UISystem being executed by this node."
        if target_node.description:
            desc = f"{target_node.description}\n\n{desc}"

        self.target_state: SyncedDataPropertyState = value_pin.state
        self.target_state.synced_state = self
        super().__init__(target_node.name, kind, desc)

    def get(self):
        return self.target_state.parent_pin.get_value()

    def set(self, value):
        return self.target_state.set(value)

    def type(self):
        return self.target_state.type()

    def subtypes(self):
        return self.target_state.subtypes()


###########################################
# Related Nodes to connect widgets
###########################################
class ExternalWidget(LeafWidget):
    """Allows the graph to link to an external Widget.

    When using this UISystem as a node (or "subsystem") in another graph with the `UseSystem` node,
    the `UseSystem` node will have a slot for each of these External Widgets, thus allowing the UISystem
    using widgets that are defined outside its graph.
    """

    def __init__(self):
        super().__init__()
        self.node_bg_color = Color(0.1, 0.25, 0.15, 0.75)
        self.node_header_color = WidgetColors.External
        self.external_slot: SystemSlot = None

    @input_property()
    def name(self) -> str:
        """Name to identify this External Widget when using this UISystem elsewhere."""

    @input_property()
    def description(self) -> str:
        """Description of this External Widget property. Used as a tooltip for the pin in a UseSystem
        node that is connected to this ExternalWidget node."""

    def render(self):
        if self.external_slot:
            self.external_slot.area = self.area.copy()
            self.external_slot.render()
        self._handle_interaction()


class SystemSlot(Slot):
    """Slot for a UseSystem Container.

    Meant for internal use by the UseSystem node: this slot is associated (1:1) with a `ExternalWidget` inside
    the subsystem in the UseSystem node. That `ExternalWidget` will update and render this slot.
    """

    def __init__(self, parent: ContainerWidget, external: ExternalWidget):
        super().__init__(parent, external.name)
        self.pin_tooltip = external.description
        self.can_be_deleted = False
        external.external_slot = self
