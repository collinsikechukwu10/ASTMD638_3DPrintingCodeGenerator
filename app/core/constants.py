import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLOT_TITLE = '3D Astm D638 Plot'
GCODE_FILE_SAVE_NAME = "astmD638Sample.gcode"


def get_cross_section_factor_adjustment(x):
    return 0.7063 * math.pow(x, -0.652)
