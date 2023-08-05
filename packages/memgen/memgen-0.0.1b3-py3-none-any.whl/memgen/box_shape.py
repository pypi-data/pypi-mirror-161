from enum import Enum


class BoxShape(Enum):
    square = 'square'
    hexagonal = 'hexagonal'

    def __str__(self):
        return self.value
