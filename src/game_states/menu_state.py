"""
MenuState - equivalent to MenuState.java
Main menu with options to start game, view help, or quit
"""
import pygame
import os
from paths import asset
from game_states.game_state import GameState


class MenuState(GameState):
    def __init__(self, gsm):
        super().__init__(gsm)
        self.current_choice = 0
        self.options = []
        self.font = None
        self.title_font = None
        self.music_loaded = False
        self.bg_layers = []   # list of (surface, scroll_speed)
        self.bg_scroll = 0.0
        self._bg_loaded = False

    def _load_backgrounds(self):
        bg_dir = asset("backgrounds/main_menu")
        # Speeds for layers 1-6: layer 1 is closest (fastest), 6 is furthest (slowest)
        speeds = [0.5, 0.4, 0.3, 0.2, 0.15, 0.08]
        self.bg_layers = []
        for i, speed in enumerate(speeds, start=1):
            path = os.path.join(bg_dir, f"{i}.png")
            if not os.path.exists(path):
                continue
            img = pygame.image.load(path).convert_alpha()
            # Scale to fill screen height; keep aspect so it can tile/scroll horizontally
            aspect = img.get_width() / img.get_height()
            w = max(320, int(240 * aspect) + 1)
            img = pygame.transform.scale(img, (w, 240))
            self.bg_layers.append((img, speed))
        self._bg_loaded = True

    def init(self):
        font_path = asset("fonts/upheavtt.ttf")
        self.font = pygame.font.Font(font_path, 24)
        self.title_font = pygame.font.Font(font_path, 48)
        self.current_choice = 0

        if not self._bg_loaded:
            self._load_backgrounds()

        # Build option list dynamically based on save/unlock state
        self.options = ["Play"]
        if self.gsm.save_slot is not None:
            self.options.append("Load Game")
        if self.gsm.level_checkpoint is not None:
            self.options.append("Continue")
        if self.gsm.rollin1_unlocked:
            self.options.append("Rollin 1")
        self.options += ["Options", "Quit"]

        if not self.music_loaded:
            audio = self.gsm.audio_manager
            audio.load_music("menu", "mainTheme.wav")
            self.music_loaded = True

        self.gsm.audio_manager.play_music("menu", loops=-1, fade_ms=1000)

    def update(self):
        self.bg_scroll += 1.0

        input_handler = self.gsm.input_handler

        if input_handler.is_pressed(input_handler.UP) or input_handler.is_pressed(input_handler.W):
            self.current_choice -= 1
            if self.current_choice < 0:
                self.current_choice = len(self.options) - 1

        if input_handler.is_pressed(input_handler.DOWN) or input_handler.is_pressed(input_handler.S):
            self.current_choice += 1
            if self.current_choice >= len(self.options):
                self.current_choice = 0

        if input_handler.is_pressed(input_handler.BUTTON1) or input_handler.is_pressed(input_handler.BUTTON3):
            self.select()

    def select(self):
        option = self.options[self.current_choice]
        if option == "Play":
            self.gsm.set_state(self.gsm.MODE_SELECT_STATE)
        elif option == "Load Game":
            slot = self.gsm.save_slot
            self.gsm.set_score(slot['score'])
            self.gsm.set_lives(slot['lives'])
            self.gsm.run_coins_collected = slot['run_coins_collected']
            self.gsm.run_coins_total = slot['run_coins_total']
            self.gsm.pending_load = slot
            self.gsm.clear_save()
            self.gsm.set_state(slot['level_state'])
        elif option == "Continue":
            chk = self.gsm.level_checkpoint
            self.gsm.current_mode = chk["mode"]
            self.gsm.set_lives(chk["lives"])
            self.gsm.set_state(chk["state"])
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
        # Draw parallax background layers furthest-first (index 5 → 0)
        if self.bg_layers:
            for img, speed in reversed(self.bg_layers):
                w = img.get_width()
                offset = int(self.bg_scroll * speed) % w
                surface.blit(img, (-offset, 0))
                # Tile a second copy to fill the gap when scrolling
                if w - offset < 320:
                    surface.blit(img, (w - offset, 0))
        else:
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

            if i == self.current_choice:
                indicator = self.font.render(">", True, (255, 255, 100))
                indicator_rect = indicator.get_rect(right=rect.left - 10, centery=rect.centery)
                surface.blit(indicator, indicator_rect)

            surface.blit(text, rect)
