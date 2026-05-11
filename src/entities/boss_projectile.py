import pygame
import math


SPEED  = 2.5    # pixels per frame (at ~60 fps)
RADIUS = 6      # visual radius
COLOR_OUTER = (180, 40, 220)
COLOR_INNER = (255, 160, 255)


class BossProjectile:
    def __init__(self, tilemap, start_x, start_y, target_x, target_y):
        self.tilemap = tilemap
        self.x = float(start_x)
        self.y = float(start_y)

        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.sqrt(dx * dx + dy * dy) or 1.0
        self.vx = (dx / dist) * SPEED
        self.vy = (dy / dist) * SPEED

        self.collision_width  = RADIUS * 2
        self.collision_height = RADIUS * 2
        self.active = True

    # Needed for player.hit_spike() compatibility
    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        # Deactivate once it has scrolled off the left edge of the world
        if self.x < -200:
            self.active = False

    def draw(self, surface):
        sx = int(self.x + self.tilemap.get_x())
        sy = int(self.y + self.tilemap.get_y())
        pygame.draw.circle(surface, COLOR_OUTER, (sx, sy), RADIUS)
        pygame.draw.circle(surface, COLOR_INNER, (sx, sy), RADIUS // 2)
