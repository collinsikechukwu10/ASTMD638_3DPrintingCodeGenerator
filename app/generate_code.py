import datetime as dt
import math
from typing import List, Dict, Union

from app.core.constants import get_cross_section_factor_adjustment
from app.core.enums import PrinterType
from app.core.exceptions import NegativeValueException
from app.core.models import GCode


class ASTM638TestSampleGCodeGenerator:
    def __init__(self, settings: Dict[str, Union[int, float, bool, str]]):
        kwargs = settings
        self._coords: List[GCode] = list()

        self._counter_idx = 0
        self._init_speed = kwargs["initialization_speed"]
        self._print_speed = kwargs["print_speed"]

        self._startX = kwargs["start_point_x"] or 0
        self._startY = kwargs["start_point_y"] or 0
        self._sample_height = kwargs["sample_height"]
        self._layer_height = kwargs["layer_thickness"]
        self._layer_width = kwargs["layer_width"]
        self._layer_length = kwargs["layer_length"]
        self._layer_raster_spacing = kwargs["layer_raster_spacing"]
        self._filament_size = kwargs["filament_size"]

        # Make sure that this is the actual start of the build,
        # and aalso checvk that this is not represented in the config already
        self._currentZ = 0

        # FILLET SECTION
        self._midsection_length = kwargs["midsection_length"]
        self._midsection_height = kwargs["midsection_height"]
        self._fillet_radius = kwargs["fillet_radius"]
        self._grip_distance = kwargs["grip_distance"]
        self._theta = kwargs["theta"]

        # PRINTER SETTINGS
        self._printer_type = kwargs["printer_type"]
        self._nozzle_temperature = kwargs["nozzle_temperature"]
        self._bed_temperature = kwargs["bed_temperature"]
        self._nozzle_diameter = kwargs["nozzle_diameter"]
        self._add_adhesion = kwargs["add_adhesion"]
        self._adhesion_width = kwargs["adhesion_layer_width"]
        self._adhesion_thickness = kwargs["adhesion_layer_thickness"]

        # should maybe include the adhesion layer as well
        self._num_layers = int((self._currentZ + self._sample_height) / self._layer_height)

        # Generate code
        self._curve_height = (self._grip_distance - self._midsection_height) / 2

        # midsection layer z variables.
        self._bottom_grip_start = self._currentZ + (self._sample_height - self._grip_distance) / 2
        self._bottom_grip_end = self._bottom_grip_start + self._curve_height
        self._top_grip_start = self._bottom_grip_end + self._midsection_height
        self._top_grip_end = self._top_grip_start + self._curve_height

        # midesction x variables
        self._midsection_start_x = self._startX + (self._layer_length - self._midsection_length) / 2
        self._midesction_end_x = self._midsection_start_x + self._midsection_length
        self.build()

    def build(self):

        if self._add_adhesion:
            self._build_adhesion_layer(self._startX, self._startY, self._currentZ, self._adhesion_width)

        for layer in range(1, self._num_layers + 1):
            current_z_layer = self._currentZ + (layer * self._layer_height)
            (start_x, end_x) = self._get_startx_endx(current_z_layer)
            self._build_layer(start_x, end_x, self._startY, current_z_layer)

    def _get_startx_endx(self, layer_z):
        d0 = self._fillet_radius * math.sin(self._theta * (math.pi / 180))
        if self._bottom_grip_start <= layer_z < self._bottom_grip_end:
            # lower half
            h2 = self._bottom_grip_end - layer_z
            d2 = math.sqrt(math.pow(self._fillet_radius, 2) - math.pow(h2, 2)) - d0
            x0 = self._startX + d2
            x1 = x0 + self._layer_length - (2 * d2)
            return x0, x1
        elif self._top_grip_start <= layer_z < self._top_grip_end:
            # upper half
            h2 = layer_z - self._top_grip_start
            d2 = math.sqrt(math.pow(self._fillet_radius, 2) - math.pow(h2, 2)) - d0
            x0 = self._startX + d2
            x1 = x0 + self._layer_length - (2 * d2)
            return x0, x1
        elif self._bottom_grip_end <= layer_z < self._top_grip_start:
            x0, x1 = self._midsection_start_x, self._midesction_end_x
        else:
            x0, x1 = self._startX, self._startX + self._layer_length
        return x0, x1

    def _build_layer(self, start_x, end_x, start_y, layer_z):
        cx = start_x
        end_y = start_y + self._layer_width
        while cx <= end_x:
            cx += self._layer_raster_spacing
            self._add_path(cx, start_y, layer_z)
            self._add_path(cx, end_y, layer_z)
            cx += self._layer_raster_spacing
            self._add_path(cx, end_y, layer_z)
            self._add_path(cx, start_y, layer_z)

    def _build_adhesion_layer(self, start_x, start_y, z_layer, adhesion_width):
        adhes_end_x = adhes_end_y = adhesion_width
        c_x = start_x - adhes_end_x
        c_y = start_y - adhes_end_y
        if c_x < 0 or c_y < 0:
            raise NegativeValueException()
        self._add_path(c_x, c_y, z_layer, True)
        while adhes_end_x <= 0.4 or adhes_end_y <= 0.4:
            c_y += (adhes_end_y * 2 + self._layer_width)
            self._add_path(c_x, c_y, z_layer, True)
            c_x += (adhes_end_x * 2 + self._layer_length)
            self._add_path(c_x, c_y, z_layer, True)
            c_y -= (adhes_end_y * 2 + self._layer_width)
            self._add_path(c_x, c_y, z_layer, True)
            c_x -= (adhes_end_x * 2 + self._layer_length)
            self._add_path(c_x, c_y, z_layer, True)
            c_x += 0.4765
            c_y += 0.4765
            adhes_end_x -= (2 * 0.4765 / 3)
            adhes_end_x -= (2 * self._layer_raster_spacing / 3)

    def _add_path(self, x, y, z, is_adhesion_layer=False):
        self._coords.append(GCode(x=x, y=y, z=z, e=self._calculate_extrusion_amount(x, y, z, is_adhesion_layer)))

    def _calculate_extrusion_amount(self, x, y, z, is_adhesion_layer):
        if self._counter_idx == 0:
            return 0
        csa = get_cross_section_factor_adjustment(self._layer_raster_spacing)
        csa = self._adhesion_thickness * 0.4 / csa if is_adhesion_layer else self._layer_height * 0.4 / csa
        px, py, pz, pe = self._coords[self._counter_idx - 1].tuple()
        return pe + csa * math.sqrt(math.pow(x - px, 2) + math.pow(y - py, 2) + math.pow(z - pz, 2))

    def gcode_traversal(self):
        return self._coords

    def _prepare_initialization_code(self):
        if self._printer_type == PrinterType.ULTIMAKER:
            opening_str = f";FLAVOR:UltiGCode\n" + \
                          ";MATERIAL:1795\n" + \
                          ";MATERIAL2:0\n" + \
                          f";NOZZLE_DIAMETER:{self._nozzle_diameter}\n" + \
                          ";ASTM TYPE 5 Design\n" + \
                          f";LAYER COUNT:{self._num_layers}\n" + \
                          "M107 ;FAN OFF\n" + \
                          f"G0 F{self._init_speed} X{self._startX} Y{self._startY} Z0\n" + \
                          "M106 S255 ;FAN ON\n"
        else:
            opening_str = ";REPRAP GCODE ASTM D638 BUILD\n" + \
                          f"M104 S{self._nozzle_temperature}\n" + \
                          f"M190 S{self._bed_temperature}\n" + \
                          f"M109 {self._nozzle_temperature}\n" + \
                          "M82\n" + \
                          "M107\n" + \
                          f"G1 F{self._print_speed} X20 Y20 Z10\n" + \
                          "G92 E0\n" + \
                          f"F1 F{self._print_speed} E3\n" + \
                          "G92 E0\n" + \
                          f"G1 F{self._print_speed} X{self._startX} Y{self._startY} Z0.05\n" + \
                          "G92 X0 Y0 Z0\n" + \
                          "M106 S190\n"
        return f";Generated on {dt.datetime.now()};\n" + opening_str

    def _prepare_close_code(self):
        return "G10;\nM107;\n" if self._printer_type == PrinterType.ULTIMAKER else \
            "M104 S0;\nM140 S0;\nG91;\nG1 E-2 F300;\nG28 X0 Y0;\nM84;\nG90;\nM107;\n"

    def _prepare_traversals(self):
        return "".join([
            f"G{(idx == 0) * 0 + (idx != 0) * 1} F{(idx == 0) * self._init_speed + (idx != 0) * self._print_speed} " +
            f"X{coord.x:.4f} Y{coord.y:.4f} Z{coord.z:.4f} E{coord.e:.4f};\n" for idx, coord in
            enumerate(self._coords)]
        )

    def gcode_file(self, as_bytes: bool = False):
        code = self._prepare_initialization_code() + self._prepare_traversals() + self._prepare_close_code()
        return bytes(code.encode("utf8")) if as_bytes else code
