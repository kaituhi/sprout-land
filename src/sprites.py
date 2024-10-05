import pygame
from settings import *
from pathlib import Path
from random import randint, choice


class Generic(pygame.sprite.Sprite):
    """Generic sprite class for static objects."""
    
    def __init__(self, position, surf, groups, z=None):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=position)
        self.z = LAYERS['main'] if z is None else z
        self.hitbox = self.rect.copy().inflate(
            -self.rect.width * 0.2, -self.rect.height * 0.75
        )


class Interaction(Generic):
    def __init__(self, position, size, groups, name):
        surf = pygame.Surface(size)
        super().__init__(position, surf, groups)
        self.name = name


class Water(Generic):
    """Water sprite class for animated water."""
    
    def __init__(self, position, frames, groups):
        self.frames = frames
        self.frame_index = 0
        super().__init__(
            position, self.frames[self.frame_index], groups, LAYERS['water']
        )

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
    """Wildflower sprite class."""
    
    def __init__(self, position, surf, groups):
        super().__init__(position, surf, groups)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)


class Particle(Generic):
    def __init__(self, position, surf, groups, z, duration=200):
        super().__init__(position, surf, groups, z)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        
        # White surface
        mask_surf = pygame.mask.from_surface(self.image)
        new_surf = mask_surf.to_surface()
        new_surf.set_colorkey((0, 0, 0))
        self.image = new_surf

    def update(self, delta_time):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill()


class Tree(Generic):
    """Tree sprite class."""
    
    def __init__(self, position, surf, groups, name, add_item):
        super().__init__(position, surf, groups)
        
        # Tree attributes
        self.health = 5
        self.alive = True
        self.stump_surf = pygame.image.load(
            current_dir.parent / 'graphics' / 'stumps' / f'{name.lower()}.png'
        ).convert_alpha()
        self.apple_surf = pygame.image.load(
            current_dir.parent / 'graphics' / 'fruit' / 'apple.png'
        )
        self.apple_position = APPLE_POSITIONS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()

        self.add_item = add_item
        
        # Sounds
        self.axe_sound = pygame.mixer.Sound(
            current_dir.parent / Path('audio/axe.mp3'))

    def damage(self):
        self.health -= 1
        
        # Play sound
        self.axe_sound.play()

        if len(self.apple_sprites.sprites()) > 0:
            random_apple = choice(self.apple_sprites.sprites())
            Particle(
                position=random_apple.rect.topleft,
                surf=random_apple.image,
                groups=self.groups()[0],
                z=LAYERS['fruit']
            )
            self.add_item('apple')
            random_apple.kill()

    def create_fruit(self):
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
            self.add_item('wood')

    def update(self, delta_time):
        if self.alive:
            self.check_death()
