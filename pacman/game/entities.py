from .maze import Direction
from typing import Optional

class Entities:

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.direction: Optional[Direction]

    def position(self) -> tuple[float, float]:
        if self.direction is None:
            return float(self.x), float(self.y)
        return (self.x + self.direction.dx, self.y + self.direction.dy)

    
