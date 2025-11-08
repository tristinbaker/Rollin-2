"""
PlayerCollisionHandler - Handles collision detection and resolution for the player
Separated from player.py to reduce complexity
"""
from tilemap.tile import Tile


class PlayerCollisionHandler:
    """Handles all collision detection and resolution for the player entity"""

    def __init__(self, player):
        """
        Initialize collision handler

        Args:
            player: Reference to the Player object
        """
        self.player = player

    def handle_horizontal_collision(self, next_x, moving_platforms=None):
        """
        Handle horizontal (X-axis) collision detection and resolution

        Args:
            next_x: The intended next X position
            moving_platforms: List of moving platform objects

        Returns:
            The resolved X position after collision checks
        """
        # Check tile collision
        self.player.check_collision(next_x, self.player.y)

        # Check if player is currently on a slope (only when moving horizontally on ground)
        on_slope = False
        if abs(self.player.dy) < 0.5:  # Only check when not jumping/falling fast
            slope_hit, slope_y, slope_type = self.player.tilemap.check_slope_collision(
                next_x, self.player.y, self.player.cwidth, self.player.cheight, self.player.dy
            )
            on_slope = slope_hit

        if self.player.dx < 0 and (self.player.top_left or self.player.bottom_left):
            # Allow movement if on slope (slope movement should override blocked tiles above)
            if not on_slope:
                self.player.dx = 0
                tile_size = self.player.tilemap.get_tile_size()
                return int(next_x / tile_size) * tile_size + self.player.cwidth / 2
        elif self.player.dx > 0 and (self.player.top_right or self.player.bottom_right):
            # Allow movement if on slope (slope movement should override blocked tiles above)
            if not on_slope:
                self.player.dx = 0
                tile_size = self.player.tilemap.get_tile_size()
                return (int(next_x / tile_size) + 1) * tile_size - self.player.cwidth / 2

        # Apply boundary check
        min_x = self.player.cwidth / 2
        if next_x < min_x:
            self.player.dx = 0
            return min_x
        return next_x
