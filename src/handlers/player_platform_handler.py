"""
PlayerPlatformHandler - Handles player interaction with moving platforms
"""


class PlayerPlatformHandler:
    """Handles platform tracking and movement for the player"""

    def __init__(self, player):
        self.player = player

    def check_horizontal_platform(self):
        """
        Check if player is on horizontal platform from last frame

        Returns:
            bool: True if on horizontal platform
        """
        if self.player.last_platform and hasattr(self.player.last_platform, 'start_x'):
            player_bottom = self.player.y + self.player.cheight / 2
            platform_top = self.player.last_platform.get_y() - self.player.last_platform.get_height() / 2
            if abs(player_bottom - platform_top) <= 2:
                return True
        return False

    def check_vertical_platform(self):
        """
        Check if player is on vertical platform from last frame

        Returns:
            bool: True if on vertical platform
        """
        if self.player.last_platform and hasattr(self.player.last_platform, 'start_y'):
            player_bottom = self.player.y + self.player.cheight / 2
            platform_top = self.player.last_platform.get_y() - self.player.last_platform.get_height() / 2
            if abs(player_bottom - platform_top) <= 2:
                return True
        return False

    def apply_platform_movement(self, standing_platform, dt):
        """
        Apply platform movement to player when standing on a moving platform

        Args:
            standing_platform: The platform the player is standing on
            dt: Delta time in milliseconds
        """
        if not standing_platform or not self.player.on_ground:
            return

        if hasattr(standing_platform, 'start_y'):  # Vertical platform
            platform_velocity_y = standing_platform.move_speed * (dt / 1000.0) * standing_platform.direction
            self.player.y += platform_velocity_y
        elif hasattr(standing_platform, 'start_x'):  # Horizontal platform
            platform_velocity = standing_platform.move_speed * (dt / 1000.0) * standing_platform.direction
            new_x = self.player.x + platform_velocity
            self.player.check_collision(new_x, self.player.y)
            if platform_velocity < 0:
                if not (self.player.top_left or self.player.bottom_left):
                    self.player.x = new_x
            elif platform_velocity > 0:
                if not (self.player.top_right or self.player.bottom_right):
                    self.player.x = new_x

    def check_still_on_platform(self, standing_platform):
        """
        Check if player is still on the given platform and update last_platform

        Args:
            standing_platform: The platform to check

        Returns:
            tuple: (on_moving_platform, updated_standing_platform)
        """
        on_moving_platform = False
        if standing_platform:
            player_bottom = self.player.y + self.player.cheight / 2
            platform_top = standing_platform.get_y() - standing_platform.get_height() / 2

            # Check vertical alignment AND horizontal overlap
            vertically_aligned = abs(player_bottom - platform_top) <= 2
            horizontally_on_platform = standing_platform.intersects(
                self.player.x, self.player.y,
                self.player.cwidth, self.player.cheight
            )

            if vertically_aligned and horizontally_on_platform:
                on_moving_platform = True
                self.player.last_platform = standing_platform
            else:
                standing_platform = None
                self.player.last_platform = None

        # Also check if we're still on last frame's platform
        if not on_moving_platform and self.player.last_platform:
            player_bottom = self.player.y + self.player.cheight / 2
            platform_top = self.player.last_platform.get_y() - self.player.last_platform.get_height() / 2

            # Check vertical alignment AND horizontal overlap
            vertically_aligned = abs(player_bottom - platform_top) <= 2
            horizontally_on_platform = self.player.last_platform.intersects(
                self.player.x, self.player.y,
                self.player.cwidth, self.player.cheight
            )

            if vertically_aligned and horizontally_on_platform:
                on_moving_platform = True
                standing_platform = self.player.last_platform
            else:
                self.player.last_platform = None

        return on_moving_platform, standing_platform
