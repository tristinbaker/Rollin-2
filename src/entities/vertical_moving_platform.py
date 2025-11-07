"""
VerticalMovingPlatform - A platform that moves up and down vertically
"""
import pygame


class VerticalMovingPlatform:
    """Platform entity that moves vertically and is fully collidable"""

    def __init__(self, tilemap, tile_id=None):
        """
        Initialize a vertical moving platform

        Args:
            tilemap: Reference to the TileMap for camera positioning
            tile_id: The tile ID from the Tiled map (used to determine visual appearance)
        """
        self.tilemap = tilemap
        self.tile_id = tile_id

        # Position
        self.x = 0
        self.y = 0
        self.start_y = 0  # Starting Y position

        # Movement
        self.move_distance = 64  # Move 64 pixels (2 tiles at 32px) up and down
        self.move_speed = 30  # Pixels per second
        self.direction = 1  # 1 = moving down, -1 = moving up

        # Size (one tile)
        self.width = tilemap.tile_size
        self.height = tilemap.tile_size

        # Collision box (full tile size)
        self.cwidth = self.width
        self.cheight = self.height

        # Visual
        self.sprite = None
        self._load_sprite()

    def _load_sprite(self):
        """Load the platform sprite from the tileset"""
        # If we have a tile_id, try to load the tile image from the tilemap
        if self.tile_id and hasattr(self.tilemap, 'tiled_tiles') and self.tile_id in self.tilemap.tiled_tiles:
            self.sprite = self.tilemap.tiled_tiles[self.tile_id]['image'].copy()
        else:
            # Fallback: create a simple colored rectangle
            self.sprite = pygame.Surface((self.width, self.height))
            self.sprite.fill((100, 100, 200))  # Blue-ish color

    def set_position(self, x, y):
        """Set the platform's initial position"""
        self.x = x
        self.y = y
        self.start_y = y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_width(self):
        return self.cwidth

    def get_height(self):
        return self.cheight

    def update(self, dt):
        """
        Update platform movement

        Args:
            dt: Delta time in milliseconds
        """
        # Calculate movement
        move_amount = self.move_speed * (dt / 1000.0) * self.direction

        # Update position
        self.y += move_amount

        # Check bounds and reverse direction if needed
        distance_from_start = self.y - self.start_y

        if distance_from_start >= self.move_distance:
            # Reached bottom, move up
            self.y = self.start_y + self.move_distance
            self.direction = -1
        elif distance_from_start <= -self.move_distance:
            # Reached top, move down
            self.y = self.start_y - self.move_distance
            self.direction = 1

        # Make sure platform doesn't go off-screen (above y=0)
        if self.y < self.height / 2:
            self.y = self.height / 2
            self.direction = 1  # Force downward movement

    def draw(self, surface):
        """Draw the platform"""
        if self.sprite is None:
            return

        # Calculate screen position (account for camera)
        draw_x = int(self.x - self.width / 2 + self.tilemap.get_x())
        draw_y = int(self.y - self.height / 2 + self.tilemap.get_y())
        surface.blit(self.sprite, (draw_x, draw_y))

    def intersects(self, x, y, width, height):
        """
        Check if a rectangle intersects with this platform
        Used for collision detection

        Args:
            x, y: Center position of the rectangle
            width, height: Dimensions of the rectangle

        Returns:
            bool: True if intersecting
        """
        # Calculate bounds of this platform
        left1 = self.x - self.cwidth / 2
        right1 = self.x + self.cwidth / 2
        top1 = self.y - self.cheight / 2
        bottom1 = self.y + self.cheight / 2

        # Calculate bounds of the other rectangle
        left2 = x - width / 2
        right2 = x + width / 2
        top2 = y - height / 2
        bottom2 = y + height / 2

        # Check for intersection
        return not (left1 >= right2 or right1 <= left2 or top1 >= bottom2 or bottom1 <= top2)
