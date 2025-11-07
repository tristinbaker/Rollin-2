import pygame
import os
from entities.animation import Animation
from handlers.player_collision_handler import PlayerCollisionHandler
from handlers.player_physics_handler import PlayerPhysicsHandler
from handlers.player_platform_handler import PlayerPlatformHandler
from tilemap.tile import Tile


class Player:
    # Animation states
    IDLE = 0
    WALKING = 1
    JUMPING = 2
    FALLING = 3
    GLIDING = 4

    def __init__(self, tilemap):
        self.tilemap = tilemap

        # Position and movement
        self.x = 0
        self.y = 0
        self.dx = 0
        self.dy = 0

        # Collision box
        self.width = 20
        self.height = 20
        self.cwidth = 20
        self.cheight = 20

        # Physics constants
        self.move_speed = 0.3
        self.max_speed = 1.6
        self.stop_speed = 0.4
        self.fall_speed = 0.15
        self.max_fall_speed = 4.0
        self.jump_start = -4.8  # Reduced from -4.8 (half the jump height)
        self.stop_jump_speed = 0.3
        self.swim_speed = -2.0  # Upward swimming speed when underwater
        self.underwater_sink_speed = 1.5  # Maximum sinking speed underwater (adjust as needed)

        # State
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.jumping = False
        self.gliding = False
        self.facing_right = True
        self.on_ground = False
        self.underwater = False  # Set by level state
        self.has_swam = False  # Track if player already swam (for underwater)

        # Platform tracking
        self.last_platform = None  # Track which platform player was on last frame
        self.platform_offset_x = 0  # Player's X offset relative to platform center

        # Game state
        self.dead = False
        self.win = False
        self.hp = 3
        self.invincible_timer = 0  # Invincibility frames after taking damage
        self.invincible_duration = 1000  # 1 second of invincibility
        self.lava_death_timer = 0  # Timer for delayed lava death
        self.lava_sound_played = False  # Track if lava sound has been played

        # Collision flags
        self.top_left = False
        self.top_right = False
        self.bottom_left = False
        self.bottom_right = False

        # Animation
        self.animation = Animation()
        self.current_action = self.IDLE
        self.sprites = {}

        # Handlers
        self.collision_handler = PlayerCollisionHandler(self)
        self.physics_handler = PlayerPhysicsHandler(self)
        self.platform_handler = PlayerPlatformHandler(self)

        self._load_sprites()

    def _load_sprites(self):
        """Load player sprite sheet"""
        sprite_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../assets/sprites/playerSprites.gif"))

        if not os.path.exists(sprite_path):
            print("Error: Could not find playerSprites.gif")
            for i in range(5):
                self.sprites[i] = []
            return

        sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
        sprite_width, sprite_height = 30, 30

        self.sprites[self.IDLE] = [
            sprite_sheet.subsurface((i * sprite_width, 0, sprite_width, sprite_height)).copy()
            for i in range(2)
        ]
        self.sprites[self.WALKING] = [
            sprite_sheet.subsurface((i * sprite_width, sprite_height, sprite_width, sprite_height)).copy()
            for i in range(8)
        ]
        self.sprites[self.JUMPING] = [
            sprite_sheet.subsurface((0, sprite_height * 2, sprite_width, sprite_height)).copy()
        ]
        self.sprites[self.FALLING] = [
            sprite_sheet.subsurface((i * sprite_width, sprite_height * 3, sprite_width, sprite_height)).copy()
            for i in range(2)
        ]
        self.sprites[self.GLIDING] = [
            sprite_sheet.subsurface((i * sprite_width, sprite_height * 4, sprite_width, sprite_height)).copy()
            for i in range(2)
        ]

        self.animation.set_frames(self.sprites[self.IDLE])
        self.animation.set_delay(400)

    def set_position(self, x, y):
        self.x, self.y = x, y

    def set_left(self, left): self.left = left
    def set_right(self, right): self.right = right
    def set_up(self, up): self.up = up
    def set_down(self, down): self.down = down
    def set_jumping(self, jumping): self.jumping = jumping
    def set_gliding(self, gliding): self.gliding = gliding

    def check_collision(self, x, y):
        tile_size = self.tilemap.get_tile_size()
        x_left = int((x - self.cwidth / 2) / tile_size)
        x_right = int((x + self.cwidth / 2 - 1) / tile_size)
        y_top = int((y - self.cheight / 2) / tile_size)
        y_bottom = int((y + self.cheight / 2 - 1) / tile_size)

        self.top_left = self.tilemap.get_type(y_top, x_left) == Tile.BLOCKED
        self.top_right = self.tilemap.get_type(y_top, x_right) == Tile.BLOCKED
        self.bottom_left = self.tilemap.get_type(y_bottom, x_left) == Tile.BLOCKED
        self.bottom_right = self.tilemap.get_type(y_bottom, x_right) == Tile.BLOCKED

    def update(self, dt, audio_manager=None, moving_platforms=None):
        # Update invincibility timer
        if self.invincible_timer > 0:
            self.invincible_timer -= dt

        # Update lava death timer
        if self.lava_death_timer > 0:
            self.lava_death_timer -= dt
            if self.lava_death_timer <= 0:
                self.hp = 0
                self.dead = True

        # FIRST: Move with vertical platform if we were on one last frame
        # This prevents falling through when platform moves down faster than gravity
        if self.last_platform and hasattr(self.last_platform, 'start_y'):
            player_left = self.x - self.cwidth / 2
            player_right = self.x + self.cwidth / 2
            platform_left = self.last_platform.get_x() - self.last_platform.get_width() / 2
            platform_right = self.last_platform.get_x() + self.last_platform.get_width() / 2
            player_bottom = self.y + self.cheight / 2
            platform_top = self.last_platform.get_y() - self.last_platform.get_height() / 2

            horizontal_on = player_right > platform_left + 2 and player_left < platform_right - 2
            vertical_aligned = abs(player_bottom - platform_top) <= 5

            if horizontal_on and vertical_aligned:
                # Move with vertical platform BEFORE applying gravity
                platform_velocity_y = self.last_platform.move_speed * (dt / 1000.0) * self.last_platform.direction
                self.y += platform_velocity_y

        # Get physics multipliers and apply horizontal movement
        move_mult, max_speed_mult, stop_mult = self.physics_handler.get_physics_multipliers()
        on_horizontal_platform = self.last_platform and hasattr(self.last_platform, 'start_x')
        self.physics_handler.apply_horizontal_movement(move_mult, max_speed_mult, stop_mult, on_horizontal_platform)

        # Handle horizontal (X) collision
        next_x = self.x + self.dx

        # Handle side collision with moving platforms first
        hit_platform_side = False
        if moving_platforms and self.dx != 0:
            for platform in moving_platforms:
                player_top = self.y - self.cheight / 2
                player_bottom = self.y + self.cheight / 2
                platform_top = platform.get_y() - platform.get_height() / 2
                platform_bottom = platform.get_y() + platform.get_height() / 2

                # Check if player has vertical overlap with platform
                has_vertical_overlap = (player_bottom > platform_top + 1 and
                                       player_top < platform_bottom - 1)

                if has_vertical_overlap:
                    player_left = self.x - self.cwidth / 2
                    player_right = self.x + self.cwidth / 2
                    next_player_left = next_x - self.cwidth / 2
                    next_player_right = next_x + self.cwidth / 2
                    platform_left = platform.get_x() - platform.get_width() / 2
                    platform_right = platform.get_x() + platform.get_width() / 2

                    # Hitting right side of platform (moving left)
                    if self.dx < 0 and player_left >= platform_right - 1 and next_player_left <= platform_right:
                        self.x = platform_right + self.cwidth / 2
                        self.dx = 0
                        hit_platform_side = True
                        break
                    # Hitting left side of platform (moving right)
                    elif self.dx > 0 and player_right <= platform_left + 1 and next_player_right >= platform_left:
                        self.x = platform_left - self.cwidth / 2
                        self.dx = 0
                        hit_platform_side = True
                        break

        # Handle tile collision if no platform collision
        if not hit_platform_side:
            self.x = self.collision_handler.handle_horizontal_collision(next_x, moving_platforms)

        # Gravity
        if self.underwater:
            if self.up:
                self.dy = self.swim_speed
                self.has_swam = True
            elif self.dy < self.underwater_sink_speed:
                self.dy += self.fall_speed * 0.3
        else:
            # Apply gravity (slower when gliding)
            if self.gliding and self.dy > 0:
                # Gliding - slow fall
                if self.dy < 1.5:  # Slower max fall speed when gliding
                    self.dy += self.fall_speed * 0.3
            else:
                # Normal gravity
                if self.dy < self.max_fall_speed:
                    self.dy += self.fall_speed

        # Y collision with platforms
        standing_platform = None
        if moving_platforms and self.dy != 0:
            for platform in moving_platforms:
                player_left = self.x - self.cwidth / 2
                player_right = self.x + self.cwidth / 2
                platform_left = platform.get_x() - platform.get_width() / 2
                platform_right = platform.get_x() + platform.get_width() / 2

                # Check horizontal overlap (player must be inside platform horizontally)
                horizontal_overlap = (player_right > platform_left + 2 and
                                    player_left < platform_right - 2)

                if horizontal_overlap:
                    player_bottom = self.y + self.cheight / 2
                    player_top = self.y - self.cheight / 2
                    next_player_bottom = self.y + self.dy + self.cheight / 2
                    next_player_top = self.y + self.dy - self.cheight / 2
                    platform_top = platform.get_y() - platform.get_height() / 2
                    platform_bottom = platform.get_y() + platform.get_height() / 2

                    # Landing on top
                    if self.dy > 0 and player_bottom <= platform_top + 1 and next_player_bottom >= platform_top - 1:
                        self.y = platform_top - self.cheight / 2
                        self.dy = 0
                        standing_platform = platform
                        break
                    # Hitting bottom (head bonk)
                    elif self.dy < 0 and player_top >= platform_bottom - 1 and next_player_top <= platform_bottom + 1:
                        self.y = platform_bottom + self.cheight / 2
                        self.dy = 0
                        break

        # Y collision with tiles
        next_y = self.y + self.dy
        self.check_collision(self.x, next_y)
        if self.dy < 0:  # upward
            if self.top_left or self.top_right:
                self.dy = 0
                tile_size = self.tilemap.get_tile_size()
                self.y = int(self.y / tile_size) * tile_size + self.cheight / 2
        elif self.dy > 0:  # downward
            if self.bottom_left or self.bottom_right:
                self.dy = 0
                tile_size = self.tilemap.get_tile_size()
                self.y = (int(self.y / tile_size) + 1) * tile_size - self.cheight / 2

        # Apply Y velocity
        self.y += self.dy

        # Check if still on platform
        on_moving_platform = False
        if standing_platform:
            player_left = self.x - self.cwidth / 2
            player_right = self.x + self.cwidth / 2
            platform_left = standing_platform.get_x() - standing_platform.get_width() / 2
            platform_right = standing_platform.get_x() + standing_platform.get_width() / 2
            player_bottom = self.y + self.cheight / 2
            platform_top = standing_platform.get_y() - standing_platform.get_height() / 2

            # Check both horizontal and vertical alignment
            horizontal_on = player_right > platform_left + 2 and player_left < platform_right - 2
            vertical_aligned = abs(player_bottom - platform_top) <= 5

            if horizontal_on and vertical_aligned:
                on_moving_platform = True
                self.last_platform = standing_platform
            else:
                # Only clear if player walked off (not just tolerance issue)
                if not horizontal_on:
                    self.last_platform = None
                standing_platform = None
        elif self.last_platform:
            # Check if still on last frame's platform
            player_left = self.x - self.cwidth / 2
            player_right = self.x + self.cwidth / 2
            platform_left = self.last_platform.get_x() - self.last_platform.get_width() / 2
            platform_right = self.last_platform.get_x() + self.last_platform.get_width() / 2
            player_bottom = self.y + self.cheight / 2
            platform_top = self.last_platform.get_y() - self.last_platform.get_height() / 2

            horizontal_on = player_right > platform_left + 2 and player_left < platform_right - 2
            vertical_aligned = abs(player_bottom - platform_top) <= 5

            if horizontal_on and vertical_aligned:
                on_moving_platform = True
                standing_platform = self.last_platform
            else:
                if not horizontal_on:
                    self.last_platform = None

        # Ground detection
        self.check_collision(self.x, self.y + 1)
        self.on_ground = (self.bottom_left or self.bottom_right) or on_moving_platform

        # Move with horizontal platform (vertical already done at start of update)
        if standing_platform and self.on_ground and hasattr(standing_platform, 'start_x'):
            platform_velocity = standing_platform.move_speed * (dt / 1000.0) * standing_platform.direction
            new_x = self.x + platform_velocity
            self.check_collision(new_x, self.y)
            if platform_velocity < 0:
                if not (self.top_left or self.bottom_left):
                    self.x = new_x
            elif platform_velocity > 0:
                if not (self.top_right or self.bottom_right):
                    self.x = new_x

        # Jumping (only for non-underwater levels)
        if not self.underwater:
            if self.jumping and self.on_ground:
                self.dy = self.jump_start
                self.on_ground = False
                # Clear platform tracking when jumping
                self.last_platform = None
                # Play jump sound
                if audio_manager:
                    audio_manager.play_sound("jump")

        # Animation
        self._update_animation()
        self.animation.update(dt)

        # Facing
        if self.left:
            self.facing_right = False
        elif self.right:
            self.facing_right = True

        # Death/win conditions
        tm_width, tm_height = self.tilemap.get_width(), self.tilemap.get_height()
        # Only set dead to True if falling off bottom (not left side - that has invisible wall)
        if self.y > tm_height:
            self.dead = True
        self.win = self.x > tm_width

    def _set_action(self, action, frames, delay):
        if self.current_action != action:
            self.current_action = action
            self.animation.set_frames(frames)
            self.animation.set_delay(delay)

    def _update_animation(self):
        """Stable animation logic"""
        EPS = 0.05  # movement threshold

        if not self.on_ground:
            if self.dy < 0:
                self._set_action(self.JUMPING, self.sprites[self.JUMPING], -1)
            elif self.gliding and self.dy > 0 and not self.underwater:
                # Only show gliding animation if not underwater
                self._set_action(self.GLIDING, self.sprites[self.GLIDING], 200)
            else:
                self._set_action(self.FALLING, self.sprites[self.FALLING], 100)
            return

        moving = abs(self.dx) > EPS
        if moving:
            self._set_action(self.WALKING, self.sprites[self.WALKING], 100)
        else:
            self._set_action(self.IDLE, self.sprites[self.IDLE], 400)

    def draw(self, surface):
        # Flash when invincible
        if self.invincible_timer > 0:
            # Flash every 100ms
            if int(self.invincible_timer / 100) % 2 == 0:
                return  # Don't draw on even frames

        image = self.animation.get_image()
        if image is None:
            return
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)

        draw_x = int(self.x - image.get_width() / 2 + self.tilemap.get_x())
        draw_y = int(self.y - image.get_height() / 2 + self.tilemap.get_y())
        surface.blit(image, (draw_x, draw_y))

    def get_x(self): return self.x
    def get_y(self): return self.y
    def is_dead(self): return self.dead
    def has_won(self): return self.win

    def got_coin(self, coin):
        """Check if player collected a coin"""
        return (coin.get_x() <= (self.x + 15) and
                coin.get_x() >= (self.x - 15) and
                coin.get_y() <= (self.y + 15) and
                coin.get_y() >= (self.y - 15))

    def hit_spike(self, spike):
        """Check if player hit a spike or enemy"""
        # Use collision dimensions if available (for accurate spike collision)
        if hasattr(spike, 'collision_width') and hasattr(spike, 'collision_height'):
            offset_x = getattr(spike, 'collision_offset_x', 0)
            spike_left = spike.get_x() - spike.collision_width / 2 + offset_x
            spike_right = spike.get_x() + spike.collision_width / 2 + offset_x
            spike_top = spike.get_y() - spike.collision_height / 2
            spike_bottom = spike.get_y() + spike.collision_height / 2

            player_left = self.x - self.cwidth / 2
            player_right = self.x + self.cwidth / 2
            player_top = self.y - self.cheight / 2
            player_bottom = self.y + self.cheight / 2

            # AABB collision check
            return (player_right > spike_left and
                    player_left < spike_right and
                    player_bottom > spike_top and
                    player_top < spike_bottom)
        else:
            # Fallback for enemies without collision dimensions
            buffer = 24
            return (spike.get_x() <= (self.x + buffer) and
                    spike.get_x() >= (self.x - buffer) and
                    spike.get_y() <= (self.y + buffer) and
                    spike.get_y() >= (self.y - buffer))

    def take_damage(self, spike_x=None):
        """Take damage from a spike"""
        if self.invincible_timer <= 0:
            self.hp -= 1
            self.invincible_timer = self.invincible_duration

            # Knockback effect
            if spike_x is not None:
                # Knock player away from spike
                if self.x < spike_x:
                    self.dx = -3  # Knock left
                else:
                    self.dx = 3   # Knock right

            # Check if dead
            if self.hp <= 0:
                self.dead = True
            return True
        return False

    def touch_lava(self):
        """Start the delayed death sequence from lava"""
        if self.lava_death_timer == 0:
            self.lava_death_timer = 150  # 200ms delay before death
            self.lava_sound_played = False  # Reset sound flag
            return True  # Signal that sound should be played
        return False  # Already touched lava, don't play sound again

    def get_hp(self):
        return self.hp

    def reset_hp(self):
        """Reset HP to full (called at start of level)"""
        self.hp = 3
        self.invincible_timer = 0

    def is_invincible(self):
        return self.invincible_timer > 0
