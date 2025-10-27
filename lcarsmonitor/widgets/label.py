import re
import libasvat.imgui.editors.primitives as primitives
from lcarsmonitor.widgets.base import LeafWidget, WidgetColors
from libasvat.imgui.colors import Colors, Color
from libasvat.imgui.nodes import input_property
from libasvat.imgui.math import Vector2, Rectangle
from libasvat.imgui.fonts import FontDatabase, FontID
from lcarsmonitor.widgets.style import VisualStyle
from imgui_bundle import imgui
from enum import Enum


class LCARSFont(Enum):
    """Available LCARS fonts to use with FontDatabase and the Widgets system."""
    LCARS = "LCARS"
    LCARS_WIDE = "LCARS_WIDE"
    LCARS_BOLD = "LCARS_BOLD"
    LCARS_SEMI_BOLD = "LCARS_SEMI_BOLD"
    LCARS_MEDIUM = "LCARS_MEDIUM"
    LCARS_LIGHT = "LCARS_LIGHT"
    LCARS_EXTRA_LIGHT = "LCARS_EXTRA_LIGHT"
    LCARS_THIN = "LCARS_THIN"

    @property
    def font_path(self):
        """Gets the path to the font file for this LCARS Font."""
        mapping = {
            self.LCARS: "LCARS/Antonio-Regular",
            self.LCARS_WIDE: "LCARS/Federation_Wide",
            self.LCARS_BOLD: "LCARS/Antonio-Bold",
            self.LCARS_SEMI_BOLD: "LCARS/Antonio-SemiBold",
            self.LCARS_MEDIUM: "LCARS/Antonio-Medium",
            self.LCARS_LIGHT: "LCARS/Antonio-Light",
            self.LCARS_EXTRA_LIGHT: "LCARS/Antonio-ExtraLight",
            self.LCARS_THIN: "LCARS/Antonio-Thin",
        }
        return mapping.get(self, self.value)

    def get_pos_fix_multiplier(self):
        """Gets the pos-fix multiplier for this kind of LCARS Font.
        This is used in FontDatabase to have fonts with tight-fitting bounding boxes.
        """
        default_multiplier = 2
        multipliers = {
            self.LCARS_WIDE: 1
        }
        return multipliers.get(self, default_multiplier)

    def get_size_fix_multiplier(self):
        """Gets the size-fix multiplier for this kind of LCARS Font.
        This is used in FontDatabase to have fonts with tight-fitting bounding boxes.
        """
        default_multiplier = 3
        multipliers = {
            self.LCARS_WIDE: 2
        }
        return multipliers.get(self, default_multiplier)

    def __str__(self):
        return self.value


def setup_lcars_fonts():
    """Sets up the LCARS Fonts with the FontDatabase. This should be called on App Initialization."""
    font_db = FontDatabase()
    for lcarsfont in LCARSFont:
        font_id = lcarsfont.font_path
        alias = lcarsfont.value
        # Setup font alias
        font_db.set_font_alias(font_id, alias)
        # Setup font pos/size fix
        cache = font_db.get_cache(font_id)
        cache.pos_fix_multiplier = lcarsfont.get_pos_fix_multiplier()
        cache.size_fix_multiplier = lcarsfont.get_size_fix_multiplier()
    # Setup default font
    font_db.default_font = LCARSFont.LCARS


class Alignment(Enum):
    """How to align a visual element to its parent area."""
    TOP_LEFT = "TOP_LEFT"
    TOP = "TOP"
    TOP_RIGHT = "TOP_RIGHT"
    RIGHT = "RIGHT"
    BOTTOM_RIGHT = "BOTTOM_RIGHT"
    BOTTOM = "BOTTOM"
    BOTTOM_LEFT = "BOTTOM_LEFT"
    LEFT = "LEFT"
    CENTER = "CENTER"

    def get_dir(self):
        """Returns a vector indicating the direction of this Alignment in the 2D plane,
        considering center as the (0, 0) center of the area.

        Returns:
            Vector2: vector of the alignment direction. This is NOT a normalized vector!
            Its a "factor" or "multiplier": each component has value of 1 or -1 to indicate going in that direction.
            If required, user can normalize the vector himself.
        """
        dirs = {
            self.TOP_LEFT: Vector2(-1, -1),
            self.TOP: Vector2(0, -1),
            self.TOP_RIGHT: Vector2(1, -1),
            self.RIGHT: Vector2(1, 0),
            self.BOTTOM_RIGHT: Vector2(1, 1),
            self.BOTTOM: Vector2(0, 1),
            self.BOTTOM_LEFT: Vector2(-1, 1),
            self.LEFT: Vector2(-1, 0),
            self.CENTER: Vector2(),
        }
        return dirs[self]

    def get_pos_offset(self, area_size: Vector2, obj_size: Vector2, margin=0.0):
        """Calculates the position offset (top-left corner) of a OBJECT for drawing it in a AREA,
        given the AREA and OBJ sizes and this Alignment setting.

        Args:
            area_size (Vector2): The size of the area containing the object.
            obj_size (Vector2): The size of the object itself.
            margin (float, optional): Optional margin to consider between the object and the area's borders. Defaults to 0.0.

        Returns:
            Vector2: top-left position offset in absolute coords.
        """
        pos = Vector2()

        # Update Pos X
        if self in (Alignment.TOP_RIGHT, Alignment.RIGHT, Alignment.BOTTOM_RIGHT):
            pos.x += area_size.x - obj_size.x
        elif self in (Alignment.TOP, Alignment.CENTER, Alignment.BOTTOM):
            pos.x += area_size.x * 0.5 - obj_size.x * 0.5

        # Update Pos Y
        if self in (Alignment.BOTTOM_LEFT, Alignment.BOTTOM, Alignment.BOTTOM_RIGHT):
            pos.y += area_size.y - obj_size.y - 1
        elif self in (Alignment.LEFT, Alignment.CENTER, Alignment.RIGHT):
            pos.y += area_size.y * 0.5 - obj_size.y * 0.5

        # Add margin
        align_dir = self.get_dir()
        pos = pos + (align_dir * -margin)

        return pos


class TextObject:
    """Low-level text rendering object in LCARSMonitor's Widgets system.

    This holds all the necessary data and is capable of rendering text in IMGUI using our standard in the Widgets System.
    However, this class is completely independent of a widget.

    Our purpose is to be used in a widget by association, not inheritance: a widget might hold several TextObjects at the
    same time, in order to easily render text with different properties.

    For a specific simple text widget see ``Label``.
    For a mixin for widget classes that adds simple text rendering (same as Label), see ``TextMixin``.
    """

    def __init__(self, text=""):
        self.text: str = text
        self.align: Alignment = Alignment.CENTER
        self.area: Rectangle = Rectangle()
        """Position and size of area where to draw this text."""
        self.wrapped: bool = False
        self.scale = 1.0
        """Scale of the text.
        * 0 < scale < 1: scaled-down text.
        * scale == 1: original text size. Default font-size is 20, but font-size is automatically calculated based on this scale
        in a few frames, so that when rendering we try to use the closest font-size and less scaling to achieve the desired result.
        * 1 < scale < 2: scaled-up text.
        * scale == 2: text at the largest size possible to fit our area.
        """
        self.color = Colors.white
        self.current_font_size: int = 20
        """Font size calculated automatically based on our area and scale. After changing scale, this may take a few frames to update."""
        self.last_font_size: int = 20
        self.font_size_counter: int = 0
        self.font: LCARSFont = LCARSFont.LCARS
        """Which font to use. Default to LCARS."""
        self.margin: float = 0.0
        """Spacing between the text and our area's borders. Does not apply when using CENTER text-alignment."""
        self.debug_draw_boxes = False
        """Used for debugging. Draws some thin rects to display internal text sizes."""
        self._text_rect = Rectangle()

    @property
    def text_area(self):
        """The text's bounding rect. This is the actual text position/size inside our area, and as such
        this rect should be fully contained in it. This is updated everytime ``self.draw()`` is called."""
        return self._text_rect

    def draw(self):
        """Draws this text object to IMGUI.

        Text is drawn using IMGUI's DrawLists and our absolute area coords.
        Text, area, color and other parameters that alter how the text is rendered are all defined as public attributes
        of this object, so change them at will.
        """
        if self.text is not None and len(self.text) > 0:
            lines = self.text.split("\n")
            wrap_width = self.area.size.x if self.wrapped else 0

            font_size = self.calculate_font_size(lines, wrap_width)
            if self.debug_draw_boxes:
                self.area.draw(Colors.blue)

            font_db = FontDatabase()
            # Second pass to render the text with proper font size.
            with font_db.using_font(font_size, self.font) as font:
                # Since fonts have a maximum possible size, we might still need to scale.
                font_scale = (font_size / font.font_size) * (font_size / int(font_size))
                self._text_rect, line_rects = self.get_text_rects(lines, wrap_width, font_scale)

                draw = imgui.get_window_draw_list()
                if self.debug_draw_boxes:
                    self.text_area.draw(Colors.green)
                for line, line_rect in zip(lines, line_rects):
                    if self.debug_draw_boxes:
                        # Individual line rect. Tight glyph fit, the desired size.
                        line_rect.draw(Colors.red)
                        # How the line rect would be if we didn't fix it to tightly fit.
                        fpos = line_rect.position
                        fsize = line_rect.size
                        fpos -= font_db.get_text_pos_fix(font, self.font) * font_scale
                        fsize += font_db.get_text_size_fix(font, self.font) * font_scale
                        draw.add_rect(fpos, fpos + fsize, Colors.yellow.u32)
                    draw.add_text(
                        font=font,
                        font_size=font_size,
                        pos=line_rect.position - font_db.get_text_pos_fix(font, self.font) * font_scale,  # NOTE: text rect Ypos fix for font
                        col=self.color.u32,
                        text_begin=line,
                        text_end=None,
                        wrap_width=wrap_width,
                        cpu_fine_clip_rect=None
                    )

    def calculate_font_size(self, lines: list[str], wrap_width=0):
        """Calculates the proper font size to use when rendering the text of this TextMixin.

        This considers this object's area, text, alignment, wrapping and scaling to calculate
        the font-size required to render the text in the way (and scale) the user wants, without actually scaling
        the text, which would lead to blurry and otherwise ugly rendered text.

        User selected text-scaling is what most affect the font-size. Since ``self.scale`` can change each frame when editing it,
        this instance method stores newly calculated values of font-size, but only actually returns an updated value after a few
        calls to it have calculated the same value.

        Since this is expected to be called once each frame, it'll thus take a few frames to properly update the font
        size after changing parameters (particularly scale).

        Args:
            lines (list[str]): list of text lines that would be rendered.
            wrap_width (int, optional): wrap width to use when calculating text sizes. Defaults to 0.

        Returns:
            int: font size to render the texts.
        """
        font_db = FontDatabase()
        # First pass with default-sized font to calculate text sizes and proper desired font size
        with font_db.using_font(20, self.font) as base_font:
            text_rect = self.get_text_rects(lines, wrap_width)[0]

            max_font_scale = (self.area.size / text_rect.size).min_component()
            actual_scale = 1.0
            if self.scale > 1:
                actual_scale += (self.scale - 1) * (max_font_scale - 1)
            elif self.scale > 0:
                actual_scale = self.scale

            base_font_height = base_font.font_size
            final_font_size = int(base_font_height * actual_scale)

            frames_to_wait = 5
            if final_font_size != self.last_font_size:
                self.font_size_counter = 0
                self.last_font_size = final_font_size
            elif self.font_size_counter < frames_to_wait:
                self.font_size_counter += 1

            if self.font_size_counter == frames_to_wait and self.current_font_size != self.last_font_size:
                self.current_font_size = self.last_font_size

        return self.current_font_size

    def get_text_rects(self, lines: list[str], wrap_width=0, scale=1):
        """Calculates the text rectangles (position and size) for each of the given text lines, according to our
        current area and text alignment.

        This just uses the current font. So to get the rects of the proper size for a given font, the font should be changed in imgui
        before using this.

        Args:
            lines (list[str]): list of text lines to calculate rects from.
            wrap_width (int, optional): wrap width to use when calculating text sizes. Defaults to 0.
            scale (float, optional): text scale to use. Defaults to 1.

        Returns:
            tuple[Rectangle, list[Rectangle]]: a tuple with two values, in order:
            * ``Rectangle``: the total text rectangle - the position/size rectangle of all lines together.
            * ``list[Rectangle]``: the individual rectangle for each line (matching indexes to the lines arg).
        """
        font_db = FontDatabase()
        line_rects: list[Rectangle] = []
        for line in lines:
            y = line_rects[-1].bottom_left_pos.y if len(line_rects) > 0 else 0
            line_size = imgui.calc_text_size(line, wrap_width=wrap_width)
            line_size.y -= font_db.get_text_size_fix(font=self.font).y  # NOTE: text rect height fix for font
            line_rects.append(Rectangle((0, y), line_size))
        text_rect = self.update_line_rects(line_rects, scale)
        return text_rect, line_rects

    def update_line_rects(self, line_rects: list[Rectangle], scale: float):
        """Updates the position and size of each line rectangle according to our current text alignment
        and given scale.

        The line rectangles will be updated in-place. After this, these lines will be ready for text-drawing.

        Args:
            line_rects (list[Rectangle]): list of line rectangles of this label. At this point passed as input here,
                each line's position means nothing, but its size is the text line's size in regular font-size (no scaling)
                with text-wrap applied. After this method, these rectangles will've been updated in-place with their proper
                positions and scaled sizes.
            scale (float): The current actual scale for drawing text in this label.

        Returns:
            Rectangle: the rectangle bounding all updated line rectangles.
        """
        pos = self.area.position
        prev_y = 0.0
        # Adjust positions of each line.
        for rect in line_rects:
            rect.size = rect.size * scale
            rect.position = self.get_text_pos(rect.size) + (0, prev_y)
            prev_y += rect.size.y

        # Adjust position of whole group of lines
        text_rect = sum(line_rects, line_rects[0])
        group_offset = text_rect.position
        text_rect.position = pos + self.get_text_pos(text_rect.size)
        for rect in line_rects:
            rect.position += text_rect.position - group_offset
        return text_rect

    def get_text_pos(self, text_size: Vector2):
        """Calculates the position offset (top-left corner) of the given text size for drawing in our
        area, given the area size and our text alignment setting.

        Returns the offset in absolute coords.
        """
        return self.align.get_pos_offset(self.area.size, text_size, self.margin)


class TextMixin:
    """Provides text rendering for a widget using an internal TextObject instance.

    Includes Imgui/NodeData properties for editing the TextObject's attributes.
    """

    def __init__(self, text: str = ""):
        self._text_internal = TextObject()
        self.text = text

    @input_property(multiline=True)
    def text(self) -> str:
        """The text being displayed [GET/SET]"""
        return ""  # this is essentially the default value.

    @primitives.bool_property()
    def is_wrapped(self):
        """If the text will wrap around to not exceed our available width space [GET/SET]"""
        return self._text_internal.wrapped

    @is_wrapped.setter
    def is_wrapped(self, value: bool):
        self._text_internal.wrapped = value

    @primitives.enum_property()
    def align(self):
        """How the text is aligned to our area [GET/SET]"""
        return self._text_internal.align

    @align.setter
    def align(self, value: Alignment):
        self._text_internal.align = value

    @property
    def max_text_margin(self):
        """Maximum text margin possible.

        Corresponds to the lesser component of `Area Size - Text Size`. This way, with this margin the text
        will usually be touching the opposite border of its text-alignment corner.
        """
        empty_space = self._text_internal.area.size - self._text_internal.text_area.size
        return max(1, empty_space.min_component())

    @primitives.float_property(min=0, max=1, is_slider=True)
    def text_margin(self):
        """Spacing between the text and our area's borders. Does not apply when using CENTER text-alignment.

        This is a value in the range [0,1]. It is a relative percentage of the minimum (no margin, or 0) value and
        the maximum margin possible (so the text touches the opposite border).
        """
        return self._text_internal.margin / self.max_text_margin

    @text_margin.setter
    def text_margin(self, value: float):
        value = max(0, min(1, value))
        self._text_internal.margin = value * self.max_text_margin

    @input_property(min=0.0, max=2.0, is_slider=True, flags=imgui.SliderFlags_.always_clamp)
    def scale(self) -> float:
        """The scale of the text. [GET/SET]
        * 0 (min): impossible. Since we can't have scale=0, at this value scale will behave as if it was =1.
        * close to 0: theoretical min size possible, pratically invisible/unreadable.
        * [0, 1]: scaled down text
        * 1.0: regular text size (default font-size is 20).
        * [1, 2]: scaled up text
        * 2 (max): max size possible in current label slot area.

        Note that scaling won't work properly when text is long, since its regular size might already match our slot size.

        The actual font-size used is calculated based on the Text's properties, with this being the value that most affects it.
        The calculated font-size is the required size to display the text in the configured way, without actually scaling the
        text (which would be blurry at best).

        After changing this value, it may take a few moments for the font-size to be properly updated.
        """
        return 1.0  # this is essentially the default value.

    @primitives.enum_property()
    def font(self) -> LCARSFont:
        """Font to use when rendering this text [GET/SET]"""
        return self._text_internal.font

    @font.setter
    def font(self, value: LCARSFont):
        self._text_internal.font = value

    def _draw_text(self, color: Color):
        """Internal utility to render our label's text."""
        self._text_internal.area = self.area
        self._text_internal.text = self._format_text(self.text)
        self._text_internal.color = color
        self._text_internal.scale = self.scale
        self._text_internal.draw()

    def _format_text(self, text: str):
        """Formats the given text and returns an updated string.

        Widget classes that use this mixin may override this method to implement their own logic for formatting text.
        A common implementation may use ``self._substitute()`` to update tags in the text for actual values dynamically.
        The default implementation of this method just returns TEXT itself.

        Args:
            text (str): text to format. When drawing this TextMixin, this is called with ``self.text``.

        Returns:
            str: updated text. When drawing this TextMixin, this return value is what will be rendered.
        """
        return text


class Label(TextMixin, LeafWidget):
    """Simple text widget."""

    def __init__(self, text: str = ""):
        LeafWidget.__init__(self)
        TextMixin.__init__(self, text)
        self.node_header_color = WidgetColors.Primitives

    @input_property()
    def style(self) -> VisualStyle:
        """Visual style of this label. [GET/SET]"""
        return VisualStyle()

    def render(self):
        self._draw_text(self.style.text_color)
        self._handle_interaction()
