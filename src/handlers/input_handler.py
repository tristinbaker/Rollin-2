"""
InputHandler - equivalent to MyInput.java
Handles keyboard input with previous/current state tracking
for detecting key presses vs key holds
"""
import pygame


class InputHandler:
    """
    Static-like input handler that tracks key states
    Provides is_down() for continuous and is_pressed() for one-time events
    """

    # Key mappings (matching Java original)
    NUM_KEYS = 12

    # Key indices
    BUTTON1 = 0  # Enter
    BUTTON2 = 1  # Escape
    BUTTON3 = 2  # Space
    BUTTON4 = 3  # Shift

    UP = 4
    LEFT = 5
    DOWN = 6
    RIGHT = 7

    W = 8
    A = 9
    S = 10
    D = 11

    def __init__(self):
        # Current and previous key states
        self.keys = [False] * self.NUM_KEYS
        self.prev_keys = [False] * self.NUM_KEYS

    def update(self):
        """
        Update input state - call once per frame
        Saves current keys to previous before updating
        """
        # Save current state to previous
        self.prev_keys = self.keys.copy()

        # Get current pygame key state
        pygame_keys = pygame.key.get_pressed()

        # Update key states
        self.keys[self.BUTTON1] = pygame_keys[pygame.K_RETURN]
        self.keys[self.BUTTON2] = pygame_keys[pygame.K_ESCAPE]
        self.keys[self.BUTTON3] = pygame_keys[pygame.K_SPACE]
        self.keys[self.BUTTON4] = pygame_keys[pygame.K_LSHIFT] or pygame_keys[pygame.K_RSHIFT]

        self.keys[self.UP] = pygame_keys[pygame.K_UP]
        self.keys[self.LEFT] = pygame_keys[pygame.K_LEFT]
        self.keys[self.DOWN] = pygame_keys[pygame.K_DOWN]
        self.keys[self.RIGHT] = pygame_keys[pygame.K_RIGHT]

        self.keys[self.W] = pygame_keys[pygame.K_w]
        self.keys[self.A] = pygame_keys[pygame.K_a]
        self.keys[self.S] = pygame_keys[pygame.K_s]
        self.keys[self.D] = pygame_keys[pygame.K_d]

    def is_down(self, key_code):
        """
        Check if key is currently held down
        Use for continuous actions (e.g., movement)
        """
        if 0 <= key_code < self.NUM_KEYS:
            return self.keys[key_code]
        return False

    def is_pressed(self, key_code):
        """
        Check if key was just pressed this frame
        Use for one-time actions (e.g., menu selection, jumping)
        Returns True only on the frame the key was first pressed
        """
        if 0 <= key_code < self.NUM_KEYS:
            return self.keys[key_code] and not self.prev_keys[key_code]
        return False

    def is_up_or_down(self):
        """Check if either up key is pressed"""
        return self.is_down(self.UP) or self.is_down(self.W)

    def is_left_or_right(self):
        """Check if either horizontal key is pressed"""
        return (self.is_down(self.LEFT) or self.is_down(self.A) or
                self.is_down(self.RIGHT) or self.is_down(self.D))

    def get_horizontal_input(self):
        """
        Get horizontal input direction
        Returns: -1 (left), 0 (none), 1 (right)
        """
        left = self.is_down(self.LEFT) or self.is_down(self.A)
        right = self.is_down(self.RIGHT) or self.is_down(self.D)

        if left and not right:
            return -1
        elif right and not left:
            return 1
        return 0

    def get_vertical_input(self):
        """
        Get vertical input direction
        Returns: -1 (up), 0 (none), 1 (down)
        """
        up = self.is_down(self.UP) or self.is_down(self.W)
        down = self.is_down(self.DOWN) or self.is_down(self.S)

        if up and not down:
            return -1
        elif down and not up:
            return 1
        return 0
