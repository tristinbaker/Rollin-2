import pygame
import os
from paths import asset
from entities.animation import Animation
from tilemap.tile import Tile

FRAME_W = 96
FRAME_H = 96

WALK_FRAMES  = 6
RUN_FRAMES   = 8
SNEER_FRAMES = 6

WALK_SPEED   = 1.04
RUN_SPEED    = 1.56
PATROL_SPEED = 0.52
VISUAL_SCALE = 1.4
GRAVITY      = 0.4
JUMP_VY      = -12.0

SNEER_DELAY = 150
WALK_DELAY  = 100
RUN_DELAY   = 70

PATROL_LEFT  = 66  * 32 + 16
PATROL_RIGHT = 119 * 32 + 16
SPAWN_X = 79 * 32 + 16
SPAWN_Y = 17 * 32 - 48

CHASE_ACTIVATE   = 10 * 32
WALK_THRESHOLD   = 8  * 32
CHASE_DEACTIVATE = 15 * 32


class Level5Boss:
    def __init__(self, tilemap):
        self.tilemap = tilemap
        self.x = float(SPAWN_X)
        self.y = float(SPAWN_Y)
        self.width  = int(FRAME_W * VISUAL_SCALE)
        self.height = int(FRAME_H * VISUAL_SCALE)
        self.collision_width  = 40
        self.collision_height = 56

        self._state = "patrol"
        self._patrol_dir = 1
        self._facing_right = True
        self.vy = 0.0
        self.on_ground = False

        self.walk_anim  = Animation()
        self.run_anim   = Animation()
        self.sneer_anim = Animation()
        self.animation  = self.sneer_anim

        self._load_sprites()

    def _load_sprites(self):
        base = asset("sprites/boss")

        scaled_w = int(FRAME_W * VISUAL_SCALE)
        scaled_h = int(FRAME_H * VISUAL_SCALE)

        def load_sheet(name, num_frames):
            path = os.path.join(base, name)
            if not os.path.exists(path):
                print(f"Level5Boss: missing {name}")
                return []
            sheet = pygame.image.load(path).convert_alpha()
            frames = [sheet.subsurface((i * FRAME_W, 0, FRAME_W, FRAME_H)).copy()
                      for i in range(num_frames)]
            return [pygame.transform.scale(f, (scaled_w, scaled_h)) for f in frames]

        walk_frames  = load_sheet("Demon_Boss_walk.png",  WALK_FRAMES)
        run_frames   = load_sheet("Demon_Boss_run.png",   RUN_FRAMES)
        sneer_frames = load_sheet("Demon_Boss_sneer.png", SNEER_FRAMES)

        if walk_frames:
            self.walk_anim.set_frames(walk_frames)
            self.walk_anim.set_delay(WALK_DELAY)
        if run_frames:
            self.run_anim.set_frames(run_frames)
            self.run_anim.set_delay(RUN_DELAY)
        if sneer_frames:
            self.sneer_anim.set_frames(sneer_frames)
            self.sneer_anim.set_delay(SNEER_DELAY)
            self.animation = self.sneer_anim

    def get_x(self): return self.x
    def get_y(self): return self.y

    def _apply_gravity(self, dt):
        self.vy += GRAVITY * (dt / 16.67)
        self.y += self.vy * (dt / 16.67)

        ts = self.tilemap.tile_size
        feet_y = self.y + self.collision_height / 2
        feet_row = int(feet_y / ts)
        for col_offset in (-self.collision_width // 4, self.collision_width // 4):
            check_col = int((self.x + col_offset) / ts)
            if self.tilemap.get_type(feet_row, check_col) == Tile.BLOCKED:
                self.y = feet_row * ts - self.collision_height / 2
                self.vy = 0.0
                self.on_ground = True
                return

        self.on_ground = False

    def _try_jump(self, move_dir):
        if not self.on_ground:
            return
        ts = self.tilemap.tile_size
        ahead_x = self.x + move_dir * (self.collision_width / 2 + 4)
        # Check at waist level — catches walls the boss would walk into
        waist_row = int((self.y + self.collision_height / 4) / ts)
        ahead_col = int(ahead_x / ts)
        if self.tilemap.get_type(waist_row, ahead_col) == Tile.BLOCKED:
            self.vy = JUMP_VY
            self.on_ground = False

    def update(self, dt):
        player_x = 160 - self.tilemap.get_x()
        player_y = 120 - self.tilemap.get_y()
        dx = player_x - self.x
        dist = abs(dx)

        if self._state == "patrol":
            if dist <= CHASE_ACTIVATE:
                self._state = "chase"
            else:
                self._do_patrol(dt)
                self._set_anim(self.sneer_anim)
        else:
            if dist > CHASE_DEACTIVATE:
                self._state = "patrol"
            else:
                self._facing_right = dx > 0
                move_dir = 1 if dx > 0 else -1
                if dist > WALK_THRESHOLD:
                    speed = RUN_SPEED
                    target_anim = self.run_anim
                else:
                    speed = WALK_SPEED
                    target_anim = self.walk_anim
                self._set_anim(target_anim)
                if abs(dx) > 2:
                    self._try_jump(move_dir)
                    move = move_dir * speed * (dt / 16.67)
                    self.x = max(PATROL_LEFT, min(PATROL_RIGHT, self.x + move))

        self._apply_gravity(dt)
        self.animation.update(dt)

    def _do_patrol(self, dt):
        self._try_jump(self._patrol_dir)
        self.x += self._patrol_dir * PATROL_SPEED * (dt / 16.67)
        if self.x >= PATROL_RIGHT:
            self.x = float(PATROL_RIGHT)
            self._patrol_dir = -1
        elif self.x <= PATROL_LEFT:
            self.x = float(PATROL_LEFT)
            self._patrol_dir = 1
        self._facing_right = self._patrol_dir > 0

    def _set_anim(self, anim):
        if self.animation is not anim:
            self.animation = anim

    def draw(self, surface):
        image = self.animation.get_image()
        if image is None:
            return
        if self._facing_right:
            image = pygame.transform.flip(image, True, False)
        draw_x = int(self.x - self.width / 2 + self.tilemap.get_x())
        draw_y = int(self.y + self.collision_height / 2 - self.height + self.tilemap.get_y())
        surface.blit(image, (draw_x, draw_y))
