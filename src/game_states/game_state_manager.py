"""
GameStateManager - equivalent to GameStateManager.java
Manages game states and transitions between them
"""
from game_states.menu_state import MenuState
from game_states.rollin1.level1_state import Level1State as Rollin1Level1State
from game_states.rollin1.level2_state import Level2State as Rollin1Level2State
from game_states.rollin1.level3_state import Level3State as Rollin1Level3State
from game_states.rollin1.level4_state import Level4State as Rollin1Level4State
from game_states.rollin2.level_1_state import Level1State as Rollin2Level1State
from game_states.rollin2.level_2_state import Level2State as Rollin2Level2State
from game_states.options_state import OptionsState
from game_states.pause_state import PauseState


class GameStateManager:
    # State constants (matching Java original)
    MENU_STATE = 0
    LEVEL1_STATE = 1
    HELP_STATE = 2
    LEVEL2_STATE = 3
    PAUSE_STATE = 4
    CREDITS_STATE = 5
    LEVEL3_STATE = 6
    OVERWORLD1_STATE = 7
    OVERWORLD2_STATE = 8
    OVERWORLD3_STATE = 9
    OVERWORLD4_STATE = 10
    HARDMODE_STATE = 11
    GAMEOVER_STATE = 12
    OPTIONS_STATE = 13
    LEVEL4_STATE = 14  # Secret level
    ROLLIN2_LEVEL1_STATE = 15  # Rollin 2 Level 1
    ROLLIN2_LEVEL2_STATE = 16  # Rollin 2 Level 2

    def __init__(self, input_handler, audio_manager):
        # Input handler reference
        self.input_handler = input_handler

        # Audio manager reference
        self.audio_manager = audio_manager

        # Game state array
        self.game_states = [None] * 17  # Increased for ROLLIN2_LEVEL2_STATE

        # Global game variables
        self.score = 0
        self.lives = 5
        self.hard_mode = False

        # Current state
        self.current_state = self.MENU_STATE

        # Initialize states
        self._init_states()

    def _init_states(self):
        """Initialize all game states"""
        # Start with menu state only
        self.game_states[self.MENU_STATE] = MenuState(self)

        # Initialize the menu state
        if self.game_states[self.current_state]:
            self.game_states[self.current_state].init()

    def set_state(self, state, init=True):
        """Change to a different game state

        Args:
            state: The state to switch to
            init: Whether to call init() on the new state (default True)
        """
        if 0 <= state < len(self.game_states):
            self.current_state = state

            # Initialize state if it hasn't been created yet
            if self.game_states[state] is None:
                self._create_state(state)

            # Call init on the new state (unless init=False for resuming)
            if init and self.game_states[state]:
                self.game_states[state].init()

    def _create_state(self, state):
        """Lazy initialization of game states"""
        if state == self.LEVEL1_STATE:
            self.game_states[state] = Rollin1Level1State(self)
        elif state == self.LEVEL2_STATE:
            self.game_states[state] = Rollin1Level2State(self)
        elif state == self.LEVEL3_STATE:
            self.game_states[state] = Rollin1Level3State(self)
        elif state == self.LEVEL4_STATE:
            self.game_states[state] = Rollin1Level4State(self)
        elif state == self.ROLLIN2_LEVEL1_STATE:
            self.game_states[state] = Rollin2Level1State(self)
        elif state == self.ROLLIN2_LEVEL2_STATE:
            self.game_states[state] = Rollin2Level2State(self)
        elif state == self.OPTIONS_STATE:
            self.game_states[state] = OptionsState(self)
        elif state == self.PAUSE_STATE:
            self.game_states[state] = PauseState(self)
        # TODO: Create other states as needed

    def update(self):
        """Update current game state"""
        if self.game_states[self.current_state]:
            self.game_states[self.current_state].update()

    def draw(self, surface):
        """Draw current game state"""
        if self.game_states[self.current_state]:
            self.game_states[self.current_state].draw(surface)

    def get_score(self):
        """Get current score"""
        return self.score

    def set_score(self, score):
        """Set current score"""
        self.score = score

    def add_score(self, amount):
        """Add to current score"""
        self.score += amount

    def get_lives(self):
        """Get current lives"""
        return self.lives

    def set_lives(self, lives):
        """Set current lives"""
        self.lives = lives

    def lose_life(self):
        """Lose a life"""
        self.lives -= 1

    def is_hard_mode(self):
        """Check if hard mode is enabled"""
        return self.hard_mode

    def set_hard_mode(self, enabled):
        """Enable/disable hard mode"""
        self.hard_mode = enabled
