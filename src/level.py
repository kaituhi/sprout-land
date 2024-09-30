import pygame
from pathlib import Path
from pytmx.util_pygame import load_pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree
from support import import_folder

class Level:
    def __init__(self):
        """Initialize the level, load the display surface, and set up sprite groups."""
        self.display_surface = pygame.display.get_surface()
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()

        self.player = None  # Initialize player as None
        self.setup_level()
        self.overlay = Overlay(self.player)  # Pass player after it's been set up

    def setup_level(self):
        """Load the level from the TMX file and initialize sprites."""
        tmx_data = load_pygame(Path('data/map.tmx'))

        self.load_house(tmx_data)
        self.load_fence(tmx_data)
        self.load_water(tmx_data)
        self.load_trees(tmx_data)
        self.load_wildflowers(tmx_data)
        self.load_collision_tiles(tmx_data)
        self.load_player(tmx_data)  # Player should be set up first
        self.load_ground()

    def load_house(self, tmx_data):
        """Load house-related sprites from the TMX data."""
        house_layers = ['HouseFloor', 'HouseFurnitureBottom', 'HouseWalls', 'HouseFurnitureTop']
        for layer in house_layers:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                z_order = LAYERS['house bottom'] if layer in ['HouseFloor', 'HouseFurnitureBottom'] else None
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, z_order)

    def load_fence(self, tmx_data):
        """Load fence sprites."""
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])

    def load_water(self, tmx_data):
        """Load water sprites."""
        water_frames = import_folder(Path('graphics/water'))
        for x, y, _ in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)

    def load_trees(self, tmx_data):
        """Load tree sprites."""
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites], obj.name)

    def load_wildflowers(self, tmx_data):
        """Load wildflower sprites."""
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

    def load_collision_tiles(self, tmx_data):
        """Load collision tiles."""
        for x, y, _ in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)

    def load_player(self, tmx_data):
        """Load the player sprite from TMX data."""
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)

    def load_ground(self):
        """Load the ground sprite."""
        ground_surface = pygame.image.load(Path('graphics/world/ground.png')).convert_alpha()
        Generic(
            position=(0, 0),
            surf=ground_surface,
            groups=self.all_sprites,
            z=LAYERS['ground']
        )

    def run(self, dt):
        """Update and draw the level."""
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)
        self.overlay.display()


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        """Initialize the camera group with the display surface."""
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        """Draw sprites with camera offset."""
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
