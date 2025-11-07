import pygame
import os
import math
from entities.enemy import Enemy


class Wasp(Enemy):
    """Wasp enemy - floats until player approaches, then flies left in a sin wave"""

    def __init__(self, tilemap, color="black"):
        super().__init__(tilemap)

        # Wasp size (32x32 per frame)
        self.width = 32
        self.height = 32
        self.cwidth = 24  # Collision width
        self.cheight = 24  # Collision height

        # Color
        self.color = color

        # Movement - varies by color
        self.speed = 1.5  # Horizontal speed when flying

        # Set amplitude and frequency based on color
        color_properties = {
            "black": {"amplitude": 30, "frequency": 0.5},
            "orange": {"amplitude": 40, "frequency": 0.7},
            "red": {"amplitude": 25, "frequency": 0.6},
            "yellow": {"amplitude": 35, "frequency": 0.4}
        }

        props = color_properties.get(color, {"amplitude": 30, "frequency": 0.5})
        self.amplitude = props["amplitude"]  # Height of sin wave
        self.frequency = props["frequency"]  # How quickly it oscillates (cycles per second)

        # State
        self.state = "idle"  # "idle" or "flying"
        self.activation_distance = 320 + 50  # Activate just before scrolling on screen (screen width + buffer)
        self.start_y = 0  # Store starting Y position
        self.time = 0  # Time counter for sin wave

        # Load sprites
        self._load_sprites()

    def _load_sprites(self):
        """Load wasp sprite sheet"""
        sprite_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), f"../../assets/sprites/wasp_{self.color}.png")
        )

        if not os.path.exists(sprite_path):
            print(f"Error: Could not find wasp_{self.color}.png")
            return

        try:
            sprite_sheet = pygame.image.load(sprite_path).convert_alpha()

            # Wasp: 4 frames (32x32 each)
            sprite_width = 32
            sprite_height = 32
            num_frames = 4

            self.sprites = [
                sprite_sheet.subsurface((i * sprite_width, 0, sprite_width, sprite_height)).copy()
                for i in range(num_frames)
            ]

            self.animation.set_frames(self.sprites)
            self.animation.set_delay(100)  # 100ms per frame for animation
        except Exception as e:
            print(f"Error loading wasp sprites: {e}")

    def set_position(self, x, y):
        """Set wasp position and store starting Y"""
        super().set_position(x, y)
        self.start_y = y

    def update(self, dt, spikes=None, moving_platforms=None):
        """Update wasp"""
        # Update animation
        super().update(dt)

        # Get player position (approximate from tilemap offset)
        # Player is typically at screen center (x=160), so player_x = 160 - tilemap.x
        player_x = 160 - self.tilemap.get_x()

        if self.state == "idle":
            # Check if player is close enough to activate
            distance_to_player = self.x - player_x
            if distance_to_player <= self.activation_distance:
                self.state = "flying"
                self.time = 0

        elif self.state == "flying":
            # Fly left in a sin wave
            self.x -= self.speed
            self.time += dt / 1000.0  # Convert to seconds

            # Calculate Y position using sin wave
            self.y = self.start_y + math.sin(self.time * self.frequency * 2 * math.pi) * self.amplitude

    def draw(self, surface):
        """Draw the wasp (facing left when flying)"""
        image = self.animation.get_image()
        if image is None:
            return

        # Flip sprite to face left when flying
        if self.state == "flying":
            image = pygame.transform.flip(image, True, False)

        draw_x = int(self.x - self.width / 2 + self.tilemap.get_x())
        draw_y = int(self.y - self.height / 2 + self.tilemap.get_y())
        surface.blit(image, (draw_x, draw_y))
