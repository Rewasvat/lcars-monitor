import libasvat.imgui.type_editor as types
from lcarsmonitor.widgets.base import LeafWidget, WidgetColors
from lcarsmonitor.widgets.lcars.alerts import XAMLPath
from libasvat.imgui.nodes import input_property
from libasvat.imgui.colors import Color, Colors
from libasvat.imgui.math import Vector2, Rectangle
from imgui_bundle import imgui


class MainControls(LeafWidget):
    """A LCARS "Main Controls" widget.

    This is a collection of several buttons of different sizes disposed generally in an inner and outer
    circle around a central circle of buttons. Usually seen in Star Trek's LCARS screens of Federation
    starships.

    TODO: THIS IS NOT FINISHED! Missing UI elements and logic.
    """

    def __init__(self):
        super().__init__()
        self.node_header_color = WidgetColors.Interactible
        self._xaml_scale = Vector2(1/132.0, 1/125.0)
        self._build()

    def _build(self):
        """Sets up the fixed values of internal attributes used later when rendering this widget.

        This uses some of the properties of this widget in order to setup the values, so this method
        can be used to "update" the contents of the widget after changing some property."""
        thickness = 0.2
        self._buttons = {
            "TL-Inner-2": XAMLPath(
                "M 46.531,34.430 L 55.161,47.610 C 55.161,47.610 51.541,49.220 48.821,52.020 L 37.021,41.700 \
                    C 41.391,37.150 46.531,34.430 46.531,34.430 Z",
                self._xaml_scale,
                Color.from_hex("ffedb582", use_argb=True),
                Colors.background,
                thickness,
                True
            ),
            "TL-Inner-1": XAMLPath(
                "M 59.831,29.670 L 60.871,45.550 C 60.871,45.550 58.451,46.150 56.081,47.160 L 47.681,33.800 \
                    C 53.421,30.470 59.831,29.670 59.831,29.670 Z",
                self._xaml_scale,
                Color.from_hex("ffff9800", use_argb=True),
                Colors.background,
                thickness,
                True
            ),
            "T-Inner": XAMLPath(
                "M 71.981,45.070 L 73.061,29.400 C 73.061,29.400 67.221,28.470 60.721,29.500 L 61.931,44.700 \
                    C 61.931,44.700 66.621,43.910 71.981,45.080 Z",
                self._xaml_scale,
                Color.from_hex("ffedb582", use_argb=True),
                Colors.background,
                thickness,
                True
            ),
            "TR-Inner": XAMLPath(
                "M 108.241,64.410 L 92.461,64.500 C 87.761,48.800 73.061,45.420 73.061,45.420 L 73.841,29.450 \
                    C 104.571,34.930 108.231,64.400 108.231,64.400 Z",
                self._xaml_scale,
                Color.from_hex("ffeeb556", use_argb=True),
                Colors.background,
                thickness
            ),
            "R-Inner": XAMLPath(
                "M 108.401,76.450 L 92.831,76.550 C 92.831,76.550 94.141,70.810 92.741,65.630 L 108.401,65.530 \
                    C 109.291,71.000 108.401,76.450 108.401,76.450 Z",
                self._xaml_scale,
                Color.from_hex("ffeeb556", use_argb=True),
                Colors.background,
                thickness,
                True
            ),
            "BR-Inner": XAMLPath(
                "M 108.241,77.580 L 92.591,77.580 C 92.591,77.580 90.271,92.050 73.741,96.860 L 74.241,112.280 \
                    C 74.241,112.280 102.721,108.620 108.231,77.570 L 108.241,77.580 Z",
                self._xaml_scale,
                Color.from_hex("ff9f6c8b", use_argb=True),
                Colors.background,
                thickness,
                True
            ),
            "B-Inner": XAMLPath(
                "M 60.201,112.470 L 61.241,97.150 C 67.901,98.510 72.541,97.150 72.541,97.150 L 72.971,112.510 \
                    C 72.971,112.510 66.551,113.360 60.191,112.470 Z",
                self._xaml_scale,
                Color.from_hex("ffeeb556", use_argb=True),
                Colors.background,
                thickness,
                True
            ),
            "BL-Btn-3": XAMLPath(
                "M 35.091,124.710 L 53.841,94.390 C 53.841,94.390 56.701,96.190 60.471,96.970 L 58.061,124.710 \
                    C 58.061,124.710 35.091,124.710 35.091,124.710 Z",
                self._xaml_scale,
                Color.from_hex("ffeeb556", use_argb=True),
                Colors.background,
                thickness
            ),
            "BL-Btn-1": XAMLPath(
                "M 0.501,79.250 L 41.201,77.450 C 41.201,77.450 41.521,78.960 41.891,79.930 L 0.501,99.810 Z",
                self._xaml_scale,
                Color.from_hex("ff98cbff", use_argb=True),
                Colors.background,
                thickness,
                True
            ),
            "L-Inner": XAMLPath(
                "M 25.411,64.820 L 41.041,65.750 C 39.911,70.990 40.861,75.960 40.861,75.960 L 25.431,76.680 \
                    C 24.541,70.990 25.411,64.820 25.411,64.820 Z",
                self._xaml_scale,
                Color.from_hex("ff9f6c8b", use_argb=True),
                Colors.background,
                thickness
            ),
            "TL-Inner-3": XAMLPath(
                "M 25.631,63.990 L 41.261,64.820 C 41.261,64.820 41.891,61.700 43.501,58.980 L 29.191,52.820 \
                    C 29.191,52.820 26.581,58.020 25.631,63.980 Z",
                self._xaml_scale,
                Color.from_hex("ffeeb556", use_argb=True),
                Colors.background,
                thickness
            ),
            "L-Outer": XAMLPath(
                "M 13.041,77.240 L 25.231,76.680 C 25.231,76.680 24.381,70.790 25.021,64.820 L 12.791,64.080 \
                    C 12.141,69.970 13.051,77.240 13.051,77.240 Z",
                self._xaml_scale,
                Color.from_hex("ff9f6c8b", use_argb=True),
                Colors.background,
                thickness
            ),
            "TL-Outer-4": XAMLPath(
                "M 0.501,41.660 L 28.711,52.830 C 28.711,52.830 26.281,58.030 25.361,63.730 L 0.501,62.330 L 0.501,41.670 Z",
                self._xaml_scale,
                Color.from_hex("ffeeb556", use_argb=True),
                Colors.background,
                thickness
            ),
            "TL-Outer-3": XAMLPath(
                "M 26.201,34.730 L 35.671,42.280 C 32.421,46.000 29.091,52.020 29.091,52.020 L 17.821,47.250 \
                    C 21.161,40.000 26.191,34.740 26.191,34.740 Z",
                self._xaml_scale,
                Color.from_hex("ffedb582", use_argb=True),
                Colors.background,
                thickness
            ),
            "TL-Outer-2": XAMLPath(
                "M 46.091,33.840 L 39.841,23.780 C 39.841,23.780 32.611,27.770 27.121,33.720 L 36.631,41.230 \
                    C 41.161,36.870 46.081,33.830 46.081,33.830 Z",
                self._xaml_scale,
                Color.from_hex("ffedb582", use_argb=True),
                Colors.background,
                thickness
            ),
            "TL-Outer-1": XAMLPath(
                "M 59.531,28.910 L 58.581,17.480 C 58.581,17.480 49.151,18.590 41.121,23.090 L 47.211,33.230 \
                    C 53.231,29.840 59.531,28.920 59.531,28.920 Z",
                self._xaml_scale,
                Color.from_hex("ffff9800", use_argb=True),
                Colors.background,
                thickness
            ),
            "T-Outer": XAMLPath(
                "M 73.841,17.560 L 73.311,28.650 C 73.311,28.650 66.891,27.810 60.461,28.750 L 59.391,17.380 \
                    C 66.621,16.330 73.851,17.570 73.851,17.570 Z",
                self._xaml_scale,
                Color.from_hex("ffedb582", use_argb=True),
                Colors.background,
                thickness,
                True
            ),
            "TR-Outer-1": XAMLPath(
                "M 87.541,33.380 L 93.171,24.440 C 93.171,24.440 84.911,19.100 74.501,17.650 L 73.841,28.560 \
                    C 81.671,29.600 87.541,33.370 87.541,33.370 L 87.541,33.380 Z",
                self._xaml_scale,
                Color.from_hex("ffeeb556", use_argb=True),
                Colors.background,
                thickness
            ),
            "TR-Outer-2": XAMLPath(
                "M 106.031,35.140 L 98.621,42.100 C 98.621,42.100 93.931,37.070 88.241,33.770 L 94.041,24.970 \
                    C 100.951,29.010 106.031,35.130 106.031,35.130 Z",
                self._xaml_scale,
                Color.from_hex("ffeeb556", use_argb=True),
                Colors.background,
                thickness,
                True
            ),
            "TR-Outer-3": XAMLPath(
                "M 127.391,43.670 L 105.991,53.380 C 105.991,53.380 103.461,47.340 99.061,42.590 L 116.761,28.210 \
                    C 124.651,34.840 127.391,43.670 127.391,43.670 Z",
                self._xaml_scale,
                Color.from_hex("ffeeb556", use_argb=True),
                Colors.background,
                thickness,
                True
            ),
            "TR-Outer-4": XAMLPath(
                "M 131.801,63.720 L 109.091,63.720 C 109.091,63.720 108.541,59.030 106.381,54.260 L 127.711,44.750 \
                    C 131.541,53.810 131.801,63.710 131.801,63.710 Z",
                self._xaml_scale,
                Color.from_hex("ffeeb556", use_argb=True),
                Colors.background,
                thickness,
                True
            ),
            "R-Outer": XAMLPath(
                "M 119.381,76.550 L 108.791,76.550 C 108.791,76.550 109.291,70.590 108.791,65.530 L 119.481,65.530 \
                    C 120.211,71.040 119.381,76.550 119.381,76.550 Z",
                self._xaml_scale,
                Color.from_hex("ffeeb556", use_argb=True),
                Colors.background,
                thickness
            ),
            "BR-Outer": XAMLPath(
                "M 74.831,124.040 L 74.311,112.470 C 105.841,106.620 109.091,77.550 109.091,77.550 L 119.271,77.550 \
                    C 119.271,77.550 118.981,115.720 74.841,124.040 Z",
                self._xaml_scale,
                Color.from_hex("ff9f6c8b", use_argb=True),
                Colors.background,
                thickness
            ),
            "B-Outer": XAMLPath(
                "M 59.241,124.710 L 60.201,113.060 C 66.591,113.490 72.991,113.060 72.991,113.060 L 73.381,124.210 \
                    C 69.091,124.780 59.241,124.700 59.241,124.700 Z",
                self._xaml_scale,
                Color.from_hex("ffeeb556", use_argb=True),
                Colors.background,
                thickness
            ),
            "BL-Btn-2": XAMLPath(
                "M 0.541,124.710 L 0.501,102.030 L 42.451,81.400 C 46.101,89.960 52.841,93.710 52.841,93.710 L 33.031,124.710 Z",
                self._xaml_scale,
                Color.from_hex("ffeeb556", use_argb=True),
                Colors.background,
                thickness
            ),
            "TL-External-Bridge": XAMLPath(
                "M 32.871,12.030 L 39.841,23.780 C 39.841,23.780 32.321,27.530 27.121,33.720 L 1.981,12.030 Z",
                self._xaml_scale,
                Color.from_hex("ff9f6c8b", use_argb=True),
                Colors.background,
                thickness
            ),
            "T-External-Bridge": XAMLPath(
                "M 59.391,17.370 L 58.931,12.030 L 74.371,12.030 L 73.861,17.370 C 73.861,17.370 66.891,16.420 59.391,17.370 Z",
                self._xaml_scale,
                Color.from_hex("ffedb582", use_argb=True),
                Colors.background,
                thickness
            ),
            "TR-CornerRect-2-down": XAMLPath(
                "M 101.931,12.750 L 117.011,12.750 C 120.048,12.750 122.511,15.212 122.511,18.250 L 122.511,18.250 \
                    C 122.511,21.288 120.048,23.750 117.011,23.750 L 101.931,23.750 C 98.893,23.750 96.431,21.288 96.431,18.250 \
                    L 96.431,18.250 C 96.431,15.212 98.893,12.750 101.931,12.750 Z",
                self._xaml_scale,
                Color.from_hex("ff9f6c8b", use_argb=True),
                Colors.background,
                thickness,
                True
            ),
            "TR-CornerRect-1-top": XAMLPath(
                "M 101.931,0.530 L 117.011,0.530 C 120.048,0.530 122.511,2.992 122.511,6.030 L 122.511,6.030 \
                    C 122.511,9.068 120.048,11.530 117.011,11.530 L 101.931,11.530 C 98.893,11.530 96.431,9.068 96.431,6.030 \
                    L 96.431,6.030 C 96.431,2.992 98.893,0.530 101.931,0.530 Z",
                self._xaml_scale,
                Color.from_hex("ff98cbff", use_argb=True),
                Colors.background,
                thickness,
                True
            ),
            "T-BorderRect-3-right": XAMLPath(
                "M 75.801,0.500 L 87.191,0.500 C 90.231,0.500 92.691,2.960 92.691,6.000 L 92.691,6.000 C 92.691,9.040 90.231,11.500 87.191,11.500 \
                    L 75.801,11.500 Z",
                self._xaml_scale,
                Color.from_hex("ffeeb556", use_argb=True),
                Colors.background,
                thickness,
                True
            ),
            "T-BorderRect-1-left": XAMLPath(
                "M 57.241,11.500 L 45.851,11.500 C 42.811,11.500 40.351,9.040 40.351,6.000 L 40.351,6.000 C 40.351,2.960 42.811,0.500 45.851,0.500 \
                    L 57.241,0.500 Z",
                self._xaml_scale,
                Color.from_hex("ffedb582", use_argb=True),
                Colors.background,
                thickness,
                True
            ),
            "T-BorderRect-2-center": XAMLPath(
                "M 74.971,11.500 L 58.081,11.500 L 58.081,0.500 L 74.971,0.500 Z",
                self._xaml_scale,
                Color.from_hex("ffff9800", use_argb=True),
                Colors.background,
                thickness,
                True
            ),
            "TL-CornerRect": XAMLPath(
                "M 33.041,11.530 L 1.991,11.530 L 1.991,0.530 L 33.041,0.530 Z",
                self._xaml_scale,
                Color.from_hex("ff9f6c8b", use_argb=True),
                Colors.background,
                thickness,
                True
            ),
        }

    def _draw_main_controls(self):
        """Draws the LCARS main controls widget using imgui"""
        ratio = 1.0 / self._xaml_scale.aspect_ratio()
        controls_area = self.area.get_inner_rect(ratio)

        pos = controls_area.position
        size = controls_area.size
        for btn_name, btn_path in self._buttons.items():
            btn_path.render(pos, size)

        controls_area.draw(Colors.green)

    def render(self):
        self._draw_main_controls()
        self._handle_interaction()
