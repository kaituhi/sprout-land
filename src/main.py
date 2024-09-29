import sys
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from level import Level


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sprout Land")
        self.clock = pygame.time.Clock()
        self.level = Level()

    def run(self):
        while True:
            self._process_events()
            delta_time = self.clock.tick() / 1000  # Convert milliseconds to seconds
            self.level.run(delta_time)
            pygame.display.update()

    def _process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


if __name__ == '__main__':
    game_instance = Game()
    game_instance.run()
