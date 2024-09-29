import pygame
from settings import *
from player import Player
from overlay import Overlay


class Level:
    def __init__(self):
        # Get the display surface
        self.display_surface = pygame.display.get_surface()

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()

        # Initialize level setup
        self._initialize_level()
        self.overlay = Overlay(self.player)

    def _initialize_level(self):
        self.player = Player((640, 360), self.all_sprites)

    def run(self, delta_time):
        self.display_surface.fill("black")
        self.all_sprites.draw(self.display_surface)
        self.all_sprites.update(delta_time)

        self.overlay.display()
