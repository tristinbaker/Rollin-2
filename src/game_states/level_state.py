"""
LevelState - parent class for all level states
Contains common level functionality like underwater physics flag
"""
import pygame
import os
from game_states.game_state import GameState
from entities.spike import Spike
from entities.slime import Slime
from entities.bat import Bat
from entities.wasp import Wasp
from entities.coin import Coin
from entities.heart import Heart
from entities.lava import Lava
from entities.vertical_moving_platform import VerticalMovingPlatform
from entities.horizontal_moving_platform import HorizontalMovingPlatform


class LevelState(GameState):
    """Base class for all level states"""

    def __init__(self, gsm, hud_color=(255, 255, 255)):
        super().__init__(gsm)
        self.underwater = False  # Set to True for underwater physics
        self.tilemap = None
        self.player = None
        self.coins = []
        self.hearts = []
        self.spikes = []
        self.lava = []
        self.enemies = []
        self.moving_platforms = []
        self.total_coins = 0
        self.max_coins = 0  # Total coins in the level
        self.font = None
        self.has_won = False
        self.win_sound_played = False
        self.death_screen_timer = 0
        self.death_screen_duration = 2000  # 2 seconds
        self.hud_color = hud_color
        self.health_sprites = None
        self.coin_hud_icon = None
        self.life_icon = None
        self.parallax_layers = []  # List of (image, scroll_speed) tuples
        self.simple_background = None  # Single background image (for Rollin 1 levels)
        self.simple_bg_scroll_speed = 0.0  # Scroll speed for simple background
        self.level_start_score = 0  # Score at the start of this level
    def spawn_hearts_from_layer(self, layer_name="Hearts"):
        """Spawn hearts from a Tiled layer

        Args:
            layer_name: Name of the Tiled layer containing heart positions (default: "Hearts")
        """
        heart_positions = self.tilemap.get_entity_positions_from_layer(layer_name)
        for x, y in heart_positions:
            heart = Heart(x - 8, y - 8, self.tilemap)  # Centered in 32x32 tile
            self.hearts.append(heart)

    def update_hearts(self):
        for heart in self.hearts:
            heart.update(self)

    def draw_hearts(self, surface):
        for heart in self.hearts:
            heart.draw(surface)

    def init(self):
        """Initialize the level (override in subclasses)"""
        pass

    def load_simple_background(self, filename, scroll_speed=0.1, subfolder="rollin1"):
        """Load a single background image (for Rollin 1 levels)

        Args:
            filename: Background image filename (e.g., "Background.png")
            scroll_speed: Parallax scroll speed (0.0 = static, 1.0 = moves with camera)
            subfolder: Subfolder within backgrounds/ (default: "rollin1")
        """
        bg_path = os.path.normpath(os.path.join(
            os.path.dirname(__file__),
            f"../../assets/backgrounds/{subfolder}/{filename}"
        ))

        if os.path.exists(bg_path):
            self.simple_background = pygame.image.load(bg_path).convert()
            self.simple_bg_scroll_speed = scroll_speed

        else:
            print(f"Warning: Background not found at {bg_path}")
            self.simple_background = None

    def load_parallax_layers(self, layer_configs, subfolder=None):
        """Load parallax background layers

        Args:
            layer_configs: List of tuples (filename, scroll_speed)
                          filename: name of image file in backgrounds/ folder
                          scroll_speed: float, 0.0 = static, 1.0 = moves with camera
                          Lower values = further back, higher values = closer
            subfolder: Optional subfolder within backgrounds/ (e.g., "level_1")

        Example:
            self.load_parallax_layers([
                ("forest_sky.png", 0.0),      # Static background
                ("forest_moon.png", 0.1),     # Very slow
                ("forest_mountain.png", 0.3), # Slow
                ("forest_back.png", 0.5),     # Medium
                ("forest_mid.png", 0.7),      # Fast
                ("forest_long.png", 0.85),    # Very fast
                ("forest_short.png", 0.95),   # Nearly 1:1 with camera
            ], subfolder="level_1")
        """
        self.parallax_layers = []

        for filename, scroll_speed in layer_configs:
            if subfolder:
                bg_path = os.path.normpath(os.path.join(
                    os.path.dirname(__file__),
                    f"../../assets/backgrounds/{subfolder}/{filename}"
                ))
            else:
                bg_path = os.path.normpath(os.path.join(
                    os.path.dirname(__file__),
                    f"../../assets/backgrounds/{filename}"
                ))

            if os.path.exists(bg_path):
                image = pygame.image.load(bg_path).convert_alpha()

                # Scale image to screen height (240px) while maintaining aspect ratio
                # This allows backgrounds designed for higher resolutions to work
                original_width = image.get_width()
                original_height = image.get_height()
                target_height = 240  # Screen height

                if original_height != target_height:
                    scale_factor = target_height / original_height
                    new_width = int(original_width * scale_factor)
                    image = pygame.transform.scale(image, (new_width, target_height))


                self.parallax_layers.append((image, scroll_speed))
            else:
                print(f"Warning: Background layer not found at {bg_path}")

    def draw_background(self, surface):
        """Draw background - automatically chooses simple or parallax based on what's loaded"""
        if self.simple_background:
            self.draw_simple_background(surface)
        elif self.parallax_layers:
            self.draw_parallax(surface)

    def draw_simple_background(self, surface):
        """Draw simple background with parallax scrolling (for Rollin 1 levels)"""
        if not self.simple_background or not self.tilemap:
            return

        # Get camera position
        camera_x = -self.tilemap.x
        camera_y = -self.tilemap.y

        # Calculate parallax offset
        offset_x = camera_x * self.simple_bg_scroll_speed
        offset_y = camera_y * self.simple_bg_scroll_speed

        # Get image dimensions
        img_width = self.simple_background.get_width()
        img_height = self.simple_background.get_height()

        # Tile the background to fill the screen
        screen_width = 320
        screen_height = 240

        start_x = -(offset_x % img_width)
        num_tiles_x = int((screen_width + abs(start_x) + img_width - 1) // img_width + 1)

        start_y = -(offset_y % img_height)
        num_tiles_y = int((screen_height + abs(start_y) + img_height - 1) // img_height + 1)

        # Draw tiled background
        for ty in range(num_tiles_y):
            for tx in range(num_tiles_x):
                x = start_x + tx * img_width
                y = start_y + ty * img_height
                surface.blit(self.simple_background, (x, y))

    def draw_parallax(self, surface):
        """Draw parallax background layers - call this before drawing tilemap"""
        if not self.tilemap:
            return

        # Get camera position (tilemap x/y are negative when camera moves right/down)
        camera_x = -self.tilemap.x
        # Don't use camera_y for parallax - backgrounds should not scroll vertically

        screen_width = 320
        screen_height = 240

        for i, (image, scroll_speed) in enumerate(self.parallax_layers):
            # Calculate parallax offset (horizontal only)
            offset_x = camera_x * scroll_speed

            # Get image dimensions
            img_width = image.get_width()
            img_height = image.get_height()

            # Calculate how many times to tile horizontally to cover screen plus movement
            # We need to account for the offset and ensure full coverage
            start_x = -(offset_x % img_width)
            num_tiles_x = int((screen_width + abs(start_x) + img_width - 1) // img_width + 1)

            # Vertical positioning: center the image if it's 240px tall, otherwise tile
            if img_height == screen_height:
                # Image is exactly screen height, draw it at y=0
                start_y = 0
                num_tiles_y = 1
            else:
                # Tile vertically if needed
                start_y = 0
                num_tiles_y = int((screen_height + img_height - 1) // img_height)

            # Draw tiled background
            for ty in range(num_tiles_y):
                for tx in range(num_tiles_x):
                    x = start_x + tx * img_width
                    y = start_y + ty * img_height
                    surface.blit(image, (x, y))

    def load_hud_assets(self):
        """Load HUD sprites and icons - call this from subclass init()"""
        # Load health sprite
        health_sprite_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../assets/sprites/health.png"))
        if os.path.exists(health_sprite_path):
            health_sheet = pygame.image.load(health_sprite_path).convert_alpha()
            # Each row is 120x36 (120 width, 144 total height / 4 rows = 36 per row)
            self.health_sprites = []
            for i in range(4):
                sprite = health_sheet.subsurface((0, i * 36, 120, 36)).copy()
                self.health_sprites.append(sprite)
        else:
            print(f"Warning: Health sprite not found at {health_sprite_path}")
            self.health_sprites = None

        # Load coin HUD icon
        coin_hud_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../assets/sprites/hud_coin.png"))
        if os.path.exists(coin_hud_path):
            self.coin_hud_icon = pygame.image.load(coin_hud_path).convert_alpha()
        else:
            print(f"Warning: Coin HUD icon not found at {coin_hud_path}")
            self.coin_hud_icon = None

        # Load life icon (first sprite from player sprite sheet)
        player_sprite_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../assets/sprites/playerSprites.gif"))
        if os.path.exists(player_sprite_path):
            player_sheet = pygame.image.load(player_sprite_path).convert_alpha()
            # Extract first sprite (30x30 pixels at position 0,0)
            self.life_icon = player_sheet.subsurface((0, 0, 30, 30)).copy()
        else:
            print(f"Warning: Player sprite not found at {player_sprite_path}")
            self.life_icon = None

    def draw_hud(self, surface):
        """Draw heads-up display - call this from subclass draw()"""
        hud_alpha = 230  # Slightly transparent (90% opacity)

        # Helper function to render text with alpha
        def render_text_alpha(font, text, color, alpha):
            text_surface = font.render(text, True, color)
            text_surface.set_alpha(alpha)
            return text_surface

        # HP - Display health sprite instead of text
        if self.health_sprites:
            player_hp = self.player.get_hp()
            # Map HP to sprite index: 3 HP -> index 0, 2 HP -> index 1, 1 HP -> index 2, 0 HP -> index 3
            sprite_index = 3 - player_hp if player_hp >= 0 else 3
            sprite_index = max(0, min(3, sprite_index))
            health_sprite = self.health_sprites[sprite_index]
            # Scale down the sprite (120x36 is too big, scale to 60x18)
            scaled_sprite = pygame.transform.scale(health_sprite, (60, 18))
            surface.blit(scaled_sprite, (5, 5))
        else:
            # Fallback to text if sprite not loaded
            hp_text = render_text_alpha(self.font, f"HP: {self.player.get_hp()}/3", self.hud_color, hud_alpha)
            surface.blit(hp_text, (5, 10))

        # Coin count with icon (top right)
        current_x = 315  # Start from right edge
        if self.coin_hud_icon:
            # Display coin count as "x <collected> / <total>"
            coin_count_text = render_text_alpha(self.font, f"{self.total_coins} / {self.max_coins}", self.hud_color, hud_alpha)
            coin_count_rect = coin_count_text.get_rect(topright=(current_x, 5))
            surface.blit(coin_count_text, coin_count_rect)
            current_x = coin_count_rect.left - 3

            # Display 'x'
            x_text = render_text_alpha(self.font, "x", self.hud_color, hud_alpha)
            x_rect = x_text.get_rect(topright=(current_x, 5))
            surface.blit(x_text, x_rect)
            current_x = x_rect.left - 3

            # Display coin icon
            coin_icon = self.coin_hud_icon
            # Get icon size and scale if needed
            icon_height = 16  # Target height
            scale_factor = icon_height / coin_icon.get_height()
            icon_width = int(coin_icon.get_width() * scale_factor)
            scaled_icon = pygame.transform.scale(coin_icon, (icon_width, icon_height))
            icon_rect = scaled_icon.get_rect(topright=(current_x, 4))  # Adjusted to 4
            surface.blit(scaled_icon, icon_rect)
        else:
            # Fallback to text
            coins_text = render_text_alpha(self.font, f"Coins: {self.total_coins}/{self.max_coins}", self.hud_color, hud_alpha)
            coins_rect = coins_text.get_rect(topright=(current_x, 5))
            surface.blit(coins_text, coins_rect)

        # Score (below coins, top right, no "Score:" label)
        score_text = render_text_alpha(self.font, str(self.gsm.get_score()), self.hud_color, hud_alpha)
        score_rect = score_text.get_rect(topright=(315, 25))
        surface.blit(score_text, score_rect)

        # Lives (bottom right, displayed as icon x number)
        if self.life_icon:
            current_x = 315  # Start from right edge
            start_y = 240 - 16 - 5  # 5 pixels from bottom

            # Display life count
            life_count_text = render_text_alpha(self.font, str(self.gsm.get_lives()), self.hud_color, hud_alpha)
            life_count_rect = life_count_text.get_rect(bottomright=(current_x, 240 - 5))
            surface.blit(life_count_text, life_count_rect)
            current_x = life_count_rect.left - 3

            # Display 'x'
            x_text = render_text_alpha(self.font, "x", self.hud_color, hud_alpha)
            x_rect = x_text.get_rect(bottomright=(current_x, 240 - 5))
            surface.blit(x_text, x_rect)
            current_x = x_rect.left - 3

            # Display life icon
            icon_height = 20
            scale_factor = icon_height / self.life_icon.get_height()
            icon_width = int(self.life_icon.get_width() * scale_factor)
            scaled_icon = pygame.transform.scale(self.life_icon, (icon_width, icon_height))
            icon_rect = scaled_icon.get_rect(bottomright=(current_x, 240 - 5))
            surface.blit(scaled_icon, icon_rect)
        else:
            # Fallback to text
            lives_text = render_text_alpha(self.font, f"Lives: {self.gsm.get_lives()}", self.hud_color, hud_alpha)
            lives_rect = lives_text.get_rect(bottomright=(315, 235))
            surface.blit(lives_text, lives_rect)

    def spawn_coins_from_layer(self, layer_name="Coin", coin_color="blue", y_offset=32):
        """Spawn coins from a Tiled layer

        Args:
            layer_name: Name of the Tiled layer containing coin positions (default: "Coin")
            coin_color: Color of the coins to spawn (default: "blue")
            y_offset: Y position adjustment (default: 32, one tile)
        """
        coin_positions = self.tilemap.get_entity_positions_from_layer(layer_name)
        for x, y in coin_positions:
            coin = Coin(self.tilemap, coin_color)
            coin.set_position(x, y + y_offset)
            self.coins.append(coin)
        self.max_coins = len(self.coins)  # Set total coins after spawning

    def spawn_spikes_from_layer(self, layer_name="Spike Trap", y_offset=32):
        """Spawn spikes from a Tiled layer

        Args:
            layer_name: Name of the Tiled layer containing spike positions (default: "Spike Trap")
            y_offset: Y position adjustment to make spikes sit on ground (default: 32, one tile)
        """
        spike_positions = self.tilemap.get_entity_positions_from_layer(layer_name)
        for x, y in spike_positions:
            spike = Spike(self.tilemap)
            spike.set_position(x, y + y_offset)
            self.spikes.append(spike)

    def spawn_slimes_from_layer(self, layer_name="Slime", y_offset=32):
        """Spawn slimes from a Tiled layer

        Args:
            layer_name: Name of the Tiled layer containing slime positions (default: "Slime")
            y_offset: Y position adjustment to make slimes sit on ground (default: 32, one tile)
        """
        slime_positions = self.tilemap.get_entity_positions_from_layer(layer_name)
        for x, y in slime_positions:
            slime = Slime(self.tilemap)
            slime.set_position(x, y + y_offset)
            self.enemies.append(slime)

    def spawn_bats_from_layer(self, layer_name="Bat", boundary_range=150):
        """Spawn bats from a Tiled layer

        Args:
            layer_name: Name of the Tiled layer containing bat positions (default: "Bat")
            boundary_range: Movement boundary range around spawn point (default: 150)

        Note:
            Uses tile IDs to determine movement mode:
            - Lower tile ID = predictable movement
            - Higher tile ID = random movement
        """
        bat_data = self.tilemap.get_entity_positions_with_tiles(layer_name)

        # First pass: determine which tile IDs are used and which is lower
        bat_tile_ids = sorted(set(tile_id for _, _, tile_id in bat_data))
        predictable_tile_id = bat_tile_ids[0] if bat_tile_ids else None


        for x, y, tile_id in bat_data:
            # Determine movement mode based on tile_id
            movement_mode = "predictable" if tile_id == predictable_tile_id else "random"

            # Set boundaries around the spawn point
            min_x = max(0, x - boundary_range)
            max_x = x + boundary_range

            bat = Bat(self.tilemap, min_x, max_x, movement_mode=movement_mode)
            bat.set_position(x, y)

            self.enemies.append(bat)

    def spawn_wasps_from_layer(self, layer_name="Wasp"):
        """Spawn wasps from a Tiled layer

        Args:
            layer_name: Name of the Tiled layer containing wasp positions (default: "Wasp")

        Note:
            Uses tile IDs to determine wasp color:
            - Lowest tile ID = black
            - 2nd lowest = orange
            - 3rd lowest = red
            - 4th lowest = yellow
        """
        wasp_data = self.tilemap.get_entity_positions_with_tiles(layer_name)

        # First pass: determine which tile IDs are used and map them to colors
        wasp_tile_ids = sorted(set(tile_id for _, _, tile_id in wasp_data))
        color_map = ["black", "orange", "red", "yellow"]

        for x, y, tile_id in wasp_data:
            # Determine color based on tile_id index
            tile_index = wasp_tile_ids.index(tile_id)
            color = color_map[tile_index] if tile_index < len(color_map) else "black"

            wasp = Wasp(self.tilemap, color=color)
            wasp.set_position(x, y)
            self.enemies.append(wasp)

    def spawn_lava_from_layer(self, layer_name="Lava", y_offset=32):
        """Spawn lava from a Tiled layer

        The topmost lava in each column uses the top row animation (16px collision).
        All other lava uses the bottom row animation (full 32px collision).

        Args:
            layer_name: Name of the Tiled layer containing lava positions (default: "Lava")
            y_offset: Y position adjustment to make lava sit on ground (default: 32, one tile)
        """
        lava_positions = self.tilemap.get_entity_positions_from_layer(layer_name)

        # Group lava by column (x coordinate) to identify top lava
        columns = {}
        for x, y in lava_positions:
            if x not in columns:
                columns[x] = []
            columns[x].append(y)

        # Sort each column to find the topmost lava
        for x in columns:
            columns[x].sort()

        # Spawn lava
        for x, y in lava_positions:
            # Check if this is the topmost lava in its column
            is_top = (y == columns[x][0])

            lava = Lava(self.tilemap, is_top=is_top)
            lava.set_position(x - 1, y + y_offset)
            self.lava.append(lava)

    def _group_adjacent_platforms(self, platform_data):
        """Group adjacent platform tiles using flood fill algorithm"""
        import random
        from collections import deque
        
        # Convert positions to grid coordinates for adjacency checking
        tile_size = self.tilemap.tile_size
        position_to_grid = {}
        grid_to_data = {}
        
        for x, y, tile_id in platform_data:
            # Convert pixel coordinates to grid coordinates
            grid_x = round((x - tile_size // 2) / tile_size)
            grid_y = round((y - tile_size // 2) / tile_size)
            position_to_grid[(x, y)] = (grid_x, grid_y)
            grid_to_data[(grid_x, grid_y)] = (x, y, tile_id)
        
        visited = set()
        groups = []
        
        for (grid_x, grid_y), (x, y, tile_id) in grid_to_data.items():
            if (grid_x, grid_y) in visited:
                continue
                
            # Start new group using flood fill
            group = []
            queue = deque([(grid_x, grid_y)])
            visited.add((grid_x, grid_y))
            
            while queue:
                curr_x, curr_y = queue.popleft()
                curr_data = grid_to_data[(curr_x, curr_y)]
                group.append(curr_data)
                
                # Check 4-directional neighbors (up, down, left, right)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    next_x, next_y = curr_x + dx, curr_y + dy
                    if (next_x, next_y) in grid_to_data and (next_x, next_y) not in visited:
                        queue.append((next_x, next_y))
                        visited.add((next_x, next_y))
            
            groups.append(group)
        
        return groups

    def spawn_vertical_platforms_from_layer(self, layer_name="Vertical Moving Platforms"):
        """Spawn vertical moving platforms from a Tiled layer

        Args:
            layer_name: Name of the Tiled layer containing platform positions
        """
        import random
        
        platform_data = self.tilemap.get_entity_positions_with_tiles(layer_name)
        groups = self._group_adjacent_platforms(platform_data)
        
        # Store the direction for regular vertical platforms (we'll use the opposite for opposite platforms)
        if not hasattr(self, '_vertical_platform_direction'):
            self._vertical_platform_direction = random.choice([-1, 1])
        
        for group in groups:
            # All groups in the regular layer use the same base direction
            group_direction = self._vertical_platform_direction
            
            for x, y, tile_id in group:
                platform = VerticalMovingPlatform(self.tilemap, tile_id)
                platform.set_position(x, y)
                platform.direction = group_direction
                self.moving_platforms.append(platform)
        
        # Automatically attach spikes to platforms if both exist
        self._auto_attach_spikes_to_platforms()

    def spawn_opposite_vertical_platforms_from_layer(self, layer_name="Opposite Vertical Moving Platforms"):
        """Spawn opposite vertical moving platforms from a Tiled layer
        These platforms start in the opposite direction from regular vertical platforms

        Args:
            layer_name: Name of the Tiled layer containing platform positions
        """
        import random
        
        platform_data = self.tilemap.get_entity_positions_with_tiles(layer_name)
        groups = self._group_adjacent_platforms(platform_data)
        
        # Get the base direction (opposite of regular vertical platforms)
        if not hasattr(self, '_vertical_platform_direction'):
            self._vertical_platform_direction = random.choice([-1, 1])
        
        opposite_base_direction = -self._vertical_platform_direction
        
        for group in groups:
            # All groups in the opposite layer use the opposite direction
            group_direction = opposite_base_direction
            
            for x, y, tile_id in group:
                platform = VerticalMovingPlatform(self.tilemap, tile_id)
                platform.set_position(x, y)
                platform.direction = group_direction
                self.moving_platforms.append(platform)
        
        # Automatically attach spikes to platforms if both exist
        self._auto_attach_spikes_to_platforms()

    def spawn_horizontal_platforms_from_layer(self, layer_name="Horizontal Moving Platforms"):
        """Spawn horizontal moving platforms from a Tiled layer

        Args:
            layer_name: Name of the Tiled layer containing platform positions
        """
        import random
        
        platform_data = self.tilemap.get_entity_positions_with_tiles(layer_name)
        groups = self._group_adjacent_platforms(platform_data)
        
        for group in groups:
            # Assign random direction to this group
            group_direction = random.choice([-1, 1])
            
            for x, y, tile_id in group:
                platform = HorizontalMovingPlatform(self.tilemap, tile_id)
                platform.set_position(x, y)
                platform.direction = group_direction
                self.moving_platforms.append(platform)
        
        # Automatically attach spikes to platforms if both exist
        self._auto_attach_spikes_to_platforms()

    def attach_spikes_to_platforms(self):
        """Attach spikes to moving platforms if they are positioned on them"""
        for spike in self.spikes:
            spike.find_and_attach_to_platform(self.moving_platforms)
    
    def _auto_attach_spikes_to_platforms(self):
        """Automatically attach spikes to platforms if both spikes and platforms exist"""
        if self.spikes and self.moving_platforms:
            self.attach_spikes_to_platforms()

    def check_pause(self):
        """Check for pause input - call this in subclass update methods"""
        input_handler = self.gsm.input_handler
        if input_handler.is_pressed(input_handler.BUTTON2):  # Escape
            # Store current state before switching
            current = self.gsm.current_state
            # Switch to pause state
            self.gsm.set_state(self.gsm.PAUSE_STATE)
            # Set previous state AFTER init() has been called
            if self.gsm.game_states[self.gsm.PAUSE_STATE]:
                self.gsm.game_states[self.gsm.PAUSE_STATE].set_previous_state(current)

    def handle_death_screen(self, target_state):
        """
        Handle death screen timer logic

        Args:
            target_state: The state to restart when timer expires

        Returns:
            bool: True if death screen is active, False otherwise
        """
        if self.death_screen_timer > 0:
            self.death_screen_timer -= 16.67
            if self.death_screen_timer <= 0:
                self.gsm.lose_life()
                self.gsm.set_score(self.level_start_score)
                if self.gsm.get_lives() <= 0:
                    self.gsm.set_lives(5)
                    self.gsm.set_state(self.gsm.MENU_STATE)
                else:
                    self.gsm.set_state(target_state)
            return True
        return False

    def handle_player_input(self):
        """Handle common player input"""
        input_handler = self.gsm.input_handler
        self.player.set_left(input_handler.is_down(input_handler.LEFT) or input_handler.is_down(input_handler.A))
        self.player.set_right(input_handler.is_down(input_handler.RIGHT) or input_handler.is_down(input_handler.D))
        self.player.set_up(input_handler.is_down(input_handler.UP) or input_handler.is_down(input_handler.W))
        self.player.set_down(input_handler.is_down(input_handler.DOWN) or input_handler.is_down(input_handler.S))
        self.player.set_jumping(input_handler.is_down(input_handler.BUTTON3))
        self.player.set_gliding(input_handler.is_down(input_handler.BUTTON4))

    def update_coins(self):
        """Update coins and check for collection"""
        for coin in self.coins:
            if self.player.got_coin(coin) and coin.is_on_screen:
                self.total_coins += 1
                self.gsm.add_score(100)
                coin.player_got(self.gsm.audio_manager)
            coin.update(16.67)

    def check_win_condition(self, level_name="Level"):
        """
        Check if player has won and handle win state

        Args:
            level_name: Name of the level for display

        Returns:
            bool: True if win state is active, False otherwise
        """
        if self.player.has_won():
            if not self.has_won:
                self.has_won = True
                if not self.win_sound_played:
                    self.gsm.audio_manager.stop_music()
                    self.gsm.audio_manager.play_sound("win")
                    self.win_sound_played = True
            if self.gsm.input_handler.is_pressed(self.gsm.input_handler.BUTTON1):
                self.gsm.set_state(self.gsm.MENU_STATE)
            return True
        return False

    def check_win_condition_with_next_level(self, level_name="Level", next_level_state=None):
        """
        Check if player has won and handle win state with progression to next level

        Args:
            level_name: Name of the level for display
            next_level_state: The state to transition to on win (None for menu)

        Returns:
            bool: True if win state is active, False otherwise
        """
        if self.player.has_won():
            if not self.has_won:
                self.has_won = True
                if not self.win_sound_played:
                    self.gsm.audio_manager.stop_music()
                    self.gsm.audio_manager.play_sound("win")
                    self.win_sound_played = True
            if self.gsm.input_handler.is_pressed(self.gsm.input_handler.BUTTON1):
                if next_level_state is not None:
                    self.gsm.set_state(next_level_state)
                else:
                    self.gsm.set_state(self.gsm.MENU_STATE)
            return True
        return False

    def check_death_condition(self):
        """Check if player died and start death screen"""
        if self.player.is_dead():
            if self.death_screen_timer == 0:
                self.gsm.audio_manager.stop_music()
                if "death" not in self.gsm.audio_manager.sound_effects:
                    self.gsm.audio_manager.load_sound("death", "death.wav")
                self.gsm.audio_manager.play_sound("death")
                self.death_screen_timer = self.death_screen_duration
            return True
        return False

    def draw_death_screen(self, surface):
        """Draw death screen overlay"""
        if self.death_screen_timer > 0:
            overlay = pygame.Surface((320, 240))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            surface.blit(overlay, (0, 0))

            font_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../assets/fonts/upheavtt.ttf"))
            death_font = pygame.font.Font(font_path, 48)
            death_text = death_font.render("YOU DIED!", True, (255, 0, 0))
            death_rect = death_text.get_rect(center=(160, 120))
            surface.blit(death_text, death_rect)

    def update(self):
        """Update level logic (override in subclasses)"""
        pass

    def draw(self, surface):
        """Draw level (override in subclasses)"""
        pass
