import pygame
import os
from entities.enemy import Enemy
from tilemap.tile import Tile


class Slime(Enemy):
    """Slime enemy - animated blob enemy"""

    def __init__(self, tilemap):
        super().__init__(tilemap)

        # Slime size (32x32 per frame)
        self.width = 32
        self.height = 32
        self.cwidth = 24  # Collision width
        self.cheight = 24  # Collision height

        # Movement
        self.speed = 0.5
        self.move_right = True  # Direction

        # Load sprites
        self._load_sprites()

    def _load_sprites(self):
        """Load slime sprite sheet"""
        sprite_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "../../assets/sprites/slime.png")
        )

        if not os.path.exists(sprite_path):
            print("Error: Could not find slime.png")
            return

        try:
            sprite_sheet = pygame.image.load(sprite_path).convert_alpha()

            # Slime: 7 frames (32x32 each)
            sprite_width = 32
            sprite_height = 32
            num_frames = 7

            self.sprites = [
                sprite_sheet.subsurface((i * sprite_width, 0, sprite_width, sprite_height)).copy()
                for i in range(num_frames)
            ]

            self.animation.set_frames(self.sprites)
            self.animation.set_delay(100)  # 100ms per frame for smoother animation
        except Exception as e:
            print(f"Error loading slime sprites: {e}")

    def check_tile_collision(self, x, y):
        """Check if position collides with blocked tiles"""
        tile_size = self.tilemap.get_tile_size()
        tile_x = int(x / tile_size)
        tile_y = int(y / tile_size)
        return self.tilemap.get_type(tile_y, tile_x) == Tile.BLOCKED

    def check_ledge(self, x, y):
        """Check if there's a ledge (no ground) at the given position"""
        tile_size = self.tilemap.get_tile_size()
        # Check one tile below the given position
        check_y = y + tile_size
        tile_x = int(x / tile_size)
        tile_y = int(check_y / tile_size)
        # If there's no blocked tile below, it's a ledge
        return self.tilemap.get_type(tile_y, tile_x) != Tile.BLOCKED

    def check_spike_ahead(self, spikes):
        """Check if there's a spike ahead in movement direction"""
        # Check distance from edge of slime's collision box
        collision_edge = self.cwidth / 2
        buffer = 15  # Buffer to detect spike edge

        for spike in spikes:
            spike_x = spike.get_x()
            spike_y = spike.get_y()

            # Check if spike is at roughly same height
            if abs(spike_y - self.y) < 20:
                if self.move_right:
                    # Distance from right edge of slime to spike
                    distance = spike_x - (self.x + collision_edge)
                    if 0 < distance < buffer:
                        return True
                else:
                    # Distance from left edge of slime to spike
                    distance = (self.x - collision_edge) - spike_x
                    if 0 < distance < buffer:
                        return True
        return False

    def should_turn_around(self, spikes=None):
        """Check if slime should turn around (wall, ledge, or spike ahead)"""
        tile_size = self.tilemap.get_tile_size()
        buffer = 3  # Small buffer distance ahead

        if self.move_right:
            # Check right side - just slightly ahead of collision edge
            check_x = self.x + self.cwidth / 2 + buffer
            # Check for wall at current height
            if self.check_tile_collision(check_x, self.y):
                return True
            # Check for ledge (no ground below next position)
            if self.check_ledge(check_x, self.y):
                return True
        else:
            # Check left side - just slightly ahead of collision edge
            check_x = self.x - self.cwidth / 2 - buffer
            # Check for wall at current height
            if self.check_tile_collision(check_x, self.y):
                return True
            # Check for ledge (no ground below next position)
            if self.check_ledge(check_x, self.y):
                return True

        # Check for spikes ahead
        if spikes and self.check_spike_ahead(spikes):
            return True

        return False

    def update(self, dt, spikes=None, moving_platforms=None):
        """Update slime"""
        # Update animation
        super().update(dt)

        # Check if we should turn around
        if self.should_turn_around(spikes):
            self.move_right = not self.move_right

        # Move in current direction
        if self.move_right:
            self.x += self.speed
        else:
            self.x -= self.speed

    def draw(self, surface):
        """Draw the slime (with flipping based on direction)"""
        image = self.animation.get_image()
        if image is None:
            return

        # Flip sprite based on direction (facing right when moving right)
        if self.move_right:
            image = pygame.transform.flip(image, True, False)

        draw_x = int(self.x - self.width / 2 + self.tilemap.get_x())
        draw_y = int(self.y - self.height / 2 + self.tilemap.get_y())
        surface.blit(image, (draw_x, draw_y))
