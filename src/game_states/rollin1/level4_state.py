"""
Level4State - equivalent to Level4State.java
Secret level of the game (unlocked by collecting all 19 coins in Level 3)
121 blue coins arranged in a pyramid
"""
import pygame
import os
from game_states.level_state import LevelState
from tilemap.tilemap import TileMap
from entities.player import Player
from entities.coin import Coin


class Level4State(LevelState):
    def __init__(self, gsm):
        super().__init__(gsm, hud_color=(0, 0, 0))  # Black HUD for level 4
        # self.underwater is inherited from LevelState

    def init(self):
        """Initialize Level 4 (Secret Level)"""


        # Save starting score for this level
        self.level_start_score = self.gsm.get_score()

        # Set level physics
        self.underwater = False

        # Load simple background (Rollin 1 style - static, no scrolling)
        self.load_simple_background("Background4.gif", scroll_speed=0.0)

        # Create tilemap
        self.tilemap = TileMap(30)  # 30 pixel tiles
        self.tilemap.load_tiles("tilesets/rollin1/tileset4.gif")
        self.tilemap.load_map("maps/rollin1/map4.map")

        # Create player
        self.player = Player(self.tilemap)
        self.player.set_position(16, 400)
        self.player.reset_hp()  # Reset HP to 3 at start of level

        # Create coins (121 total blue coins in pyramid formation)
        # This is a direct port of the Java coin placement logic
        self.coins = []
        self.total_coins = 0

        # Row 1: 15 coins at y=410
        j = 120
        for i in range(15):
            coin = Coin(self.tilemap, "blue")
            coin.set_position(j, 410)
            self.coins.append(coin)
            j += 30

        # Row 2: 14 coins at y=380 (one missing from end)
        j = 150
        for i in range(14):
            coin = Coin(self.tilemap, "blue")
            coin.set_position(j, 380)
            self.coins.append(coin)
            j += 30

        # Row 3: 12 coins at y=350
        j = 210
        for i in range(12):
            coin = Coin(self.tilemap, "blue")
            coin.set_position(j, 350)
            self.coins.append(coin)
            j += 30

        # Row 4: 10 coins at y=290
        j = 240
        for i in range(10):
            coin = Coin(self.tilemap, "blue")
            coin.set_position(j, 290)
            self.coins.append(coin)
            j += 30

        # Row 5: 8 coins at y=260
        j = 240
        for i in range(8):
            coin = Coin(self.tilemap, "blue")
            coin.set_position(j, 260)
            self.coins.append(coin)
            j += 30

        # Row 6: 13 coins at y=200
        j = 90
        for i in range(13):
            coin = Coin(self.tilemap, "blue")
            coin.set_position(j, 200)
            self.coins.append(coin)
            j += 30

        # Row 7: 12 coins at y=170
        j = 120
        for i in range(12):
            coin = Coin(self.tilemap, "blue")
            coin.set_position(j, 170)
            self.coins.append(coin)
            j += 30

        # Row 8: 10 coins at y=140
        j = 180
        for i in range(10):
            coin = Coin(self.tilemap, "blue")
            coin.set_position(j, 140)
            self.coins.append(coin)
            j += 30

        # Row 9: 11 coins at y=80
        j = 210
        for i in range(11):
            coin = Coin(self.tilemap, "blue")
            coin.set_position(j, 80)
            self.coins.append(coin)
            j += 30

        # Row 10: 15 coins at y=20 (top)
        j = 60
        for i in range(15):
            coin = Coin(self.tilemap, "blue")
            coin.set_position(j, 20)
            self.coins.append(coin)
            j += 30

        # No spikes or enemies
        self.spikes = []
        self.enemies = []

        # Set initial camera position immediately (no tweening)
        self.tilemap.set_position_immediate(
            160 - self.player.get_x(),
            120 - self.player.get_y()
        )

        # Load and play level music
        audio = self.gsm.audio_manager
        if "level4" not in audio.music_clips:
            audio.load_music("level4", "rollin1/Level4.wav")
        if "win" not in audio.sound_effects:
            audio.load_sound("win", "rollin1/win.wav")
        if "coin" not in audio.sound_effects:
            audio.load_sound("coin", "rollin1/hitsound.wav", relative_volume=0.2)
        if "playerhit" not in audio.sound_effects:
            audio.load_sound("playerhit", "playerhit.mp3")
        if "jump" not in audio.sound_effects:
            audio.load_sound("jump", "Jump.wav", relative_volume=0.2)
        audio.play_music("level4", loops=-1, fade_ms=1000)

        # Font for HUD
        font_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../assets/fonts/upheavtt.ttf"))
        self.font = pygame.font.Font(font_path, 14)

        # Load HUD assets
        self.load_hud_assets()

        # Reset win state
        self.has_won = False
        self.win_sound_played = False
        self.death_screen_timer = 0
        self.at_goal = False  # Flag for when player reaches goal area



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
                    self.gsm.set_state(self.gsm.LEVEL4_STATE)
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
                self.gsm.add_score(10)  # 10 points per coin (less than other levels, many coins)
                coin.player_got(self.gsm.audio_manager)
            coin.update(16.67)

        # Update player (60 FPS = ~16.67ms per frame)
        self.player.update(16.67, self.gsm.audio_manager)

        # Check if player is at goal area (x < 60 and y <= 20)
        if self.player.get_x() < 60 and self.player.get_y() <= 20:
            self.at_goal = True
            # Check if player has all coins
            if self.total_coins >= 120:  # Need at least 120 coins
                if not self.has_won:
                    self.has_won = True
                    # Play win sound and stop music
                    if not self.win_sound_played:
                        self.gsm.audio_manager.stop_music()
                        self.gsm.audio_manager.play_sound("win")
                        self.win_sound_played = True

                # Return to menu after a moment
                if input_handler.is_pressed(input_handler.BUTTON1):  # Enter
                    self.gsm.set_state(self.gsm.MENU_STATE)
                return
        else:
            self.at_goal = False

        # Check if player died (HP reached 0 or fell off map) - AFTER update
        if self.player.is_dead():
            if self.death_screen_timer == 0:
                # Start death screen
                self.gsm.audio_manager.stop_music()
                self.death_screen_timer = self.death_screen_duration
            return

        # Update camera to follow player
        self.tilemap.set_position(
            160 - self.player.get_x(),  # Center on screen (320/2 = 160)
            120 - self.player.get_y()   # Center on screen (240/2 = 120)
        )

        # Check for pause (ESC key)
        self.check_pause()

    def draw(self, surface):
        """Draw level"""
        # Draw background
        self.draw_background(surface)

        # Draw tilemap
        self.tilemap.draw(surface)

        # Draw coins
        for coin in self.coins:
            coin.draw(surface)

        # Draw player
        self.player.draw(surface)

        # Draw HUD
        self.draw_hud(surface)

        # If at goal but not enough coins, show message
        if self.at_goal and not self.has_won:
            message_text = self.font.render("Come back with more coins.", True, (0, 0, 0))
            message_rect = message_text.get_rect(center=(160, 100))
            surface.blit(message_text, message_rect)

        # Draw win message if won
        if self.has_won:
            font_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../assets/fonts/upheavtt.ttf"))
            win_font = pygame.font.Font(font_path, 24)

            congrats_text = win_font.render("Congratulations!", True, (0, 0, 0))
            congrats_rect = congrats_text.get_rect(center=(160, 100))
            surface.blit(congrats_text, congrats_rect)

            completed_text = self.font.render("You completed the secret", True, (0, 0, 0))
            completed_rect = completed_text.get_rect(center=(160, 120))
            surface.blit(completed_text, completed_rect)

            level_text = self.font.render("level of Rollin' with", True, (0, 0, 0))
            level_rect = level_text.get_rect(center=(160, 140))
            surface.blit(level_text, level_rect)

            score_text = self.font.render(f"a total score of: {self.gsm.get_score()}", True, (0, 0, 0))
            score_rect = score_text.get_rect(center=(160, 160))
            surface.blit(score_text, score_rect)

            thanks_text = self.font.render("Thank you for playing!", True, (0, 0, 0))
            thanks_rect = thanks_text.get_rect(center=(160, 180))
            surface.blit(thanks_text, thanks_rect)

            continue_text = self.font.render("Press ENTER to continue", True, (0, 0, 0))
            continue_rect = continue_text.get_rect(center=(160, 200))
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
