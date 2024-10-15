import pygame
from pathlib import Path
from settings import LAYERS, PLAYER_TOOL_OFFSET
from support import import_folder
from timer import Timer


class Player(pygame.sprite.Sprite):
    def __init__(
        self,
        position,
        group,
        collision_sprites,
        tree_sprites,
        interaction,
        soil_layer,
        toggle_shop,
    ):
        super().__init__(group)

        self._load_assets()
        self.status = "down_idle"
        self.frame_index = 0

        # General setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=position)
        self.z = LAYERS["main"]

        # Movement attributes
        self.direction = pygame.math.Vector2()
        self.position = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        # Collision
        self.collision_sprites = collision_sprites
        self.hitbox = self.rect.copy().inflate((-126, -70))

        # Initialize timers for tool and seed usage
        self.timers = {
            "tool_use": Timer(350, self.use_tool),
            "tool_switch": Timer(200),
            "seed_use": Timer(350, self.use_seed),
            "seed_switch": Timer(200),
        }

        # Initialize tools and seeds
        self.tools = ["hoe", "axe", "water"]
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

        self.seeds = ["corn", "tomato"]
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

        # Inventory
        self.inventory_items = {item: 0 for item in ["wood", "apple", "corn", "tomato"]}
        self.seed_inventory = {item: 5 for item in self.seeds}
        self.money = 200

        # Interaction
        self.tree_sprites = tree_sprites
        self.interaction = interaction
        self.is_sleeping = False
        self.soil_layer = soil_layer
        self.toggle_shop = toggle_shop

        # Sounds
        self.watering_sound = self._load_sound("audio/water.mp3")

    def _load_sound(self, file_path):
        """Load a sound from the given file path."""
        sound = pygame.mixer.Sound(Path(file_path))
        sound.set_volume(0.2)
        return sound

    def use_tool(self):
        """Use the selected tool."""
        if self.selected_tool == "hoe":
            self.soil_layer.get_hit(self.target_position)
        elif self.selected_tool == "axe":
            self._damage_tree()
        elif self.selected_tool == "water":
            self.soil_layer.water(self.target_position)
            self.watering_sound.play()

    def _damage_tree(self):
        """Damage the tree at the target position."""
        for tree in self.tree_sprites.sprites():
            if tree.rect.collidepoint(self.target_position):
                tree.damage()

    def get_target_position(self):
        """Calculate the target position based on the player's current status."""
        offset = PLAYER_TOOL_OFFSET[self.status.split("_")[0]]
        self.target_position = self.rect.center + offset

    def use_seed(self):
        """Plant the selected seed if available."""
        if self.seed_inventory[self.selected_seed] > 0:
            self.soil_layer.plant_seed(self.target_position, self.selected_seed)
            self.seed_inventory[self.selected_seed] -= 1

    def _load_assets(self):
        """Load character animations from the graphics directory."""
        graphics_dir = Path("graphics/character")
        self.animations = {
            direction: import_folder(graphics_dir / direction)
            for direction in self._animation_directions()
        }

    def _animation_directions(self):
        """Return a list of animation directions."""
        return [
            "up",
            "down",
            "left",
            "right",
            "right_idle",
            "left_idle",
            "up_idle",
            "down_idle",
            "right_hoe",
            "left_hoe",
            "up_hoe",
            "down_hoe",
            "right_axe",
            "left_axe",
            "up_axe",
            "down_axe",
            "right_water",
            "left_water",
            "up_water",
            "down_water",
        ]

    def animate(self, delta_time):
        """Animate the player based on current status and delta time."""
        self.frame_index += 4 * delta_time
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        self.image = self.animations[self.status][int(self.frame_index)]

    def _handle_input(self):
        """Handle player input for movement and actions."""
        keys = pygame.key.get_pressed()

        if not self.timers["tool_use"].is_active and not self.is_sleeping:
            self.handle_movement(keys)
            self.handle_tool_usage(keys)
            self.handle_seed_usage(keys)

            if keys[pygame.K_RETURN]:
                self._handle_interaction()

    def _handle_interaction(self):
        """Handle player interaction with nearby sprites."""
        collided_interaction_sprite = pygame.sprite.spritecollide(
            self, self.interaction, False
        )
        if collided_interaction_sprite:
            if collided_interaction_sprite[0].name == "Trader":
                self.toggle_shop()
            else:
                self.status = "left_idle"
                self.is_sleeping = True

    def handle_movement(self, keys):
        """Handle player movement and update status."""
        self.direction.y = -1 if keys[pygame.K_w] else (1 if keys[pygame.K_s] else 0)
        self.direction.x = 1 if keys[pygame.K_d] else (-1 if keys[pygame.K_a] else 0)

        if self.direction.magnitude() > 0:
            self.update_status_based_on_direction()

    def handle_tool_usage(self, keys):
        """Handle tool usage and switching."""
        if keys[pygame.K_SPACE]:
            self.timers["tool_use"].start()
            self.direction = pygame.math.Vector2()
            self.frame_index = 0

        if keys[pygame.K_q] and not self.timers["tool_switch"].is_active:
            self.timers["tool_switch"].start()
            self.tool_index = (self.tool_index + 1) % len(self.tools)
            self.selected_tool = self.tools[self.tool_index]

    def handle_seed_usage(self, keys):
        """Handle seed usage and switching."""
        if keys[pygame.K_LCTRL]:
            self.timers["seed_use"].start()
            self.direction = pygame.math.Vector2()
            self.frame_index = 0

        if keys[pygame.K_e] and not self.timers["seed_switch"].is_active:
            self.timers["seed_switch"].start()
            self.seed_index = (self.seed_index + 1) % len(self.seeds)
            self.selected_seed = self.seeds[self.seed_index]

    def update_status_based_on_direction(self):
        """Update player status based on movement direction."""
        if self.direction.y < 0:
            self.status = "up"
        elif self.direction.y > 0:
            self.status = "down"

        if self.direction.x > 0:
            self.status = "right"
        elif self.direction.x < 0:
            self.status = "left"

    def _update_status(self):
        """Update player status based on movement and tool usage."""
        if self.direction.magnitude() == 0:
            self.status = f"{self.status.split('_')[0]}_idle"

        if self.timers["tool_use"].is_active:
            self.status = f"{self.status.split('_')[0]}_{self.selected_tool}"

    def _update_timers(self):
        """Update all active timers."""
        for timer in self.timers.values():
            timer.update()

    def _collision(self, direction):
        """Handle collision based on movement direction."""
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, "hitbox") and sprite.hitbox.colliderect(self.hitbox):
                self.resolve_collision(direction, sprite)

    def resolve_collision(self, direction, sprite):
        """Resolve collision with the specified direction."""
        if direction == "horizontal":
            self._resolve_horizontal_collision(sprite)
        elif direction == "vertical":
            self._resolve_vertical_collision(sprite)

    def _resolve_horizontal_collision(self, sprite):
        """Resolve horizontal collision with another sprite."""
        if self.direction.x > 0:  # Moving right
            self.hitbox.right = sprite.hitbox.left
        elif self.direction.x < 0:  # Moving left
            self.hitbox.left = sprite.hitbox.right
        self._update_position()

    def _resolve_vertical_collision(self, sprite):
        """Resolve vertical collision with another sprite."""
        if self.direction.y > 0:  # Moving down
            self.hitbox.bottom = sprite.hitbox.top
        elif self.direction.y < 0:  # Moving up
            self.hitbox.top = sprite.hitbox.bottom
        self._update_position()

    def _update_position(self):
        """Update the player's rectangle and position based on hitbox."""
        self.rect.centerx = self.hitbox.centerx
        self.rect.centery = self.hitbox.centery
        self.position.x = self.hitbox.centerx
        self.position.y = self.hitbox.centery

    def _move(self, delta_time):
        """Update player position based on direction and speed."""
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        self.move_horizontally(delta_time)
        self.move_vertically(delta_time)

    def move_horizontally(self, delta_time):
        """Move player horizontally and check for collisions."""
        self.position.x += self.direction.x * self.speed * delta_time
        self.hitbox.centerx = round(self.position.x)
        self.rect.centerx = self.hitbox.centerx
        self._collision("horizontal")

    def move_vertically(self, delta_time):
        """Move player vertically and check for collisions."""
        self.position.y += self.direction.y * self.speed * delta_time
        self.hitbox.centery = round(self.position.y)
        self.rect.centery = self.hitbox.centery
        self._collision("vertical")

    def update(self, delta_time):
        """Update the player state based on delta time."""
        self._handle_input()
        self._update_status()
        self._update_timers()
        self.get_target_position()
        self._move(delta_time)
        self.animate(delta_time)
