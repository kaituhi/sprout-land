import pygame
from pathlib import Path
from pytmx.util_pygame import load_pygame
from settings import *


class SoilTile(pygame.sprite.Sprite):
    def __init__(self, position, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=position)
        self.z = LAYERS['soil']

class SoliLayer:
    def __init__(self, all_sprites):
        # sprite groups
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()

        # graphics
        self.soil_surf = pygame.image.load(current_dir.parent / 'graphics' / 'soil' / 'o.png')

        self.create_soil_grid()
        self.create_hit_rects()
        
    def create_soil_grid(self):
        ground = pygame.image.load(current_dir.parent / 'graphics' / 'world' / 'ground.png')
        h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE
        print(h_tiles)
        print(v_tiles)

        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
        for x, y, _ in load_pygame(current_dir.parent / 'data' / 'map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')

    def create_hit_rects(self):
        self.hit_rects = []
        for index_row, row in enumerate(self.grid):
            for index_column, cell in enumerate(row):
                if 'F' in cell:
                    x = index_column * TILE_SIZE
                    y = index_row * TILE_SIZE
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.hit_rects.append(rect)

    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE

                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()
    
    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_column, cell in enumerate(row):
                if 'X' in cell:
                    print('YES')
                    print(self.soil_surf, 'SOILSURF')
                    SoilTile(
                        position=(index_column * TILE_SIZE, index_row * TILE_SIZE), 
                        surf=self.soil_surf, 
                        groups=[self.all_sprites, self.soil_sprites]
                    )