"""
Main game class - equivalent to GamePanel.java
Handles the core game loop, rendering, and updates
"""
import pygame
from game_states.game_state_manager import GameStateManager
from handlers.input_handler import InputHandler
from audio.audio_manager import AudioManager


class Game:
    # Display constants (matching Java original)
    GAME_WIDTH = 320
    GAME_HEIGHT = 240
    SCALE = 2
    WINDOW_WIDTH = GAME_WIDTH * SCALE  # 640
    WINDOW_HEIGHT = GAME_HEIGHT * SCALE  # 480

    # Game loop constants
    TARGET_FPS = 60
    TARGET_TIME = 1000 // TARGET_FPS  # ~16.67ms per frame

    def __init__(self):
        pygame.init()

        # Create resizable window
        self.window = pygame.display.set_mode(
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT),
            pygame.RESIZABLE
        )
        pygame.display.set_caption("Rollin' - Python Edition")

        # Create game surface (internal resolution - always 320x240)
        self.game_surface = pygame.Surface((self.GAME_WIDTH, self.GAME_HEIGHT))

        # Clock for frame timing
        self.clock = pygame.time.Clock()

        # Input handler
        self.input_handler = InputHandler()

        # Audio manager
        self.audio_manager = AudioManager()

        # Game state manager
        self.gsm = GameStateManager(self.input_handler, self.audio_manager)

        # Game state
        self.running = True

    def update(self):
        """Update game logic"""
        self.gsm.update()

    def draw(self):
        """Draw to game surface"""
        # Clear surface
        self.game_surface.fill((0, 0, 0))

        # Draw current game state
        self.gsm.draw(self.game_surface)

    def draw_to_screen(self):
        """Scale game surface to window and display, maintaining aspect ratio"""
        # Get current window size
        window_width, window_height = self.window.get_size()

        # Calculate aspect ratios
        game_aspect = self.GAME_WIDTH / self.GAME_HEIGHT  # 320/240 = 4/3
        window_aspect = window_width / window_height

        # Calculate scaled size maintaining aspect ratio
        if window_aspect > game_aspect:
            # Window is wider - fit to height
            scaled_height = window_height
            scaled_width = int(scaled_height * game_aspect)
        else:
            # Window is taller - fit to width
            scaled_width = window_width
            scaled_height = int(scaled_width / game_aspect)

        # Calculate position to center the game
        x_offset = (window_width - scaled_width) // 2
        y_offset = (window_height - scaled_height) // 2

        # Scale the game surface
        scaled_surface = pygame.transform.scale(
            self.game_surface,
            (scaled_width, scaled_height)
        )

        # Clear window with black bars
        self.window.fill((0, 0, 0))

        # Draw centered scaled surface
        self.window.blit(scaled_surface, (x_offset, y_offset))
        pygame.display.flip()

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def run(self):
        """Main game loop - equivalent to GamePanel.run()"""
        print("Game starting...")
        print(f"Window size: {self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        print(f"Game resolution: {self.GAME_WIDTH}x{self.GAME_HEIGHT}")
        print(f"Target FPS: {self.TARGET_FPS}")

        while self.running:
            # Handle events
            self.handle_events()

            # Update input state
            self.input_handler.update()

            # Update game state
            self.update()

            # Draw game
            self.draw()

            # Scale and display
            self.draw_to_screen()

            # Maintain target FPS
            self.clock.tick(self.TARGET_FPS)

        # Cleanup
        self.audio_manager.cleanup()
        pygame.quit()
        print("Game ended.")


def main():
    """Entry point"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
