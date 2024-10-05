import pygame
from pathlib import Path
from timer import Timer
from settings import (
    SCREEN_WIDTH, 
    SCREEN_HEIGHT, 
    SALE_PRICES, 
    PURCHASE_PRICES
)


class Menu:
    def __init__(self, player, toggle_menu):
        """Initialize the menu with player and toggle function."""
        self.player = player
        self.toggle_menu = toggle_menu
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(Path('font/LycheeSoda.ttf'), 30)

        # Menu configuration
        self.menu_width = 400
        self.space_between_items = 10
        self.padding = 8

        # Menu options
        self.options = self._get_menu_options()
        self.sell_border_index = len(self.player.inventory_items) - 1
        self.text_surfaces = []
        self.total_menu_height = 0
        self._setup_menu()

        # Menu navigation
        self.selected_index = 0
        self.input_timer = Timer(200)

    def _get_menu_options(self):
        """Retrieve available menu options from the player's inventory."""
        return (list(self.player.inventory_items.keys()) +
                list(self.player.seed_inventory.keys()))

    def display_money(self):
        """Render and display the player's current money."""
        money_surface = self.font.render(f'${self.player.money}', True, 'black')
        money_rect = money_surface.get_rect(midbottom=(SCREEN_WIDTH / 2,
                                                       SCREEN_HEIGHT - 20))

        pygame.draw.rect(self.display_surface, 'white',
                         money_rect.inflate(10, 10), 0, 4)
        self.display_surface.blit(money_surface, money_rect)

    def _setup_menu(self):
        """Prepare menu layout and item text surfaces."""
        for item in self.options:
            text_surface = self.font.render(item, True, 'black')
            self.text_surfaces.append(text_surface)
            self.total_menu_height += (text_surface.get_height() +
                                        self.padding * 2)

        self.total_menu_height += (len(self.text_surfaces) - 1) * \
            self.space_between_items

        menu_top = SCREEN_HEIGHT / 2 - self.total_menu_height / 2
        self.menu_rect = pygame.Rect(SCREEN_WIDTH / 2 - self.menu_width / 2,
                                      menu_top, self.menu_width,
                                      self.total_menu_height)

        # Create buy/sell text surfaces
        self.buy_text_surface = self.font.render('buy', True, 'black')
        self.sell_text_surface = self.font.render('sell', True, 'black')

    def handle_input(self):
        """Process user input for menu navigation and item selection."""
        keys = pygame.key.get_pressed()
        self.input_timer.update()

        if keys[pygame.K_ESCAPE]:
            self.toggle_menu()

        if not self.input_timer.is_active:
            if keys[pygame.K_UP]:
                self.selected_index -= 1
                self.input_timer.start()

            if keys[pygame.K_DOWN]:
                self.selected_index += 1
                self.input_timer.start()

            if keys[pygame.K_SPACE]:
                self.input_timer.start()
                self._select_item()

            self.selected_index %= len(self.options)

    def _select_item(self):
        """Handle the selection of an item based on the current index."""
        current_item = self.options[self.selected_index]

        # Sell item
        if self.selected_index <= self.sell_border_index:
            if self.player.inventory_items[current_item] > 0:
                self.player.inventory_items[current_item] -= 1
                self.player.money += SALE_PRICES[current_item]

        # Buy item
        else:
            seed_price = PURCHASE_PRICES[current_item]
            if self.player.money >= seed_price:
                self.player.seed_inventory[current_item] += 1
                self.player.money -= seed_price

    def show_entry(self, text_surface, amount, top_position, is_selected):
        """Render a single menu entry with amount and selection state."""
        # Background rectangle
        background_rect = pygame.Rect(
            self.menu_rect.left,
            top_position,
            self.menu_width,
            text_surface.get_height() + (self.padding * 2)
        )
        pygame.draw.rect(self.display_surface, 'white',
                         background_rect, 0, 4)

        # Render text
        text_rect = text_surface.get_rect(
            midleft=(self.menu_rect.left + 20, background_rect.centery)
        )
        self.display_surface.blit(text_surface, text_rect)

        # Render amount
        amount_surface = self.font.render(str(amount), True, 'black')
        amount_rect = amount_surface.get_rect(
            midright=(self.menu_rect.right - 20, background_rect.centery)
        )
        self.display_surface.blit(amount_surface, amount_rect)

        # Highlight selected entry
        if is_selected:
            pygame.draw.rect(self.display_surface, 'black',
                             background_rect, 4, 4)
            action_text_surface = self.sell_text_surface if \
                self.selected_index <= self.sell_border_index else \
                self.buy_text_surface
            action_rect = action_text_surface.get_rect(
                midleft=(self.menu_rect.left + 175, background_rect.centery)
            )
            self.display_surface.blit(action_text_surface, action_rect)

    def update(self):
        """Update the menu by processing input and rendering items."""
        self.handle_input()
        self.display_money()

        for index, text_surface in enumerate(self.text_surfaces):
            top_position = self.menu_rect.top + index * \
                (text_surface.get_height() + (self.padding * 2) +
                 self.space_between_items)

            amount_list = (list(self.player.inventory_items.values()) +
                           list(self.player.seed_inventory.values()))
            amount = amount_list[index]
            self.show_entry(text_surface, amount, top_position,
                            self.selected_index == index)
