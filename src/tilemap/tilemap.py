"""
TileMap - equivalent to TileMap.java
Handles tile-based map rendering and collision detection
"""
import pygame
import os
from tilemap.tile import Tile
from paths import asset


class TileMap:
    def __init__(self, tile_size):
        """
        Initialize tilemap

        Args:
            tile_size: Size of each tile in pixels (30 in original)
        """
        self.tile_size = tile_size

        # Position (camera)
        self.x = 0
        self.y = 0

        # Bounds
        self.xmin = 0
        self.ymin = 0
        self.xmax = 0
        self.ymax = 0

        # Camera smoothing (not used in simple implementation)
        self.tween = 0.07

        # Map data
        self.map = []
        self.num_rows = 0
        self.num_cols = 0
        self.width = 0
        self.height = 0

        # Map format tracking
        self.map_format = None  # 'legacy' or 'tiled'

        # Tileset
        self.tileset = None
        self.num_tiles_across = 0
        self.tiles = []  # 2D array: [row][col] where row 0=NORMAL, row 1=BLOCKED

        # Tiled-specific data
        self.tiled_tiles = {}  # For Tiled: {tile_id: {'image': surface, 'type': NORMAL/BLOCKED, 'slope_type': NONE/LEFT/RIGHT}}
        self.slope_layer_map = []  # Separate 2D array for slope tiles from "Static Sloped Platforms" layer
        self.background_layers = []  # List of background layer maps (rendered behind main layer, no collision)

        # Drawing optimization
        self.row_offset = 0
        self.col_offset = 0
        self.num_rows_to_draw = 320 // tile_size + 2
        self.num_cols_to_draw = 240 // tile_size + 2

        # Base path for assets
        self.assets_path = self._find_assets_path()

    def _find_assets_path(self):
        return asset()

    def load_tiles(self, tileset_path):
        """
        Load tileset image and create tile objects

        Args:
            tileset_path: Path to tileset image (relative to assets)
        """
        full_path = os.path.join(self.assets_path, tileset_path)

        try:
            self.tileset = pygame.image.load(full_path).convert_alpha()
            self.num_tiles_across = self.tileset.get_width() // self.tile_size

            # Create 2D tile array: row 0 = NORMAL, row 1 = BLOCKED
            self.tiles = [[], []]

            for col in range(self.num_tiles_across):
                # Normal tiles (top row of tileset)
                tile_image = self.tileset.subsurface(
                    (col * self.tile_size, 0, self.tile_size, self.tile_size)
                )
                self.tiles[0].append(Tile(tile_image, Tile.NORMAL))

                # Blocked tiles (bottom row of tileset)
                tile_image = self.tileset.subsurface(
                    (col * self.tile_size, self.tile_size, self.tile_size, self.tile_size)
                )
                self.tiles[1].append(Tile(tile_image, Tile.BLOCKED))

        except Exception as e:
            print(f"Error loading tileset {tileset_path}: {e}")

    def load_map(self, map_path):
        """
        Auto-detect map format and load appropriately

        Args:
            map_path: Path to map file (relative to assets)
        """
        if map_path.endswith('.map'):
            self.load_legacy_map(map_path)
        elif map_path.endswith('.tmj') or map_path.endswith('.json'):
            self.load_tiled_map(map_path)
        else:
            pass

    def load_legacy_map(self, map_path):
        """
        Load legacy .map format

        Map format:
        Line 1: number of columns
        Line 2: number of rows
        Rest: space-separated tile indices

        Args:
            map_path: Path to map file (relative to assets)
        """
        self.map_format = 'legacy'
        full_path = os.path.join(self.assets_path, map_path)

        try:
            with open(full_path, 'r') as f:
                # Read dimensions
                self.num_cols = int(f.readline().strip())
                self.num_rows = int(f.readline().strip())

                # Initialize map array
                self.map = []

                # Calculate map dimensions
                self.width = self.num_cols * self.tile_size
                self.height = self.num_rows * self.tile_size

                # Set bounds (for camera limits)
                self.xmin = 320 - self.width  # GamePanel.WIDTH - width
                self.xmax = 0
                self.ymin = 240 - self.height  # GamePanel.HEIGHT - height
                self.ymax = 0

                # Read map data
                for row in range(self.num_rows):
                    line = f.readline().strip()
                    tokens = line.split()
                    row_data = [int(token) for token in tokens]
                    self.map.append(row_data)

        except Exception as e:
            print(f"Error loading map {map_path}: {e}")

    def load_tiled_map(self, map_path):
        """
        Load Tiled .tmj (JSON) format

        Args:
            map_path: Path to .tmj file (relative to assets)
        """
        import json
        import zlib
        import base64

        self.map_format = 'tiled'
        self._last_loaded_map_path = map_path  # Store for later entity extraction
        full_path = os.path.join(self.assets_path, map_path)

        try:
            with open(full_path, 'r') as f:
                data = json.load(f)

            # Get map dimensions
            self.num_cols = data['width']
            self.num_rows = data['height']
            self.width = self.num_cols * self.tile_size
            self.height = self.num_rows * self.tile_size

            # Set camera bounds
            self.xmin = 320 - self.width
            self.xmax = 0
            self.ymin = 240 - self.height
            self.ymax = 0

            # Load all tilesets and handle firstgid offsets
            self.tiled_tiles = {}
            self.tiled_tilesets_info = []  # List of (firstgid, tilecount, source)
            if 'tilesets' in data:
                for tileset_data in data['tilesets']:
                    if 'source' in tileset_data:
                        tsx_path = tileset_data['source']
                        firstgid = tileset_data.get('firstgid', 1)
                        # Parse .tsx to get tilecount
                        import xml.etree.ElementTree as ET
                        maps_dir = os.path.join(self.assets_path, "maps")
                        tsx_full_path = os.path.join(maps_dir, tsx_path)
                        try:
                            tree = ET.parse(tsx_full_path)
                            root = tree.getroot()
                            tilecount = int(root.get('tilecount'))
                        except Exception:
                            tilecount = 0
                        self.tiled_tilesets_info.append((firstgid, tilecount, tsx_path))
                        self._load_tiled_tileset_with_gid(tsx_path, firstgid)
                    else:
                        print("Warning: Embedded tilesets not yet supported")

            # Load tile layer data and track collision layers
            collision_layer_names = ['platforms', 'collision', 'solid', 'ground']
            slope_layer_names = ['static sloped platforms', 'sloped platforms', 'slopes']
            background_layer_names = ['background', 'background 2']
            
            # Initialize slope layer map with zeros
            self.slope_layer_map = [[0 for _ in range(self.num_cols)] for _ in range(self.num_rows)]
            
            if 'layers' in data:
                for layer in data['layers']:
                    if layer['type'] == 'tilelayer' and layer.get('visible', True):
                        layer_name = layer.get('name', '').lower()
                        is_collision_layer = any(name in layer_name for name in collision_layer_names)
                        is_slope_layer = any(name in layer_name for name in slope_layer_names)
                        is_background_layer = any(name in layer_name for name in background_layer_names)

                        # Decompress tile data
                        encoded_data = layer['data']
                        compressed_data = base64.b64decode(encoded_data)
                        decompressed_data = zlib.decompress(compressed_data)

                        # Convert bytes to tile indices (little-endian 4-byte integers)
                        import struct
                        tile_count = len(decompressed_data) // 4
                        tiles = struct.unpack(f'<{tile_count}I', decompressed_data)

                        # Handle different layer types
                        if is_background_layer:
                            # Store background layer data (no collision)
                            background_layer = []
                            for row in range(self.num_rows):
                                row_data = []
                                for col in range(self.num_cols):
                                    index = row * self.num_cols + col
                                    tile_id = tiles[index]
                                    row_data.append(tile_id)
                                background_layer.append(row_data)
                            self.background_layers.append(background_layer)

                        elif is_slope_layer:
                            # Store slope layer data separately 
                            for row in range(self.num_rows):
                                for col in range(self.num_cols):
                                    index = row * self.num_cols + col
                                    tile_id = tiles[index]
                                    self.slope_layer_map[row][col] = tile_id
                        elif not hasattr(self, 'map') or not self.map:
                            # Convert to 2D array for the main collision layer
                            self.map = []
                            for row in range(self.num_rows):
                                row_data = []
                                for col in range(self.num_cols):
                                    index = row * self.num_cols + col
                                    tile_id = tiles[index]
                                    row_data.append(tile_id)
                                self.map.append(row_data)

                            # If this is a collision layer, mark tiles as BLOCKED only if they don't have slope properties
                            if is_collision_layer:
                                # Update non-zero tiles to be BLOCKED, but preserve slope tiles as NORMAL
                                for tile_id in set(tiles):
                                    if tile_id > 0 and tile_id in self.tiled_tiles:
                                        if self.tiled_tiles[tile_id].get('slope_type') is None:
                                            self.tiled_tiles[tile_id]['type'] = Tile.BLOCKED
                                        else:
                                            self.tiled_tiles[tile_id]['type'] = Tile.NORMAL
                        else:
                            pass

                        # Continue processing more layers (don't break on first layer)

        except Exception as e:
            print(f"Error loading Tiled map {map_path}: {e}")
            import traceback
            traceback.print_exc()

    def _load_tiled_tileset_with_gid(self, tsx_path, firstgid):
        """
        Load Tiled tileset (.tsx) file

        Args:
            tsx_path: Path to .tsx file (relative to maps directory)
            firstgid: The first global tile ID for this tileset
        """
        import xml.etree.ElementTree as ET

        # tsx_path is relative to the map file location
        # Map files are in assets/maps/, so tileset is relative to that
        maps_dir = os.path.join(self.assets_path, "maps")
        full_path = os.path.join(maps_dir, tsx_path)

        try:
            tree = ET.parse(full_path)
            root = tree.getroot()

            # Get tileset image
            image_elem = root.find('image')
            if image_elem is not None:
                image_source = image_elem.get('source')
                # Image path is relative to the .tsx file
                tsx_dir = os.path.dirname(full_path)
                image_path = os.path.join(tsx_dir, image_source)

                # Load tileset image
                tileset_image = pygame.image.load(image_path).convert_alpha()

                # Get tileset dimensions from XML
                tile_width = int(root.get('tilewidth'))
                tile_height = int(root.get('tileheight'))
                tile_count = int(root.get('tilecount'))
                columns = int(root.get('columns'))

                # Create tile dictionary
                # self.tiled_tiles = {} # Already initialized in load_tiled_map

                # First, parse tile properties from the tileset
                tile_properties = {}  # {tile_id: properties_dict}
                for tile_elem in root.findall('tile'):
                    tid = int(tile_elem.get('id'))  # Tiled uses 0-based IDs in tile definitions
                    properties = {}
                    properties_elem = tile_elem.find('properties')
                    if properties_elem is not None:
                        for prop in properties_elem.findall('property'):
                            prop_name = prop.get('name')
                            prop_value = prop.get('value')
                            properties[prop_name] = prop_value
                    tile_properties[tid] = properties

                # Now create tile images with collision info
                # tile_id in map is firstgid-based, so we need to offset
                tile_id = firstgid
                rows = (tile_count + columns - 1) // columns
                for row in range(rows):
                    for col in range(columns):
                        if tile_id >= firstgid + tile_count:
                            break
                        # Extract tile image
                        tile_image = tileset_image.subsurface(
                            (col * tile_width, row * tile_height, tile_width, tile_height)
                        )
                        # Check if this tile has collision properties
                        props = tile_properties.get(tile_id - firstgid, {})
                        tile_type = Tile.NORMAL
                        slope_type = None
                        if props.get('type') == 'BLOCKED' or props.get('collision') == 'true' or props.get('blocked') == 'true':
                            tile_type = Tile.BLOCKED
                        if props.get('right_slope') == 'true':
                            slope_type = Tile.RIGHT_SLOPE
                        elif props.get('left_slope') == 'true':
                            slope_type = Tile.LEFT_SLOPE
                        self.tiled_tiles[tile_id] = {
                            'image': tile_image.copy(),
                            'type': tile_type,
                            'slope_type': slope_type
                        }
                        tile_id += 1
        except Exception as e:
            print(f"Error loading Tiled tileset {tsx_path}: {e}")
            import traceback
            traceback.print_exc()

    def set_position(self, x, y):
        """
        Set camera position with smooth tweening

        Args:
            x: Target X position
            y: Target Y position
        """
        # Smooth camera movement (tween)
        self.x += (x - self.x) * self.tween
        self.y += (y - self.y) * self.tween

        # Clamp to bounds
        if self.x < self.xmin:
            self.x = self.xmin
        if self.x > self.xmax:
            self.x = self.xmax
        if self.y < self.ymin:
            self.y = self.ymin
        if self.y > self.ymax:
            self.y = self.ymax

        # Calculate which tiles to draw
        self.col_offset = int(-self.x / self.tile_size)
        self.row_offset = int(-self.y / self.tile_size)

    def set_position_immediate(self, x, y):
        """
        Set camera position immediately without tweening
        Use this for initialization

        Args:
            x: X position
            y: Y position
        """
        self.x = x
        self.y = y

        # Clamp to bounds
        if self.x < self.xmin:
            self.x = self.xmin
        if self.x > self.xmax:
            self.x = self.xmax
        if self.y < self.ymin:
            self.y = self.ymin
        if self.y > self.ymax:
            self.y = self.ymax

        # Calculate which tiles to draw
        self.col_offset = int(-self.x / self.tile_size)
        self.row_offset = int(-self.y / self.tile_size)

    def get_type(self, row, col):
        """
        Get tile type at position (works with both legacy and Tiled maps)

        Args:
            row: Row index
            col: Column index

        Returns:
            Tile.NORMAL or Tile.BLOCKED, or NORMAL if out of bounds
        """
        if row < 0 or row >= self.num_rows or col < 0 or col >= self.num_cols:
            return Tile.NORMAL

        tile_index = self.map[row][col]

        # Tile index 0 = empty (no tile)
        if tile_index == 0:
            return Tile.NORMAL

        # Use appropriate collision system based on map format
        if self.map_format == 'tiled':
            # Check if this position has a slope tile in the slope layer first
            if (hasattr(self, 'slope_layer_map') and self.slope_layer_map and
                row < len(self.slope_layer_map) and col < len(self.slope_layer_map[row]) and
                self.slope_layer_map[row][col] != 0):
                # This position has a slope in separate slope layer, so don't use rectangular collision
                return Tile.NORMAL
            
            # Tiled format: lookup tile in dictionary
            if tile_index in self.tiled_tiles:
                # Check if this tile has slope properties (mixed slope/collision layer)
                tile_data = self.tiled_tiles[tile_index]
                if tile_data.get('slope_type') is not None:
                    # This tile has slope properties, so don't use rectangular collision
                    return Tile.NORMAL
                # Regular tile, use its collision type
                return tile_data['type']
            return Tile.NORMAL
        else:
            # Legacy format: calculate tileset row/col
            tile_row = tile_index // self.num_tiles_across
            tile_col = tile_index % self.num_tiles_across

            # Make sure indices are valid
            if tile_row >= len(self.tiles) or tile_col >= len(self.tiles[tile_row]):
                return Tile.NORMAL

            return self.tiles[tile_row][tile_col].type

    def get_slope_type(self, row, col):
        """
        Get slope type at position - checks both slope layer and main map
        
        Args:
            row: Row index
            col: Column index
            
        Returns:
            Tile.LEFT_SLOPE, Tile.RIGHT_SLOPE, or None if no slope
        """
        if (row < 0 or row >= self.num_rows or 
            col < 0 or col >= self.num_cols):
            return None
        
        # First check the separate slope layer if it exists
        if (hasattr(self, 'slope_layer_map') and 
            self.slope_layer_map and 
            row < len(self.slope_layer_map) and 
            col < len(self.slope_layer_map[row])):
            
            tile_index = self.slope_layer_map[row][col]
            if tile_index != 0 and self.map_format == 'tiled' and tile_index in self.tiled_tiles:
                slope_type = self.tiled_tiles[tile_index].get('slope_type')
                if slope_type is not None:
                    return slope_type
        
        # If no slope in separate layer, check main map for slope properties
        if (hasattr(self, 'map') and self.map and 
            row < len(self.map) and col < len(self.map[row])):
            
            tile_index = self.map[row][col]
            if tile_index != 0 and self.map_format == 'tiled' and tile_index in self.tiled_tiles:
                slope_type = self.tiled_tiles[tile_index].get('slope_type')
                if slope_type is not None:
                    return slope_type
            
        return None

    def check_slope_collision(self, x, y, player_width, player_height, dy=0, debug=False):
        """
        Check for slope collision and return the adjusted Y position
        
        Args:
            x: Player center X position
            y: Player center Y position
            player_width: Player collision width
            player_height: Player collision height
            dy: Player's vertical velocity (optional, used to prevent jump interference)
            debug: Enable debug output
            
        Returns:
            tuple: (collision_occurred, adjusted_y, slope_type)
        """

        # Don't detect slopes when jumping upward (prevents infinite jump bug)
        if dy < -0.5:  # Player is moving up with significant velocity
            return (False, y, None)
        tile_size = self.tile_size
        
        # Get the tile coordinates for the player's bottom edge
        player_bottom = y + player_height / 2
        player_left = x - player_width / 2
        player_right = x + player_width / 2
        

        # Check tiles that the player might be standing on or falling into
        tile_left = int(player_left / tile_size)
        tile_right = int(player_right / tile_size)
        
        # Check current tile row and the one below (for when falling/landing on slopes)
        current_tile_row = int(y / tile_size)  # Player center tile row
        bottom_tile_row = int(player_bottom / tile_size)  # Player bottom tile row
        

        # Store the best slope match (closest to player's bottom)
        best_slope_y = None
        best_slope_type = None
        
        # Check both the current row and bottom row for slopes (avoid duplicates)
        tile_rows_to_check = list(dict.fromkeys([current_tile_row, bottom_tile_row]))  # Remove duplicates while preserving order
        
        if debug:
            print(f"Checking tiles in rows: {tile_rows_to_check}")
        
        for tile_row in tile_rows_to_check:
            for tile_col in range(tile_left, tile_right + 1):

                # Check slope layer first
                slope_type = self.get_slope_type(tile_row, tile_col)
                
                # If no slope in separate layer, check main collision layer for slope tiles
                if slope_type is None and hasattr(self, 'map') and self.map:
                    if (tile_row >= 0 and tile_row < len(self.map) and 
                        tile_col >= 0 and tile_col < len(self.map[tile_row])):
                        tile_index = self.map[tile_row][tile_col]
                        if tile_index > 0 and tile_index in self.tiled_tiles:
                            slope_type = self.tiled_tiles[tile_index].get('slope_type')
                
                if slope_type is None:
                    continue
                    
                # Calculate the slope height at the player's X position within this tile
                tile_x_start = tile_col * tile_size
                tile_x_end = tile_x_start + tile_size  # This is 160 for tile_col=4
                tile_y_start = tile_row * tile_size
                tile_y_end = tile_y_start + tile_size
                
                # Check if player overlaps with this tile (player could straddle boundary)
                player_left_edge = x - player_width / 2
                player_right_edge = x + player_width / 2
                
                # Skip if player doesn't overlap this tile at all
                if player_right_edge <= tile_x_start or player_left_edge >= tile_x_end:
                    continue
                
                # Use player center X for slope calculation, but clamp to tile bounds
                # Ensure we don't go exactly to the edge to avoid floating point issues
                player_x_in_tile = max(tile_x_start + 0.01, min(tile_x_end - 0.01, x))
                
                # Calculate relative position within tile (0.0 to 1.0)
                relative_x = (player_x_in_tile - tile_x_start) / tile_size
                
                if slope_type == Tile.RIGHT_SLOPE:
                    # Right slope: high on left (0), low on right (1)
                    # slope height decreases from left to right
                    # Height goes from full tile height at left to 0 at right
                    slope_height_ratio = 1.0 - relative_x
                elif slope_type == Tile.LEFT_SLOPE:
                    # Left slope: low on left (0), high on right (1) 
                    # slope height increases from left to right
                    # Height goes from 0 at left to full tile height at right
                    slope_height_ratio = relative_x
                else:
                    continue
                    
                # Calculate the actual Y position of the slope at this X
                slope_y = tile_y_start + (1.0 - slope_height_ratio) * tile_size
                

                # Check if player should be on the slope
                # Player must be at or below slope surface (with generous tolerance for smooth movement)
                tolerance = 15  # Increased tolerance to prevent ledges during horizontal movement
                
                # Check tolerance
                tolerance_check = player_bottom >= (slope_y - tolerance)
                

                if tolerance_check:
                    # Store slopes separately for center vs edge tiles
                    player_center_in_tile = (x >= tile_x_start and x < tile_x_end)
                    
                    if player_center_in_tile:
                        # Player center is in this tile - this takes absolute priority
                        best_slope_y = slope_y
                        best_slope_type = slope_type
                    elif best_slope_y is None:
                        # No slope found yet and this isn't a center tile, but use it as fallback
                        best_slope_y = slope_y
                        best_slope_type = slope_type
                    # If we already have a slope and this isn't a center tile, ignore it
        
        # Apply the best slope collision found
        if best_slope_y is not None:
            adjusted_y = best_slope_y - player_height / 2
            

            return (True, adjusted_y, best_slope_type)
        

        
        return (False, y, None)

    def draw(self, surface):
        """
        Draw ALL tiles in the map (works with both legacy and Tiled maps)
        Renders background layers first, then lava layers, then main layer

        Args:
            surface: pygame.Surface to draw on
        """
        # First, draw all background layers (behind everything else)
        # Ensure 'Background' is drawn first, then 'Background 2', then others
        ordered_backgrounds = []
        names = [layer.get('name', '').lower() for layer in getattr(self, '_raw_layers', [])]
        # If _raw_layers is not set, fallback to current order
        if hasattr(self, '_raw_layers'):
            # Find indices for 'background' and 'background 2'
            bg_indices = [i for i, n in enumerate(names) if n == 'background']
            bg2_indices = [i for i, n in enumerate(names) if n == 'background 2']
            # Add 'Background' first
            for i in bg_indices:
                ordered_backgrounds.append(self.background_layers[i])
            # Then 'Background 2'
            for i in bg2_indices:
                ordered_backgrounds.append(self.background_layers[i])
            # Then any other background layers
            for i, n in enumerate(names):
                if n not in ('background', 'background 2'):
                    ordered_backgrounds.append(self.background_layers[i])
        else:
            ordered_backgrounds = self.background_layers
        for background_layer in ordered_backgrounds:
            self._draw_layer(surface, background_layer)
        

        
        # Then draw the main collision/foreground layer (includes Static Platforms)
        self._draw_layer(surface, self.map)

    def draw_with_lava_entities(self, surface, lava_entities):
        """
        Draw tilemap with lava entities rendered under Static Platforms layer
        
        Args:
            surface: pygame.Surface to draw on
            lava_entities: List of lava entities to draw between background and static platforms
        """
        # First, draw all background layers (behind everything else)
        for background_layer in self.background_layers:
            self._draw_layer(surface, background_layer)
        
        # Then draw lava entities (underneath static platforms)
        for lava_entity in lava_entities:
            lava_entity.draw(surface)
        
        # Finally draw the main collision/foreground layer (includes Static Platforms)
        self._draw_layer(surface, self.map)

    def _draw_layer(self, surface, layer_map):
        """
        Draw a specific layer

        Args:
            surface: pygame.Surface to draw on
            layer_map: 2D array representing the layer
        """
        if not layer_map:
            return
            
        # Draw every tile in the layer
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                # Make sure we don't go out of bounds
                if row >= len(layer_map) or col >= len(layer_map[row]):
                    continue
                    
                tile_index = layer_map[row][col]

                # Skip empty tiles
                if tile_index == 0:
                    continue

                # Get tile image based on map format
                if self.map_format == 'tiled':
                    # Tiled format: lookup tile in dictionary
                    if tile_index not in self.tiled_tiles:
                        continue
                    tile_image = self.tiled_tiles[tile_index]['image']
                else:
                    # Legacy format: calculate tileset row/col
                    tile_row = tile_index // self.num_tiles_across
                    tile_col = tile_index % self.num_tiles_across

                    # Make sure indices are valid
                    if tile_row >= len(self.tiles) or tile_col >= len(self.tiles[tile_row]):
                        continue

                    tile_image = self.tiles[tile_row][tile_col].image

                # Calculate screen position
                x = int(self.x + col * self.tile_size)
                y = int(self.y + row * self.tile_size)

                # Only draw if on screen (optimization)
                if x + self.tile_size > 0 and x < 320 and y + self.tile_size > 0 and y < 240:
                    surface.blit(tile_image, (x, y))

    # Getters
    def get_tile_size(self):
        return self.tile_size

    def get_x(self):
        return int(self.x)

    def get_y(self):
        return int(self.y)

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_num_rows(self):
        return self.num_rows

    def get_num_cols(self):
        return self.num_cols

    def get_entity_positions_from_layer(self, layer_name):
        """
        Extract entity positions from a specific tile layer in a Tiled map.
        Returns a list of (x, y) tuples for each non-empty tile in the layer.

        Args:
            layer_name: Name of the layer (e.g., "Spikes", "Coins", "Enemies")

        Returns:
            list: List of (x, y) world position tuples
        """
        if self.map_format != 'tiled':
            print(f"Warning: get_entity_positions_from_layer only works with Tiled maps")
            return []

        # Re-load the map file to access all layers (not just the first one)
        import json
        import zlib
        import base64
        import struct

        map_path = self._last_loaded_map_path if hasattr(self, '_last_loaded_map_path') else None
        if not map_path:
            print(f"Warning: Cannot extract entities - map path not stored")
            return []

        full_path = os.path.join(self.assets_path, map_path)

        try:
            with open(full_path, 'r') as f:
                data = json.load(f)

            positions = []

            if 'layers' in data:
                for layer in data['layers']:
                    if layer['type'] == 'tilelayer' and layer.get('name', '').lower() == layer_name.lower():
                        # Found the target layer
                        encoded_data = layer['data']
                        compressed_data = base64.b64decode(encoded_data)
                        decompressed_data = zlib.decompress(compressed_data)

                        tile_count = len(decompressed_data) // 4
                        tiles = struct.unpack(f'<{tile_count}I', decompressed_data)

                        # Extract positions of non-empty tiles
                        for row in range(self.num_rows):
                            for col in range(self.num_cols):
                                index = row * self.num_cols + col
                                tile_id = tiles[index]

                                if tile_id > 0:  # Non-empty tile
                                    # Calculate world position
                                    # X: center of tile
                                    # Y: half a tile above the top of the tile position
                                    x = col * self.tile_size + self.tile_size // 2
                                    y = row * self.tile_size - self.tile_size // 2
                                    positions.append((x, y))


                        return positions

            print(f"Warning: Layer '{layer_name}' not found in map")
            return []

        except Exception as e:
            print(f"Error extracting entities from layer '{layer_name}': {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_entity_positions_with_tiles(self, layer_name):
        """
        Extract entity positions with tile IDs from a specific tile layer in a Tiled map.
        Returns a list of (x, y, tile_id) tuples for each non-empty tile in the layer.

        Args:
            layer_name: Name of the layer (e.g., "Vertical Moving Platforms")

        Returns:
            list: List of (x, y, tile_id) world position tuples
        """
        if self.map_format != 'tiled':
            print(f"Warning: get_entity_positions_with_tiles only works with Tiled maps")
            return []

        # Re-load the map file to access all layers (not just the first one)
        import json
        import zlib
        import base64
        import struct

        map_path = self._last_loaded_map_path if hasattr(self, '_last_loaded_map_path') else None
        if not map_path:
            print(f"Warning: Cannot extract entities - map path not stored")
            return []

        full_path = os.path.join(self.assets_path, map_path)

        try:
            with open(full_path, 'r') as f:
                data = json.load(f)

            positions = []

            if 'layers' in data:
                for layer in data['layers']:
                    if layer['type'] == 'tilelayer' and layer.get('name', '').lower() == layer_name.lower():
                        # Found the target layer
                        encoded_data = layer['data']
                        compressed_data = base64.b64decode(encoded_data)
                        decompressed_data = zlib.decompress(compressed_data)

                        tile_count = len(decompressed_data) // 4
                        tiles = struct.unpack(f'<{tile_count}I', decompressed_data)

                        # Extract positions of non-empty tiles with tile IDs
                        for row in range(self.num_rows):
                            for col in range(self.num_cols):
                                index = row * self.num_cols + col
                                tile_id = tiles[index]

                                if tile_id > 0:  # Non-empty tile
                                    # Calculate world position
                                    # X: center of tile
                                    # Y: center of tile (for platforms)
                                    x = col * self.tile_size + self.tile_size // 2
                                    y = row * self.tile_size + self.tile_size // 2
                                    positions.append((x, y, tile_id))


                        return positions

            print(f"Warning: Layer '{layer_name}' not found in map")
            return []

        except Exception as e:
            print(f"Error extracting entities from layer '{layer_name}': {e}")
            import traceback
            traceback.print_exc()
            return []

    def find_spawn_position(self):
        """
        Find the spawn position from the "Player Spawn" layer.
        Returns (x, y) in world coordinates, positioned at the center of the spawn tile.

        Returns:
            tuple: (x, y) spawn position, or (25, 160) as default if no spawn tile found
        """
        # First try to get spawn position from "Player Spawn" layer
        spawn_positions = self.get_entity_positions_from_layer("Player Spawn")
        
        if spawn_positions:
            # Use the first (and should be only) spawn position
            spawn_x, spawn_y = spawn_positions[0]
            # Lower the player by one tile length (32px)
            spawn_y += self.tile_size

            return (spawn_x, spawn_y)
        
        # Fallback: scan for highest leftmost collision tile (legacy behavior)
        print("Warning: No 'Player Spawn' layer found, falling back to collision tile detection")
        for col in range(self.num_cols):
            for row in range(self.num_rows):
                tile_type = self.get_type(row, col)

                # Found a collision tile
                if tile_type == Tile.BLOCKED:
                    # Position player on top of this tile
                    # World position = tile position
                    spawn_x = col * self.tile_size + self.tile_size // 2  # Center of tile horizontally
                    spawn_y = row * self.tile_size - 10  # Just above the tile (player height consideration)


                    return (spawn_x, spawn_y)

        # No spawn or collision tiles found, return default
        print("Warning: No spawn or collision tiles found for spawn, using default position")
        return (25, 160)
