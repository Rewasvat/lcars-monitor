import lcarsmonitor.actions as actions
import libasvat.imgui.editors.primitives as primitives
from libasvat.imgui.math import Vector2, Rectangle
from libasvat.imgui.colors import Color, Colors
from libasvat.imgui.assets import ImageInfo, AssetPath
from libasvat.imgui.nodes import input_property, PinKind
from lcarsmonitor.widgets.base import LeafWidget, WidgetColors
from lcarsmonitor.widgets.rect import RectMixin
from lcarsmonitor.widgets.label import TextMixin, Alignment
from lcarsmonitor.widgets.style import VisualStyle
from imgui_bundle import imgui
from enum import Enum


class ImageLayoutMode(Enum):
    """How to draw a image in a given area."""
    STRETCH = "STRETCH"
    """Image is stretched to cover the entire containing area. May deform the image's aspect-ratio, but no part
    of the area will be empty. As such, positioning/alignment settings do not matter."""
    FIT = "FIT"
    """Image is shrunk/enlarged in order to fit the containing area. The image's aspect-ratio is preserved.
    If the containing area does not match the image's ratio, then some empty area will remain either on the sides or
    on top/bottom. In these cases, positioning/alignment settings can be used."""


class Image(RectMixin, LeafWidget):
    """Basic image-drawing widget.

    Behaves similarly to a Rect, but draws a image instead of just a colored rect.
    Image is tinted with the image-style's normal-color. For interaction-based tinting, see
    the `ImageButton` widget.
    """

    def __init__(self):
        RectMixin.__init__(self)
        LeafWidget.__init__(self)
        self.node_header_color = WidgetColors.Assets
        self.image: ImageInfo = None
        self._mode: ImageLayoutMode = ImageLayoutMode.STRETCH
        self._image_align: Alignment = Alignment.CENTER
        self._uv_rect = Rectangle(size=(1, 1))

    @primitives.enum_property()
    def mode(self):
        """How the image is drawn in our area [GET/SET]"""
        return self._mode

    @mode.setter
    def mode(self, value: ImageLayoutMode):
        self._mode = value

    @primitives.enum_property()
    def image_align(self):
        """How the text is aligned to our area [GET/SET]"""
        return self._image_align

    @image_align.setter
    def image_align(self, value: Alignment):
        self._image_align = value

    @input_property(allow_external_assets=True)
    def image_path(self) -> AssetPath:
        """Path to the image to draw. Can select a app image or an external asset [GET/SET]."""
        return ""

    @input_property()
    def image_style(self) -> VisualStyle:
        """Visual style of this image. [GET/SET]"""
        return VisualStyle()

    def _draw_image(self, tint_color: Color):
        """Draws this image widget."""
        # Update loaded image in case selected image-path has changed.
        path_ok = self.image_path is not None and len(self.image_path) > 0 and self.image_path != "None"
        if path_ok:
            if self.image is None:
                self.image = ImageInfo.from_path(self.image_path)
            elif self.image.path != self.image_path:
                self.image = None
                self.image = ImageInfo.from_path(self.image_path)
        else:
            self.image = None

        if self.image:
            # Draw loaded image
            if self._mode is ImageLayoutMode.STRETCH:
                img_rect = self.area
            elif self._mode is ImageLayoutMode.FIT:
                image_size = self.image.size
                img_rect = self.area.get_inner_rect(image_size.aspect_ratio())
                img_rect.position = self.area.top_left_pos + self._image_align.get_pos_offset(self.area.size, img_rect.size)

            self.image.adv_draw(img_rect, self._uv_rect, tint_color, self.actual_rounding, self.corners.get_flags())
        else:
            # Draw placeholder for no image selected.
            color = Colors.red
            thick = 5
            self.area.draw(color, thickness=thick)
            draw = imgui.get_window_draw_list()
            draw.add_line(self.area.top_left_pos, self.area.bottom_right_pos, color.u32, thick)
            draw.add_line(self.area.top_right_pos, self.area.bottom_left_pos, color.u32, thick)

    def render(self):
        self._handle_interaction()
        self._draw_image(self.image_style.normal_color)


class ImageButton(TextMixin, Image):
    """An image button widget.

    Visually, its a ``Image`` + ``Label`` widget with image tint-color based
    on Image style and widget interaction state.

    Allows to set a command that will be executed when clicked.
    """

    def __init__(self):
        TextMixin.__init__(self)
        Image.__init__(self)
        self.node_header_color = WidgetColors.Interactible
        self._on_clicked = actions.ActionFlow(self, PinKind.output, "On Click")
        self.add_pin(self._on_clicked)

    def render(self):
        if self._handle_interaction():
            self._on_clicked.trigger()
        self._draw_image(self.image_style.get_current_color(self))
        self._draw_text(self.image_style.text_color)

    def _format_text(self, text):
        if self.image is None:
            return f"<INVALID IMAGE>\n{text}"
        return text
