import pygame
import os


class Spike:
    """Damaging spike entity"""

    def __init__(self, tilemap):
        from .animation import Animation

        self.tilemap = tilemap

        # Position
        self.x = 0
        self.y = 0

        # Size
        self.width = 32
        self.height = 32

        # Collision dimensions (spike only occupies bottom 14 pixels visually)
        # and is offset 9 pixels from left, 7 pixels from right (so 16 pixels wide)
        self.collision_width = 16
        self.collision_height = 14
        self.collision_offset_x = 1  # Offset 1 pixel to the right to account for 9px left, 7px right

        # Animation
        self.animation = Animation()
        self.animation.set_delay(100)  # 100ms per frame

        # Load sprite sheet and create frames
        self.sprite_sheet = None
        self._load_sprite_sheet()

    def _load_sprite_sheet(self):
        """Load spike sprite sheet and extract individual frames"""
        sprite_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "../../assets/sprites/spike.png")
        )

        if not os.path.exists(sprite_path):
            print("Error: Could not find spike.png")
            return

        try:
            self.sprite_sheet = pygame.image.load(sprite_path).convert_alpha()

            # Extract 12 frames from the sprite sheet (assumes 384x32 for 12x32x32 frames)
            # Each frame is 32x32
            frames = []
            for i in range(12):
                frame_rect = pygame.Rect(i * 32, 0, 32, 32)
                frame = self.sprite_sheet.subsurface(frame_rect).copy()
                frames.append(frame)

            self.animation.set_frames(frames)
        except Exception as e:
            print(f"Error loading spike sprite sheet: {e}")

    def set_position(self, x, y):
        """Set the spike's position"""
        self.x, self.y = x, y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def update(self, dt):
        """Update animation"""
        self.animation.update(dt)

    def draw(self, surface):
        """Draw the spike with current animation frame"""
        current_frame = self.animation.get_image()
        if current_frame is None:
            return

        draw_x = int(self.x - self.width / 2 + self.tilemap.get_x())
        draw_y = int(self.y - self.height / 2 + self.tilemap.get_y())
        surface.blit(current_frame, (draw_x, draw_y))
