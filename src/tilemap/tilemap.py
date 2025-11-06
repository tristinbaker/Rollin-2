"""
TileMap - equivalent to TileMap.java
Handles tile-based map rendering and collision detection
"""
import pygame
import os
from tilemap.tile import Tile


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
        self.tiled_tiles = {}  # For Tiled: {tile_id: {'image': surface, 'type': NORMAL/BLOCKED}}

        # Drawing optimization
        self.row_offset = 0
        self.col_offset = 0
        self.num_rows_to_draw = 320 // tile_size + 2
        self.num_cols_to_draw = 240 // tile_size + 2

        # Base path for assets
        self.assets_path = self._find_assets_path()

    def _find_assets_path(self):
        """Find the assets directory"""
        # Need to go up two levels from tilemap/
        possible_paths = [
            "../../assets/",
            "../../../res/",
        ]

        for path in possible_paths:
            full_path = os.path.join(os.path.dirname(__file__), path)
            full_path = os.path.normpath(full_path)
            if os.path.exists(full_path):
                print(f"TileMap assets path: {full_path}")
                return full_path

        return os.path.normpath(os.path.join(os.path.dirname(__file__), "../../assets/"))

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

            print(f"Loaded tileset: {tileset_path} ({self.num_tiles_across} tiles)")

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
            print(f"Unknown map format: {map_path}")

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

            print(f"Loaded map: {map_path} ({self.num_cols}x{self.num_rows})")

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

            # Load tileset
            if 'tilesets' in data and len(data['tilesets']) > 0:
                tileset_data = data['tilesets'][0]
                if 'source' in tileset_data:
                    # External tileset
                    tsx_path = tileset_data['source']
                    self.load_tiled_tileset(tsx_path)
                else:
                    # Embedded tileset
                    print("Warning: Embedded tilesets not yet supported")

            # Load tile layer data and track collision layers
            collision_layer_names = ['platforms', 'collision', 'solid', 'ground']
            if 'layers' in data:
                for layer in data['layers']:
                    if layer['type'] == 'tilelayer' and layer.get('visible', True):
                        layer_name = layer.get('name', '').lower()
                        is_collision_layer = any(name in layer_name for name in collision_layer_names)

                        # Decompress tile data
                        encoded_data = layer['data']
                        compressed_data = base64.b64decode(encoded_data)
                        decompressed_data = zlib.decompress(compressed_data)

                        # Convert bytes to tile indices (little-endian 4-byte integers)
                        import struct
                        tile_count = len(decompressed_data) // 4
                        tiles = struct.unpack(f'<{tile_count}I', decompressed_data)

                        # Convert to 2D array
                        self.map = []
                        for row in range(self.num_rows):
                            row_data = []
                            for col in range(self.num_cols):
                                index = row * self.num_cols + col
                                tile_id = tiles[index]
                                row_data.append(tile_id)
                            self.map.append(row_data)

                        # If this is a collision layer, mark all its tiles as BLOCKED
                        if is_collision_layer:
                            print(f"Marking layer '{layer.get('name')}' as collision layer")
                            # Update all non-zero tiles in this layer to be BLOCKED
                            for tile_id in set(tiles):
                                if tile_id > 0 and tile_id in self.tiled_tiles:
                                    self.tiled_tiles[tile_id]['type'] = Tile.BLOCKED

                        # Only load first visible tile layer for now
                        break

            print(f"Loaded Tiled map: {map_path} ({self.num_cols}x{self.num_rows})")

        except Exception as e:
            print(f"Error loading Tiled map {map_path}: {e}")
            import traceback
            traceback.print_exc()

    def load_tiled_tileset(self, tsx_path):
        """
        Load Tiled tileset (.tsx) file

        Args:
            tsx_path: Path to .tsx file (relative to maps directory)
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
                self.tileset = pygame.image.load(image_path).convert_alpha()

                # Get tileset dimensions from XML
                tile_width = int(root.get('tilewidth'))
                tile_height = int(root.get('tileheight'))
                tile_count = int(root.get('tilecount'))
                columns = int(root.get('columns'))

                # Create tile dictionary
                self.tiled_tiles = {}

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
                tile_id = 1  # Tiled uses 1-based indexing (0 = empty) in map data

                rows = (tile_count + columns - 1) // columns
                for row in range(rows):
                    for col in range(columns):
                        if tile_id > tile_count:
                            break

                        # Extract tile image
                        tile_image = self.tileset.subsurface(
                            (col * tile_width, row * tile_height, tile_width, tile_height)
                        )

                        # Check if this tile has collision properties
                        # tile_id in map is 1-based, but tile definitions use 0-based IDs
                        props = tile_properties.get(tile_id - 1, {})
                        tile_type = Tile.NORMAL

                        # Check for collision property (support various naming conventions)
                        if props.get('type') == 'BLOCKED' or props.get('collision') == 'true' or props.get('blocked') == 'true':
                            tile_type = Tile.BLOCKED

                        self.tiled_tiles[tile_id] = {
                            'image': tile_image.copy(),
                            'type': tile_type
                        }

                        tile_id += 1

                blocked_count = sum(1 for t in self.tiled_tiles.values() if t['type'] == Tile.BLOCKED)
                print(f"Loaded Tiled tileset: {tsx_path} ({tile_count} tiles, {columns} columns, {blocked_count} blocked)")

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
            # Tiled format: lookup tile in dictionary
            if tile_index in self.tiled_tiles:
                return self.tiled_tiles[tile_index]['type']
            return Tile.NORMAL
        else:
            # Legacy format: calculate tileset row/col
            tile_row = tile_index // self.num_tiles_across
            tile_col = tile_index % self.num_tiles_across

            # Make sure indices are valid
            if tile_row >= len(self.tiles) or tile_col >= len(self.tiles[tile_row]):
                return Tile.NORMAL

            return self.tiles[tile_row][tile_col].type

    def draw(self, surface):
        """
        Draw ALL tiles in the map (works with both legacy and Tiled maps)

        Args:
            surface: pygame.Surface to draw on
        """
        # Draw every single tile in the entire map
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                tile_index = self.map[row][col]

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

                        print(f"Found {len(positions)} entities in '{layer_name}' layer")
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

                        print(f"Found {len(positions)} entities with tiles in '{layer_name}' layer")
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
        Find the spawn position on the highest leftmost collision tile.
        Returns (x, y) in world coordinates, positioned on top of the tile.

        Returns:
            tuple: (x, y) spawn position, or (25, 160) as default if no collision found
        """
        # Scan from left to right, top to bottom
        for col in range(self.num_cols):
            for row in range(self.num_rows):
                tile_type = self.get_type(row, col)

                # Found a collision tile
                if tile_type == Tile.BLOCKED:
                    # Position player on top of this tile
                    # World position = tile position
                    spawn_x = col * self.tile_size + self.tile_size // 2  # Center of tile horizontally
                    spawn_y = row * self.tile_size - 10  # Just above the tile (player height consideration)

                    print(f"Spawn position found at tile ({row}, {col}): world position ({spawn_x}, {spawn_y})")
                    return (spawn_x, spawn_y)

        # No collision tiles found, return default
        print("Warning: No collision tiles found for spawn, using default position")
        return (25, 160)
