import pygame
import os
from game_states.game_state import GameState


class ModeSelectState(GameState):
    def __init__(self, gsm):
        super().__init__(gsm)
        self.current_choice = 0
        self.font = None
        self.title_font = None

    def init(self):
        font_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "../../assets/fonts/upheavtt.ttf")
        )
        self.font       = pygame.font.Font(font_path, 24)
        self.title_font = pygame.font.Font(font_path, 36)
        self.current_choice = 0

    # --- helpers ----------------------------------------------------------

    def _modes(self):
        """Return list of (label, unlocked) tuples in display order."""
        return [
            ("Normal Mode",  True),
            ("Demon Mode",   self.gsm.demon_mode_unlocked),
            ("Hardcore",     self.gsm.hardcore_unlocked),
        ]

    def _selectable_indices(self):
        return [i for i, (_, unlocked) in enumerate(self._modes()) if unlocked]

    # --- update -----------------------------------------------------------

    def update(self):
        ih = self.gsm.input_handler
        selectable = self._selectable_indices()

        if ih.is_pressed(ih.UP) or ih.is_pressed(ih.W):
            idx = selectable.index(self.current_choice) if self.current_choice in selectable else 0
            self.current_choice = selectable[(idx - 1) % len(selectable)]

        if ih.is_pressed(ih.DOWN) or ih.is_pressed(ih.S):
            idx = selectable.index(self.current_choice) if self.current_choice in selectable else 0
            self.current_choice = selectable[(idx + 1) % len(selectable)]

        if ih.is_pressed(ih.BUTTON1) or ih.is_pressed(ih.BUTTON3):
            modes = self._modes()
            label, unlocked = modes[self.current_choice]
            if unlocked:
                self._start_game(label)

        if ih.is_pressed(ih.BUTTON2):
            self.gsm.set_state(self.gsm.MENU_STATE)

    def _start_game(self, mode_label):
        mode_map = {
            "Normal Mode": "normal",
            "Demon Mode":  "demon",
            "Hardcore":    "hardcore",
        }
        self.gsm.current_mode = mode_map[mode_label]
        self.gsm.set_score(0)
        self.gsm.set_lives(5)
        self.gsm.run_coins_collected = 0
        self.gsm.run_coins_total = 0
        self.gsm.set_state(self.gsm.ROLLIN2_LEVEL1_STATE)

    # --- draw -------------------------------------------------------------

    def draw(self, surface):
        surface.fill((20, 20, 40))

        title = self.title_font.render("Select Mode", True, (255, 255, 100))
        surface.blit(title, title.get_rect(center=(160, 50)))

        modes = self._modes()
        start_y = 100
        spacing = 36

        for i, (label, unlocked) in enumerate(modes):
            display = label if unlocked else "???"
            is_selected = (i == self.current_choice)

            if not unlocked:
                color = (80, 80, 80)
            elif is_selected:
                color = (255, 255, 255)
            else:
                color = (150, 150, 150)

            text = self.font.render(display, True, color)
            rect = text.get_rect(center=(160, start_y + i * spacing))

            if is_selected and unlocked:
                indicator = self.font.render(">", True, (255, 255, 100))
                surface.blit(indicator, indicator.get_rect(right=rect.left - 10, centery=rect.centery))

            surface.blit(text, rect)

        hint = pygame.font.Font(
            os.path.normpath(os.path.join(os.path.dirname(__file__), "../../assets/fonts/upheavtt.ttf")), 12
        ).render("ESC - Back", True, (80, 80, 80))
        surface.blit(hint, hint.get_rect(center=(160, 220)))
