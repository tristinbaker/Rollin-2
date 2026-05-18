"""
PauseState - Pause menu overlay for levels
"""
import pygame
import os
from paths import asset
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
        font_path = asset("fonts/upheavtt.ttf")
        self.font = pygame.font.Font(font_path, 24)
        self.title_font = pygame.font.Font(font_path, 36)
        self.current_choice = 0
        self.gsm.audio_manager.pause_music()

    def set_previous_state(self, state):
        self.previous_state = state

    # ------------------------------------------------------------------ helpers

    def _restart_disabled(self):
        safe = getattr(self.gsm, 'player_has_safe_ground', True)
        return not safe and self.gsm.get_lives() <= 1

    def _available_indices(self):
        return [i for i, opt in enumerate(self.options)
                if not (opt == "Restart Level" and self._restart_disabled())]

    # ------------------------------------------------------------------ update

    def update(self):
        ih = self.gsm.input_handler
        available = self._available_indices()

        if ih.is_pressed(ih.UP) or ih.is_pressed(ih.W):
            pos = available.index(self.current_choice) if self.current_choice in available else 0
            self.current_choice = available[(pos - 1) % len(available)]

        if ih.is_pressed(ih.DOWN) or ih.is_pressed(ih.S):
            pos = available.index(self.current_choice) if self.current_choice in available else 0
            self.current_choice = available[(pos + 1) % len(available)]

        # Keep cursor on a valid option (e.g. if safe-ground changed since last open)
        if self.current_choice not in available:
            self.current_choice = available[0]

        if ih.is_pressed(ih.BUTTON1) or ih.is_pressed(ih.BUTTON3):
            self.select()

        if ih.is_pressed(ih.BUTTON2):
            if self.previous_state is not None:
                self.gsm.audio_manager.resume_music()
                self.gsm.set_state(self.previous_state, init=False)

    def select(self):
        option = self.options[self.current_choice]

        if option == "Resume":
            if self.previous_state is not None:
                self.gsm.audio_manager.resume_music()
                self.gsm.set_state(self.previous_state, init=False)

        elif option == "Restart Level":
            if self._restart_disabled():
                return
            if self.previous_state is not None:
                safe = getattr(self.gsm, 'player_has_safe_ground', True)
                if not safe:
                    self.gsm.lose_life()
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

    # ------------------------------------------------------------------ draw

    def draw(self, surface):
        overlay = pygame.Surface((320, 240))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        title_text = self.title_font.render("PAUSED", True, (255, 255, 100))
        surface.blit(title_text, title_text.get_rect(center=(160, 50)))

        start_y = 85
        spacing = 27

        for i, option in enumerate(self.options):
            disabled = (option == "Restart Level" and self._restart_disabled())
            is_selected = (i == self.current_choice)

            if disabled:
                color = (60, 60, 60)
            elif is_selected:
                color = (255, 255, 255)
            else:
                color = (150, 150, 150)

            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(160, start_y + i * spacing))

            if is_selected and not disabled:
                indicator = self.font.render(">", True, (255, 255, 100))
                surface.blit(indicator, indicator.get_rect(right=rect.left - 10, centery=rect.centery))

            surface.blit(text, rect)

            # Annotate why restart is disabled
            if disabled:
                small_font = pygame.font.Font(
                    asset("fonts/upheavtt.ttf"), 10
                )
                note = small_font.render("(no ground below)", True, (80, 80, 80))
                surface.blit(note, note.get_rect(center=(160, rect.bottom + 4)))
