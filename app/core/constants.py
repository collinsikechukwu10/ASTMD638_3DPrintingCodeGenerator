import math

PLOT_TITLE = '3D Astm D638 Plot'
def get_cross_section_factor_adjustment(x):
    return 0.7063 * math.pow(x, -0.652)
