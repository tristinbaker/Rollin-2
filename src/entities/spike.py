import pygame
import os


class Spike:
    """Damaging spike entity"""

    def __init__(self, tilemap):
        self.tilemap = tilemap

        # Position
        self.x = 0
        self.y = 0

        # Size
        self.width = 32
        self.height = 32

        # Load sprite
        self.sprite = None
        self._load_sprite()

    def _load_sprite(self):
        """Load spike sprite"""
        sprite_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "../../assets/sprites/spike.png")
        )

        if not os.path.exists(sprite_path):
            print("Error: Could not find spike.png")
            return

        try:
            self.sprite = pygame.image.load(sprite_path).convert_alpha()
        except Exception as e:
            print(f"Error loading spike sprite: {e}")

    def set_position(self, x, y):
        """Set the spike's position"""
        self.x, self.y = x, y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def draw(self, surface):
        """Draw the spike"""
        if self.sprite is None:
            return

        draw_x = int(self.x - self.width / 2 + self.tilemap.get_x())
        draw_y = int(self.y - self.height / 2 + self.tilemap.get_y())
        surface.blit(self.sprite, (draw_x, draw_y))
