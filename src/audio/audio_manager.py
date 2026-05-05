"""
AudioManager - equivalent to Audio.java
Handles music and sound effect playback using pygame.mixer
"""
import pygame
import os


class AudioManager:
    """
    Manages audio playback for music and sound effects
    """

    def __init__(self):
        """Initialize the audio system"""
        # Initialize pygame mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

        # Audio storage
        self.music_clips = {}
        self.sound_effects = {}
        self.sound_relative_volumes = {}  # Store relative volumes for each sound

        # Current music state
        self.current_music = None
        self.music_volume = 0.5  # 0% volume by default (for testing)
        self.sfx_volume = 0.7    # 70% volume by default

        # Base path for audio files
        self.audio_path = self._find_audio_path()

    def _find_audio_path(self):
        """Find the audio assets directory"""
        # Try multiple possible locations
        possible_paths = [
            "../../assets/audio/",        # Python project assets (priority)
            "../assets/audio/",           # If assets copied to Python project
            "../../res/Audio/",           # Relative to src directory
            "../../../res/Audio/",        # From deeper directory
        ]

        for path in possible_paths:
            full_path = os.path.join(os.path.dirname(__file__), path)
            full_path = os.path.normpath(full_path)
            if os.path.exists(full_path):

                return full_path

        # Default fallback
        return os.path.normpath(os.path.join(os.path.dirname(__file__), "../../assets/audio/"))

    def load_music(self, name, filename):
        """
        Load a music track (for background music)

        Args:
            name: Internal name for the music
            filename: Filename of the audio file
        """
        filepath = os.path.join(self.audio_path, filename)

        if os.path.exists(filepath):
            self.music_clips[name] = filepath

        else:
            print(f"Warning: Music file not found: {filepath}")

    def load_sound(self, name, filename, relative_volume=1.0):
        """
        Load a sound effect

        Args:
            name: Internal name for the sound
            filename: Filename of the audio file
            relative_volume: Relative volume for this sound (0.0 to 1.0), multiplied with global SFX volume
        """
        filepath = os.path.join(self.audio_path, filename)

        if os.path.exists(filepath):
            try:
                sound = pygame.mixer.Sound(filepath)
                self.sound_relative_volumes[name] = relative_volume
                sound.set_volume(self.sfx_volume * relative_volume)
                self.sound_effects[name] = sound

            except Exception as e:
                print(f"Error loading sound {filename}: {e}")
        else:
            print(f"Warning: Sound file not found: {filepath}")

    def play_music(self, name, loops=-1, fade_ms=0):
        """
        Play a music track

        Args:
            name: Name of the music to play
            loops: Number of times to loop (-1 = infinite)
            fade_ms: Fade in time in milliseconds
        """
        if name not in self.music_clips:
            print(f"Warning: Music '{name}' not loaded")
            return

        # Stop current music if playing
        if pygame.mixer.music.get_busy():
            self.stop_music(fade_ms=fade_ms)

        # Load and play the music
        try:
            pygame.mixer.music.load(self.music_clips[name])
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
            self.current_music = name

        except Exception as e:
            print(f"Error playing music {name}: {e}")

    def stop_music(self, fade_ms=0):
        """
        Stop the currently playing music

        Args:
            fade_ms: Fade out time in milliseconds
        """
        if pygame.mixer.music.get_busy():
            if fade_ms > 0:
                pygame.mixer.music.fadeout(fade_ms)
            else:
                pygame.mixer.music.stop()
            self.current_music = None

    def pause_music(self):
        """Pause the currently playing music"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()

    def resume_music(self):
        """Resume paused music"""
        pygame.mixer.music.unpause()

    def play_sound(self, name):
        """
        Play a sound effect

        Args:
            name: Name of the sound to play
        """
        if name in self.sound_effects:
            self.sound_effects[name].play()
        else:
            print(f"Warning: Sound '{name}' not loaded")

    def set_music_volume(self, volume):
        """
        Set music volume

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def set_sfx_volume(self, volume):
        """
        Set sound effects volume

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
        for name, sound in self.sound_effects.items():
            relative_vol = self.sound_relative_volumes.get(name, 1.0)
            sound.set_volume(self.sfx_volume * relative_vol)

    def get_music_volume(self):
        """Get current music volume"""
        return self.music_volume

    def get_sfx_volume(self):
        """Get current sound effects volume"""
        return self.sfx_volume

    def is_music_playing(self):
        """Check if music is currently playing"""
        return pygame.mixer.music.get_busy()

    def cleanup(self):
        """Clean up audio resources"""
        pygame.mixer.music.stop()
        pygame.mixer.quit()
