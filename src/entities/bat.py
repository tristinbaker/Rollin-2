import pygame
import os
from paths import asset
import random
from entities.enemy import Enemy
from tilemap.tile import Tile


class Bat(Enemy):
    """Bat enemy - flies around within a defined boundary"""

    def __init__(self, tilemap, min_x, max_x, movement_mode="random"):
        super().__init__(tilemap)

        # Bat size (assuming 32x32 per frame)
        self.width = 32
        self.height = 32
        self.cwidth = 18  # Collision width
        self.cheight = 18  # Collision height

        # Movement boundaries
        self.min_x = min_x
        self.max_x = max_x
        # Set vertical boundaries relative to spawn position (will be set in set_position)
        self.min_y = 0
        self.max_y = 240

        # Movement mode: "predictable" or "random"
        self.movement_mode = movement_mode

        # Movement
        self.speed = 0.8
        self.dx = random.choice([-1, 1]) * self.speed  # Random initial horizontal direction
        self.dy = random.choice([-1, 1]) * self.speed  # Random initial vertical direction

        # Random movement variables
        self.direction_change_timer = 0
        self.direction_change_interval = random.randint(500, 1500)  # Change direction every 0.5-1.5 seconds
        


        # Load sprites
        self._load_sprites()

    def set_position(self, x, y):
        """Set bat position and calculate vertical boundaries"""
        super().set_position(x, y)
        # Set vertical boundaries relative to spawn position (±50 pixels)
        boundary_range = 50
        self.min_y = max(0, y - boundary_range)
        self.max_y = y + boundary_range

    def _load_sprites(self):
        """Load bat sprite sheet"""
        sprite_path = asset("sprites/bat.gif")

        if not os.path.exists(sprite_path):
            print("Error: Could not find bat.gif")
            return

        try:
            sprite_sheet = pygame.image.load(sprite_path).convert()

            # Set pink as transparent color (common GIF background color)
            # This makes the pink background transparent
            sprite_sheet.set_colorkey((255, 0, 255))  # Magenta/Pink

            # Get sprite sheet dimensions to determine frame size
            sheet_width = sprite_sheet.get_width()
            sheet_height = sprite_sheet.get_height()

            # Assume square frames for now, adjust if needed
            sprite_width = 32
            sprite_height = 32
            num_frames = sheet_width // sprite_width

            all_sprites = [
                sprite_sheet.subsurface((i * sprite_width, 0, sprite_width, sprite_height)).copy()
                for i in range(num_frames)
            ]

            # Apply colorkey to each sprite
            for sprite in all_sprites:
                sprite.set_colorkey((255, 0, 255))

            # Use first 5 frames for flying animation (6th frame is for landing, not used for now)
            flying_sprites = all_sprites[:5] if len(all_sprites) >= 5 else all_sprites

            if len(flying_sprites) > 0:
                self.animation.set_frames(flying_sprites)
                self.animation.set_delay(150)  # 150ms per frame
        except Exception as e:
            print(f"Error loading bat sprites: {e}")

    def check_tile_collision(self, x, y):
        """Check if position collides with blocked tiles"""
        tile_size = self.tilemap.get_tile_size()
        tile_x = int(x / tile_size)
        tile_y = int(y / tile_size)
        return self.tilemap.get_type(tile_y, tile_x) == Tile.BLOCKED

    def update(self, dt, spikes=None, moving_platforms=None):
        """Update bat"""
        # Update animation
        super().update(dt)

        if self.movement_mode == "random":
            self._update_random_movement(dt, moving_platforms)
        else:
            self._update_predictable_movement(dt, moving_platforms)

    def _update_predictable_movement(self, dt, moving_platforms=None):
        """Predictable W-pattern movement (easy mode)"""
        # Calculate next position
        next_x = self.x + self.dx
        next_y = self.y + self.dy

        # Check horizontal boundaries - when hitting boundary, reverse horizontal AND vertical
        # This creates the W pattern zigzag effect
        if next_x < self.min_x or next_x > self.max_x:

            self.dx = -self.dx  # Reverse horizontal direction
            self.dy = -self.dy  # Also reverse vertical to create W pattern
            next_x = self.x + self.dx
            next_y = self.y + self.dy

        # Check vertical boundaries - only reverse vertical, keep horizontal
        if next_y < self.min_y or next_y > self.max_y:

            self.dy = -self.dy  # Reverse vertical direction
            next_y = self.y + self.dy

        # Check tile collisions
        if self.check_tile_collision(next_x, self.y):
            self.dx = -self.dx  # Reverse horizontal direction
            self.dy = -self.dy  # Also reverse vertical for W pattern
            next_x = self.x + self.dx
            next_y = self.y + self.dy

        if self.check_tile_collision(self.x, next_y):
            self.dy = -self.dy  # Reverse vertical direction
            next_y = self.y + self.dy

        # Check moving platform collisions
        if moving_platforms:
            for platform in moving_platforms:
                if platform.intersects(next_x, self.y, self.cwidth, self.cheight):
                    self.dx = -self.dx
                    self.dy = -self.dy  # Also reverse vertical for W pattern
                    next_x = self.x + self.dx
                    next_y = self.y + self.dy
                if platform.intersects(self.x, next_y, self.cwidth, self.cheight):
                    self.dy = -self.dy
                    next_y = self.y + self.dy

        # Update position
        self.x = next_x
        self.y = next_y

    def _update_random_movement(self, dt, moving_platforms=None):
        """Random erratic movement (normal mode)"""
        # Update direction change timer
        self.direction_change_timer += dt

        # Randomly change direction
        if self.direction_change_timer >= self.direction_change_interval:
            self.direction_change_timer = 0
            self.direction_change_interval = random.randint(500, 1500)

            # Random chance to change each direction component
            if random.random() < 0.7:  # 70% chance to change horizontal
                self.dx = random.uniform(-self.speed, self.speed)
            if random.random() < 0.7:  # 70% chance to change vertical
                self.dy = random.uniform(-self.speed, self.speed)

        # Small random adjustments each frame for organic movement
        if random.random() < 0.05:  # 5% chance per frame
            self.dx += random.uniform(-0.2, 0.2)
            self.dy += random.uniform(-0.2, 0.2)

        # Clamp speed to max
        speed_magnitude = (self.dx ** 2 + self.dy ** 2) ** 0.5
        if speed_magnitude > self.speed * 1.5:
            self.dx = (self.dx / speed_magnitude) * self.speed * 1.5
            self.dy = (self.dy / speed_magnitude) * self.speed * 1.5

        # Calculate next position
        next_x = self.x + self.dx
        next_y = self.y + self.dy

        # Check horizontal boundaries
        if next_x < self.min_x or next_x > self.max_x:
            self.dx = -self.dx  # Reverse horizontal direction
            # Add some randomness to the bounce
            self.dx += random.uniform(-0.3, 0.3)
            next_x = self.x + self.dx

        # Check vertical boundaries
        if next_y < self.min_y or next_y > self.max_y:
            self.dy = -self.dy  # Reverse vertical direction
            # Add some randomness to the bounce
            self.dy += random.uniform(-0.3, 0.3)
            next_y = self.y + self.dy

        # Check tile collisions
        if self.check_tile_collision(next_x, self.y):
            self.dx = -self.dx + random.uniform(-0.3, 0.3)
            next_x = self.x + self.dx

        if self.check_tile_collision(self.x, next_y):
            self.dy = -self.dy + random.uniform(-0.3, 0.3)
            next_y = self.y + self.dy

        # Check moving platform collisions
        if moving_platforms:
            for platform in moving_platforms:
                if platform.intersects(next_x, self.y, self.cwidth, self.cheight):
                    self.dx = -self.dx + random.uniform(-0.3, 0.3)
                    next_x = self.x + self.dx
                if platform.intersects(self.x, next_y, self.cwidth, self.cheight):
                    self.dy = -self.dy + random.uniform(-0.3, 0.3)
                    next_y = self.y + self.dy

        # Update position
        self.x = next_x
        self.y = next_y

    def draw(self, surface):
        """Draw the bat (with flipping based on horizontal direction)"""
        image = self.animation.get_image()
        if image is None:
            return

        # Flip sprite based on direction (facing right when moving right)
        if self.dx > 0:
            image = pygame.transform.flip(image, True, False)

        draw_x = int(self.x - self.width / 2 + self.tilemap.get_x())
        draw_y = int(self.y - self.height / 2 + self.tilemap.get_y())
        surface.blit(image, (draw_x, draw_y))
