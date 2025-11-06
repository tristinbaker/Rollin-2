"""
Base GameState class - equivalent to GameState.java
All game states inherit from this
"""


class GameState:
    """Abstract base class for all game states"""

    def __init__(self, gsm):
        self.gsm = gsm

    def init(self):
        """Initialize the state (called when state is entered)"""
        pass

    def update(self):
        """Update game logic"""
        pass

    def draw(self, surface):
        """Draw to the game surface"""
        pass

    def handle_input(self, keys):
        """Handle keyboard input"""
        pass
