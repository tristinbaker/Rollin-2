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

        if self.player.dx < 0 and (self.player.top_left or self.player.bottom_left):
            self.player.dx = 0
            tile_size = self.player.tilemap.get_tile_size()
            return int(next_x / tile_size) * tile_size + self.player.cwidth / 2
        elif self.player.dx > 0 and (self.player.top_right or self.player.bottom_right):
            self.player.dx = 0
            tile_size = self.player.tilemap.get_tile_size()
            return (int(next_x / tile_size) + 1) * tile_size - self.player.cwidth / 2
        else:
            # Apply boundary check
            min_x = self.player.cwidth / 2
            if next_x < min_x:
                self.player.dx = 0
                return min_x
            return next_x

    def handle_vertical_collision_platform(self, next_y, moving_platforms):
        """
        Handle vertical collision with platforms

        Args:
            next_y: The intended next Y position
            moving_platforms: List of moving platform objects

        Returns:
            platform if collision detected, None otherwise
        """
        if not self.player.dy or not moving_platforms:
            return None

        for platform in moving_platforms:
            # Check if player overlaps platform horizontally
            player_left = self.player.x - self.player.cwidth / 2
            player_right = self.player.x + self.player.cwidth / 2
            platform_left = platform.get_x() - platform.get_width() / 2
            platform_right = platform.get_x() + platform.get_width() / 2

            horizontal_overlap = player_right > platform_left and player_left < platform_right

            if not horizontal_overlap:
                continue

            player_bottom = self.player.y + self.player.cheight / 2
            platform_top = platform.get_y() - platform.get_height() / 2

            if self.player.dy > 0:  # Falling down
                # Check if player was above platform before and is now intersecting
                next_player_bottom = next_y + self.player.cheight / 2
                if player_bottom <= platform_top + 2 and next_player_bottom >= platform_top - 2:
                    self.player.y = platform_top - self.player.cheight / 2
                    self.player.dy = 0
                    return platform
            elif self.player.dy < 0:  # Moving up
                platform_bottom = platform.get_y() + platform.get_height() / 2
                player_top = self.player.y - self.player.cheight / 2
                next_player_top = next_y - self.player.cheight / 2
                if player_top >= platform_bottom - 2 and next_player_top <= platform_bottom + 2:
                    self.player.y = platform_bottom + self.player.cheight / 2
                    self.player.dy = 0
                    return None
        return None

    def handle_vertical_collision_tiles(self, next_y):
        """
        Handle vertical collision with tiles

        Args:
            next_y: The intended next Y position
        """
        if not self.player.dy:
            return

        self.player.check_collision(self.player.x, next_y)
        if self.player.dy < 0:  # upward
            if self.player.top_left or self.player.top_right:
                self.player.dy = 0
                tile_size = self.player.tilemap.get_tile_size()
                self.player.y = int(self.player.y / tile_size) * tile_size + self.player.cheight / 2
        elif self.player.dy > 0:  # downward
            if self.player.bottom_left or self.player.bottom_right:
                self.player.dy = 0
                tile_size = self.player.tilemap.get_tile_size()
                self.player.y = (int(self.player.y / tile_size) + 1) * tile_size - self.player.cheight / 2

    def handle_vertical_collision_downward(self, next_y, moving_platforms=None):
        """
        Handle vertical collision when moving downward (falling)

        Args:
            next_y: The intended next Y position
            moving_platforms: List of moving platform objects

        Returns:
            tuple: (resolved_y, standing_platform, on_ground)
        """
        standing_platform = None
        platform_collision = False

        # Check moving platform collision first
        if moving_platforms:
            for platform in moving_platforms:
                if platform.intersects(self.player.x, next_y, self.player.cwidth, self.player.cheight):
                    player_bottom = self.player.y + self.player.cheight / 2
                    platform_top = platform.get_y() - platform.get_height() / 2

                    # Only collide if player was above platform (landing on top)
                    if player_bottom - self.player.dy <= platform_top + 2:
                        # Debug
                        if hasattr(platform, 'start_y'):
                            print(f"COLLISION RETURN: plat_x={platform.get_x():.1f}, player_x={self.player.x:.1f}, snapping={abs(player_bottom - platform_top) > 0.5}")

                        # Only snap if significantly off (more than 2 pixels) to prevent bouncing
                        # Use 2.0 instead of 0.5 to avoid micro-snaps when transitioning between adjacent platform tiles
                        if abs(player_bottom - platform_top) > 2.0:
                            resolved_y = platform_top - self.player.cheight / 2
                        else:
                            resolved_y = self.player.y
                        self.player.dy = 0
                        standing_platform = platform
                        platform_collision = True
                        return resolved_y, standing_platform, True

        # Check tile collision
        if not platform_collision:
            self.player.check_collision(self.player.x, next_y)
            if self.player.bottom_left or self.player.bottom_right:
                self.player.dy = 0
                tile_size = self.player.tilemap.get_tile_size()
                resolved_y = (int(self.player.y / tile_size) + 1) * tile_size - self.player.cheight / 2
                return resolved_y, None, True
            else:
                return next_y, None, False

    def check_ground_correction(self, standing_platform=None):
        """
        Check and correct ground detection flags

        Args:
            standing_platform: The platform player is standing on (if any)

        Returns:
            bool: Whether player is on ground
        """
        # Don't override on_ground if standing on a moving platform
        if standing_platform:
            return self.player.on_ground

        if self.player.bottom_left or self.player.bottom_right:
            tile_size = self.player.tilemap.get_tile_size()
            offset = ((self.player.y + self.player.cheight / 2) % tile_size)
            if offset < 0.5:
                self.player.dy = 0
                return True

        return False
