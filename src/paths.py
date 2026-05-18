"""
Centralised asset path resolution.

Works both when running from source and when frozen by PyInstaller:
  - Source:  paths are resolved relative to this file (src/paths.py → project root)
  - Frozen:  sys._MEIPASS is the extraction root; assets are bundled there
"""
import os
import sys


def _assets_root():
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "assets")
    # Running from source: src/ → ../ → project root → assets/
    return os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets"))


def _save_root():
    """Directory where save.json should live."""
    if hasattr(sys, "_MEIPASS"):
        # Place save file next to the executable, not inside the bundle
        return os.path.dirname(sys.executable)
    return os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def asset(*parts):
    """Return the absolute path to an asset file/directory."""
    return os.path.normpath(os.path.join(_assets_root(), *parts))


def save_file(name="save.json"):
    """Return the absolute path to a save/config file in the user-writable root."""
    return os.path.normpath(os.path.join(_save_root(), name))
