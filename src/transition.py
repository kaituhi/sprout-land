import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class ScreenTransition:
    """Handles the screen transition effect during state changes."""

    def __init__(self, reset_level_callback, player):
        self.display_surface = pygame.display.get_surface()
        self.reset_level_callback = reset_level_callback
        self.player = player

        self.transition_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color_intensity = 255
        self.transition_speed = -2

    def play_transition(self):
        """Play the transition effect."""
        self.update_color_intensity()
        self.fill_transition_surface()

        # Draw the transition effect
        self.display_surface.blit(
            self.transition_surface, (0, 0), special_flags=pygame.BLEND_RGB_MULT
        )

    def update_color_intensity(self):
        """Update the color intensity for the transition effect."""
        self.color_intensity += self.transition_speed

        if self.color_intensity <= 0:
            self.reverse_transition()
        elif self.color_intensity >= 255:
            self.finalize_transition()

    def reverse_transition(self):
        """Reverse the transition effect and reset the level state."""
        self.transition_speed *= -1
        self.color_intensity = 0
        self.reset_level_callback()

    def finalize_transition(self):
        """Finalize the transition effect and set the player state."""
        self.color_intensity = 255
        self.player.is_sleeping = False
        self.transition_speed = -2  # Reset speed for future transitions

    def fill_transition_surface(self):
        """Fill the transition surface with the current color intensity."""
        self.transition_surface.fill(
            (self.color_intensity, self.color_intensity, self.color_intensity)
        )
