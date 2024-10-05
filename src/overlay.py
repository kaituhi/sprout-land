import pygame
from pathlib import Path
from settings import OVERLAY_POSITIONS


class Overlay:
    def __init__(self, player):
        """Initialize the overlay with player information and graphics."""
        self.display_surface = pygame.display.get_surface()
        self.player = player

        # Load overlay graphics
        overlay_directory = Path('graphics/overlay')
        self.tool_surfaces = self._load_graphics(
            overlay_directory, player.tools)
        self.seed_surfaces = self._load_graphics(
            overlay_directory, player.seeds)

    def _load_graphics(self, directory, items):
        """Load graphics for tools and seeds from the given directory."""
        return {item: self._load_image(directory / f'{item}.png') 
                for item in items}

    def _load_image(self, file_path):
        """Load a single image and convert it to alpha."""
        return pygame.image.load(file_path).convert_alpha()

    def display(self):
        """Display the current tool and seed overlays."""
        self._draw_overlay(
            self.tool_surfaces[self.player.selected_tool],
            OVERLAY_POSITIONS['tool']
        )
        self._draw_overlay(
            self.seed_surfaces[self.player.selected_seed],
            OVERLAY_POSITIONS['seed']
        )

    def _draw_overlay(self, surface, position):
        """Draw the overlay surface at the specified position."""
        rect = surface.get_rect(midbottom=position)
        self.display_surface.blit(surface, rect)
