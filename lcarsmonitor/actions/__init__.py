from lcarsmonitor.actions.actions import Action, ActionColors, ActionFlow
import libasvat.utils as utils

import os
utils.load_all_modules(os.path.dirname(__file__), "lcarsmonitor.actions")
