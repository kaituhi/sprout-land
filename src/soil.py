import pygame
from pathlib import Path
from random import choice
from pytmx.util_pygame import load_pygame
from settings import TILE_SIZE, LAYERS, GROWTH_SPEED
from support import import_folder_dict, import_folder


class SoilTile(pygame.sprite.Sprite):
    """
    Represents a single soil tile in the game.
    """
    def __init__(self, position, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=position)
        self.z = LAYERS['soil']


class WaterTile(pygame.sprite.Sprite):
    def __init__(self, position, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=position)
        self.z = LAYERS['soil water']


class Plant(pygame.sprite.Sprite):
    def __init__(self, plant_type, groups, soil, check_watered):
        super().__init__(groups)
        # setup
        self.plant_type = plant_type
        self.frames = import_folder(Path(f'graphics/fruit/{plant_type}'))
        self.soil = soil
        self.check_watered = check_watered

        # plant growing
        self.age = 0
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROWTH_SPEED[plant_type]
        self.harvestable = False

        # sprite set up
        self.image = self.frames[self.age]
        self.y_offsett = -16 if plant_type == 'corn' else -8
        self.rect = self.image.get_rect(
            midbottom=soil.rect.midbottom + pygame.math.Vector2(0, self.y_offsett)
        )
        self.z = LAYERS['ground plant']

    def grow(self):
        if self.check_watered(self.rect.center):
            self.age += self.grow_speed

            if int(self.age) > 0:
                self.z = LAYERS['main']
                self.hitbox = self.rect.copy().inflate(-26, -self.rect.height * 0.4)

            if self.age >= self.max_age:
                self.age = self.max_age
                self.harvestable = True

            self.image = self.frames[int(self.age)]
            self.rect = self.image
            self.rect = self.image.get_rect(
                midbottom=self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offsett)
            )

class SoilLayer:
    """
    Manages the soil tiles and their interaction in the game world.
    """
    def __init__(self, all_sprites, collision_sprites):
        # sprite groups
        self.all_sprites = all_sprites
        self.collision_sprites = collision_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()

        # graphics
        self.soil_surfs = import_folder_dict(Path('graphics/soil'))
        self.water_surfs = import_folder(Path('graphics/soil_water'))
        
        # create grid and hit rects
        self.create_soil_grid()
        self.create_hit_rects()

    def create_soil_grid(self):
        """
        Creates a grid based on the 'Farmable' layer from the map, marking farmable spots.
        """
        ground_image = pygame.image.load(Path('graphics/world/ground.png'))
        h_tiles = ground_image.get_width() // TILE_SIZE
        v_tiles = ground_image.get_height() // TILE_SIZE

        self.grid = [[[] for _ in range(h_tiles)] for _ in range(v_tiles)]
        
        farmable_layer = load_pygame(Path('data/map.tmx')).get_layer_by_name('Farmable')
        for x, y, _ in farmable_layer.tiles():
            self.grid[y][x].append('F')

    def create_hit_rects(self):
        """
        Creates hit rectangles for all farmable tiles.
        """
        self.hit_rects = [
            pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            for y, row in enumerate(self.grid)
            for x, cell in enumerate(row) if 'F' in cell
        ]

    def get_hit(self, point):
        """
        Registers a hit on the soil at the specified point.
        """
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE
                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()
                    
                    if self.raining:
                        self.water_all()
                    
    def water(self, tagret_position):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(tagret_position):
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                self.grid[y][x].append('W')

                WaterTile(
                    position=soil_sprite.rect.topleft,
                    surf=choice(self.water_surfs),
                    groups=[self.all_sprites, self.water_sprites]
                )

    def water_all(self):
        for index_row, row in enumerate(self.grid):
            for index_column, cell in enumerate(row):
                if 'X' in cell and 'W' not in cell:
                    cell.append('W')
                    WaterTile(
                        position=(index_column * TILE_SIZE, index_row * TILE_SIZE),
                        surf=choice(self.water_surfs),
                        groups=[self.all_sprites, self.water_sprites]
                    )

    def remove_water(self):
        for sprite in self.water_sprites.sprites():
            sprite.kill()

        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')

    def check_watered(self, position):
        x = position[0] // TILE_SIZE
        y = position[1] // TILE_SIZE
        cell = self.grid[y][x]
        is_watered = 'W' in cell
        return is_watered

    def plant_seed(self, target_position, seed):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_position):
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE

                if 'P' not in self.grid[y][x]:
                    self.grid[y][x].append('P')
                    Plant(seed, [self.all_sprites, self.plant_sprites, self.collision_sprites], soil_sprite, self.check_watered)

    def update_plants(self):
        for plant in self.plant_sprites.sprites():
            plant.grow()

    def create_soil_tiles(self):
        """
        Creates and updates soil tiles based on the grid's state.
        """
        self.soil_sprites.empty()
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if 'X' in cell:
                    tile_type = self.determine_tile_type(x, y)
                    SoilTile(
                        position=(x * TILE_SIZE, y * TILE_SIZE),
                        surf=self.soil_surfs[tile_type],
                        groups=[self.all_sprites, self.soil_sprites]
                    )

    def determine_tile_type(self, x, y):
        """
        Determines the type of tile to render based on its neighbors.
        """
        top = 'X' in self.grid[y - 1][x] if y > 0 else False
        bottom = 'X' in self.grid[y + 1][x] if y < len(self.grid) - 1 else False
        left = 'X' in self.grid[y][x - 1] if x > 0 else False
        right = 'X' in self.grid[y][x + 1] if x < len(self.grid[y]) - 1 else False

        # Default tile type
        tile_type = 'o'

        # All sides
        if top and bottom and left and right:
            tile_type = 'x'
        # Horizontal tiles
        elif left and not top and not bottom and not right:
            tile_type = 'r'
        elif right and not top and not bottom and not left:
            tile_type = 'l'
        elif right and left and not top and not bottom:
            tile_type = 'lr'
        # Vertical tiles
        elif top and not right and not left and not bottom:
            tile_type = 'b'
        elif bottom and not right and not left and not top:
            tile_type = 't'
        elif top and bottom and not right and not left:
            tile_type = 'tb'
        # Corners
        elif left and bottom and not top and not right:
            tile_type = 'tr'
        elif right and bottom and not top and not left:
            tile_type = 'tl'
        elif left and top and not bottom and not right:
            tile_type = 'br'
        elif right and top and not bottom and not left:
            tile_type = 'bl'
        # T shapes
        elif top and bottom and right and not left:
            tile_type = 'tbr'
        elif top and bottom and left and not right:
            tile_type = 'tbl'
        elif left and right and top and not bottom:
            tile_type = 'lrb'
        elif left and right and bottom and not top:
            tile_type = 'lrt'

        return tile_type
