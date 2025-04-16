# NOTE: Having to hardcode the imports of widget classes since this was the only way I tried
# that worked having the classes and their documentation work with intellisense when importing
# this module from anywhere.

# Basic Widget types
from lcarsmonitor.widgets.system import UISystem, UIManager
from lcarsmonitor.widgets.base import BaseWidget, LeafWidget, ContainerWidget
from lcarsmonitor.widgets.system_node import UseSystem

# Container Widget Types
from lcarsmonitor.widgets.board import Board
from lcarsmonitor.widgets.axis_list import AxisList
from lcarsmonitor.widgets.panel import Panel
from lcarsmonitor.widgets.canvas import Canvas

# Simple (Leaf) Widget Types
from lcarsmonitor.widgets.rect import Rect
from lcarsmonitor.widgets.label import Label
from lcarsmonitor.widgets.corner import Corner
from lcarsmonitor.widgets.button import Button
from lcarsmonitor.widgets.progressbar import ProgressBar

# LCARS
import lcarsmonitor.widgets.lcars
