import libasvat.imgui.type_editor as types
from lcarsmonitor.widgets.base import ContainerWidget, Slot
from libasvat.imgui.math import Vector2
from imgui_bundle import imgui


# TODO: permitir drag&drop pra alterar pos dos slots no canvas
# TODO: permitir drag&drop pra alterar size dos slots no canvas (tipo com aqueles markers de canto pra puxar mudar tamanho)
class CanvasSlot(Slot):
    """Slot for a Canvas Container.

    Allows user-selection of the slot's position, size and few other attributes.
    """

    def __init__(self, parent: ContainerWidget, name: str):
        super().__init__(parent, name)
        self.pos_ratio: Vector2 = Vector2()
        self.size_ratio: Vector2 = Vector2(0.5, 0.5)

    @types.string_property(imgui.InputTextFlags_.enter_returns_true)
    def name(self) -> str:
        """Name of this slot. User can change this, but it should be unique amongst all slots of this container. [GET/SET]"""
        return self.pin_name

    @name.setter
    def name(self, value):
        self.pin_name = value

    @types.vector2_property(x_range=(0, 1), y_range=(0, 1), flags=imgui.SliderFlags_.always_clamp)
    def position(self) -> Vector2:
        """The position of the slot, as a ratio of the canvas's size. [GET/SET]"""
        return self.pos_ratio

    @position.setter
    def position(self, value: Vector2):
        self.pos_ratio = value

    @types.vector2_property(x_range=(0, 1), y_range=(0, 1), flags=imgui.SliderFlags_.always_clamp)
    def size(self) -> Vector2:
        """The size of the slot, as a ratio of the canvas's size. [GET/SET]"""
        return self.size_ratio

    @size.setter
    def size(self, value: Vector2):
        self.size_ratio = value


class Canvas(ContainerWidget):
    """A Canvas widget container.

    User can control position and size of each slot individually, the container has no logic automatically setting
    the slot's area. Also allows arbitrary number of slots.
    """

    def __init__(self):
        super().__init__()
        self._slot_class = CanvasSlot

    def update_slots(self):
        for slot in self._slots:
            slot.area.position = self.area.position + self.area.size * slot.pos_ratio
            slot.area.size = self.area.size * slot.size_ratio
