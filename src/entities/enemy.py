import pygame
from entities.animation import Animation


class Enemy:
    """Base enemy class"""

    def __init__(self, tilemap):
        self.tilemap = tilemap

        # Position
        self.x = 0
        self.y = 0

        # Size (override in subclasses)
        self.width = 20
        self.height = 20

        # Animation
        self.animation = Animation()
        self.sprites = []

    def set_position(self, x, y):
        """Set the enemy's position"""
        self.x, self.y = x, y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def update(self, dt):
        """Update enemy (override in subclasses)"""
        self.animation.update(dt)

    def draw(self, surface):
        """Draw the enemy"""
        image = self.animation.get_image()
        if image is None:
            return

        draw_x = int(self.x - self.width / 2 + self.tilemap.get_x())
        draw_y = int(self.y - self.height / 2 + self.tilemap.get_y())
        surface.blit(image, (draw_x, draw_y))
