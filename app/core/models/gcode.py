from pydantic import BaseModel


class GCode(BaseModel):
    """
    A class to represent a GCode coordinate.
    Coordinate is represented by a 3d location on the printing surface (x,y,z) and an extrusion value (e).
    """
    x: float
    y: float
    z: float = 0
    e: float = 0

    def tuple(self):
        return self.x, self.y, self.z, self.e

    def coordinate(self):
        return self.x, self.y, self.z

    def __sub__(self, other):
        return self.x - other.x, self.y - other.y, self.z - other.z

    def __add__(self, other):
        return self.x + other.x, self.y + other.y, self.z + other.z
