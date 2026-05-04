"""
PauseState - Pause menu overlay for levels
Allows player to resume game or quit to main menu
"""
import pygame
from game_states.game_state import GameState


class PauseState(GameState):
    def __init__(self, gsm):
        super().__init__(gsm)
        self.current_choice = 0
        self.options = ["Resume", "Restart Level", "Options", "Save and Quit", "Quit to Main Menu"]
        self.font = None
        self.title_font = None
        self.previous_state = None

    def init(self):
        """Initialize pause state"""
        # Initialize fonts
        import os
        font_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../assets/fonts/upheavtt.ttf"))
        self.font = pygame.font.Font(font_path, 24)
        self.title_font = pygame.font.Font(font_path, 36)
        self.current_choice = 0

        # Pause the music when entering pause state
        self.gsm.audio_manager.pause_music()

    def set_previous_state(self, state):
        """Set the state to return to when resuming"""
        self.previous_state = state

    def update(self):
        """Update pause menu logic"""
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
        if input_handler.is_pressed(input_handler.BUTTON1) or input_handler.is_pressed(input_handler.BUTTON3):
            self.select()

        # ESC also resumes
        if input_handler.is_pressed(input_handler.BUTTON2):
            if self.previous_state is not None:
                # Resume music before returning to level
                self.gsm.audio_manager.resume_music()
                # Don't call init() - just switch state to preserve progress
                self.gsm.set_state(self.previous_state, init=False)

    def select(self):
        """Handle pause menu selection"""
        option = self.options[self.current_choice]
        if option == "Resume":
            if self.previous_state is not None:
                self.gsm.audio_manager.resume_music()
                self.gsm.set_state(self.previous_state, init=False)
        elif option == "Restart Level":
            if self.previous_state is not None:
                self.gsm.audio_manager.stop_music()
                self.gsm.set_state(self.previous_state)
        elif option == "Options":
            self.gsm.set_state(self.gsm.OPTIONS_STATE)
            if self.gsm.game_states[self.gsm.OPTIONS_STATE]:
                self.gsm.game_states[self.gsm.OPTIONS_STATE].set_return_state(self.gsm.PAUSE_STATE)
        elif option == "Save and Quit":
            if self.previous_state is not None:
                level = self.gsm.game_states[self.previous_state]
                collected = [i for i, c in enumerate(level.coins) if not c.is_on_screen]
                self.gsm.save_game(
                    level_state_id=self.previous_state,
                    score=self.gsm.get_score(),
                    lives=self.gsm.get_lives(),
                    run_coins_collected=self.gsm.run_coins_collected,
                    run_coins_total=self.gsm.run_coins_total,
                    player_x=level.player.get_x(),
                    player_y=level.player.get_y(),
                    collected_coin_indices=collected,
                )
            self.gsm.audio_manager.stop_music()
            self.gsm.set_state(self.gsm.MENU_STATE)
        elif option == "Quit to Main Menu":
            self.gsm.audio_manager.stop_music()
            self.gsm.set_state(self.gsm.MENU_STATE)

    def draw(self, surface):
        """Draw pause menu as overlay"""
        # Semi-transparent dark overlay
        overlay = pygame.Surface((320, 240))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        # Draw title
        title_text = self.title_font.render("PAUSED", True, (255, 255, 100))
        title_rect = title_text.get_rect(center=(160, 50))
        surface.blit(title_text, title_rect)

        # Draw menu options
        start_y = 85
        spacing = 27

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
