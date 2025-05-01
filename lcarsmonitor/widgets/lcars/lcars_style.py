# LCARS PALLETTE:
#
# Every button gets Main White when activated, both for clicks and fixed [PRESSED] state
# Every other color has an [UNPRESSED] state and a [HOVER] state that has around 20% extra saturation on the K channel
# on a CMYK scale when not [PRESSED].
# Labels INSIDE other elements are always Main Black. Labels OUTSIDE any elements are always Main Orange.
# Background for transparency elements are always Light Blue with [HOVER] mode not active (only [UNPRESSED] mode)
#
# Main Black: (RGB: 0 0 0)  (Hex: #000000)
# Grey: 128 128 128
# Main White:
# 	PRESSED: (RGB: 255 255 255)  (Hex: #ffffff)
# Main Red:
# 	UNPRESSED: (RGB: 204 102 102)  (Hex: #cc6666)
# 	HOVER: (RGB: 171 85 85)  (Hex: #ab5555)
# Main Pink:
# 	UNPRESSED: (RGB: 230 176 212)  (Hex: #e6b0d4)
# 	HOVER: (RGB: 189 146 175)  (Hex: #bd92af)
# Main Blue:
# 	UNPRESSED: (RGB: 153 204 255)  (Hex: #99ccff)
# 	HOVER: (RGB: 133 168 197)  (Hex: #85a8c5)
# Light Blue:
# 	UNPRESSED: (RGB: 173 216 230)  (Hex: #add8e6)
# 	HOVER: (RGB: 145 181 192)  (Hex: #91b5c0)
# Main Orange:
# 	UNPRESSED: (RGB: 255 153 0)  (Hex: #ff9900)
# 	HOVER: (RGB: 204 127 22)  (Hex: #cc7f16)
# Main Yellow:
# 	UNPRESSED: (RGB: 239 182 87)  (Hex: #efb657)
# 	HOVER: (RGB: 196 151 73)  (Hex: #c49749)
# Main Beige:
# 	UNPRESSED: (RGB: 238 182 131)  (Hex: #eeb683)
# 	HOVER: (RGB: 196 152 109)  (Hex: #c4986d)
# Main Green:
# 	UNPRESSED: (RGB: 21 169 87)  (Hex: #15a957)
# 	HOVER: (RGB: 8 142 72)  (Hex: #088e48)
from libasvat.imgui.colors import Color, Colors
from libasvat.imgui.nodes import input_property, output_property
from lcarsmonitor.widgets.style import VisualStyle
from lcarsmonitor.actions.conversion_actions import ConversionAction
from enum import Enum


class LCARSStyle(Enum):
    """Standard LCARS Styles."""
    COMMON = "COMMON"
    """Common LCARS style. This is the same as `MAIN_YELLOW`."""
    MAIN_RED = "MAIN_RED"
    MAIN_PINK = "MAIN_PINK"
    MAIN_BLUE = "MAIN_BLUE"
    LIGHT_BLUE = "LIGHT_BLUE"
    MAIN_ORANGE = "MAIN_ORANGE"
    MAIN_YELLOW = "MAIN_YELLOW"
    MAIN_BEIGE = "MAIN_BEIGE"
    MAIN_GREEN = "MAIN_GREEN"
    EXTERNAL_LABEL = "EXTERNAL_LABEL"
    """LCARS style for labels outside any other element."""

    def get_style(self) -> VisualStyle:
        """Gets the VisualStyle object for this LCARS style."""
        style = VisualStyle()
        style.pressed_color = Colors.white
        style.disabled_color = Color.from_hex("7F7F7FFF")
        style.text_color = Colors.black

        if self is self.MAIN_RED:
            style.normal_color = Color.from_hex("CC6666FF")
            style.hovered_color = Color.from_hex("AB5555FF")
        elif self is self.MAIN_PINK:
            style.normal_color = Color.from_hex("E6B0D4FF")
            style.hovered_color = Color.from_hex("BD92AFFF")
        elif self is self.MAIN_BLUE:
            style.normal_color = Color.from_hex("99CCFFFF")
            style.hovered_color = Color.from_hex("85A8C5FF")
        elif self is self.LIGHT_BLUE:
            style.normal_color = Color.from_hex("ADD8E6FF")
            style.hovered_color = Color.from_hex("91B5C0FF")
        elif self is self.MAIN_ORANGE:
            style.normal_color = Color.from_hex("FF9900FF")
            style.hovered_color = Color.from_hex("CC7F16FF")
        elif self in (self.MAIN_YELLOW, self.COMMON):
            style.normal_color = Color.from_hex("EFB657FF")
            style.hovered_color = Color.from_hex("C49749FF")
        elif self is self.MAIN_BEIGE:
            style.normal_color = Color.from_hex("EEB683FF")
            style.hovered_color = Color.from_hex("C4986DFF")
        elif self is self.MAIN_GREEN:
            style.normal_color = Color.from_hex("15A957FF")
            style.hovered_color = Color.from_hex("088E48FF")
        elif self is self.EXTERNAL_LABEL:
            style.normal_color = style.hovered_color = style.pressed_color = style.disabled_color = Colors.black
            style.text_color = Color.from_hex("FF9900FF")  # same as MainOrange
        return style


class GetLCARSStyle(ConversionAction):
    """Gets the VisualStyle object for the given LCARS style."""

    @input_property()
    def lcars_style(self) -> LCARSStyle:
        """LCARS style to use."""
        return LCARSStyle.COMMON

    @output_property(use_prop_value=True)
    def visual_style(self) -> VisualStyle:
        """The visual style of our LCARS style."""
        return self.lcars_style.get_style()
