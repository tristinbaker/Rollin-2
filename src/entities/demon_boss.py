import pygame
import os
from paths import asset
import math
from entities.enemy import Enemy
from entities.animation import Animation


FRAME_W = 64
FRAME_H = 64

IDLE_ROW    = 0; IDLE_FRAMES    = 4
WALK_ROW    = 1; WALK_FRAMES    = 4
ATTACK_ROW  = 3; ATTACK_FRAMES  = 7  # punch combo — projectile animation

ATTACK_COOLDOWN      = 2000   # ms between attacks
ATTACK_FRAME_DELAY   = 120    # ms per attack frame (~840ms total)
IDLE_FRAME_DELAY     = 200    # ms per idle frame
WALK_FRAME_DELAY     = 120    # ms per walk frame
PROJECTILE_SPAWN_FRAME = 4    # fire projectile on this frame index
MOVE_SPEED             = 0.6  # pixels per frame toward player
MIN_CHASE_DIST         = 55   # stop closing in once this close

MAX_HP = 10


class DemonBoss(Enemy):
    def __init__(self, tilemap):
        super().__init__(tilemap)

        self.width  = 64
        self.height = 64
        self.collision_width  = 36
        self.collision_height = 56

        self.hp    = MAX_HP
        self.state = "idle"   # "idle" | "attacking" | "dead"

        self.idle_anim   = Animation()
        self.walk_anim   = Animation()
        self.attack_anim = Animation()
        self.animation   = self.idle_anim

        self._idle_frames   = []
        self._walk_frames   = []
        self._attack_frames = []

        self.attack_timer        = ATTACK_COOLDOWN
        self.projectile_spawned  = False
        self.invincible_timer    = 0

        self._load_sprites()

    # ------------------------------------------------------------------
    # Sprites
    # ------------------------------------------------------------------

    def _load_sprites(self):
        path = asset("sprites/demon.png")
        if not os.path.exists(path):
            print("DemonBoss: demon.png not found")
            return

        sheet = pygame.image.load(path).convert_alpha()

        self._idle_frames   = self._extract_row(sheet, IDLE_ROW,   IDLE_FRAMES)
        self._walk_frames   = self._extract_row(sheet, WALK_ROW,   WALK_FRAMES)
        self._attack_frames = self._extract_row(sheet, ATTACK_ROW, ATTACK_FRAMES)

        self.idle_anim.set_frames(self._idle_frames)
        self.idle_anim.set_delay(IDLE_FRAME_DELAY)

        self.walk_anim.set_frames(self._walk_frames)
        self.walk_anim.set_delay(WALK_FRAME_DELAY)

        self.attack_anim.set_frames(self._attack_frames)
        self.attack_anim.set_delay(ATTACK_FRAME_DELAY)

        self.animation = self.idle_anim

    def _extract_row(self, sheet, row, count):
        return [
            sheet.subsurface((col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H)).copy()
            for col in range(count)
        ]

    # ------------------------------------------------------------------
    # State management
    # ------------------------------------------------------------------

    def _start_attack(self):
        self.state = "attacking"
        self.attack_anim.set_frames(self._attack_frames)   # resets played_once and frame index
        self.animation = self.attack_anim
        self.projectile_spawned = False

    def _end_attack(self):
        self.state = "idle"
        self.attack_timer = ATTACK_COOLDOWN
        # animation selection is handled each frame in update()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def take_damage(self):
        """Called externally when the boss is hit. Returns True if damage landed."""
        if self.invincible_timer > 0 or self.state == "dead":
            return False
        self.hp -= 1
        self.invincible_timer = 600
        if self.hp <= 0:
            self.state = "dead"
        return True

    def is_dead(self):
        return self.state == "dead"

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt, projectiles):
        """
        Args:
            dt: delta time in ms
            projectiles: list — new BossProjectile objects are appended here
        """
        if self.state == "dead":
            return

        self.animation.update(dt)

        if self.invincible_timer > 0:
            self.invincible_timer = max(0, self.invincible_timer - dt)

        # Homing movement — float toward the player in any direction
        player_x = 160 - self.tilemap.get_x()
        player_y = 120 - self.tilemap.get_y()
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy) or 1.0
        is_moving = dist > MIN_CHASE_DIST
        if is_moving:
            self.x += (dx / dist) * MOVE_SPEED
            self.y += (dy / dist) * MOVE_SPEED

        # Drive animation: attack anim only while attacking; walk/idle otherwise
        if self.state != "attacking":
            target_anim = self.walk_anim if is_moving else self.idle_anim
            if self.animation is not target_anim:
                self.animation = target_anim

        if self.state == "idle":
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self._start_attack()

        elif self.state == "attacking":
            if (not self.projectile_spawned
                    and self.attack_anim.current_frame >= PROJECTILE_SPAWN_FRAME):
                self._spawn_projectile(projectiles)
                self.projectile_spawned = True

            if self.attack_anim.has_played_once():
                self._end_attack()

    def _spawn_projectile(self, projectiles):
        from entities.boss_projectile import BossProjectile
        # Estimate player position from tilemap offset
        player_x = 160 - self.tilemap.get_x()
        player_y = 120 - self.tilemap.get_y()
        proj = BossProjectile(self.tilemap, self.x, self.y, player_x, player_y)
        projectiles.append(proj)

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface):
        image = self.animation.get_image()
        if image is None:
            return

        # Blink when invincible
        if self.invincible_timer > 0 and (int(self.invincible_timer / 80) % 2 == 0):
            return

        # Face toward the player (sprite naturally faces left)
        player_x = 160 - self.tilemap.get_x()
        if player_x > self.x:
            image = pygame.transform.flip(image, True, False)

        draw_x = int(self.x - self.width  / 2 + self.tilemap.get_x())
        draw_y = int(self.y - self.height / 2 + self.tilemap.get_y())
        surface.blit(image, (draw_x, draw_y))
