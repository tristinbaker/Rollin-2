import pygame
import os
from entities.animation import Animation

class Heart:
    """Collectible heart entity"""
    def __init__(self, x, y, tilemap, sprite_path=None):
        self.tilemap = tilemap
        # Center heart in 32x32 tile, add 32px y offset
        self.x = x + 8
        self.y = y + 32
        self.width = 16
        self.height = 16
        self.is_on_screen = True
        self.has_played_sound = False
        self.animation = Animation()
        self.sprites = []
        self._load_sprites(sprite_path)


    def _load_sprites(self, sprite_path):
        if sprite_path is None:
            sprite_path = os.path.normpath(
                os.path.join(os.path.dirname(__file__),
                             "../../assets/sprites/heart.png")
            )
        if not os.path.exists(sprite_path):
            print(f"Error: Could not find heart sprite at {sprite_path}")
            return
        try:
            sheet = pygame.image.load(sprite_path).convert_alpha()
            # 3 frames, 16x16 each
            self.sprites = [sheet.subsurface((i * 16, 0, 16, 16)).copy() for i in range(3)]
            self.animation.set_frames(self.sprites)
            self.animation.set_delay(300)  # Slower animation
        except Exception as e:
            print(f"Error loading heart sprite: {e}")

    def update(self, level_state):
        if not self.is_on_screen:
            return
        # Animate heart
        self.animation.update(16.67)  # Assume ~60 FPS
        player = level_state.player
        # Simple AABB collision
        if (player.x < self.x + self.width and
            player.x + player.width > self.x and
            player.y < self.y + self.height and
            player.y + player.height > self.y):
            # Use get_hp() and assume max HP is 3
            player_hp = player.get_hp() if hasattr(player, 'get_hp') else getattr(player, 'hp', 3)
            max_hp = 3
            coin_value = getattr(player, 'coin_value', 100)
            audio_manager = getattr(level_state.gsm, 'audio_manager', None)
            if player_hp < max_hp:
                if hasattr(player, 'hp'):
                    player.hp += 1
            else:
                # Always increment global score
                if hasattr(level_state, 'gsm') and hasattr(level_state.gsm, 'add_score'):
                    level_state.gsm.add_score(coin_value)
            self.is_on_screen = False
            if audio_manager and not self.has_played_sound:
                audio_manager.play_sound("health_pickup")
                self.has_played_sound = True

    def draw(self, surface):
        if self.is_on_screen and self.sprites:
            # Draw at tilemap position adjusted for camera
            draw_x = self.x + self.tilemap.x
            draw_y = self.y + self.tilemap.y
            image = self.animation.get_image()
            surface.blit(image, (draw_x, draw_y))