import pygame
from settings import *
from support import import_folder
from timer import Timer


class Player(pygame.sprite.Sprite):
    def __init__(self, position, group):
        super().__init__(group)

        self._load_assets()
        self.status = 'down_idle'
        self.frame_index = 0

        # General setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=position)
        self.z = LAYERS['main']

        # Movement attributes
        self.direction = pygame.math.Vector2()
        self.position = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        # Initialize timers for tool and seed usage
        self.timers = {
            'tool_use': Timer(350, self.use_tool),
            'tool_switch': Timer(200),
            'seed_use': Timer(350, self.use_seed),
            'seed_switch': Timer(200),
        }

        # Initialize tools and seeds
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

    def use_tool(self):
        # Implement tool use functionality
        pass

    def use_seed(self):
        # Implement seed use functionality
        pass

    def _load_assets(self):
        # Get the current file's directory
        graphics_dir = current_dir.parent / 'graphics' / 'character'

        self.animations = {direction: [] for direction in [
            'up', 'down', 'left', 'right',
            'right_idle', 'left_idle', 'up_idle', 'down_idle',
            'right_hoe', 'left_hoe', 'up_hoe', 'down_hoe',
            'right_axe', 'left_axe', 'up_axe', 'down_axe',
            'right_water', 'left_water', 'up_water', 'down_water'
        ]}

        for animation in self.animations.keys():
            full_path = graphics_dir / animation
            self.animations[animation] = import_folder(full_path)

    def animate(self, delta_time):
        self.frame_index += 4 * delta_time
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        self.image = self.animations[self.status][int(self.frame_index)]

    def _handle_input(self):
        keys = pygame.key.get_pressed()

        if not self.timers['tool_use'].active:
            # Movement controls
            self.direction.y = -1 if keys[pygame.K_UP] else (1 if keys[pygame.K_DOWN] else 0)
            self.direction.x = 1 if keys[pygame.K_RIGHT] else (-1 if keys[pygame.K_LEFT] else 0)

            # Update status based on direction
            self.status = 'up' if self.direction.y < 0 else 'down' if self.direction.y > 0 else self.status
            self.status = 'right' if self.direction.x > 0 else 'left' if self.direction.x < 0 else self.status

            # Tool usage
            if keys[pygame.K_SPACE]:
                self.timers['tool_use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            # Change tools
            if keys[pygame.K_q] and not self.timers['tool_switch'].active:
                self.timers['tool_switch'].activate()
                self.tool_index = (self.tool_index + 1) % len(self.tools)
                self.selected_tool = self.tools[self.tool_index]

            # Seed usage
            if keys[pygame.K_LCTRL]:
                self.timers['seed_use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            # Change seeds
            if keys[pygame.K_e] and not self.timers['seed_switch'].active:
                self.timers['seed_switch'].activate()
                self.seed_index = (self.seed_index + 1) % len(self.seeds)
                self.selected_seed = self.seeds[self.seed_index]

    def _update_status(self):
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'

        if self.timers['tool_use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

    def _update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def _move(self, delta_time):
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # Update position based on direction and speed
        self.position += self.direction * self.speed * delta_time
        self.rect.center = self.position

    def update(self, delta_time):
        self._handle_input()
        self._update_status()
        self._update_timers()
        self._move(delta_time)
        self.animate(delta_time)
