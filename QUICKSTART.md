# Quick Start Guide - Rollin' 2

## Running the Game

### Option 1: Use the launcher script (easiest)
```bash
./run.sh
```

### Option 2: Direct Python
```bash
python3 src/game.py
```

### Option 3: With virtual environment
```bash
# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the game
python src/game.py
```

## What's Playable Right Now

✅ **Fully Functional:**
- **Level 1** - Complete playable level with:
  - Coin collection
  - Three enemy types (Slimes, Bats, Wasps)
  - Moving platforms (vertical and horizontal)
  - Spike hazards
  - Parallax scrolling backgrounds
  - HP system (3 hearts)
  - Lives system
  - Score tracking
  - Death screen with restart
  - Win screen
- **Menu System** - Navigate with arrow keys/WASD, Enter to select
- **Pause** - Press ESC during gameplay
- **60 FPS** gameplay with smooth physics

## Controls

**Menu:**
- Arrow Keys / WASD: Navigate
- Enter: Select option
- ESC: Back/Quit

**In-Game:**
- Left/Right or A/D: Move
- Space: Jump
- Shift: Glide (hold while falling)
- ESC: Pause

## Architecture Overview

```
Main Game Loop (game.py) - 60 FPS
    ↓
GameStateManager - Manages state transitions
    ↓
Current State (MenuState / LevelState)
    ↓
Update Logic → Draw to Buffer → Scale & Display
    ↓
Input Handler → Audio Manager → Collision Handler
```

## Key Systems

### Entity System
- **Player** - Physics-based movement with jumping/gliding
- **Enemies** - Slime (patrol), Bat (zigzag), Wasp (sin wave)
- **Coins** - Animated collectibles
- **Spikes** - Static hazards

### Tilemap System
- Tiled map editor integration (.tmj JSON format)
- 32x32 pixel tiles
- Collision detection with 4-corner testing
- Entity spawning from object layers

### Level Design Workflow
1. Create map in Tiled (32x32 tiles)
2. Add layers: Collision, Coin, Spike, Slime, Bat, Wasp, VerticalPlatform, HorizontalPlatform
3. Create level state class inheriting from `LevelState`
4. Call spawn methods in `init()`

## Next Steps for Development

**To add more levels:**
1. Design level in Tiled Map Editor
2. Create new level state class (copy `level_1_state.py`)
3. Add state to GameStateManager
4. Update menu to access new level

**Future enhancements:**
- Boss battles
- Power-ups
- More enemy types
- Level select screen
- Save system

## File Structure (Simplified)

```
Rollin2/
├── run.sh                    # Launcher script
├── requirements.txt          # pygame dependency
├── README.md                 # Full documentation
├── QUICKSTART.md            # This file
├── src/
│   ├── game.py              # Main entry point
│   ├── game_states/         # Menu, levels, pause
│   ├── entities/            # Player, enemies, coins
│   ├── tilemap/             # Map loading, platforms
│   ├── handlers/            # Input, audio, collision
│   └── graphics/            # Animation system
├── assets/
│   ├── sprites/             # Character & enemy graphics
│   ├── tilesets/            # Tile graphics
│   ├── backgrounds/         # Parallax layers
│   ├── audio/               # Music & sound effects
│   ├── maps/                # Tiled .tmj files
│   └── fonts/               # Game fonts
└── venv/                    # Virtual environment (optional)
```

## Common Issues

**Problem:** `ModuleNotFoundError: No module named 'pygame'`
**Solution:** Install pygame:
```bash
pip install pygame
```

**Problem:** Music or sound not playing
**Solution:** Check that audio files exist in `assets/audio/` and are in the correct format (WAV/MP3)

**Problem:** Level won't load / crashes on start
**Solution:** Verify the Tiled map file exists and has the required layers (Collision, Coin, etc.)

## Development Tips

- 60 FPS frame-independent physics using delta time (16.67ms per frame)
- Internal resolution: 320x240 (retro style), scaled 2x for display
- Use `is_pressed()` for one-time actions, `is_down()` for continuous
- All entities spawn from Tiled map layers (data-driven design)
- Player has 3 HP (hearts), loses 1 per hit with invincibility frames
- Gliding reduces fall speed by 90% - hold Shift while falling

## Performance

Runs at 60 FPS with low CPU usage (~2-5%). Tested on Linux with pygame 2.5+.
