import pygame
import os


class PingPongAnimation:
    """Animation that plays forward then backward (ping-pong)"""

    def __init__(self):
        """Initialize animation"""
        self.frames = []
        self.current_frame = 0
        self.delay = 100  # milliseconds per frame
        self.time_elapsed = 0
        self.direction = 1  # 1 for forward, -1 for backward

    def set_frames(self, frames):
        """Set animation frames"""
        self.frames = frames
        self.current_frame = 0
        self.direction = 1

    def set_delay(self, delay):
        """Set delay between frames"""
        self.delay = delay

    def update(self, dt):
        """Update animation with ping-pong behavior"""
        if self.delay == -1:
            return

        self.time_elapsed += dt

        if self.time_elapsed >= self.delay:
            self.time_elapsed = 0
            self.current_frame += self.direction

            # Change direction at the ends
            if self.current_frame >= len(self.frames):
                self.current_frame = len(self.frames) - 2
                self.direction = -1
            elif self.current_frame < 0:
                self.current_frame = 1
                self.direction = 1

    def get_image(self):
        """Get current frame image"""
        if len(self.frames) == 0:
            return None
        return self.frames[self.current_frame]


class Lava:
    """Lava tile entity - animated lava with different animations for top and bottom rows"""

    def __init__(self, tilemap, is_top=False):
        self.tilemap = tilemap
        self.is_top = is_top  # True if this is the topmost lava in a column

        # Position
        self.x = 0
        self.y = 0

        # Size
        self.width = 32
        self.height = 32

        # Collision dimensions
        if is_top:
            # Top lava only has bottom 16 pixels as collision
            self.collision_width = 32
            self.collision_height = 16
        else:
            # Bottom lava is fully damaging
            self.collision_width = 32
            self.collision_height = 32

        # Animation (ping-pong style - goes forward then backward)
        self.animation = PingPongAnimation()
        self.animation.set_delay(100)  # 100ms per frame

        # Load sprites
        self._load_sprites()

    def _load_sprites(self):
        """Load lava sprite sheet"""
        sprite_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "../../assets/sprites/lava.png")
        )

        if not os.path.exists(sprite_path):
            print("Error: Could not find lava.png")
            return

        try:
            sprite_sheet = pygame.image.load(sprite_path).convert_alpha()

            # Extract 12 frames from the sprite sheet (384x64 for 12x32x32 frames)
            # Top row (y=0) for top lava, bottom row (y=32) for bottom lava
            frames = []
            row_offset = 0 if self.is_top else 32

            for i in range(12):
                frame_rect = pygame.Rect(i * 32, row_offset, 32, 32)
                frame = sprite_sheet.subsurface(frame_rect).copy()
                frames.append(frame)

            self.animation.set_frames(frames)
        except Exception as e:
            print(f"Error loading lava sprites: {e}")

    def set_position(self, x, y):
        """Set the lava's position"""
        self.x, self.y = x, y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def update(self, dt):
        """Update animation"""
        self.animation.update(dt)

    def draw(self, surface):
        """Draw the lava with current animation frame"""
        current_frame = self.animation.get_image()
        if current_frame is None:
            return

        draw_x = int(self.x - self.width / 2 + self.tilemap.get_x())
        draw_y = int(self.y - self.height / 2 + self.tilemap.get_y())
        surface.blit(current_frame, (draw_x, draw_y))
