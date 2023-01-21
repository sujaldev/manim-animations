class Vector:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __add__(self, other: "Vector"):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector"):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: int):
        return Vector(self.x * scalar, self.y * scalar)

    @property
    def xy(self):
        return self.x, self.y
