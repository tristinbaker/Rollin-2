"""
Tile - equivalent to Tile.java
Represents a single tile with an image and collision type
"""


class Tile:
    # Tile types
    NORMAL = 0
    BLOCKED = 1

    def __init__(self, image, tile_type):
        """
        Initialize a tile

        Args:
            image: pygame.Surface containing the tile image
            tile_type: NORMAL or BLOCKED
        """
        self.image = image
        self.type = tile_type

    def is_blocked(self):
        """Check if this tile is solid (blocked)"""
        return self.type == self.BLOCKED
