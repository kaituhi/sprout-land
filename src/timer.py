import pygame


class Timer:
    def __init__(self, duration, callback=None):
        self.duration = duration
        self.callback = callback
        self.start_time = 0
        self.active = False

    def activate(self):
        self.active = True
        self.start_time = pygame.time.get_ticks()

    def deactivate(self):
        self.active = False
        self.start_time = 0

    def update(self):
        if self.active and pygame.time.get_ticks() - self.start_time >= self.duration:
            self.deactivate()
            if self.callback:
                self.callback()
