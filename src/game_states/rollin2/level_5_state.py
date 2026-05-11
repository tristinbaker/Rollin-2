"""
Level 5 State for Rollin 2
Basic boss arena — flat ground with a few static platforms.
Designed for testing the boss + projectile system.
"""
import pygame
import os
from game_states.level_state import LevelState
from tilemap.tilemap import TileMap
from entities.player import Player
from entities.demon_boss import DemonBoss

# Boss spawn: column 105, floating at mid-height above the arena
BOSS_X = 105 * 32 + 16   # 3376
BOSS_Y = 480              # floating start height


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

        self.spawn_hearts_from_layer()
        if self.gsm.current_mode in ("demon", "hardcore"):
            self.spawn_demon_from_layer()

        # Boss + active projectile list
        self.boss = DemonBoss(self.tilemap)
        self.boss.set_position(BOSS_X, BOSS_Y)
        self.projectiles = []

        self.tilemap.set_position_immediate(
            160 - self.player.get_x(),
            120 - self.player.get_y()
        )

        audio = self.gsm.audio_manager
        if "rollin2_level5" not in audio.music_clips:
            audio.load_music("rollin2_level5", "Level_4.wav")
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

        font_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../assets/fonts/upheavtt.ttf"))
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

        # Update boss
        self.boss.update(16.67, self.projectiles)

        # Boss body contact damages player
        if not self.boss.is_dead() and self.player.hit_spike(self.boss):
            if self.player.take_damage(self.boss.get_x()):
                self.gsm.audio_manager.play_sound("playerhit")

        # Update projectiles and check player collisions
        for proj in self.projectiles:
            proj.update(16.67)
            if proj.active and self.player.hit_spike(proj):
                if self.player.take_damage(proj.get_x()):
                    self.gsm.audio_manager.play_sound("playerhit")
                proj.active = False
        self.projectiles = [p for p in self.projectiles if p.active]

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
        for coin in self.coins:
            coin.draw(surface)
        self.boss.draw(surface)
        for proj in self.projectiles:
            proj.draw(surface)
        self.draw_demon(surface)
        self.player.draw(surface)
        self.draw_hud(surface)
        if self.has_won:
            font_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../assets/fonts/upheavtt.ttf"))
            win_font = pygame.font.Font(font_path, 32)
            if self.completion_code:
                overlay = pygame.Surface((320, 240))
                overlay.set_alpha(200)
                overlay.fill((0, 0, 0))
                surface.blit(overlay, (0, 0))
                hc_font = pygame.font.Font(font_path, 20)
                lines = [
                    ("HARDCORE COMPLETE!", (255, 215, 0), hc_font),
                    (self.completion_code, (255, 80, 255), self.font),
                    ("DM this code to Tristin on Discord", (255, 255, 255), self.font),
                    ("and he'll Venmo you $1!", (255, 255, 255), self.font),
                    ("Press ENTER to continue", (180, 180, 180), self.font),
                ]
                y = 70
                for text, color, fnt in lines:
                    surf = fnt.render(text, True, color)
                    surface.blit(surf, surf.get_rect(center=(160, y)))
                    y += 26
            else:
                win_text = win_font.render("LEVEL COMPLETE!", True, (255, 255, 0))
                surface.blit(win_text, win_text.get_rect(center=(160, 100)))
                continue_text = self.font.render("Press ENTER to continue", True, (255, 255, 255))
                surface.blit(continue_text, continue_text.get_rect(center=(160, 140)))
            return
        self.draw_death_screen(surface)
        self.draw_hearts(surface)
