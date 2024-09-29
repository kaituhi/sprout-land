import pygame
from settings import *

class Generic(pygame.sprite.Sprite):
    def __init__(self, position, surf, groups, z=None):
        """Generic sprite class for static objects."""
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=position)
        self.z = LAYERS['main'] if z is None else z

class Water(Generic):
    def __init__(self, position, frames, groups):
        """Water sprite class for animated water."""
        self.frames = frames
        self.frame_index = 0
        super().__init__(position, self.frames[self.frame_index], groups, LAYERS['water'])

    def animate(self, delta_time):
        """Animate the water frames based on time."""
        self.frame_index += 5 * delta_time
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, delta_time):
        """Update the water animation."""
        self.animate(delta_time)

class WildFlower(Generic):
    def __init__(self, position, surf, groups):
        """Wildflower sprite class."""
        super().__init__(position, surf, groups)

class Tree(Generic):
    def __init__(self, position, surf, groups, name):
        """Tree sprite class."""
        super().__init__(position, surf, groups)
