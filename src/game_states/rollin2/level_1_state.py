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
        print("Initializing Rollin 2 Level 1...")

        # Clear entity lists (in case reinitializing)
        self.coins = []
        self.spikes = []
        self.enemies = []
        self.moving_platforms = []
        self.total_coins = 0

        # Save starting score for this level
        self.level_start_score = self.gsm.get_score()

        # Set level physics
        self.underwater = False

        # Load parallax background (Rollin 2 style)
        self.load_parallax_layers([
            ("forest_sky.png", 0.0),        # Static sky
            ("forest_moon.png", 0.1),       # Very slow moon
            ("forest_mountain.png", 0.3),   # Slow mountains
            ("forest_back.png", 0.5),       # Medium back trees
            ("forest_mid.png", 0.7),        # Fast mid trees
            ("forest_long.png", 0.85),      # Very fast long trees
            ("forest_short.png", 0.95),     # Nearly 1:1 with camera
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
        self.spawn_slimes_from_layer()
        self.spawn_bats_from_layer()
        self.spawn_wasps_from_layer()
        self.spawn_vertical_platforms_from_layer()
        self.spawn_horizontal_platforms_from_layer()

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

        print("Rollin 2 Level 1 initialized!")

    def update(self):
        """Update level logic"""
        # Get input handler
        input_handler = self.gsm.input_handler

        # Handle death screen
        if self.death_screen_timer > 0:
            self.death_screen_timer -= 16.67  # Decrease timer
            if self.death_screen_timer <= 0:
                # Timer expired, restart level
                self.gsm.lose_life()
                # Restore score to what it was at the start of this level
                self.gsm.set_score(self.level_start_score)
                if self.gsm.get_lives() <= 0:
                    # Game over - return to menu
                    self.gsm.set_lives(5)  # Reset lives
                    self.gsm.set_state(self.gsm.MENU_STATE)
                else:
                    # Restart level
                    self.gsm.set_state(self.gsm.ROLLIN2_LEVEL1_STATE)
            return  # Don't process anything else during death screen

        # Set underwater physics
        self.player.underwater = self.underwater

        # Player controls
        self.player.set_left(input_handler.is_down(input_handler.LEFT) or
                            input_handler.is_down(input_handler.A))
        self.player.set_right(input_handler.is_down(input_handler.RIGHT) or
                             input_handler.is_down(input_handler.D))
        self.player.set_up(input_handler.is_down(input_handler.UP) or
                          input_handler.is_down(input_handler.W))
        self.player.set_down(input_handler.is_down(input_handler.DOWN) or
                            input_handler.is_down(input_handler.S))
        self.player.set_jumping(input_handler.is_down(input_handler.BUTTON3))  # Space
        self.player.set_gliding(input_handler.is_down(input_handler.BUTTON4))  # Shift

        # Update coins and check for collection
        for coin in self.coins:
            if self.player.got_coin(coin) and coin.is_on_screen:
                self.total_coins += 1
                self.gsm.add_score(100)  # 100 points per coin
                coin.player_got(self.gsm.audio_manager)
            coin.update(16.67)

        # Update enemies (pass spikes and platforms for collision detection)
        for enemy in self.enemies:
            enemy.update(16.67, self.spikes, self.moving_platforms)

        # Update moving platforms
        for platform in self.moving_platforms:
            platform.update(16.67)

        # Check spike collisions
        for spike in self.spikes:
            if self.player.hit_spike(spike):
                if self.player.take_damage(spike.get_x()):
                    self.gsm.audio_manager.play_sound("playerhit")

        # Check enemy collisions
        for enemy in self.enemies:
            if self.player.hit_spike(enemy):
                if self.player.take_damage(enemy.get_x()):
                    self.gsm.audio_manager.play_sound("playerhit")

        # Update player (60 FPS = ~16.67ms per frame)
        self.player.update(16.67, self.gsm.audio_manager, self.moving_platforms)

        # Check if player has won FIRST (before death check)
        if self.player.has_won():
            if not self.has_won:
                self.has_won = True
                # Play win sound and stop music
                if not self.win_sound_played:
                    self.gsm.audio_manager.stop_music()
                    self.gsm.audio_manager.play_sound("win")
                    self.win_sound_played = True
                    print("Rollin 2 Level 1 Complete!")
            # Return to menu after a moment
            if input_handler.is_pressed(input_handler.BUTTON1):  # Enter
                self.gsm.set_state(self.gsm.MENU_STATE)
            return

        # Check if player died (HP reached 0 or fell off map) - AFTER update
        if self.player.is_dead():
            if self.death_screen_timer == 0:
                # Start death screen
                self.gsm.audio_manager.stop_music()
                self.death_screen_timer = self.death_screen_duration
            return

        # Update camera to follow player
        # Position player lower on screen (y=160) to show more sky/background above
        camera_x = 160 - self.player.get_x()  # Center horizontally (320/2 = 160)

        # Prevent camera from going positive (showing past the left edge of the map)
        # This keeps player from going off the left side of the screen
        if camera_x > 0:
            camera_x = 0

        self.tilemap.set_position(
            camera_x,
            160 - self.player.get_y()   # Player at lower third of screen (shows more above)
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
        if self.death_screen_timer > 0:
            # Darken the screen
            overlay = pygame.Surface((320, 240))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            surface.blit(overlay, (0, 0))

            # Draw "YOU DIED!" text
            font_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../assets/fonts/upheavtt.ttf"))
            death_font = pygame.font.Font(font_path, 48)
            death_text = death_font.render("YOU DIED!", True, (255, 0, 0))
            death_rect = death_text.get_rect(center=(160, 120))
            surface.blit(death_text, death_rect)
