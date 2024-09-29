import pygame
from settings import *

class Overlay:
    def __init__(self, player):
        # General setup
        self.display_surface = pygame.display.get_surface()
        self.player = player

        # Load overlay graphics
        overlay_dir = current_dir.parent / 'graphics' / 'overlay'
        self.tool_surfaces = self._load_graphics(overlay_dir, player.tools)
        self.seed_surfaces = self._load_graphics(overlay_dir, player.seeds)

    def _load_graphics(self, directory, items):
        """Load graphics for tools and seeds from the given directory."""
        return {item: pygame.image.load(directory / f'{item}.png').convert_alpha() for item in items}

    def display(self):
        """Display the current tool and seed overlays."""
        self._draw_overlay(self.tool_surfaces[self.player.selected_tool], OVERLAY_POSITIONS['tool'])
        self._draw_overlay(self.seed_surfaces[self.player.selected_seed], OVERLAY_POSITIONS['seed'])

    def _draw_overlay(self, surface, position):
        """Draw the overlay surface at the specified position."""
        rect = surface.get_rect(midbottom=position)
        self.display_surface.blit(surface, rect)
