"""
Level 1 State for Rollin 2
Test level based on Rollin 1's Level 1 layout
"""
import pygame
import os
from paths import asset
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

        S = "level_2"
        SC = 0.74  # 324px source → 240px screen

        TY = 115; MY = 184; WY = 124; FY = 203

        self.bg_layers = []
        self.load_parallax_layers([("Background Layer 6- Sky.png", 0.0)], subfolder=S, clear=False)
        self.load_parallax_layers([("Background Layer 5- Sky.png", 0.05)], subfolder=S, clear=False)
        self.load_parallax_layers([("Background Layer 4 - BrightEffect.png", 0.1)], subfolder=S, clear=False)
        self.load_background_sprite("WindMill Animated - Spritesheet.png",
            100, 100, 10, x=275, y=WY, scroll_speed=0.1, frame_delay=80, scale=0.45, subfolder=S)
        self.load_parallax_layers([("Background Layer 3.png", 0.2)], subfolder=S, clear=False)
        for x in [80, 300, 520, 740, 960]:
            self.load_background_sprite("Pine Tree 1 - Spritesheet.png",
                53, 102, 10, x=x, y=TY, scroll_speed=0.2, frame_delay=150, scale=SC, subfolder=S)
        for x in [190, 430, 660, 880]:
            self.load_background_sprite("Pine Tree 3 - Mini - Spritesheet.png",
                53, 102, 10, x=x, y=MY, scroll_speed=0.2, frame_delay=150, scale=0.55, subfolder=S)
        self.load_parallax_layers([("Background Layer 2.png", 0.35)], subfolder=S, clear=False)
        for x in [60, 320, 580, 840, 1100]:
            self.load_background_sprite("Oak Tree 1 - Spritesheet.png",
                112, 102, 10, x=x, y=TY, scroll_speed=0.35, frame_delay=150, scale=SC, subfolder=S)
        for x in [150, 430, 700, 970]:
            self.load_background_sprite("Pine Tree 2 - Spritesheet.png",
                53, 102, 10, x=x, y=TY, scroll_speed=0.35, frame_delay=150, scale=SC, subfolder=S)
        self.load_parallax_layers([("Background Layer 1.png", 0.5)], subfolder=S, clear=False)
        for x in [100, 380, 660, 940, 1220]:
            self.load_background_sprite("Oak Tree 2 - Spritesheet.png",
                112, 102, 10, x=x, y=TY, scroll_speed=0.5, frame_delay=150, scale=SC, subfolder=S)
        self.load_parallax_layers([("Background Layer 0.png", 0.65)], subfolder=S, clear=False)
        for x in [30, 160, 290, 420, 550, 680, 810]:
            self.load_background_sprite("Fluers Two Variations - Spritesheet.png",
                100, 50, 5, x=x, y=FY, scroll_speed=0.65, frame_delay=120, row=0, scale=SC, subfolder=S)
        for x in [90, 220, 350, 480, 610, 740]:
            self.load_background_sprite("Fluers Two Variations - Spritesheet.png",
                100, 50, 5, x=x, y=FY, scroll_speed=0.65, frame_delay=120, row=1, scale=SC, subfolder=S)

        # Create tilemap (using Tiled format with 32x32 tiles)
        self.tilemap = TileMap(32)  # 32 pixel tiles for Rollin 2
        self.tilemap.load_map("maps/level_1.tmj")

        # Create player
        self.player = Player(self.tilemap)

        # Find spawn position on the leftmost collision tile
        spawn_x, spawn_y = self.tilemap.find_spawn_position()
        self.player.set_position(spawn_x, spawn_y)
        self.player.reset_hp()
        self.apply_mode_to_player()

        # Spawn entities from Tiled layers using inherited methods
        self.spawn_coins_from_layer()
        self.spawn_spikes_from_layer()
        self.spawn_lava_from_layer()
        self.spawn_slimes_from_layer()
        self.spawn_bats_from_layer()
        self.spawn_wasps_from_layer()
        self.spawn_vertical_platforms_from_layer()
        self.spawn_opposite_vertical_platforms_from_layer()
        self.spawn_horizontal_platforms_from_layer()
        # Spawn hearts from "Hearts" layer
        self.spawn_hearts_from_layer()
        if self.gsm.current_mode in ("demon", "hc_demon"):
            self.spawn_demon_from_layer()

        # Set initial camera position immediately (no tweening)
        self.tilemap.set_position_immediate(
            160 - self.player.get_x(),
            120 - self.player.get_y()
        )

        # Load and play level music (Rollin 2 music)
        audio = self.gsm.audio_manager
        if "rollin2_level1" not in audio.music_clips:
            audio.load_music("rollin2_level1", "Level_1.wav")  # Using Rollin 2 music
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
        font_path = asset("fonts/upheavtt.ttf")
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
        self.update_demon(16.67)
        self.update_animated_backgrounds(16.67)

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

        # Draw tilemap with custom layer order (lava under static platforms)
        self.tilemap.draw_with_lava_entities(surface, self.lava)

        # Draw moving platforms
        for platform in self.moving_platforms:
            platform.draw(surface)

        # Draw spikes
        for spike in self.spikes:
            spike.draw(surface)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(surface)

        # Draw coins
        for coin in self.coins:
            coin.draw(surface)

        # Draw player
        self.draw_demon(surface)
        self.player.draw(surface)

        # Draw HUD
        self.draw_hud(surface)

        # Draw win message if won
        if self.has_won:
            self.draw_win_overlay(surface, "Level 1")
            return

        # Draw death screen if active
        self.draw_death_screen(surface)

        # Draw hearts
        self.draw_hearts(surface)
