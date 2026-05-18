"""
Level 5 State for Rollin 2
"""
import pygame
import os
from paths import asset
from game_states.level_state import LevelState
from tilemap.tilemap import TileMap
from entities.player import Player
from entities.level5_boss import Level5Boss


class Level5State(LevelState):
    def __init__(self, gsm):
        super().__init__(gsm, hud_color=(255, 255, 255))

    def init(self):
        self.coins = []
        self.spikes = []
        self.lava = []
        self.enemies = []
        self.moving_platforms = []
        self.total_coins = 0
        self.max_coins = 0
        self.level_start_score = self.gsm.get_score()
        self.underwater = False

        self.bg_layers = []
        self.load_parallax_layers([("Back (1).png", 0.0)], subfolder="level_5", clear=False)
        self.load_animated_bg_layer("Back (2)", scroll_speed=0.0, frame_delay=80, subfolder="level_5")
        self.load_parallax_layers([("Back (3).png", 0.0), ("Back (4).png", 0.0)], subfolder="level_5", clear=False)

        self.tilemap = TileMap(32)
        self.tilemap.load_map("maps/level_5.tmj")

        self.player = Player(self.tilemap)
        spawn_x, spawn_y = self.tilemap.find_spawn_position()
        self.player.set_position(spawn_x, spawn_y)
        self.player.reset_hp()
        self.apply_mode_to_player()

        self.spawn_coins_from_layer()
        self.spawn_spikes_from_layer()
        self.spawn_lava_from_layer()
        self.spawn_slimes_from_layer()
        self.spawn_bats_from_layer()
        self.spawn_wasps_from_layer()
        self.spawn_vertical_platforms_from_layer()
        self.spawn_opposite_vertical_platforms_from_layer()
        self.spawn_horizontal_platforms_from_layer()
        self.spawn_opposite_horizontal_platforms_from_layer()
        self.spawn_hearts_from_layer()
        if self.gsm.current_mode in ("demon", "hc_demon"):
            self.spawn_demon_from_layer()

        self.level5_boss = Level5Boss(self.tilemap)

        self.tilemap.set_position_immediate(
            160 - self.player.get_x(),
            120 - self.player.get_y()
        )

        audio = self.gsm.audio_manager
        if "rollin2_level5" not in audio.music_clips:
            audio.load_music("rollin2_level5", "Level_5.wav")
        if "win" not in audio.sound_effects:
            audio.load_sound("win", "rollin1/win.wav")
        if "finalwin" not in audio.sound_effects:
            audio.load_sound("finalwin", "rollin1/finalWin.wav")
        if "coin" not in audio.sound_effects:
            audio.load_sound("coin", "rollin1/hitsound.wav", relative_volume=0.2)
        if "playerhit" not in audio.sound_effects:
            audio.load_sound("playerhit", "playerhit.mp3")
        if "health_pickup" not in audio.sound_effects:
            audio.load_sound("health_pickup", "health_pickup.wav", relative_volume=0.2)
        if "jump" not in audio.sound_effects:
            audio.load_sound("jump", "Jump.wav", relative_volume=0.2)
        audio.play_music("rollin2_level5", loops=-1, fade_ms=1000)

        font_path = asset("fonts/upheavtt.ttf")
        self.font = pygame.font.Font(font_path, 14)
        self.load_hud_assets()
        self.has_won = False
        self.win_sound_played = False
        self.death_screen_timer = 0

    def update(self):
        if self.handle_death_screen(self.gsm.ROLLIN2_LEVEL5_STATE):
            return
        self.player.underwater = self.underwater
        self.handle_player_input()
        self.update_coins()
        for platform in self.moving_platforms:
            platform.update(16.67)
        for spike in self.spikes:
            spike.update(16.67)
        for lava_tile in self.lava:
            lava_tile.update(16.67)
        for enemy in self.enemies:
            enemy.update(16.67, self.spikes, self.moving_platforms)
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

        self.level5_boss.update(16.67)
        if self.player.hit_spike(self.level5_boss):
            if self.player.take_damage(self.level5_boss.get_x()):
                self.gsm.audio_manager.play_sound("playerhit")

        self.player.update(16.67, self.gsm.audio_manager, self.moving_platforms)
        self.update_demon(16.67)
        self.update_animated_backgrounds(16.67)
        self.update_hearts()
        if self.check_final_win_condition("Rollin 2 Level 5"):
            return
        if self.check_death_condition():
            return
        camera_x = 160 - self.player.get_x()
        if camera_x > 0:
            camera_x = 0
        self.tilemap.set_position(camera_x, 120 - self.player.get_y())
        self.check_pause()

    def draw(self, surface):
        self.draw_background(surface)
        self.tilemap.draw_with_lava_entities(surface, self.lava)
        for platform in self.moving_platforms:
            platform.draw(surface)
        for spike in self.spikes:
            spike.draw(surface)
        for enemy in self.enemies:
            enemy.draw(surface)
        for coin in self.coins:
            coin.draw(surface)
        self.level5_boss.draw(surface)
        self.draw_demon(surface)
        self.player.draw(surface)
        self.draw_hud(surface)
        if self.has_won:
            font_path = asset("fonts/upheavtt.ttf")
            mode = self.gsm.current_mode
            is_perfect = (self.gsm.run_coins_total > 0 and
                          self.gsm.run_coins_collected == self.gsm.run_coins_total)
            if mode == "hc_demon" and getattr(self, 'unlocked_this_run', False):
                overlay = pygame.Surface((320, 240))
                overlay.set_alpha(210)
                overlay.fill((0, 0, 0))
                surface.blit(overlay, (0, 0))
                hc_font = pygame.font.Font(font_path, 20)
                lines = [
                    ("YOU DID IT.", (255, 50, 50), hc_font),
                    ("Send your save file to Tristin", (255, 255, 255), self.font),
                    ("as proof to claim your $5.", (255, 255, 255), self.font),
                    ("Press ENTER to continue", (180, 180, 180), self.font),
                ]
                y = 85
                for text, color, fnt in lines:
                    surf = fnt.render(text, True, color)
                    surface.blit(surf, surf.get_rect(center=(160, y)))
                    y += 26
            else:
                if is_perfect and mode == "normal":
                    extra_line  = "You've unlocked Rollin 1!"
                    extra_color = (100, 255, 150)
                elif is_perfect and mode == "demon":
                    extra_line  = "You've unlocked Hardcore Mode!"
                    extra_color = (255, 100, 255)
                elif mode == "hardcore":
                    extra_line  = "You've unlocked HC Demon Mode!"
                    extra_color = (255, 60, 60)
                else:
                    extra_line  = "Get all coins to unlock something special!"
                    extra_color = (255, 220, 80)
                self.draw_win_overlay(surface, "Level 5", extra_line=extra_line, extra_color=extra_color)
            return
        self.draw_death_screen(surface)
        self.draw_hearts(surface)
