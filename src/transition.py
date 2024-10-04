import pygame
from settings import *


class Transition:
    def __init__(self, reset, player):
        self.display_surface = pygame.display.get_surface()
        self.reset = reset
        self.player = player

        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color = 255
        self.speed = -2

    def play(self):
        self.color += self.speed

        if self.color <= 0:
            # Reverse the transition and start waking up
            self.speed *= -1
            self.color = 0
            self.reset()  # Reset level state
        
        if self.color >= 255:
            # Fully transition back to normal game state
            self.color = 255
            self.player.sleep = False
            self.speed = -2  # Reset speed so player can sleep again

        self.image.fill((self.color, self.color, self.color))
        self.display_surface.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
