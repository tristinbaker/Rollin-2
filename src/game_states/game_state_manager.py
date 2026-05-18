"""
GameStateManager - equivalent to GameStateManager.java
Manages game states and transitions between them
"""
import json
import os
from paths import asset, save_file
from game_states.menu_state import MenuState
from game_states.rollin1.level1_state import Level1State as Rollin1Level1State
from game_states.rollin1.level2_state import Level2State as Rollin1Level2State
from game_states.rollin1.level3_state import Level3State as Rollin1Level3State
from game_states.rollin1.level4_state import Level4State as Rollin1Level4State
from game_states.rollin2.level_1_state import Level1State as Rollin2Level1State
from game_states.rollin2.level_2_state import Level2State as Rollin2Level2State
from game_states.rollin2.level_3_state import Level3State as Rollin2Level3State
from game_states.rollin2.level_4_state import Level4State as Rollin2Level4State
from game_states.rollin2.level_5_state import Level5State as Rollin2Level5State
from game_states.options_state import OptionsState
from game_states.pause_state import PauseState
from game_states.mode_select_state import ModeSelectState


class GameStateManager:
    # Rollin 1 States
    MENU_STATE = 0
    LEVEL1_STATE = 1
    HELP_STATE = 2
    LEVEL2_STATE = 3
    PAUSE_STATE = 4
    CREDITS_STATE = 5
    LEVEL3_STATE = 6
    OVERWORLD1_STATE = 7
    OVERWORLD2_STATE = 8
    OVERWORLD3_STATE = 9
    OVERWORLD4_STATE = 10
    HARDMODE_STATE = 11
    GAMEOVER_STATE = 12
    OPTIONS_STATE = 13
    LEVEL4_STATE = 14  # Secret level
    # Rollin 2 States
    ROLLIN2_LEVEL1_STATE = 15
    ROLLIN2_LEVEL2_STATE = 16
    ROLLIN2_LEVEL3_STATE = 17
    ROLLIN2_LEVEL4_STATE = 18
    ROLLIN2_LEVEL5_STATE = 19
    MODE_SELECT_STATE    = 20

    def __init__(self, input_handler, audio_manager):
        # Input handler reference
        self.input_handler = input_handler

        # Audio manager reference
        self.audio_manager = audio_manager

        # Game state array
        self.game_states = [None] * 21

        # Global game variables
        self.score = 0
        self.lives = 5
        self.hard_mode = False

        # Run-wide coin tracking (committed on each level completion, reset on new game)
        self.run_coins_collected = 0
        self.run_coins_total = 0

        # Persistent unlocks
        self.rollin1_unlocked    = False
        self.demon_mode_unlocked = False
        self.hardcore_unlocked   = False
        self.hc_demon_unlocked   = False
        self.hc_demon_complete   = False

        # Current play mode (chosen per session, not persisted)
        self.current_mode = "normal"
        self.save_slot = None
        self.pending_load = None
        self._save_path = save_file("save.json")

        # Level checkpoint — lightweight resume (level + mode + lives, no position)
        self.level_checkpoint = None

        # Set by level state on pause; used by pause menu for restart safety check
        self.player_has_safe_ground = True

        # Total coins across all Rollin 2 levels (computed once at startup)
        self.grand_coin_total = self._compute_grand_coin_total()

        # Current state
        self.current_state = self.MENU_STATE

        # Load persistent progress before initializing states so the menu
        # reflects save/unlock state on first render
        self._load_progress()
        self._init_states()

    def _compute_grand_coin_total(self):
        import json, zlib, base64, struct
        assets = asset()
        maps = ["maps/level_1.tmj", "maps/level_2.tmj", "maps/level_3.tmj",
                "maps/level_4.tmj", "maps/level_5.tmj"]
        total = 0
        for map_file in maps:
            try:
                with open(os.path.join(assets, map_file)) as f:
                    data = json.load(f)
                for layer in data.get("layers", []):
                    if layer.get("name", "").lower() == "coin":
                        raw = zlib.decompress(base64.b64decode(layer["data"]))
                        tiles = struct.unpack(f'<{len(raw)//4}I', raw)
                        total += sum(1 for t in tiles if t != 0)
            except Exception:
                pass
        return total

    def _init_states(self):
        """Initialize all game states"""
        # Start with menu state only
        self.game_states[self.MENU_STATE] = MenuState(self)
        self.game_states[self.ROLLIN2_LEVEL3_STATE] = Rollin2Level3State(self)

        # Create current state if not already initialized (lazy init)
        if self.game_states[self.current_state] is None:
            self._create_state(self.current_state)

        # Initialize the current state
        if self.game_states[self.current_state]:
            self.game_states[self.current_state].init()

    def set_state(self, state, init=True):
        """Change to a different game state

        Args:
            state: The state to switch to
            init: Whether to call init() on the new state (default True)
        """
        if 0 <= state < len(self.game_states):
            self.current_state = state

            # Save a lightweight checkpoint whenever a Rollin 2 level starts
            _r2_levels = {self.ROLLIN2_LEVEL1_STATE, self.ROLLIN2_LEVEL2_STATE,
                          self.ROLLIN2_LEVEL3_STATE, self.ROLLIN2_LEVEL4_STATE,
                          self.ROLLIN2_LEVEL5_STATE}
            if state in _r2_levels:
                self.level_checkpoint = {
                    "state": state,
                    "mode":  self.current_mode,
                    "lives": self.lives,
                }
                self._save_progress()

            # Initialize state if it hasn't been created yet
            if self.game_states[state] is None:
                self._create_state(state)

            # Call init on the new state (unless init=False for resuming)
            if init and self.game_states[state]:
                self.game_states[state].init()
                if self.pending_load is not None and hasattr(self.game_states[state], 'load_state'):
                    self.game_states[state].load_state(self.pending_load)
                    self.pending_load = None

    def _create_state(self, state):
        """Lazy initialization of game states"""
        if state == self.LEVEL1_STATE:
            self.game_states[state] = Rollin1Level1State(self)
        elif state == self.LEVEL2_STATE:
            self.game_states[state] = Rollin1Level2State(self)
        elif state == self.LEVEL3_STATE:
            self.game_states[state] = Rollin1Level3State(self)
        elif state == self.LEVEL4_STATE:
            self.game_states[state] = Rollin1Level4State(self)
        elif state == self.ROLLIN2_LEVEL1_STATE:
            self.game_states[state] = Rollin2Level1State(self)
        elif state == self.ROLLIN2_LEVEL2_STATE:
            self.game_states[state] = Rollin2Level2State(self)
        elif state == self.ROLLIN2_LEVEL4_STATE:
            self.game_states[state] = Rollin2Level4State(self)
        elif state == self.ROLLIN2_LEVEL5_STATE:
            self.game_states[state] = Rollin2Level5State(self)
        elif state == self.MODE_SELECT_STATE:
            self.game_states[state] = ModeSelectState(self)
        elif state == self.OPTIONS_STATE:
            self.game_states[state] = OptionsState(self)
        elif state == self.PAUSE_STATE:
            self.game_states[state] = PauseState(self)
        # TODO: Create other states as needed

    def update(self):
        """Update current game state"""
        if self.game_states[self.current_state]:
            self.game_states[self.current_state].update()

    def draw(self, surface):
        """Draw current game state"""
        if self.game_states[self.current_state]:
            self.game_states[self.current_state].draw(surface)

    def get_score(self):
        """Get current score"""
        return self.score

    def set_score(self, score):
        """Set current score"""
        self.score = score

    def add_score(self, amount):
        """Add to current score"""
        self.score += amount

    def get_lives(self):
        """Get current lives"""
        return self.lives

    def set_lives(self, lives):
        """Set current lives"""
        self.lives = lives

    def lose_life(self):
        """Lose a life"""
        self.lives -= 1

    def is_hard_mode(self):
        """Check if hard mode is enabled"""
        return self.hard_mode

    def set_hard_mode(self, enabled):
        """Enable/disable hard mode"""
        self.hard_mode = enabled

    def commit_level_coins(self, collected, total):
        """Add a completed level's coin counts to the run totals"""
        self.run_coins_collected += collected
        self.run_coins_total += total
        self._save_progress()

    def unlock_rollin1(self):
        self.rollin1_unlocked = True
        self._save_progress()

    def unlock_demon_mode(self):
        self.demon_mode_unlocked = True
        self._save_progress()

    def unlock_hardcore(self):
        self.hardcore_unlocked = True
        self._save_progress()

    def unlock_hc_demon(self):
        self.hc_demon_unlocked = True
        self._save_progress()

    def save_hc_demon_complete(self):
        self.hc_demon_complete = True
        self._save_progress()

    def save_game(self, level_state_id, score, lives, run_coins_collected,
                  run_coins_total, player_x, player_y, collected_coin_indices):
        """Save mid-level progress to disk"""
        self.save_slot = {
            "level_state": level_state_id,
            "score": score,
            "lives": lives,
            "run_coins_collected": run_coins_collected,
            "run_coins_total": run_coins_total,
            "player_x": player_x,
            "player_y": player_y,
            "collected_coins": collected_coin_indices,
        }
        self._save_progress()

    def clear_save(self):
        """Remove the save slot from disk"""
        self.save_slot = None
        self._save_progress()

    def _save_progress(self):
        data = {
            "rollin1_unlocked":    self.rollin1_unlocked,
            "demon_mode_unlocked": self.demon_mode_unlocked,
            "hardcore_unlocked":   self.hardcore_unlocked,
            "hc_demon_unlocked":   self.hc_demon_unlocked,
            "run_coins_collected": self.run_coins_collected,
            "run_coins_total":     self.run_coins_total,
        }
        if self.hc_demon_complete:
            data["proof"] = "4920444944204954"
        if self.level_checkpoint is not None:
            data["level_checkpoint"] = self.level_checkpoint
        if self.save_slot is not None:
            data["save_slot"] = self.save_slot
        with open(self._save_path, 'w') as f:
            json.dump(data, f)

    def _load_progress(self):
        if os.path.exists(self._save_path):
            with open(self._save_path) as f:
                data = json.load(f)
            self.rollin1_unlocked    = data.get("rollin1_unlocked", False)
            self.demon_mode_unlocked = data.get("demon_mode_unlocked", False)
            self.hardcore_unlocked   = data.get("hardcore_unlocked", False)
            self.hc_demon_unlocked   = data.get("hc_demon_unlocked", False)
            self.hc_demon_complete   = "proof" in data
            self.save_slot           = data.get("save_slot", None)
            self.run_coins_collected = data.get("run_coins_collected", 0)
            self.run_coins_total     = data.get("run_coins_total", 0)
            self.level_checkpoint    = data.get("level_checkpoint", None)
