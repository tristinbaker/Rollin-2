"""
OptionsState - Settings menu for adjusting audio volumes
Allows control of sound effects and music volume
"""
import pygame
from game_states.game_state import GameState


class OptionsState(GameState):
    def __init__(self, gsm):
        super().__init__(gsm)
        self.current_choice = 0
        self.options = ["Sound Effects", "Music", "Back"]
        self.font = None
        self.title_font = None
        self.return_state = None  # Track where to return to

        # Volume settings (0.0 to 1.0)
        self.sfx_volume = 1.0
        self.music_volume = 1.0

    def init(self):
        """Initialize options state"""
        # Initialize fonts
        import os
        font_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../assets/fonts/upheavtt.ttf"))
        self.font = pygame.font.Font(font_path, 24)
        self.title_font = pygame.font.Font(font_path, 36)
        self.current_choice = 0

        # Load current volumes from audio manager
        audio = self.gsm.audio_manager
        self.music_volume = audio.get_music_volume()
        self.sfx_volume = audio.get_sfx_volume()

    def set_return_state(self, state):
        """Set the state to return to when pressing Back"""
        self.return_state = state

    def update(self):
        """Update options logic"""
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

        # Handle left/right for volume adjustment
        if self.current_choice == 0:  # Sound Effects
            if input_handler.is_pressed(input_handler.LEFT) or input_handler.is_pressed(input_handler.A):
                self.sfx_volume = max(0.0, self.sfx_volume - 0.1)
                self.gsm.audio_manager.set_sfx_volume(self.sfx_volume)
            if input_handler.is_pressed(input_handler.RIGHT) or input_handler.is_pressed(input_handler.D):
                self.sfx_volume = min(1.0, self.sfx_volume + 0.1)
                self.gsm.audio_manager.set_sfx_volume(self.sfx_volume)

        elif self.current_choice == 1:  # Music
            if input_handler.is_pressed(input_handler.LEFT) or input_handler.is_pressed(input_handler.A):
                self.music_volume = max(0.0, self.music_volume - 0.1)
                self.gsm.audio_manager.set_music_volume(self.music_volume)
            if input_handler.is_pressed(input_handler.RIGHT) or input_handler.is_pressed(input_handler.D):
                self.music_volume = min(1.0, self.music_volume + 0.1)
                self.gsm.audio_manager.set_music_volume(self.music_volume)

        # Handle selection (Back button or ESC)
        if input_handler.is_pressed(input_handler.BUTTON1) or input_handler.is_pressed(input_handler.BUTTON3):  # Enter or Space
            if self.current_choice == 2:  # Back
                self._go_back()

        # ESC also goes back
        if input_handler.is_pressed(input_handler.BUTTON2):  # Escape
            self._go_back()

    def _go_back(self):
        """Return to the appropriate previous state"""
        if self.return_state is not None:
            # Return to where we came from (pause menu or main menu)
            self.gsm.set_state(self.return_state, init=False)
            self.return_state = None  # Reset
        else:
            # Default to main menu
            self.gsm.set_state(self.gsm.MENU_STATE)

    def draw(self, surface):
        """Draw options menu to surface"""
        # Background color
        surface.fill((20, 20, 40))

        # Draw title
        title_text = self.title_font.render("OPTIONS", True, (255, 255, 100))
        title_rect = title_text.get_rect(center=(160, 30))
        surface.blit(title_text, title_rect)

        # Draw options
        start_y = 60
        spacing = 65

        # Sound Effects
        sfx_text = self.font.render("Sound Effects", True, (255, 255, 255) if self.current_choice == 0 else (150, 150, 150))
        sfx_rect = sfx_text.get_rect(center=(160, start_y))
        surface.blit(sfx_text, sfx_rect)

        # Draw volume bar for SFX
        self._draw_volume_bar(surface, 160, start_y + 18, self.sfx_volume)

        # Selection indicator for SFX
        if self.current_choice == 0:
            indicator = self.font.render(">", True, (255, 255, 100))
            indicator_rect = indicator.get_rect(right=sfx_rect.left - 10, centery=sfx_rect.centery)
            surface.blit(indicator, indicator_rect)

        # Music
        music_text = self.font.render("Music", True, (255, 255, 255) if self.current_choice == 1 else (150, 150, 150))
        music_rect = music_text.get_rect(center=(160, start_y + spacing))
        surface.blit(music_text, music_rect)

        # Draw volume bar for Music
        self._draw_volume_bar(surface, 160, start_y + spacing + 18, self.music_volume)

        # Selection indicator for Music
        if self.current_choice == 1:
            indicator = self.font.render(">", True, (255, 255, 100))
            indicator_rect = indicator.get_rect(right=music_rect.left - 10, centery=music_rect.centery)
            surface.blit(indicator, indicator_rect)

        # Back button
        back_text = self.font.render("Back", True, (255, 255, 255) if self.current_choice == 2 else (150, 150, 150))
        back_rect = back_text.get_rect(center=(160, start_y + spacing * 2 + 10))
        surface.blit(back_text, back_rect)

        # Selection indicator for Back
        if self.current_choice == 2:
            indicator = self.font.render(">", True, (255, 255, 100))
            indicator_rect = indicator.get_rect(right=back_rect.left - 10, centery=back_rect.centery)
            surface.blit(indicator, indicator_rect)

    def _draw_volume_bar(self, surface, center_x, y, volume):
        """Draw a volume bar with the current volume level"""
        bar_width = 120
        bar_height = 12
        bar_x = center_x - bar_width // 2

        # Background bar (empty)
        pygame.draw.rect(surface, (60, 60, 60), (bar_x, y, bar_width, bar_height))

        # Filled bar (volume level)
        fill_width = int(bar_width * volume)
        if fill_width > 0:
            color = (100, 200, 100) if volume > 0 else (60, 60, 60)
            pygame.draw.rect(surface, color, (bar_x, y, fill_width, bar_height))

        # Border
        pygame.draw.rect(surface, (150, 150, 150), (bar_x, y, bar_width, bar_height), 1)

        # Volume percentage text
        volume_pct = int(volume * 100)
        volume_text = self.font.render(f"{volume_pct}%", True, (200, 200, 200))
        volume_rect = volume_text.get_rect(center=(center_x, y + bar_height + 12))
        surface.blit(volume_text, volume_rect)
