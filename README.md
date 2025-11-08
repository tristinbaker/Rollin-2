# Rollin' 2 - Python Edition

A Python/pygame reimagining of the original Java platformer game "Rollin'" - a college assignment from 10 years ago, rebuilt with modern game development practices and new content.

## Overview

Rollin' 2 is a 2D platformer featuring:
- Multiple levels with increasing difficulty
- Coin collection mechanics
- Enemy variety (Slimes, Bats, Wasps)
- Moving platforms (vertical and horizontal)
- Lives and HP system
- Parallax scrolling backgrounds
- Dynamic Tiled-based level design

## Project Status

**Current Implementation:**
- ✅ Core game loop (60 FPS, 320x240 internal resolution, 2x scaling)
- ✅ State machine architecture (GameStateManager)
- ✅ Input handling system (keyboard with press/hold detection)
- ✅ Menu state with navigation
- ✅ Level 1 fully implemented and playable
- ✅ Player physics with jumping and gliding
- ✅ Tile-based collision detection
- ✅ Coin collection system with scoring
- ✅ Audio system with music and sound effects
- ✅ Entity system (enemies, coins, spikes)
- ✅ Moving platform system
- ✅ Parallax background system
- ✅ HUD with HP, lives, score, and coin counter
- ✅ Tiled map editor integration (.tmj format)
- ✅ Death and win screens

This is a **fully playable game** with Level 1 complete. The architecture is designed for easy level expansion.

## Technical Details

### Architecture

```
Rollin2/
├── src/
│   ├── game.py                           # Main game loop (60 FPS)
│   ├── game_states/
│   │   ├── game_state.py                 # Base class for all states
│   │   ├── game_state_manager.py         # State machine manager
│   │   ├── menu_state.py                 # Main menu
│   │   ├── level_state.py                # Base class for levels
│   │   └── rollin2/
│   │       └── level_1_state.py          # Level 1 implementation
│   ├── handlers/
│   │   ├── input_handler.py              # Keyboard input system
│   │   ├── audio_manager.py              # Music and sound effects
│   │   └── player_collision_handler.py   # Player collision logic
│   ├── entities/
│   │   ├── entity.py                     # Base entity class
│   │   ├── player.py                     # Player with physics
│   │   ├── coin.py                       # Collectible coins
│   │   ├── spike.py                      # Static hazards
│   │   ├── enemy.py                      # Enemy base class
│   │   ├── slime.py                      # Ground enemy
│   │   ├── bat.py                        # Flying enemy
│   │   └── wasp.py                       # Sin wave enemy
│   ├── tilemap/
│   │   ├── tilemap.py                    # Tiled map loader and renderer
│   │   ├── tile.py                       # Individual tile class
│   │   ├── vertical_platform.py          # Vertical moving platforms
│   │   └── horizontal_platform.py        # Horizontal moving platforms
│   └── graphics/
│       └── animation.py                  # Sprite animation system
├── assets/
│   ├── sprites/                          # Player, enemy, item sprites
│   ├── tilesets/                         # Tile graphics
│   ├── backgrounds/                      # Parallax layers
│   ├── fonts/                            # Game fonts
│   ├── audio/                            # Music and SFX
│   └── maps/                             # Tiled .tmj map files
├── requirements.txt
└── README.md
```

### Key Components

**Game Loop (`game.py`)**
- Runs at 60 FPS with delta time (16.67ms per frame)
- Internal resolution: 320x240 (scaled 2x to 640x480 window)
- Update → draw → display pattern with double buffering

**State Machine (`game_state_manager.py`)**
- Manages game states (menu, levels, pause, etc.)
- Tracks global state: score, lives, current level
- Handles state transitions and initialization

**Level System (`level_state.py`)**
- Base class for all levels with shared functionality
- Tiled map integration for level design
- Entity spawning from map layers (coins, enemies, platforms, spikes)
- Parallax background support
- HUD rendering with HP hearts, lives, score, and coins
- Death screen with automatic restart
- Win detection and level completion

**Player (`player.py`)**
- Full platformer physics (gravity, jumping, gliding)
- HP system (3 hearts, invincibility frames on hit)
- Underwater physics support
- Moving platform interaction
- Collision detection using PlayerCollisionHandler

**Enemies**
- **Slime**: Ground enemy that patrols left/right between walls
- **Bat**: Flying enemy that moves in zigzag pattern (up-right, down-right)
- **Wasp**: Activates when player approaches, flies left in a sin wave pattern
  - 4 color variants (black, orange, red, yellow) with different wave patterns

**Tilemap System (`tilemap.py`)**
- Loads Tiled JSON (.tmj) maps
- Tile rendering with camera offset
- Collision detection (4-corner testing)
- Entity position extraction from object layers
- Spawn point detection

**Moving Platforms**
- Vertical and horizontal moving platforms
- Defined in Tiled with custom properties (speed, distance)
- Player tracking (moves player with platform)
- Enemies can stand on platforms

**Slope Collision System (`tilemap.py`, `player.py`)**
- Static sloped platforms with 45-degree angle collision
- Supports `right_slope` (high on left, slopes down to right) and `left_slope` (high on right, slopes down to left)
- Tiles must have custom properties `right_slope="true"` or `left_slope="true"` in Tiled tileset
- Uses separate "Static Sloped Platforms" layer for slope tiles
- Smooth slope walking and landing for enhanced platformer feel

**Audio (`audio_manager.py`)**
- Background music with looping and fading
- Sound effects with volume control
- Pygame mixer integration

## Setup & Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone or download the repository**

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```
   - Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   Dependencies:
   - `pygame` - Game engine and rendering
   - `pygame-ce` (optional) - Community edition with improvements

## Running the Game

```bash
python3 src/game.py
```

Or with virtual environment:
```bash
source venv/bin/activate
python src/game.py
```

### Controls

**Menu Navigation:**
- Arrow Keys or WASD: Navigate menu options
- Enter: Select option
- ESC: Back/Quit

**In-Game:**
- Arrow Keys or WASD: Move left/right
- Space: Jump
- Shift: Glide (hold while falling to slow descent)
- ESC: Pause game
- Enter: Continue after level complete

## Development Roadmap

### Phase 1: Core Architecture ✅ COMPLETE
- [x] Project structure
- [x] Game loop with proper timing (60 FPS)
- [x] State machine implementation
- [x] Input handling system
- [x] Menu state with navigation

### Phase 2: Player & Physics ✅ COMPLETE
- [x] Player entity class
- [x] Animation system (sprite sheets)
- [x] Physics implementation (gravity, jump, movement, gliding)
- [x] Player collision detection and resolution
- [x] HP system with invincibility frames
- [x] Underwater physics support

### Phase 3: Level System ✅ COMPLETE
- [x] TileMap class with Tiled JSON support
- [x] Collision detection (AABB with 4-corner testing)
- [x] Tiled map integration (.tmj format)
- [x] Parallax background system (7-layer support)
- [x] Camera/viewport system with smooth following

### Phase 4: Game Objects ✅ COMPLETE
- [x] Coin entity with animation and collection
- [x] Spike hazards
- [x] Enemy base class
- [x] Slime enemy (ground patrol)
- [x] Bat enemy (flying zigzag)
- [x] Wasp enemy (sin wave, 4 color variants)
- [x] Vertical moving platforms
- [x] Horizontal moving platforms
- [x] HUD display (HP, lives, score, coins)

### Phase 5: Audio ✅ COMPLETE
- [x] Audio manager class
- [x] Background music with looping
- [x] Sound effects (jump, coin collect, player hit, win)
- [x] Volume control and fading

### Phase 6: Game States 🚧 IN PROGRESS
- [x] Level 1 (Rollin' 2 forest theme)
- [x] Death screen with restart
- [x] Win screen with completion
- [x] Pause functionality
- [ ] Level 2-4
- [ ] Level select/overworld
- [ ] Credits state
- [ ] Game over state

### Phase 7: Polish & Expansion
- [ ] Additional levels
- [ ] More enemy types
- [ ] Power-ups and collectibles
- [ ] Boss battles
- [ ] Save system
- [ ] Achievements/challenges
- [ ] Controller support

## Differences from Original Rollin'

### New Features in Rollin' 2
- **Tiled Map Editor integration** - Level design with visual editor
- **Parallax backgrounds** - Multi-layer scrolling backgrounds
- **Enemy variety** - Three enemy types with unique behaviors
- **Moving platforms** - Vertical and horizontal platforms
- **HP system** - Player has 3 hearts instead of instant death
- **Improved physics** - Better collision detection and platform interaction
- **Data-driven design** - Entities spawned from Tiled layers

### Technical Improvements
- Pygame instead of Java Swing/AWT
- Cleaner separation of concerns (collision handler, audio manager)
- Entity spawning via Tiled map layers
- Modular level design (base class with inheritance)
- Frame-independent movement using delta time

## Creating New Levels

Rollin' 2 uses **Tiled Map Editor** for level design. Here's how to create a new level:

1. **Create map in Tiled** (32x32 tile size, save as .tmj JSON)

2. **Add required layers:**
   - `Collision` - Tiles for collision detection
   - `Static Sloped Platforms` - Sloped tiles for 45-degree angle collision
   - `Coin` - Coin spawn positions
   - `Spike` - Spike hazard positions
   - `Slime` - Slime enemy positions
   - `Bat` - Bat enemy positions
   - `Wasp` - Wasp enemy positions (tile ID determines color)
   - `VerticalPlatform` - Vertical moving platforms (with properties: speed, distance)
   - `HorizontalPlatform` - Horizontal moving platforms (with properties: speed, distance)

3. **Create level state class** inheriting from `LevelState`:
   ```python
   class Level2State(LevelState):
       def __init__(self, gsm):
           super().__init__(gsm, hud_color=(255, 255, 255))

       def init(self):
           # Clear entities
           self.coins = []
           self.spikes = []
           self.enemies = []
           self.moving_platforms = []

           # Load map
           self.tilemap = TileMap(32)
           self.tilemap.load_map("maps/level_2.tmj")

           # Spawn entities using inherited methods
           self.spawn_coins_from_layer()
           self.spawn_spikes_from_layer()
           # ... etc
   ```

## Using Sloped Platforms

The game now supports 45-degree angled slopes for enhanced platforming. Here's how to set them up:

### Setting Up Slope Tiles in Tiled

1. **Open your tileset file** (e.g., `forest.tsx`) in Tiled
2. **Select a tile** you want to use as a slope
3. **Add custom properties** in the Properties panel:
   - For slopes going down from left to right: Add `right_slope` (boolean) = `true`
   - For slopes going down from right to left: Add `left_slope` (boolean) = `true`
4. **Save the tileset**

### Using Slopes in Maps

1. **Place slope tiles** in any collision layer (e.g., "Static Platforms", "Collision", etc.)
2. **Mix with regular tiles** - you can have both slope and regular collision tiles in the same layer
3. **The collision system will automatically:**
   - Treat tiles with slope properties as triangular slopes (no rectangular collision)
   - Treat tiles without slope properties as rectangular blocks
   - Detect when the player should be walking on slopes
   - Smoothly adjust the player's Y position to follow the slope angle
   - Allow the player to jump while on slopes
   - Handle transitions from flat ground to slopes seamlessly

### Slope Types

- **Right Slope** (`right_slope="true"`): Triangle shape high on the left, sloping down to the right
- **Left Slope** (`left_slope="true"`): Triangle shape high on the right, sloping down to the left

### Technical Notes

- Slopes work at exactly 45 degrees (1:1 ratio)
- Players can walk up and down slopes smoothly
- Jumping and landing on slopes works correctly
- Slopes are processed before regular tile collision for smooth movement
- **Slope tiles do NOT act as rectangular blocks** - they only provide triangular slope collision
- **Tiles with slope properties are automatically excluded from rectangular collision**
- **Mixed layers supported** - you can have both slope and regular collision tiles in the same layer
- Only tiles with `right_slope="true"` or `left_slope="true"` properties will have slope collision
- Regular tiles (without slope properties) in collision layers act as rectangular blocks

### Common Issues and Solutions

**Problem: Slope tiles are acting like solid rectangular blocks**  
- **Solution**: Ensure slope tiles have the correct custom properties (`right_slope="true"` or `left_slope="true"`)
- The system automatically treats tiles with slope properties as NORMAL for rectangular collision
- Slope tiles can be in the same layer as regular collision tiles (e.g., "Static Platforms")

**Problem: Player falls through slopes**
- **Solution**: Verify that slope tiles have the correct custom properties (`right_slope="true"` or `left_slope="true"`)
- Check that the tile is in the "Static Sloped Platforms" layer with the correct name (case-insensitive)

**Problem: Slopes don't look like 45-degree triangles**
- **Solution**: This is a visual issue - make sure your slope tile graphics actually show triangular slopes
- The collision works correctly regardless of the visual appearance

**Problem: "Ledges" when going up/down slopes (player becomes airborne)**
- **✅ FIXED**: Enhanced boundary overlap detection eliminates ledge effects at tile boundaries
- **✅ FIXED**: Improved collision mathematics provide seamless slope transitions  
- **✅ FIXED**: Players can now traverse slopes smoothly in both directions without mid-air jumps
- **Note**: 4px vertical change per 4px horizontal movement is correct physics for 45-degree slopes

## Physics Constants

```python
# Player movement
move_speed = 0.3
max_speed = 1.6
stop_speed = 0.4

# Gravity
fall_speed = 0.15
max_fall_speed = 4.0

# Jumping
jump_start = -4.8
stop_jump_speed = 0.3

# Gliding
glide_scale = 0.1  # Reduces fall speed by 90%

# Underwater (if level has water)
underwater_move_speed = 0.15
underwater_max_speed = 0.8
underwater_fall_speed = 0.05
underwater_max_fall_speed = 1.5
```

## Contributing

This is a personal project, but suggestions and ideas are welcome! Feel free to fork and experiment.

## Credits

- Original Java version created as a college assignment (circa 2015)
- Python reimagining with new content and features (2025)

## License

Personal/Educational project.
