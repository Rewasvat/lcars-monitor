from lcarsmonitor.widgets.base import LeafWidget
from libasvat.imgui.general import not_user_creatable


@not_user_creatable
class LCARSWidget(LeafWidget):
    """Abstract base LeafWidget class for LCARS widgets."""
