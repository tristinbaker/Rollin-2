"""
Level1State - equivalent to Level1State.java
First level of the game
10 coins in this level
"""
import pygame
import os
from game_states.level_state import LevelState
from tilemap.tilemap import TileMap
from entities.player import Player
from entities.coin import Coin


class Level1State(LevelState):
    def __init__(self, gsm):
        super().__init__(gsm, hud_color=(255, 255, 255))  # White HUD
        # self.underwater is inherited from LevelState
        # All other common attributes are inherited as well

    def init(self):
        """Initialize Level 1"""


        # Save starting score for this level
        self.level_start_score = self.gsm.get_score()

        # Set level physics (change to True for underwater physics)
        self.underwater = False

        # Load simple background (Rollin 1 style - static, no scrolling)
        self.load_simple_background("Background.png", scroll_speed=0.0)

        # Create tilemap
        self.tilemap = TileMap(30)  # 30 pixel tiles
        self.tilemap.load_tiles("tilesets/rollin1/tileset.gif")
        self.tilemap.load_map("maps/rollin1/map1.map")

        # Create player
        self.player = Player(self.tilemap)
        self.player.set_position(25, 160)
        self.player.reset_hp()
        self.player.glide_gravity_multiplier = 0.2

        # Create coins (10 total, matching Java positions)
        self.coins = []
        self.total_coins = 0
        coin_positions = [
            (50, 170), (350, 140), (600, 200), (800, 140), (1015, 110),
            (1250, 170), (1460, 110), (1575, 20), (1815, 150), (1950, 200)
        ]
        for pos in coin_positions:
            coin = Coin(self.tilemap, "blue")
            coin.set_position(pos[0], pos[1])
            self.coins.append(coin)
        self.max_coins = len(self.coins)

        # No spikes or enemies in original Rollin 1 Level 1
        self.spikes = []
        self.enemies = []

        # Set initial camera position immediately (no tweening)
        self.tilemap.set_position_immediate(
            160 - self.player.get_x(),
            120 - self.player.get_y()
        )

        # Load and play level music
        audio = self.gsm.audio_manager
        if "level1" not in audio.music_clips:
            audio.load_music("level1", "rollin1/Level1.wav")
        if "win" not in audio.sound_effects:
            audio.load_sound("win", "rollin1/win.wav")
        if "coin" not in audio.sound_effects:
            audio.load_sound("coin", "rollin1/hitsound.wav", relative_volume=0.2)
        if "playerhit" not in audio.sound_effects:
            audio.load_sound("playerhit", "playerhit.mp3")
        if "jump" not in audio.sound_effects:
            audio.load_sound("jump", "Jump.wav", relative_volume=0.2)
        audio.play_music("level1", loops=-1, fade_ms=1000)

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
                    self.gsm.set_state(self.gsm.LEVEL1_STATE)
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

        # Update player (60 FPS = ~16.67ms per frame)
        self.player.update(16.67, self.gsm.audio_manager)

        # Check if player has won FIRST (before death check)
        if self.player.has_won():
            if not self.has_won:
                self.has_won = True
                self.gsm.commit_level_coins(self.total_coins, self.max_coins)
                if not self.win_sound_played:
                    self.gsm.audio_manager.stop_music()
                    self.gsm.audio_manager.play_sound("win")
                    self.win_sound_played = True

            if input_handler.is_pressed(input_handler.BUTTON1):  # Enter
                self.gsm.set_state(self.gsm.LEVEL2_STATE)
            return

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
        # Draw background (automatically uses simple or parallax based on what's loaded)
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

        # Draw win message if won (check this FIRST, before death screen)
        if self.has_won:
            import os
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
            import os
            font_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../assets/fonts/upheavtt.ttf"))
            death_font = pygame.font.Font(font_path, 48)
            death_text = death_font.render("YOU DIED!", True, (255, 0, 0))
            death_rect = death_text.get_rect(center=(160, 120))
            surface.blit(death_text, death_rect)
