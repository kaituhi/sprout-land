import pygame
from pathlib import Path
from random import randint, choice
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, LAYERS
from support import import_folder
from sprites import Generic


class Sky:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.full_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.start_color = [255, 255, 255]  # White
        self.end_color = (38, 101, 189)  # Sky blue

    def display(self, delta_time):
        """Blend the sky color from start_color to end_color."""
        self._update_sky_color(delta_time)
        self.full_surface.fill(self.start_color)
        self.display_surface.blit(
            self.full_surface, (0, 0), special_flags=pygame.BLEND_RGB_MULT
        )

    def _update_sky_color(self, delta_time):
        """Update the sky color towards the target end color."""
        for index, target_value in enumerate(self.end_color):
            if self.start_color[index] > target_value:
                self.start_color[index] -= 2 * delta_time


class RainDrop(Generic):
    def __init__(self, position, surface, is_moving, groups, layer):
        super().__init__(position, surface, groups, layer)
        self.lifetime = randint(400, 500)  # Lifetime in milliseconds
        self.start_time = pygame.time.get_ticks()  # Set up lifetime

        # Set up movement attributes
        self.is_moving = is_moving
        if self.is_moving:
            self.position = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2, 4)  # Move left and down
            self.speed = randint(200, 250)  # Random speed

    def update(self, delta_time):
        """Update the raindrop's position and check its lifetime."""
        if self.is_moving:
            self._move(delta_time)
        self._check_lifetime()

    def _move(self, delta_time):
        """Move the raindrop based on its speed and direction."""
        self.position += self.direction * self.speed * delta_time
        self.rect.topleft = round(self.position.x), round(self.position.y)

    def _check_lifetime(self):
        """Check if the raindrop has exceeded its lifetime and kill it."""
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()


class Rain:
    def __init__(self, all_sprites):
        self.all_sprites = all_sprites
        self.rain_drops = import_folder(Path("graphics/rain/drops"))
        self.rain_floor_sprites = import_folder("graphics/rain/floor")
        self.floor_width, self.floor_height = pygame.image.load(
            Path("graphics/world/ground.png")
        ).get_size()

    def create_floor_drop(self):
        """Create a static floor drop."""
        RainDrop(
            position=(randint(0, self.floor_width), randint(0, self.floor_height)),
            surface=choice(self.rain_floor_sprites),
            is_moving=False,
            groups=self.all_sprites,
            layer=LAYERS["rain_floor"],
        )

    def create_moving_drop(self):
        """Create a moving raindrop."""
        RainDrop(
            position=(randint(0, self.floor_width), randint(0, self.floor_height)),
            surface=choice(self.rain_drops),
            is_moving=True,
            groups=self.all_sprites,
            layer=LAYERS["rain_drops"],
        )

    def update(self):
        """Create new drops and update existing ones."""
        self.create_floor_drop()
        self.create_moving_drop()
