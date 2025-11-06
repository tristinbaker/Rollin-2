"""
HorizontalMovingPlatform - A platform that moves left and right horizontally
"""
import pygame
import os


class HorizontalMovingPlatform:
    """Platform entity that moves horizontally and is fully collidable"""

    def __init__(self, tilemap, tile_id=None):
        """
        Initialize a horizontal moving platform

        Args:
            tilemap: Reference to the TileMap for camera positioning
            tile_id: The tile ID from the Tiled map (used to determine visual appearance)
        """
        self.tilemap = tilemap
        self.tile_id = tile_id

        # Position
        self.x = 0
        self.y = 0
        self.start_x = 0  # Starting X position

        # Movement
        self.move_distance = 64  # Move 64 pixels (2 tiles at 32px) left and right
        self.move_speed = 30  # Pixels per second
        self.direction = 1  # 1 = moving right, -1 = moving left

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
            self.sprite.fill((200, 100, 100))  # Red-ish color

    def set_position(self, x, y):
        """Set the platform's initial position"""
        self.x = x
        self.y = y
        self.start_x = x

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
        self.x += move_amount

        # Check bounds and reverse direction if needed
        distance_from_start = self.x - self.start_x

        if distance_from_start >= self.move_distance:
            # Reached right limit, move left
            self.x = self.start_x + self.move_distance
            self.direction = -1
        elif distance_from_start <= -self.move_distance:
            # Reached left limit, move right
            self.x = self.start_x - self.move_distance
            self.direction = 1

        # Make sure platform doesn't go off-screen (left edge at x=0)
        if self.x < self.width / 2:
            self.x = self.width / 2
            self.direction = 1  # Force rightward movement

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
