import pygame
import os
from paths import asset


class Spike:
    """Damaging spike entity"""

    def __init__(self, tilemap):
        from .animation import Animation

        self.tilemap = tilemap

        # Position
        self.x = 0
        self.y = 0
        
        # Platform attachment
        self.attached_platform = None
        self.platform_offset_x = 0  # Offset from platform center
        self.platform_offset_y = 0  # Offset from platform center

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
        sprite_path = asset("sprites/spike.png")

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

    def attach_to_platform(self, platform):
        """Attach this spike to a moving platform"""
        if platform is None:
            self.attached_platform = None
            return
            
        self.attached_platform = platform
        # Calculate offset from platform center
        self.platform_offset_x = self.x - platform.get_x()
        self.platform_offset_y = self.y - platform.get_y()

    def find_and_attach_to_platform(self, moving_platforms):
        """Find if this spike should be attached to any moving platform"""
        if not moving_platforms:
            return
            
        # Check if spike is positioned on or very near a moving platform
        spike_bottom = self.y + self.height / 2
        
        for platform in moving_platforms:
            platform_top = platform.get_y() - platform.get_height() / 2
            platform_left = platform.get_x() - platform.get_width() / 2
            platform_right = platform.get_x() + platform.get_width() / 2
            
            # Check if spike is sitting on the platform (within tolerance)
            vertical_distance = abs(spike_bottom - platform_top)
            horizontal_on_platform = (self.x >= platform_left - 5 and 
                                    self.x <= platform_right + 5)
            
            if vertical_distance <= 2 and horizontal_on_platform:
                self.attach_to_platform(platform)
                # Adjust spike position to sit exactly on platform
                self.y = platform_top - self.height / 2
                break

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def update(self, dt):
        """Update animation and position if attached to platform"""
        self.animation.update(dt)
        
        # Update position if attached to a moving platform
        if self.attached_platform is not None:
            new_x = self.attached_platform.get_x() + self.platform_offset_x
            new_y = self.attached_platform.get_y() + self.platform_offset_y
            self.x = new_x
            self.y = new_y

    def draw(self, surface):
        """Draw the spike with current animation frame"""
        current_frame = self.animation.get_image()
        if current_frame is None:
            return

        draw_x = int(self.x - self.width / 2 + self.tilemap.get_x())
        draw_y = int(self.y - self.height / 2 + self.tilemap.get_y())
        surface.blit(current_frame, (draw_x, draw_y))
