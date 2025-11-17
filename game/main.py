import pygame
import sys
import random

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
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)


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

        # Генерация препятствий
        self.generate_obstacles()

    def generate_obstacles(self):
        """Генерация случайных препятствий (20% клеток)"""
        total_cells = BOARD_SIZE * BOARD_SIZE
        obstacle_count = max(2, total_cells // 6)  # примерно 20%

        obstacles_placed = 0
        while obstacles_placed < obstacle_count:
            row = random.randint(0, BOARD_SIZE - 1)
            col = random.randint(0, BOARD_SIZE - 1)

            # Проверяем, что клетка свободна
            if self.board[row][col] == 0:
                self.board[row][col] = 1
                obstacles_placed += 1

    def get_cell_from_mouse(self, mouse_pos):
        """Преобразование координат мыши в координаты клетки"""
        x, y = mouse_pos
        col = x // CELL_SIZE
        row = y // CELL_SIZE

        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return (row, col)
        return None

    def draw_grid(self):
        """Отрисовка игровой сетки"""
        for x in range(0, WINDOW_SIZE, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, WINDOW_SIZE))
        for y in range(0, WINDOW_SIZE, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WINDOW_SIZE, y))

    def draw_board(self):
        """Отрисовка игрового поля"""
        self.screen.fill(WHITE)

        # Отрисовка препятствий
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] == 1:  # Препятствие
                    pygame.draw.rect(self.screen, RED,
                                     (col * CELL_SIZE, row * CELL_SIZE,
                                      CELL_SIZE, CELL_SIZE))

        # Отрисовка сетки
        self.draw_grid()

        # Отрисовка следа капли
        for row, col in self.visited:
            pygame.draw.rect(self.screen, LIGHT_BLUE,
                             (col * CELL_SIZE, row * CELL_SIZE,
                              CELL_SIZE, CELL_SIZE))

        # Отрисовка капли (если выбрана)
        if self.droplet_pos:
            row, col = self.droplet_pos
            pygame.draw.circle(self.screen, BLUE,
                               (col * CELL_SIZE + CELL_SIZE // 2,
                                row * CELL_SIZE + CELL_SIZE // 2),
                               CELL_SIZE // 3)

        # Отображение инструкций
        if not self.droplet_pos:
            instruction = self.font.render("Выберите стартовую позицию", True, BLACK)
            self.screen.blit(instruction, (10, 10))

        pygame.display.flip()

    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    if not self.droplet_pos:  # Если капля еще не выбрана
                        cell = self.get_cell_from_mouse(event.pos)
                        if cell and self.board[cell[0]][cell[1]] == 0:  # Свободная клетка
                            self.droplet_pos = cell
                            self.visited.add(cell)

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
