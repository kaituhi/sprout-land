import pygame
from pathlib import Path
from random import randint
from pytmx.util_pygame import load_pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction, Particle
from support import import_folder
from transition import Transition
from soil import SoilLayer
from sky import Rain


class Level:
    def __init__(self):
        """Initialize the level, load the display surface, and set up sprite groups."""
        self.display_surface = pygame.display.get_surface()
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        self.player = None  # Initialize player as None
        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
        self.setup_level()
        self.overlay = Overlay(self.player)  # Pass player after it's been set up
        self.transition = Transition(self.reset, self.player)

        # sky
        self.rain = Rain(self.all_sprites)
        self.raining = randint(0, 10) > 3
        self.soil_layer.raining = self.raining

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

    def player_add(self, item):
        self.player.inventory_items[item] += 1

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
            Tree(
                position=(obj.x, obj.y), 
                surf=obj.image, 
                groups=[self.all_sprites, self.collision_sprites, self.tree_sprites], 
                name=obj.name,
                player_add=self.player_add
            )

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
                self.player = Player(
                    position=(obj.x, obj.y), 
                    group=self.all_sprites, 
                    collision_sprites=self.collision_sprites,
                    tree_sprites=self.tree_sprites,
                    interaction=self.interaction_sprites,
                    soil_layer=self.soil_layer
                )
            if obj.name == 'Bed':
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)

    def load_ground(self):
        """Load the ground sprite."""
        ground_surface = pygame.image.load(Path('graphics/world/ground.png')).convert_alpha()
        Generic(
            position=(0, 0),
            surf=ground_surface,
            groups=self.all_sprites,
            z=LAYERS['ground']
        )

    def reset(self):
        # plants
        self.soil_layer.update_plants()

        # soil
        self.soil_layer.remove_water()
        self.raining = randint(0, 10) > 3
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()

        # apples on the trees
        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

    def plant_collision(self):
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player_add(plant.plant_type)
                    plant.kill()
                    Particle(plant.rect.topleft, plant.image, self.all_sprites, z=LAYERS['main'])
                    self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')

    def run(self, dt):
        """Update and draw the level."""
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)
        self.overlay.display()
        self.plant_collision()

        # rain
        if self.raining:
            self.rain.update()

        # transition overlay
        if self.player.sleep:
            self.transition.play()


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