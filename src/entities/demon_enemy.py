import pygame
import os
from paths import asset
import math
from entities.enemy import Enemy
from entities.animation import Animation

FRAME_W = 64
FRAME_H = 64

IDLE_ROW = 0; IDLE_FRAMES = 4
WALK_ROW = 1; WALK_FRAMES = 4

IDLE_FRAME_DELAY  = 200
WALK_FRAME_DELAY  = 120
MOVE_SPEED        = 1.0
MIN_CHASE_DIST    = 50
ATTACK_COOLDOWN   = 5000   # ms between shots


class DemonEnemy(Enemy):
    def __init__(self, tilemap):
        super().__init__(tilemap)
        self.width  = 64
        self.height = 64
        self.collision_width  = 36
        self.collision_height = 52

        self.idle_anim = Animation()
        self.walk_anim = Animation()
        self.animation = self.idle_anim

        self._facing_left = True
        self._attack_timer = 0.0
        self._idle_frames = []
        self._walk_frames = []
        self._load_sprites()

    def _load_sprites(self):
        path = asset("sprites/demon.png")
        if not os.path.exists(path):
            print("DemonEnemy: demon.png not found")
            return
        sheet = pygame.image.load(path).convert_alpha()
        self._idle_frames = [
            sheet.subsurface((c * FRAME_W, IDLE_ROW * FRAME_H, FRAME_W, FRAME_H)).copy()
            for c in range(IDLE_FRAMES)
        ]
        self._walk_frames = [
            sheet.subsurface((c * FRAME_W, WALK_ROW * FRAME_H, FRAME_W, FRAME_H)).copy()
            for c in range(WALK_FRAMES)
        ]
        self.idle_anim.set_frames(self._idle_frames)
        self.idle_anim.set_delay(IDLE_FRAME_DELAY)
        self.walk_anim.set_frames(self._walk_frames)
        self.walk_anim.set_delay(WALK_FRAME_DELAY)
        self.animation = self.idle_anim

    def update(self, dt, spikes=None, moving_platforms=None, projectiles=None):
        player_x = 160 - self.tilemap.get_x()
        player_y = 120 - self.tilemap.get_y()
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy) or 1.0

        is_moving = dist > MIN_CHASE_DIST
        if is_moving:
            self.x += (dx / dist) * MOVE_SPEED
            self.y += (dy / dist) * MOVE_SPEED

        target_anim = self.walk_anim if is_moving else self.idle_anim
        if self.animation is not target_anim:
            self.animation = target_anim
        self.animation.update(dt)

        self._facing_left = player_x <= self.x

        # Fire a projectile toward the player on cooldown
        if projectiles is not None:
            self._attack_timer -= dt
            if self._attack_timer <= 0:
                self._attack_timer = ATTACK_COOLDOWN
                from entities.boss_projectile import BossProjectile
                projectiles.append(BossProjectile(self.tilemap, self.x, self.y, player_x, player_y))

    def draw(self, surface):
        image = self.animation.get_image()
        if image is None:
            return
        if not self._facing_left:
            image = pygame.transform.flip(image, True, False)
        draw_x = int(self.x - self.width  / 2 + self.tilemap.get_x())
        draw_y = int(self.y - self.height / 2 + self.tilemap.get_y())
        surface.blit(image, (draw_x, draw_y))
