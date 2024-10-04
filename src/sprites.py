import pygame
from settings import *
from pathlib import Path
from random import randint, choice
from timer import Timer


class Generic(pygame.sprite.Sprite):
    def __init__(self, position, surf, groups, z=None):
        """Generic sprite class for static objects."""
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=position)
        self.z = LAYERS['main'] if z is None else z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)


class Interaction(Generic):
    def __init__(self, position, size, groups, name):
        surf = pygame.Surface(size)
        super().__init__(position, surf, groups)
        self.name = name


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
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)


class Particle(Generic):
    def __init__(self, position, surf, groups, z, duration=200):
        super().__init__(position, surf, groups, z)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration

        # while surface
        mask_surf = pygame.mask.from_surface(self.image)
        new_surf = mask_surf.to_surface()
        new_surf.set_colorkey((0, 0, 0))
        self.image = new_surf

    def update(self, delte_time):
        currect_time = pygame.time.get_ticks()
        if currect_time - self.start_time > self.duration:
            self.kill()

class Tree(Generic):
    def __init__(self, position, surf, groups, name, player_add):
        """Tree sprite class."""
        super().__init__(position, surf, groups)

        # tree attributes
        self.health = 5
        self.alive = True
        self.stump_surf = pygame.image.load(
            current_dir.parent / 'graphics' / 'stumps' / f'{name.lower()}.png'
        ).convert_alpha()
        self.invul_timer = Timer(200)

        self.apple_surf = pygame.image.load(current_dir.parent / 'graphics' / 'fruit' / 'apple.png')
        self.apple_position = APPLE_POSITIONS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()

        self.player_add = player_add

    def damage(self):
        self.health -= 1

        if len(self.apple_sprites.sprites()) > 0:
            random_apple = choice(self.apple_sprites.sprites())
            Particle(
                position=random_apple.rect.topleft, 
                surf=random_apple.image, 
                groups=self.groups()[0], 
                z=LAYERS['fruit'])

            self.player_add('apple')
            random_apple.kill()

    def create_fruit(self):
        print(f"Creating apples for tree at {self.rect.topleft}")  # Debugging line
        for position in self.apple_position:
            if randint(0, 10) < 2:
                Generic(
                    position=(
                        position[0] + self.rect.left,
                        position[1] + self.rect.top
                    ),
                    surf=self.apple_surf,
                    groups=[self.apple_sprites, self.groups()[0]],
                    z=LAYERS['fruit']
                )

    def check_death(self):
        if self.health <= 0:
            Particle(
                position=self.rect.topleft,
                surf=self.image,
                groups=self.groups()[0],
                z=LAYERS['fruit'],
                duration=300
            )
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)
            self.alive = False
            self.player_add('wood')

    def update(self, delta_time):
        if self.alive:
            self.check_death()
