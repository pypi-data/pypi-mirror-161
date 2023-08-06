"""
    StptTileRaw: holds metadata about a tile as part of a raw STPT section
"""


class StptTileRaw:

    def __init__(self, x_pos, y_pos):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.files = []
