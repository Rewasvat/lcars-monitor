import re
import lcarsmonitor.actions as actions
import libasvat.command_utils as cmd_utils
from imgui_bundle import imgui, imgui_node_editor  # type: ignore
from libasvat.imgui.general import object_creation_menu, menu_item
from libasvat.imgui.math import Vector2
from libasvat.imgui.nodes import Node, NodeSystem, PinKind, output_property
from libasvat.imgui.nodes.node_config import SystemConfig
from libasvat.imgui.colors import Colors, Color
from lcarsmonitor.widgets.base import BaseWidget, Slot, WidgetParentPin, draw_widget_pin_icon
from lcarsmonitor.sensors.sensors import Hardware, ComputerSystem
from lcarsmonitor.sensors.sensor_node import Sensor
from libasvat.data import DataCache


class RootSlot(Slot):
    """Specialized Slot to be used as the Root slot of all widgets in a graph.

    This is the slot in a UISystem's Root node that starts a widget hierarchy.
    """

    def __init__(self, parent: 'SystemRootNode'):
        super().__init__(parent, "Root")
        self.can_be_deleted = False
        self.no_parent_in_open_slot_menu = True

    def render(self):
        self.area.position = Vector2.from_cursor_screen_pos()
        self.area.size = Vector2.from_available_content_region()
        return super().render()


class SystemRootNode(Node):
    """Root Node for a UISystem.

    Provides base output pins from which the system may be defined:
    * A root widget slot to create the widget hierarchy.
    * System level ActionFlows for logic triggering.
    * System level DataPins providing basic system data for the graph.
    """

    def __init__(self):
        super().__init__()
        self.system: UISystem = self.system
        self.node_bg_color = Color(0.12, 0.22, 0.1, 0.75)
        self.node_header_color = Color(0.32, 0.6, 0.04, 0.6)
        self.can_be_deleted = False
        self.widget_root = RootSlot(self)
        self.on_update = actions.ActionFlow(self, PinKind.output, "On Update")
        self.add_pin(self.widget_root)
        self.add_pin(self.on_update)
        self.create_data_pins_from_properties()

    @property
    def system(self) -> 'UISystem':
        """Gets the UISystem that owns this root-node."""
        # This overrides base Node.system attribute, so that we can have the getter/setter methods.
        return self._system

    @system.setter
    def system(self, value: 'UISystem'):
        self._system = value
        self.node_title = str(value)

    @output_property(use_prop_value=True)
    def delta_time(self) -> float:
        """Gets the delta time, in seconds, between the current and last frames from IMGUI."""
        io = imgui.get_io()
        return io.delta_time

    def render_edit_details(self):
        if menu_item("Reposition Nodes"):
            self.reposition_nodes([actions.ActionFlow, Slot])
        imgui.set_item_tooltip("Rearranges all nodes following this one according to depth in the graph.")
        if menu_item("Save"):
            self.system.save_config()
        imgui.set_item_tooltip("Saves the configuration of this UISystem to disk. This config can be later used to recreate/reuse this UISystem.")


# TODO: talvez de pra separar o "UISystem" em classes diferentes. Uma basica que seria só widgets, outra com widgets+actions,
#       e finalmente uma com widget+actions+sensores
# TODO: widget novo: imagem. Scala a imagem para a area do slot. Pode escolher UV-coords usadas (sub-frames). Escolher imagem por path anywhere?
# TODO: widget novo: polygon. Tipo o XAMLPath. User pode configurar vários shapes em runtime.
#   - pra cada shape, user vai configurando segmentos, fill color, stroke color, stroke thickness, etc.
#   - poder setar o aspect-ratio: se tamanho é relativo à widget area, ou relativo a um ratio fixo
class UISystem(NodeSystem):
    """Represents a complete user-configurable UI and logic system.

    * Contains a Widget hierarchy for configuring the UI. The widgets are fully-configurable by the user.
    * Supports Actions for defining logic that can be executed on events.
    * Supports system level events and widgets events for triggering actions.
    * Widgets and Actions are defined in a single graph, allowing easy user configuration by visual node "programming".
    * Supports the Sensors System as nodes for providing sensor data and events to the graph.
    * Graph configuration can be persisted in LCARSMonitor's DataCache (key based on system name).
    """

    def __init__(self, name: str, nodes: list[Node] = None):
        super().__init__(name, nodes)
        self.edit_enabled: bool = True
        """If editing the graph is enabled in this system."""
        if nodes is None:
            self._root_node = SystemRootNode()
            imgui_node_editor.set_node_position(self._root_node.node_id, (0, 0))
            self.add_node(self._root_node)
        else:
            # The Root Node should be the first in the list.
            # However doing this is safer.
            for node in nodes:
                if isinstance(node, SystemRootNode):
                    self._root_node: SystemRootNode = node
                    break

    @property
    def root_widget(self) -> BaseWidget:
        """Gets the root widget of this system."""
        return self._root_node.widget_root.child

    @root_widget.setter
    def root_widget(self, root: BaseWidget):
        self._root_node.widget_root.child = root

    def render(self):
        """Renders this UISystem in the current region.

        This updates the Root Widget to the current region area, and renders it. Consequently, this renders the entire widget hierarchy,
        updating all widgets, triggering actions and so on.
        """
        self._root_node.on_update.trigger()

        window_flags = imgui.WindowFlags_.no_scrollbar | imgui.WindowFlags_.no_scroll_with_mouse
        imgui.begin_child(f"{repr(self)}AppRootWidget", window_flags=window_flags)
        # Draw a solid background-color rect in the background, to ensure our background is as expected.
        pos = imgui.get_cursor_screen_pos()
        size = imgui.get_content_region_avail()
        imgui.get_window_draw_list().add_rect_filled(pos, pos + size, Colors.background.u32)
        # Render widget tree hierarchy by starting with the root widget.
        self._root_node.widget_root.render()
        imgui.end_child()

    def render_system(self):
        if imgui.shortcut(imgui.Key.mod_ctrl | imgui.Key.s):
            self.save_config()
        return super().render_system()

    def save_config(self):
        """Saves this UISystem's config to the UIManager singleton, thus persisting its data for future use."""
        manager = UIManager()
        manager.update_system(self)

    @property
    def input_nodes(self):
        """Gets all System Input nodes for this system. These are nodes that contain output-pins that provide data for this system."""
        from lcarsmonitor.system.system_node import SystemAction
        return [node for node in self.nodes if isinstance(node, SystemAction) and "Input" in node.__class__.__name__]

    @property
    def output_nodes(self):
        """Gets all System Output nodes for this system. These are nodes that contain input-pins that return data from this system."""
        from lcarsmonitor.system.system_node import SystemAction, ExternalWidget
        nodes = [node for node in self.nodes if isinstance(node, ExternalWidget)]
        return nodes + [node for node in self.nodes if isinstance(node, SystemAction) and "Output" in node.__class__.__name__]

    def render_create_widget_menu(self, accepted_bases: list[type[BaseWidget]] = [BaseWidget]) -> BaseWidget | None:
        """Renders the contents for a menu that allows the user to create a new widget, given the possible options.

        Args:
            accepted_bases (list[type[BaseWidget]]): list of base types accepted as the options of new widgets to create.
            The menu will search for all possible subclasses of these given accepted types and display them for selection.
            Options in the menu are organized following the same tree-hierarchy as the classes themselves.
            Classes marked with the ``@not_user_creatable`` decorator will won't be allowed to be created by the user, but their subclasses may.
            The default list of ``[BaseWidget]`` basically allows all widgets since the only base is the base for all widgets.

        Returns:
            BaseWidget: the newly created instance of a widget, if any. None otherwise.
            Any created widget is auto-registered with this system.
        """
        new_child = None
        for cls in accepted_bases:
            new_child = object_creation_menu(cls, lambda cls: cls.__name__.replace("Widget", ""))
            if new_child is not None:
                break
        return new_child

    def render_create_action_menu(self) -> actions.Action | None:
        """Renders the contents for a menu that allows the user to create a new action, given the possible options.

        Returns:
            Action: the newly created instance of a action, if any. None otherwise.
        """
        def name_getter(cls: type):
            return re.sub(r"([a-z])([A-Z])", r"\1 \2", cls.__name__)

        return object_creation_menu(actions.Action, name_getter)

    def render_create_sensor_menu(self) -> Sensor | None:
        """Renders the contents for a menu that allows the user to create a Sensor node.

        Note that only one Sensor object may exist for any given sensor ID.

        Returns:
            Sensor: the sensor object from the MonitorManager singleton.
        """
        def render_hw(hw: Hardware) -> Sensor:
            ret = None
            opened = imgui.begin_menu(hw.name)
            imgui.set_item_tooltip(f"ID: {hw.id}\nTYPE: {hw.type}\n\n{hw.__doc__}")
            if opened:
                for sub_hw in hw.children:
                    sub_ret = render_hw(sub_hw)
                    if sub_ret:
                        ret = sub_ret
                for isensor in hw.isensors:
                    if menu_item(f"{isensor.name} ({isensor.type}: {isensor.unit})"):
                        ret = isensor.create()
                    imgui.set_item_tooltip(f"{isensor.info}\n\n{Sensor.__doc__}")
                imgui.end_menu()
            return ret

        new_sensor = None
        opened = imgui.begin_menu("Sensors:")
        imgui.set_item_tooltip("Select a sensor to create.\n\nA 'empty' sensor or one already set can be created directly.")
        if opened:
            for hardware in ComputerSystem():
                ret = render_hw(hardware)
                if ret:
                    new_sensor = ret
            imgui.end_menu()

        return new_sensor

    def draw_background_context_menu(self, linked_to_pin):
        if isinstance(linked_to_pin, Slot):
            return self.render_create_widget_menu(linked_to_pin.accepted_child_types)
        if isinstance(linked_to_pin, actions.ActionFlow):
            return self.render_create_action_menu()
        else:
            new_widget = self.render_create_widget_menu()
            new_action = self.render_create_action_menu()
            new_sensor = self.render_create_sensor_menu()
            return new_widget or new_action or new_sensor

    def __str__(self):
        return f"Widget System: {self.name}"


class UIManager(metaclass=cmd_utils.Singleton):
    """Singleton manager of UISystems.

    Handles high-level, project-wide, operations regarding UISystems and related features.

    Most notably, handles the persistent storage of SystemConfigs: the persistence of the configuration
    objects that allow saving and recreation of any saved UISystems.
    """

    def __init__(self):
        cache = DataCache()
        self._config_cache_key = "UIManagerData"
        self._configs: dict[str, SystemConfig] = cache.get_custom_cache(self._config_cache_key, {})

    def get_all_configs(self):
        """Gets a list of all stored SystemConfigs."""
        return list(self._configs.values())

    def get_all_config_names(self):
        """Gets a sorted list of all stored config names."""
        return sorted(self._configs.keys())

    def get_config(self, name: str):
        """Gets the stored SystemConfig with the given NAME. May return None if no config exists for the NAME."""
        # TODO: podemos ter problemas de lugares pegarem esse config retornado daqui, e alterarem ele sem querer, e ai quebrar o save.
        #     (já aconteceu por sinal, o ContainerWidget.setup_from_config alterava o config com um dict.pop)
        #   Então talvez seja melhor retornar uma deep-copy (talvez copy.deepcopy resolva), e talvez coisa similar no get_all_configs()
        return self._configs.get(name)

    def has_config(self, name: str):
        """Checks if a SystemConfig with the given NAME exists."""
        return name in self._configs

    def update_config(self, config: SystemConfig):
        """Updates the manager with the given UISystem config (a SystemConfig instance).

        Configs are indexed by their name (``config.name``). If any config existed previously with
        the same name, it'll be overwritten by this new given config.

        This will thus save the config in persisten storage.

        Args:
            config (SystemConfig): the SystemConfig to store.
        """
        self._configs[config.name] = config
        self.save()

    def update_system(self, system: UISystem):
        """Updates the saved UISystem configs with the config of the given system.
        This will thus save the given system's config in persistent storage.

        Args:
            system (UISystem): the system to save its config.
        """
        config = SystemConfig.from_system(system)
        self.update_config(config)

    def remove_config(self, config: SystemConfig | str):
        """Removes the given config from persistent storage, effectively deleting it.

        Args:
            config (SystemConfig | str): which config to remove. Can be the SystemConfig object itself
            or its name.
        """
        name = config if isinstance(config, str) else config.name
        if self.has_config(name):
            self._configs.pop(name)
            self.save()

    def save(self):
        """Saves the UIManager data (saved UISystem configs and so on) to disk."""
        cache = DataCache()
        cache.save_custom_cache(self._config_cache_key, self._configs)
