import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree
from pytmx.util_pygame import load_pygame
from support import import_folder
from pathlib import Path

class Level:
    def __init__(self):
        """Initialize the level and its components."""
        self.display_surface = pygame.display.get_surface()

        # Sprite groups
        self.sprites_group = CameraGroup()

        # Initialize level setup
        self.setup_level()
        self.overlay = Overlay(self.player)

    def setup_level(self):
        """Setup the level using data from a Tiled map."""
        tmx_data = load_pygame(Path('data/map.tmx'))

        # Generic map elements
        self.load_static_layers(tmx_data, ['HouseFloor', 'HouseFurnitureBottom'], LAYERS['house bottom'])
        self.load_static_layers(tmx_data, ['HouseWalls', 'HouseFurnitureTop'], LAYERS['main'])
        self.load_static_layers(tmx_data, ['Fence'], LAYERS['main'])

        # Animated water
        water_frames = import_folder(Path('graphics/water'))
        self.load_animated_tiles(tmx_data, 'Water', Water, water_frames)

        # Trees and wildflowers
        self.load_objects(tmx_data, 'Trees', Tree)
        self.load_objects(tmx_data, 'Decoration', WildFlower)

        # Player and Ground
        self.player = Player((640, 360), self.sprites_group)
        Generic(
            position=(0, 0),
            surf=pygame.image.load(Path('graphics/world/ground.png')).convert_alpha(),
            groups=self.sprites_group,
            z=LAYERS['ground']
        )

    def load_static_layers(self, tmx_data, layers, layer_z):
        """Load static tiles from specific layers of the Tiled map."""
        for layer in layers:
            for x, y, surface in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surface, self.sprites_group, layer_z)

    def load_animated_tiles(self, tmx_data, layer_name, sprite_class, frames):
        """Load animated tiles like water."""
        for x, y, _ in tmx_data.get_layer_by_name(layer_name).tiles():
            sprite_class((x * TILE_SIZE, y * TILE_SIZE), frames, self.sprites_group)

    def load_objects(self, tmx_data, layer_name, sprite_class):
        """Load object layers like trees and decorations."""
        for obj in tmx_data.get_layer_by_name(layer_name):
            if sprite_class == Tree:
                sprite_class((obj.x, obj.y), obj.image, self.sprites_group, obj.name)
            else:
                sprite_class((obj.x, obj.y), obj.image, self.sprites_group)

    def run(self, delta_time):
        """Run the level, updating and drawing all components."""
        self.display_surface.fill("black")
        self.sprites_group.custom_draw(self.player)
        self.sprites_group.update(delta_time)
        self.overlay.display()

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def custom_draw(self, player):
        """Draw all sprites with camera offset applied."""
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.topleft -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
