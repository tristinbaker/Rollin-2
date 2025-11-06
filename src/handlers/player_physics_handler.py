"""
PlayerPhysicsHandler - Handles player physics like gravity, movement, and swimming
"""


class PlayerPhysicsHandler:
    """Handles physics calculations for the player"""

    def __init__(self, player):
        self.player = player

    def apply_horizontal_movement(self, move_mult, max_speed_mult, stop_mult, on_horizontal_platform=False):
        """
        Apply horizontal movement based on input

        Args:
            move_mult: Movement speed multiplier
            max_speed_mult: Max speed multiplier
            stop_mult: Stop/deceleration multiplier
            on_horizontal_platform: Whether player is on horizontal moving platform
        """
        if self.player.left:
            self.player.dx -= self.player.move_speed * move_mult
            self.player.dx = max(self.player.dx, -self.player.max_speed * max_speed_mult)
        elif self.player.right:
            self.player.dx += self.player.move_speed * move_mult
            self.player.dx = min(self.player.dx, self.player.max_speed * max_speed_mult)
        else:
            # Only decelerate if not on horizontal platform (prevents sliding)
            if not on_horizontal_platform:
                if self.player.dx > 0:
                    self.player.dx -= self.player.stop_speed * stop_mult
                    if self.player.dx < 0:
                        self.player.dx = 0
                elif self.player.dx < 0:
                    self.player.dx += self.player.stop_speed * stop_mult
                    if self.player.dx > 0:
                        self.player.dx = 0
            else:
                # On horizontal platform - stop immediately
                self.player.dx = 0

    def apply_gravity(self, on_vertical_platform=False):
        """
        Apply gravity/swimming physics

        Args:
            on_vertical_platform: Whether player is on a vertical moving platform
        """
        if self.player.underwater:
            self._apply_underwater_physics()
        elif not self.player.on_ground and not on_vertical_platform:
            self._apply_air_physics()
        else:
            self.player.dy = 0

    def _apply_underwater_physics(self):
        """Apply underwater swimming and sinking physics"""
        if self.player.jumping and not self.player.has_swam:
            # Swimming upward
            swim_multiplier = 1.0
            if self.player.up:
                swim_multiplier = 1.5
            elif self.player.down:
                swim_multiplier = 0.5

            self.player.dy = self.player.swim_speed * swim_multiplier
            self.player.has_swam = True
        elif not self.player.jumping:
            self.player.has_swam = False
            self.player.dy += self.player.fall_speed * 0.5
        else:
            self.player.dy += self.player.fall_speed * 0.5

        # Water resistance
        self.player.dy *= 0.98
        # Clamp speeds
        self.player.dy = max(self.player.dy, -6.0)
        self.player.dy = min(self.player.dy, self.player.underwater_sink_speed)

    def _apply_air_physics(self):
        """Apply normal air physics (falling/gliding)"""
        if self.player.gliding and self.player.dy > 0:
            self.player.dy += self.player.fall_speed * 0.1
        else:
            self.player.dy += self.player.fall_speed
        self.player.dy = min(self.player.dy, self.player.max_fall_speed)

    def get_physics_multipliers(self):
        """
        Get physics multipliers based on underwater state

        Returns:
            tuple: (move_mult, max_speed_mult, stop_mult)
        """
        if self.player.underwater:
            return 0.6, 0.7, 0.5
        else:
            return 1.0, 1.0, 1.0
