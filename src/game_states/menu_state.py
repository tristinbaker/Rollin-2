"""
MenuState - equivalent to MenuState.java
Main menu with options to start game, view help, or quit
"""
import pygame
from game_states.game_state import GameState


class MenuState(GameState):
    def __init__(self, gsm):
        super().__init__(gsm)
        self.current_choice = 0
        self.options = []
        self.font = None
        self.title_font = None
        self.music_loaded = False

    def init(self):
        """Initialize menu state"""
        # Initialize fonts
        import os
        font_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../assets/fonts/upheavtt.ttf"))
        self.font = pygame.font.Font(font_path, 24)
        self.title_font = pygame.font.Font(font_path, 48)
        self.current_choice = 0

        # Build option list dynamically based on save/unlock state
        self.options = ["Play"]
        if self.gsm.save_slot is not None:
            self.options.append("Load Game")
        if self.gsm.rollin1_unlocked:
            self.options.append("Rollin 1")
        self.options += ["Options", "Quit"]

        # Load and play menu music if not already loaded
        if not self.music_loaded:
            audio = self.gsm.audio_manager
            audio.load_music("menu", "mainTheme.wav")
            self.music_loaded = True

        # Play the menu music (loop infinitely)
        self.gsm.audio_manager.play_music("menu", loops=-1, fade_ms=1000)

    def update(self):
        """Update menu logic"""
        # Get input handler
        input_handler = self.gsm.input_handler

        # Handle up/down navigation
        if input_handler.is_pressed(input_handler.UP) or input_handler.is_pressed(input_handler.W):
            self.current_choice -= 1
            if self.current_choice < 0:
                self.current_choice = len(self.options) - 1

        if input_handler.is_pressed(input_handler.DOWN) or input_handler.is_pressed(input_handler.S):
            self.current_choice += 1
            if self.current_choice >= len(self.options):
                self.current_choice = 0

        # Handle selection (Enter or Space)
        if input_handler.is_pressed(input_handler.BUTTON1) or input_handler.is_pressed(input_handler.BUTTON3):  # Enter or Space
            self.select()

    def select(self):
        """Handle menu selection"""
        option = self.options[self.current_choice]
        if option == "Play":
            self.gsm.set_score(0)
            self.gsm.set_lives(5)
            self.gsm.run_coins_collected = 0
            self.gsm.run_coins_total = 0
            self.gsm.set_state(self.gsm.ROLLIN2_LEVEL1_STATE)
        elif option == "Load Game":
            slot = self.gsm.save_slot
            self.gsm.set_score(slot['score'])
            self.gsm.set_lives(slot['lives'])
            self.gsm.run_coins_collected = slot['run_coins_collected']
            self.gsm.run_coins_total = slot['run_coins_total']
            self.gsm.pending_load = slot
            self.gsm.clear_save()
            self.gsm.set_state(slot['level_state'])
        elif option == "Rollin 1":
            self.gsm.set_score(0)
            self.gsm.set_lives(5)
            self.gsm.run_coins_collected = 0
            self.gsm.run_coins_total = 0
            self.gsm.set_state(self.gsm.LEVEL1_STATE)
        elif option == "Options":
            self.gsm.set_state(self.gsm.OPTIONS_STATE)
        elif option == "Quit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def draw(self, surface):
        """Draw menu to surface"""
        # Background color
        surface.fill((20, 20, 40))

        # Draw title
        title_text = self.title_font.render("ROLLIN' 2", True, (255, 255, 100))
        title_rect = title_text.get_rect(center=(160, 60))
        surface.blit(title_text, title_rect)

        # Draw menu options
        start_y = 100
        spacing = 30

        for i, option in enumerate(self.options):
            color = (255, 255, 255) if i == self.current_choice else (150, 150, 150)
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(160, start_y + i * spacing))

            # Draw selection indicator
            if i == self.current_choice:
                indicator = self.font.render(">", True, (255, 255, 100))
                indicator_rect = indicator.get_rect(right=rect.left - 10, centery=rect.centery)
                surface.blit(indicator, indicator_rect)

            surface.blit(text, rect)
