"""
Animation - equivalent to Animation.java
Handles sprite animation with frame timing
"""
import pygame


class Animation:
    def __init__(self):
        """Initialize animation"""
        self.frames = []
        self.current_frame = 0
        self.delay = 100  # milliseconds per frame
        self.time_elapsed = 0
        self.played_once = False

    def set_frames(self, frames):
        """
        Set animation frames

        Args:
            frames: List of pygame.Surface images
        """
        self.frames = frames
        self.current_frame = 0
        self.played_once = False

    def set_delay(self, delay):
        """
        Set delay between frames

        Args:
            delay: Milliseconds per frame, or -1 to freeze on first frame
        """
        self.delay = delay

    def set_frame(self, frame):
        """
        Set current frame

        Args:
            frame: Frame index
        """
        if 0 <= frame < len(self.frames):
            self.current_frame = frame

    def update(self, dt):
        """
        Update animation

        Args:
            dt: Delta time in milliseconds
        """
        if self.delay == -1:
            return

        self.time_elapsed += dt

        if self.time_elapsed >= self.delay:
            self.time_elapsed = 0
            self.current_frame += 1

            if self.current_frame >= len(self.frames):
                self.current_frame = 0
                self.played_once = True

    def get_image(self):
        """Get current frame image"""
        if len(self.frames) == 0:
            return None
        return self.frames[self.current_frame]

    def has_played_once(self):
        """Check if animation has played through once"""
        return self.played_once
