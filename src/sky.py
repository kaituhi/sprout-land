import pygame
from pathlib import Path
from random import randint, choice
from settings import *
from support import import_folder
from sprites import Generic


class Sky:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.full_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.start_color = [255, 255, 255]
        self.end_color = (38, 101, 189)

    def display(self, delta_time):
        for index, value in enumerate(self.end_color):
            if self.start_color[index] > value:
                self.start_color[index] -= 2 * delta_time

        self.full_surface.fill(self.start_color)
        self.display_surface.blit(self.full_surface, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        

class Drop(Generic):
    def __init__(self, position, surf, moving, groups, z):
        # general
        super().__init__(position, surf, groups, z)
        self.lifetime = randint(400, 500)
        self.start_time = pygame.time.get_ticks()

        # moving
        self.moving = moving
        if self.moving:
            self.position = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2, 4)
            self.speed = randint(200, 250)

    def update(self, delta_time):
        # movement
        if self.moving:
            self.position += self.direction * self.speed * delta_time
            self.rect.topleft = round(self.position.x), round(self.position.y)

        # timer
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()


class Rain:
    def __init__(self, all_sprites):
        self.all_sprites = all_sprites
        self.rain_drops = import_folder(Path('graphics/rain/drops'))
        self.rain_floor = import_folder('graphics/rain/floor')
        self.floor_w, self.floor_h = pygame.image.load(Path('graphics/world/ground.png')).get_size()

    def create_floor(self):
        Drop(
            position=(randint(0, self.floor_w), randint(0, self.floor_h)),
            surf=choice(self.rain_floor),
            moving=False,
            groups=self.all_sprites,
            z=LAYERS['rain floor']
        )

    def create_drops(self):
       Drop(
            position=(randint(0, self.floor_w), randint(0, self.floor_h)),
            surf=choice(self.rain_drops),
            moving=True,
            groups=self.all_sprites,
            z=LAYERS['rain drops']
        )

    def update(self):
        self.create_floor()
        self.create_drops()