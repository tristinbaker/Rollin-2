#!/usr/bin/env python3
"""
generate_level5.py
Generates assets/maps/level_5.tmj — a flat boss arena for Rollin 2 Level 5.
Run from the repo root: python generate_level5.py
"""
import json, zlib, base64, struct, os

WIDTH  = 120
HEIGHT = 35
TOTAL  = WIDTH * HEIGHT  # 4200 tiles


def decode_layer(data_b64):
    raw = zlib.decompress(base64.b64decode(data_b64))
    return list(struct.unpack(f'<{len(raw) // 4}I', raw))


def encode(tile_list):
    raw = struct.pack(f'<{len(tile_list)}I', *tile_list)
    return base64.b64encode(zlib.compress(raw)).decode()


def empty_layer():
    return [0] * TOTAL


# --- Sample tile GIDs from existing level_4.tmj ---
script_dir = os.path.dirname(os.path.abspath(__file__))
l4_path = os.path.join(script_dir, "assets/maps/level_4.tmj")
with open(l4_path) as f:
    l4 = json.load(f)

l4_layers = {layer["name"]: layer for layer in l4["layers"]}

# Sample fill tile IDs from level_4's ground body (rows 28-30, middle columns)
platforms_tiles = decode_layer(l4_layers["Static Platforms"]["data"])
floor_samples = [
    platforms_tiles[row * WIDTH + col]
    for row in range(28, 31)
    for col in range(10, 110, 5)
    if platforms_tiles[row * WIDTH + col] != 0
]
fill_gid = max(set(floor_samples), key=floor_samples.count)

# Sample top-surface tile IDs from row 27
top_samples = [
    platforms_tiles[27 * WIDTH + col]
    for col in range(10, 110, 5)
    if platforms_tiles[27 * WIDTH + col] != 0
]
top_gid = max(set(top_samples), key=top_samples.count) if top_samples else fill_gid

# Get the player spawn GID from level_4
spawn_tiles = decode_layer(l4_layers["Player Spawn"]["data"])
spawn_gid = next(t for t in spawn_tiles if t != 0)

print(f"Sampled GIDs — top: {top_gid}, fill: {fill_gid}, spawn: {spawn_gid}")


# --- Build Static Platforms layer ---
def make_static_platforms():
    tiles = empty_layer()

    def set_row(row, col_start, col_end, gid):
        for col in range(col_start, col_end + 1):
            tiles[row * WIDTH + col] = gid

    # Full-width flat ground
    set_row(27, 0, 119, top_gid)   # top surface
    for row in range(28, 35):
        set_row(row, 0, 119, fill_gid)

    # Elevated platforms: (col_start, col_end, surface_row)
    platforms = [
        (15, 22, 22),
        (35, 42, 19),
        (55, 62, 22),
        (72, 79, 19),
    ]
    for c0, c1, surf_row in platforms:
        set_row(surf_row,     c0, c1, top_gid)
        set_row(surf_row + 1, c0, c1, fill_gid)

    return tiles


def make_player_spawn():
    tiles = empty_layer()
    tiles[26 * WIDTH + 2] = spawn_gid
    return tiles


def make_layer(name, layer_id, tile_list):
    return {
        "compression": "zlib",
        "data": encode(tile_list),
        "encoding": "base64",
        "height": HEIGHT,
        "id": layer_id,
        "name": name,
        "opacity": 1,
        "type": "tilelayer",
        "visible": True,
        "width": WIDTH,
        "x": 0,
        "y": 0,
    }


layers = [
    make_layer("Background",                          16, empty_layer()),
    make_layer("Background 2",                        17, empty_layer()),
    make_layer("Static Platforms",                     1, make_static_platforms()),
    make_layer("Player Spawn",                        15, make_player_spawn()),
    make_layer("Spike Trap",                           3, empty_layer()),
    make_layer("Hearts",                              13, empty_layer()),
    make_layer("Lava",                                10, empty_layer()),
    make_layer("Opposite Vertical Moving Platforms",  18, empty_layer()),
    make_layer("Vertical Moving Platforms",            4, empty_layer()),
    make_layer("Horizontal Moving Platforms",          5, empty_layer()),
    make_layer("Coin",                                 8, empty_layer()),
    make_layer("Wasp",                                 9, empty_layer()),
    make_layer("Slime",                                7, empty_layer()),
    make_layer("Bat",                                  6, empty_layer()),
]

tmj = {
    "compressionlevel": -1,
    "height": HEIGHT,
    "infinite": False,
    "layers": layers,
    "nextlayerid": 19,
    "nextobjectid": 1,
    "orientation": "orthogonal",
    "renderorder": "right-down",
    "tiledversion": "1.12.1",
    "tileheight": 32,
    "tilesets": l4["tilesets"],  # exact copy from level_4
    "tilewidth": 32,
    "type": "map",
    "version": "1.10",
    "width": WIDTH,
}

out_path = os.path.join(script_dir, "assets/maps/level_5.tmj")
with open(out_path, "w") as f:
    json.dump(tmj, f, indent=1)
print(f"Written: {out_path}")
