import libasvat.imgui.type_editor as types
from lcarsmonitor.widgets.base import BaseWidget, LeafWidget, ContainerWidget, Slot
from libasvat.imgui.math import Vector2
from imgui_bundle import imgui


class AxisListSlot(Slot):
    """Slot for a AxisList container.

    Provides the configuration of the size of an item inside the list, in the list's axis of ordering children.
    """

    def __init__(self, parent: ContainerWidget, name: str, slice: float = 1.0):
        super().__init__(parent, name)
        self._slice = 1.0

    @types.float_property(min=1, flags=imgui.SliderFlags_.always_clamp)
    def slice(self) -> float:
        """The 'slice' of this slot. [GET/SET]

        The slice is the size factor for the slot. The sum of slices of all slots represent the full size of the list, in
        its ordering direction axis.

        So the slice defines the slot's size proportionally to the list's available size, but also proportionally to other slots in the list.

        Slots with the same slice value will have the same size, while a slot A with slice=2 and a slot B with slice=1 means
        A will be twice as big as B.
        """
        return self._slice

    @slice.setter
    def slice(self, value: float):
        self._slice = value


# TODO: permitir um separator entre os itens? tipo uma linha, como imgui.separator()
class AxisList(ContainerWidget):
    """List-like container of widgets.

    An AxisList contains and displays a list of child widgets, distributed either horizontally or vertically amongst the container's region.
    By default the space is divided uniformly amongst all childs, but this can be changed so that some children get a larger or lesser slice
    of space.
    """

    def __init__(self, slices: list[float] = None, is_horizontal=False):
        super().__init__()
        if slices is None or len(slices) <= 0:
            slices = [1.0]
        self._slot_class = AxisListSlot
        self._slots = [AxisListSlot(self, f"#{i+1}", s) for i, s in enumerate(slices)]
        self.slot_counter = len(self._slots)
        self._is_horizontal: bool = is_horizontal
        self._margin: float = 0.0
        self._only_accept_leafs = False

    @types.bool_property()
    def only_accept_leafs(self) -> bool:
        """If this List only accepts LeafWidgets as children, otherwise accept any BaseWidget. Default is false. [GET/SET]"""
        return self._only_accept_leafs

    @only_accept_leafs.setter
    def only_accept_leafs(self, value: bool):
        self._only_accept_leafs = value
        for slot in self._slots:
            if value:
                slot.accepted_child_types = [LeafWidget]
            else:
                slot.accepted_child_types = [BaseWidget]

    @types.float_property()
    def margin(self) -> float:
        """The space between each children, and between the children and our borders. Default is 0. [GET/SET]"""
        return self._margin

    @margin.setter
    def margin(self, value: float):
        self._margin = value

    @types.bool_property()
    def is_horizontal(self) -> bool:
        """If this list orders its children horizontally. If not, it'll order them vertically. Default is vertical. [GET/SET]"""
        return self._is_horizontal

    @is_horizontal.setter
    def is_horizontal(self, value: bool):
        self._is_horizontal = value

    @property
    def slices(self):
        """Gets the list of 'slices' of this list.

        Each slice is the size factor for a child slot. So the list of slices not only represents how many childs this
        list may have, it also configures how the list space will be divided amongst the slots.

        The sum of all slices correspond to our full size in the axis this list will order children into. So each size
        factor represents the size of that slice in relation to other.

        For example, if all slices are the same number, then the list space will be divided uniformly amongs all childs (which
        is the default). But if using ``2, 1, 1`` slices, the list will have 3 slots, with the first being 50% of the available
        size, while the remaining slots will each be 25% of the available size.
        ``total_space = sum(slices)``. [GET]
        """
        return [slot.slice for slot in self._slots]

    def update_slots(self):
        current_slots: list[AxisListSlot] = self._slots

        total_slices_size = max(sum(self.slices), 1)

        axis_size = self.area.size.x if self._is_horizontal else self.area.size.y
        axis_size -= self._margin * (len(current_slots) + 1)
        piece_size = axis_size / total_slices_size
        pos = self._margin

        for i, slot in enumerate(current_slots):
            slice_size = slot.slice
            size = piece_size * slice_size

            if self._is_horizontal:
                slot_pos = Vector2(pos, self._margin)
                slot_size = Vector2(size, self.area.size.y - self._margin*2)
            else:
                slot_pos = Vector2(self._margin, pos)
                slot_size = Vector2(self.area.size.x - self._margin*2, size)
            slot_size = slot_size.max((10, 10))

            slot.pin_name = f"#{i+1}"
            # NOTE: se somamos self.position, pra esse slot_pos ficar absoluto, caga tudo...
            #   Mas em tese todas slot positions deviam ser absolutas, não?
            slot.area.position = slot_pos + self.area.position
            slot.area.size = slot_size

            pos += size + self._margin

    def on_slots_changed(self):
        self.only_accept_leafs = self._only_accept_leafs
