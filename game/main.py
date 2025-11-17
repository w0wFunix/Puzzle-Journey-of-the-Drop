import pygame
import sys

# Инициализация Pygame
pygame.init()

# Константы
BOARD_SIZE = 5
CELL_SIZE = 80
WINDOW_SIZE = BOARD_SIZE * CELL_SIZE
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)


class DropletGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Путешествие капли")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        # Игровое поле (0 - свободно, 1 - препятствие)
        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        # Позиция капли (None - еще не выбрана)
        self.droplet_pos = None

        # След капли
        self.visited = set()

    def draw_grid(self):
        """Отрисовка игровой сетки"""
        for x in range(0, WINDOW_SIZE, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, WINDOW_SIZE))
        for y in range(0, WINDOW_SIZE, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WINDOW_SIZE, y))

    def draw_board(self):
        """Отрисовка игрового поля"""
        self.screen.fill(WHITE)

        # Отрисовка сетки
        self.draw_grid()

        # Отрисовка капли (если выбрана)
        if self.droplet_pos:
            row, col = self.droplet_pos
            pygame.draw.circle(self.screen, BLUE,
                               (col * CELL_SIZE + CELL_SIZE // 2,
                                row * CELL_SIZE + CELL_SIZE // 2),
                               CELL_SIZE // 3)

        pygame.display.flip()

    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True

    def run(self):
        """Главный игровой цикл"""
        running = True
        while running:
            running = self.handle_events()
            self.draw_board()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = DropletGame()
    game.run()