import pygame


class Timer:
    """A simple timer class to manage countdowns and callbacks."""

    def __init__(self, duration, callback=None):
        self.duration = duration
        self.callback = callback
        self.start_time = 0
        self.is_active = False

    def start(self):
        """Activates the timer and records the start time."""
        self.is_active = True
        self.start_time = pygame.time.get_ticks()

    def stop(self):
        """Deactivates the timer and resets the start time."""
        self.is_active = False
        self.start_time = 0

    def update(self):
        """
        Updates the timer state,
        checking for expiration and triggering the callback.
        """
        if self.is_active:
            elapsed_time = pygame.time.get_ticks() - self.start_time
            if elapsed_time >= self.duration:
                if self.callback:
                    self.callback()
                self.stop()
