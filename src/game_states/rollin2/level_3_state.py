"""
Level 3 State for Rollin 2
Setup is similar to Level 1 and Level 2
"""
import pygame
import os
from game_states.level_state import LevelState
from tilemap.tilemap import TileMap
from entities.player import Player

class Level3State(LevelState):
    def __init__(self, gsm):
        super().__init__(gsm, hud_color=(255, 255, 255))  # White HUD

    def init(self):
        # Clear entity lists (in case reinitializing)
        self.coins = []
        self.spikes = []
        self.lava = []
        self.enemies = []
        self.moving_platforms = []
        self.total_coins = 0
        self.max_coins = 0
        self.level_start_score = self.gsm.get_score()
        self.underwater = False

        # Load parallax background (customize as needed)
        self.load_parallax_layers([
            ("background_day1.png", 0.0),
            ("background_day2.png", 0.5),
            ("background_day3.png", 0.95),
        ], subfolder="level_1")

        # Create tilemap (using Tiled format with 32x32 tiles)
        self.tilemap = TileMap(32)
        self.tilemap.load_map("maps/level_3.tmj")

        # Create player
        self.player = Player(self.tilemap)
        spawn_x, spawn_y = self.tilemap.find_spawn_position()
        self.player.set_position(spawn_x, spawn_y)
        self.player.reset_hp()

        # Spawn entities from Tiled layers
        self.spawn_coins_from_layer()
        self.spawn_spikes_from_layer()
        self.spawn_lava_from_layer()
        self.spawn_slimes_from_layer()
        self.spawn_bats_from_layer()
        self.spawn_wasps_from_layer()
        self.spawn_vertical_platforms_from_layer()
        self.spawn_opposite_vertical_platforms_from_layer()
        self.spawn_horizontal_platforms_from_layer()
        self.spawn_hearts_from_layer()

        # Set initial camera position
        self.tilemap.set_position_immediate(
            160 - self.player.get_x(),
            120 - self.player.get_y()
        )

        # Load and play level music
        audio = self.gsm.audio_manager
        if "rollin2_level3" not in audio.music_clips:
            audio.load_music("rollin2_level3", "Level_2.wav")
        if "win" not in audio.sound_effects:
            audio.load_sound("win", "rollin1/win.wav")
        if "coin" not in audio.sound_effects:
            audio.load_sound("coin", "rollin1/hitsound.wav", relative_volume=0.2)
        if "playerhit" not in audio.sound_effects:
            audio.load_sound("playerhit", "playerhit.mp3")
        if "health_pickup" not in audio.sound_effects:
            audio.load_sound("health_pickup", "health_pickup.wav", relative_volume=0.2)
        if "jump" not in audio.sound_effects:
            audio.load_sound("jump", "Jump.wav", relative_volume=0.2)
        audio.play_music("rollin2_level3", loops=-1, fade_ms=1000)

        # Font for debug info
        font_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../assets/fonts/upheavtt.ttf"))
        self.font = pygame.font.Font(font_path, 14)
        self.load_hud_assets()
        self.has_won = False
        self.win_sound_played = False
        self.death_screen_timer = 0

    def update(self):
        if self.handle_death_screen(self.gsm.ROLLIN2_LEVEL3_STATE):
            return
        self.player.underwater = self.underwater
        self.handle_player_input()
        self.update_coins()
        for enemy in self.enemies:
            enemy.update(16.67, self.spikes, self.moving_platforms)
        for platform in self.moving_platforms:
            platform.update(16.67)
        for spike in self.spikes:
            spike.update(16.67)
        for lava_tile in self.lava:
            lava_tile.update(16.67)
        for spike in self.spikes:
            if self.player.hit_spike(spike):
                if self.player.take_damage(spike.get_x()):
                    self.gsm.audio_manager.play_sound("playerhit")
        for lava_tile in self.lava:
            if self.player.hit_spike(lava_tile):
                if self.player.touch_lava():
                    self.gsm.audio_manager.play_sound("playerhit")
        for enemy in self.enemies:
            if self.player.hit_spike(enemy):
                if self.player.take_damage(enemy.get_x()):
                    self.gsm.audio_manager.play_sound("playerhit")
        self.player.update(16.67, self.gsm.audio_manager, self.moving_platforms)
        self.update_hearts()
        if self.check_win_condition_with_next_level("Rollin 2 Level 3", self.gsm.ROLLIN2_LEVEL4_STATE):
            return
        if self.check_death_condition():
            return
        camera_x = 160 - self.player.get_x()
        if camera_x > 0:
            camera_x = 0
        self.tilemap.set_position(
            camera_x,
            120 - self.player.get_y()
        )
        self.check_pause()

    def draw(self, surface):
        self.draw_background(surface)
        # Draw tilemap with custom layer order (lava under static platforms)
        self.tilemap.draw_with_lava_entities(surface, self.lava)
        for platform in self.moving_platforms:
            platform.draw(surface)
        for spike in self.spikes:
            spike.draw(surface)
        for enemy in self.enemies:
            enemy.draw(surface)
        for coin in self.coins:
            coin.draw(surface)
        self.player.draw(surface)
        self.draw_hud(surface)
        if self.has_won:
            font_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../assets/fonts/upheavtt.ttf"))
            win_font = pygame.font.Font(font_path, 32)
            win_text = win_font.render("LEVEL COMPLETE!", True, (255, 255, 0))
            win_rect = win_text.get_rect(center=(160, 100))
            surface.blit(win_text, win_rect)
            continue_text = self.font.render("Press ENTER to continue", True, (255, 255, 255))
            continue_rect = continue_text.get_rect(center=(160, 140))
            surface.blit(continue_text, continue_rect)
            return
        self.draw_death_screen(surface)
        self.draw_hearts(surface)
