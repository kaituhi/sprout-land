import pygame
from pathlib import Path
from random import randint
from pytmx.util_pygame import load_pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction, Particle
from support import import_folder
from transition import ScreenTransition
from soil import SoilLayer
from sky import Rain, Sky
from menu import Menu


class Level:
    def __init__(self):
        """Initialize the level, load the display surface, and set up sprite groups."""
        self.display_surface = pygame.display.get_surface()
        self.sprite_groups = {
            "all": CameraGroup(),
            "collision": pygame.sprite.Group(),
            "trees": pygame.sprite.Group(),
            "interactions": pygame.sprite.Group(),
        }

        self.soil_layer = SoilLayer(
            self.sprite_groups["all"], self.sprite_groups["collision"]
        )
        self.setup_level()
        self.overlay = Overlay(self.player)
        self.transition = ScreenTransition(self.reset, self.player)

        # Sky and Weather
        self.rain = Rain(self.sprite_groups["all"])
        self.is_raining = randint(0, 10) > 3
        self.soil_layer.is_raining = self.is_raining
        self.sky = Sky()

        # Shop Menu
        self.menu = Menu(self.player, self.toggle_shop)
        self.is_shop_active = False

        # Sound Effects
        self.success_sound = pygame.mixer.Sound(
            current_dir.parent / Path("audio/success.wav")
        )
        self.success_sound.set_volume(0.3)

    def setup_level(self):
        """Load the level from the TMX file and initialize sprites."""
        tmx_data = load_pygame(Path("data/map.tmx"))
        self.load_environment(tmx_data)
        self.load_player(tmx_data)

    def add_item_to_player_inventory(self, item):
        """Add an item to the player's inventory."""
        self.player.inventory_items[item] += 1
        self.success_sound.play()

    def load_environment(self, tmx_data):
        """Load environment-related sprites."""
        layers_to_load = [
            self.load_houses,
            self.load_fences,
            self.load_water,
            self.load_trees,
            self.load_wildflowers,
            self.load_collision_tiles,
        ]
        for load_layer in layers_to_load:
            load_layer(tmx_data)
        self.load_ground()

    def load_houses(self, tmx_data):
        """Load house-related sprites from the TMX data."""
        house_layers = [
            "HouseFloor",
            "HouseFurnitureBottom",
            "HouseWalls",
            "HouseFurnitureTop",
        ]
        for layer in house_layers:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                z_order = (
                    LAYERS["house_bottom"]
                    if layer in ["HouseFloor", "HouseFurnitureBottom"]
                    else None
                )
                Generic(
                    (x * TILE_SIZE, y * TILE_SIZE),
                    surf,
                    self.sprite_groups["all"],
                    z_order,
                )

    def load_fences(self, tmx_data):
        """Load fence sprites."""
        for x, y, surf in tmx_data.get_layer_by_name("Fence").tiles():
            Generic(
                (x * TILE_SIZE, y * TILE_SIZE),
                surf,
                [self.sprite_groups["all"], self.sprite_groups["collision"]],
            )

    def load_water(self, tmx_data):
        """Load water sprites."""
        water_frames = import_folder(Path("graphics/water"))
        for x, y, _ in tmx_data.get_layer_by_name("Water").tiles():
            Water(
                (x * TILE_SIZE, y * TILE_SIZE), water_frames, self.sprite_groups["all"]
            )

    def load_trees(self, tmx_data):
        """Load tree sprites."""
        for obj in tmx_data.get_layer_by_name("Trees"):
            Tree(
                position=(obj.x, obj.y),
                surf=obj.image,
                groups=[
                    self.sprite_groups["all"],
                    self.sprite_groups["collision"],
                    self.sprite_groups["trees"],
                ],
                name=obj.name,
                add_item=self.add_item_to_player_inventory,
            )

    def load_wildflowers(self, tmx_data):
        """Load wildflower sprites."""
        for obj in tmx_data.get_layer_by_name("Decoration"):
            WildFlower(
                (obj.x, obj.y),
                obj.image,
                [self.sprite_groups["all"], self.sprite_groups["collision"]],
            )

    def load_collision_tiles(self, tmx_data):
        """Load collision tiles."""
        for x, y, _ in tmx_data.get_layer_by_name("Collision").tiles():
            Generic(
                (x * TILE_SIZE, y * TILE_SIZE),
                pygame.Surface((TILE_SIZE, TILE_SIZE)),
                self.sprite_groups["collision"],
            )

    def load_player(self, tmx_data):
        """Load the player sprite from TMX data."""
        for obj in tmx_data.get_layer_by_name("Player"):
            if obj.name == "Start":
                self.player = Player(
                    position=(obj.x, obj.y),
                    group=self.sprite_groups["all"],
                    collision_sprites=self.sprite_groups["collision"],
                    tree_sprites=self.sprite_groups["trees"],
                    interaction=self.sprite_groups["interactions"],
                    soil_layer=self.soil_layer,
                    toggle_shop=self.toggle_shop,
                )
            elif obj.name in ["Bed", "Trader"]:
                Interaction(
                    (obj.x, obj.y),
                    (obj.width, obj.height),
                    self.sprite_groups["interactions"],
                    obj.name,
                )

    def load_ground(self):
        """Load the ground sprite."""
        ground_surface = pygame.image.load(
            Path("graphics/world/ground.png")
        ).convert_alpha()
        Generic(
            position=(0, 0),
            surf=ground_surface,
            groups=self.sprite_groups["all"],
            z=LAYERS["ground"],
        )

    def toggle_shop(self):
        """Toggle the shop menu state."""
        self.is_shop_active = not self.is_shop_active

    def reset(self):
        """Reset level state and update environment conditions."""
        self.soil_layer.update_plants()
        self.soil_layer.remove_water()
        self.is_raining = randint(0, 10) > 3
        self.soil_layer.is_raining = self.is_raining
        if self.is_raining:
            self.soil_layer.water_all()

        for tree in self.sprite_groups["trees"].sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

        self.sky.start_color = [255, 255, 255]

    def check_plant_collision(self):
        """Check for collisions with harvestable plants."""
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.add_item_to_player_inventory(plant.plant_type)
                    plant.kill()
                    Particle(
                        plant.rect.topleft,
                        plant.image,
                        self.sprite_groups["all"],
                        z=LAYERS["main"],
                    )
                    self.soil_layer.grid[plant.rect.centery // TILE_SIZE][
                        plant.rect.centerx // TILE_SIZE
                    ].remove("P")

    def run(self, delta_time):
        """Update and draw the level."""
        self.display_surface.fill("black")
        self.sprite_groups["all"].custom_draw(self.player)

        if self.is_shop_active:
            self.menu.update()
        else:
            self.sprite_groups["all"].update(delta_time)
            self.check_plant_collision()

        self.overlay.display()
        if self.is_raining and not self.is_shop_active:
            self.rain.update()
        self.sky.display(delta_time)

        if self.player.is_sleeping:
            self.transition.play_transition()


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
            for sprite in sorted(
                self.sprites(), key=lambda sprite: sprite.rect.centery
            ):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
