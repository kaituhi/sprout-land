import pygame
from settings import *


class Generic(pygame.sprite.Sprite):
    def __init__(self, position, surf, groups, z=None):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=position)
        self.z = LAYERS['main'] if z is None else z