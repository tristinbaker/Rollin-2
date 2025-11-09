"""
Level 1 State for Rollin 2
Test level based on Rollin 1's Level 1 layout
"""
import pygame
import os
from game_states.level_state import LevelState
from tilemap.tilemap import TileMap
from entities.player import Player


class Level1State(LevelState):
    def __init__(self, gsm):
        super().__init__(gsm, hud_color=(255, 255, 255))  # White HUD
        # self.underwater is inherited from LevelState

    def init(self):
        """Initialize Rollin 2 Level 1"""


        # Clear entity lists (in case reinitializing)
        self.coins = []
        self.spikes = []
        self.lava = []
        self.enemies = []
        self.moving_platforms = []
        self.total_coins = 0
        self.max_coins = 0

        # Save starting score for this level
        self.level_start_score = self.gsm.get_score()

        # Set level physics
        self.underwater = False

        # Load parallax background (Rollin 2 style)
        self.load_parallax_layers([
            ("background_day1.png", 0.0),   # Furthest back, static
            ("background_day2.png", 0.5),   # Middle layer
            ("background_day3.png", 0.95),  # Closest layer, nearly 1:1 with camera
        ], subfolder="level_1")

        # Create tilemap (using Tiled format with 32x32 tiles)
        self.tilemap = TileMap(32)  # 32 pixel tiles for Rollin 2
        self.tilemap.load_map("maps/level_1.tmj")

        # Create player
        self.player = Player(self.tilemap)

        # Find spawn position on the leftmost collision tile
        spawn_x, spawn_y = self.tilemap.find_spawn_position()
        self.player.set_position(spawn_x, spawn_y)
        self.player.reset_hp()  # Reset HP to 3 at start of level

        # Spawn entities from Tiled layers using inherited methods
        self.spawn_coins_from_layer()
        self.spawn_spikes_from_layer()
        self.spawn_lava_from_layer()
        self.spawn_slimes_from_layer()
        self.spawn_bats_from_layer()
        self.spawn_wasps_from_layer()
        self.spawn_vertical_platforms_from_layer()
        self.spawn_horizontal_platforms_from_layer()
        # Spawn hearts from "Hearts" layer
        self.spawn_hearts_from_layer()

        # Set initial camera position immediately (no tweening)
        self.tilemap.set_position_immediate(
            160 - self.player.get_x(),
            120 - self.player.get_y()
        )

        # Load and play level music (Rollin 2 music)
        audio = self.gsm.audio_manager
        if "rollin2_level1" not in audio.music_clips:
            audio.load_music("rollin2_level1", "Level_2.wav")  # Using Rollin 2 music
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
        audio.play_music("rollin2_level1", loops=-1, fade_ms=1000)

        # Font for debug info
        font_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../assets/fonts/upheavtt.ttf"))
        self.font = pygame.font.Font(font_path, 14)

        # Load HUD assets
        self.load_hud_assets()

        # Reset win state
        self.has_won = False
        self.win_sound_played = False
        self.death_screen_timer = 0



    def update(self):
        """Update level logic"""
        # Handle death screen
        if self.handle_death_screen(self.gsm.ROLLIN2_LEVEL1_STATE):
            return

        # Set underwater physics
        self.player.underwater = self.underwater

        # Handle player input
        self.handle_player_input()

        # Update coins
        self.update_coins()

        # Update enemies (pass spikes and platforms for collision detection)
        for enemy in self.enemies:
            enemy.update(16.67, self.spikes, self.moving_platforms)

        # Update moving platforms
        for platform in self.moving_platforms:
            platform.update(16.67)

        # Update spikes (animation)
        for spike in self.spikes:
            spike.update(16.67)

        # Update lava (animation)
        for lava_tile in self.lava:
            lava_tile.update(16.67)

        # Check spike collisions
        for spike in self.spikes:
            if self.player.hit_spike(spike):
                if self.player.take_damage(spike.get_x()):
                    self.gsm.audio_manager.play_sound("playerhit")

        # Check lava collisions (instant death)
        for lava_tile in self.lava:
            if self.player.hit_spike(lava_tile):
                if self.player.touch_lava():
                    self.gsm.audio_manager.play_sound("playerhit")

        # Check enemy collisions
        for enemy in self.enemies:
            if self.player.hit_spike(enemy):
                if self.player.take_damage(enemy.get_x()):
                    self.gsm.audio_manager.play_sound("playerhit")

        # Update player (60 FPS = ~16.67ms per frame)
        self.player.update(16.67, self.gsm.audio_manager, self.moving_platforms)

        # Update hearts
        self.update_hearts()

        # Check win condition
        if self.check_win_condition_with_next_level("Rollin 2 Level 1", self.gsm.ROLLIN2_LEVEL2_STATE):
            return

        # Check death condition
        if self.check_death_condition():
            return

        # Update camera to follow player
        # Center horizontally, position player slightly lower on screen
        camera_x = 160 - self.player.get_x()  # Center horizontally (320/2 = 160)

        # Prevent camera from going positive (showing past the left edge of the map)
        # This keeps player from going off the left side of the screen
        if camera_x > 0:
            camera_x = 0

        self.tilemap.set_position(
            camera_x,
            120 - self.player.get_y()   # Center camera more (240/2 = 120)
        )

        # Check for pause (ESC key)
        self.check_pause()

    def draw(self, surface):
        """Draw level"""
        # Draw background (automatically uses simple or parallax based on what's loaded)
        self.draw_background(surface)

        # Draw tilemap
        self.tilemap.draw(surface)

        # Draw moving platforms
        for platform in self.moving_platforms:
            platform.draw(surface)

        # Draw spikes
        for spike in self.spikes:
            spike.draw(surface)

        # Draw lava
        for lava_tile in self.lava:
            lava_tile.draw(surface)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(surface)

        # Draw coins
        for coin in self.coins:
            coin.draw(surface)

        # Draw player
        self.player.draw(surface)

        # Draw HUD
        self.draw_hud(surface)

        # Draw win message if won
        if self.has_won:
            font_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../assets/fonts/upheavtt.ttf"))
            win_font = pygame.font.Font(font_path, 32)
            win_text = win_font.render("LEVEL COMPLETE!", True, (255, 255, 0))
            win_rect = win_text.get_rect(center=(160, 100))
            surface.blit(win_text, win_rect)

            continue_text = self.font.render("Press ENTER to continue", True, (255, 255, 255))
            continue_rect = continue_text.get_rect(center=(160, 140))
            surface.blit(continue_text, continue_rect)
            return  # Don't draw death screen if won

        # Draw death screen if active
        self.draw_death_screen(surface)

        # Draw hearts
        self.draw_hearts(surface)
