import pygame
import os
from paths import asset
from entities.animation import Animation


class Coin:
    """Collectible coin entity"""

    def __init__(self, tilemap, color="blue"):
        self.tilemap = tilemap

        # Position
        self.x = 0
        self.y = 0

        # Size
        self.width = 30
        self.height = 30

        # State
        self.is_on_screen = True
        self.has_played_sound = False

        # Animation
        self.animation = Animation()
        self.sprites = []
        self._load_sprites(color)

    def _load_sprites(self, color):
        """Load coin sprite sheet"""
        sprite_path = asset(f"sprites/{color}Coin.gif")

        if not os.path.exists(sprite_path):
            print(f"Error: Could not find {color}Coin.gif")
            return

        try:
            sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
            sprite_width, sprite_height = 30, 30
            num_frames = 8

            self.sprites = [
                sprite_sheet.subsurface((i * sprite_width, 0, sprite_width, sprite_height)).copy()
                for i in range(num_frames)
            ]

            self.animation.set_frames(self.sprites)
            self.animation.set_delay(75)
        except Exception as e:
            print(f"Error loading coin sprites: {e}")

    def set_position(self, x, y):
        """Set the coin's position"""
        self.x, self.y = x, y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def player_got(self, audio_manager):
        """Called when player collects the coin"""
        self.is_on_screen = False
        if not self.has_played_sound:
            audio_manager.play_sound("coin")
            self.has_played_sound = True

    def update(self, dt):
        """Update coin animation"""
        self.animation.update(dt)

    def draw(self, surface):
        """Draw the coin if still on screen"""
        if not self.is_on_screen:
            return

        image = self.animation.get_image()
        if image is None:
            return

        draw_x = int(self.x - self.width / 2 + self.tilemap.get_x())
        draw_y = int(self.y - self.height / 2 + self.tilemap.get_y())
        surface.blit(image, (draw_x, draw_y))
