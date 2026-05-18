import pygame
import os
from paths import asset
from game_states.game_state import GameState


class ModeSelectState(GameState):
    def __init__(self, gsm):
        super().__init__(gsm)
        self.current_choice = 0
        self.font = None
        self.title_font = None
        self.show_warning = False

    def init(self):
        font_path = asset("fonts/upheavtt.ttf")
        self.font       = pygame.font.Font(font_path, 24)
        self.title_font = pygame.font.Font(font_path, 36)
        self.small_font = pygame.font.Font(font_path, 12)
        self.current_choice = 0
        self.show_warning = False

    # --- helpers ----------------------------------------------------------

    def _modes(self):
        """Return list of (label, internal_name, unlocked) tuples in display order."""
        return [
            ("Normal Mode",   "normal",   True),
            ("Demon Mode",    "demon",    self.gsm.demon_mode_unlocked),
            ("Hardcore",      "hardcore", self.gsm.hardcore_unlocked),
            ("HC Demon Mode", "hc_demon", self.gsm.hc_demon_unlocked),
        ]

    def _selectable_indices(self):
        return [i for i, (_, __, unlocked) in enumerate(self._modes()) if unlocked]

    # --- update -----------------------------------------------------------

    def update(self):
        ih = self.gsm.input_handler

        if self.show_warning:
            if ih.is_pressed(ih.BUTTON1) or ih.is_pressed(ih.BUTTON3):
                self.show_warning = False
                self._launch_game("hc_demon")
            if ih.is_pressed(ih.BUTTON2):
                self.show_warning = False
            return

        selectable = self._selectable_indices()

        if ih.is_pressed(ih.UP) or ih.is_pressed(ih.W):
            idx = selectable.index(self.current_choice) if self.current_choice in selectable else 0
            self.current_choice = selectable[(idx - 1) % len(selectable)]

        if ih.is_pressed(ih.DOWN) or ih.is_pressed(ih.S):
            idx = selectable.index(self.current_choice) if self.current_choice in selectable else 0
            self.current_choice = selectable[(idx + 1) % len(selectable)]

        if ih.is_pressed(ih.BUTTON1) or ih.is_pressed(ih.BUTTON3):
            modes = self._modes()
            label, internal, unlocked = modes[self.current_choice]
            if unlocked:
                if internal == "hc_demon":
                    self.show_warning = True
                else:
                    self._start_game(label)

        if ih.is_pressed(ih.BUTTON2):
            self.gsm.set_state(self.gsm.MENU_STATE)

    def _start_game(self, mode_label):
        mode_map = {
            "Normal Mode": "normal",
            "Demon Mode":  "demon",
            "Hardcore":    "hardcore",
        }
        self._launch_game(mode_map[mode_label])

    def _launch_game(self, internal_mode):
        lives_map = {"normal": 5, "demon": 5, "hardcore": 1, "hc_demon": 10}
        self.gsm.current_mode = internal_mode
        self.gsm.set_score(0)
        self.gsm.set_lives(lives_map[internal_mode])
        self.gsm.run_coins_collected = 0
        self.gsm.run_coins_total = 0
        self.gsm.level_checkpoint = None
        self.gsm._save_progress()
        self.gsm.set_state(self.gsm.ROLLIN2_LEVEL1_STATE)

    # --- draw -------------------------------------------------------------

    def draw(self, surface):
        surface.fill((20, 20, 40))

        title = self.title_font.render("Select Mode", True, (255, 255, 100))
        surface.blit(title, title.get_rect(center=(160, 50)))

        modes = self._modes()
        start_y = 90
        spacing = 34

        for i, (label, internal, unlocked) in enumerate(modes):
            is_hc_demon = (internal == "hc_demon")
            is_selected = (i == self.current_choice)

            if not unlocked:
                display = "???"
                color = (180, 0, 0) if is_hc_demon else (80, 80, 80)
            elif is_selected:
                display = label
                color = (255, 80, 80) if is_hc_demon else (255, 255, 255)
            else:
                display = label
                color = (180, 40, 40) if is_hc_demon else (150, 150, 150)

            text = self.font.render(display, True, color)
            rect = text.get_rect(center=(160, start_y + i * spacing))

            if is_selected and unlocked:
                ind_color = (255, 80, 80) if is_hc_demon else (255, 255, 100)
                indicator = self.font.render(">", True, ind_color)
                surface.blit(indicator, indicator.get_rect(right=rect.left - 10, centery=rect.centery))

            surface.blit(text, rect)

        hint = self.small_font.render("ESC - Back", True, (80, 80, 80))
        surface.blit(hint, hint.get_rect(center=(160, 225)))

        if self.show_warning:
            self._draw_warning(surface)

    def _draw_warning(self, surface):
        overlay = pygame.Surface((320, 240))
        overlay.set_alpha(220)
        overlay.fill((10, 0, 0))
        surface.blit(overlay, (0, 0))

        font_path = asset("fonts/upheavtt.ttf")
        warn_font = pygame.font.Font(font_path, 18)
        body_font = pygame.font.Font(font_path, 11)

        title_surf = warn_font.render("WARNING", True, (255, 40, 40))
        surface.blit(title_surf, title_surf.get_rect(center=(160, 32)))

        para1 = [
            "This mode is extremely challenging.",
            "If you beat it and send me your",
            "completed save file as proof,",
            "I will Venmo you $5.",
            "It is possible. I've done it.",
        ]
        para2 = [
            "You do not have to collect all coins",
            "to receive the Venmo. Just beat it.",
        ]

        y = 58
        for line in para1:
            surf = body_font.render(line, True, (220, 220, 220))
            surface.blit(surf, surf.get_rect(center=(160, y)))
            y += 14

        y += 6  # gap between paragraphs
        for line in para2:
            surf = body_font.render(line, True, (255, 200, 80))
            surface.blit(surf, surf.get_rect(center=(160, y)))
            y += 14

        enter_surf = body_font.render("ENTER - Start   ESC - Back", True, (120, 120, 120))
        surface.blit(enter_surf, enter_surf.get_rect(center=(160, 228)))
