import pygame
import sys

# Инициализация Pygame
pygame.init()

# Константы
BOARD_SIZE = 5
CELL_SIZE = 80
INFO_HEIGHT = 40
WINDOW_WIDTH = BOARD_SIZE * CELL_SIZE
WINDOW_HEIGHT = BOARD_SIZE * CELL_SIZE + INFO_HEIGHT
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)
DARK_GRAY = (100, 100, 100)
GREEN = (0, 128, 0)

# Предопределенные уровни
# 0 - свободная клетка, 1 - препятствие
LEVELS = [
    # Уровень 1
    [
        [0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0]
    ],
    # Уровень 2 - диагональ
    [
        [0, 0, 0, 1, 1],
        [0, 1, 0, 0, 1],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0]
    ],
    # Уровень 3 - квадрат
    [
        [0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ],
    # Уровень 4 - крест
    [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0]
    ],
    # Уровень 5 - границы
    [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0]
    ],
    # Уровень 6 (без препятствий для обучения)
    [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ]
]


class DropletGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Путешествие капли")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Текущий уровень
        self.current_level = 0
        self.total_levels = len(LEVELS)

        # Игровое поле (0 - свободно, 1 - препятствие)
        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        # Позиция капли (None - еще не выбрана)
        self.droplet_pos = None

        # След капли
        self.visited = set()

        # Счетчик ходов
        self.moves = 0

        # Анимация движения
        self.is_animating = False
        self.animation_path = []
        self.current_animation_index = 0
        self.animation_speed = 8  # кадров на клетку

        # Загрузка уровня
        self.load_level(self.current_level)

    def load_level(self, level_index):
        """Загрузка уровня по индексу"""
        self.current_level = level_index % self.total_levels
        self.board = [row[:] for row in LEVELS[self.current_level]]  # Копируем уровень
        self.droplet_pos = None
        self.visited = set()
        self.moves = 0
        self.is_animating = False

    def get_cell_from_mouse(self, mouse_pos):
        """Преобразование координат мыши в координаты клетки"""
        x, y = mouse_pos
        if y < INFO_HEIGHT:
            return None

        col = x // CELL_SIZE
        row = (y - INFO_HEIGHT) // CELL_SIZE

        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return (row, col)
        return None

    def calculate_movement_path(self, direction):
        """Вычисление полного пути движения"""
        if not self.droplet_pos:
            return []

        row, col = self.droplet_pos
        dr, dc = direction
        path = [(row, col)]  # Начинаем с текущей позиции

        # Движение пока не упремся в препятствие
        while True:
            new_row, new_col = row + dr, col + dc

            # Проверка границ
            if not (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE):
                break

            # Проверка препятствий
            if self.board[new_row][new_col] == 1:
                break

            # Проверка уже посещенных клеток
            if (new_row, new_col) in self.visited:
                break

            row, col = new_row, new_col
            path.append((row, col))

        return path

    def start_animation(self, path):
        """Запуск анимации движения"""
        if len(path) > 1:  # Если есть куда двигаться
            self.is_animating = True
            self.animation_path = path
            self.current_animation_index = 0
            self.moves += 1

    def update_animation(self):
        """Обновление анимации"""
        if not self.is_animating:
            return False

        self.current_animation_index += 1

        # Вычисляем текущую позицию в анимации
        total_frames = len(self.animation_path) * self.animation_speed
        if self.current_animation_index >= total_frames:
            # Анимация завершена
            self.is_animating = False
            final_pos = self.animation_path[-1]
            self.droplet_pos = final_pos
            # Добавляем все клетки пути в посещенные
            for cell in self.animation_path:
                self.visited.add(cell)
            return False

        # Вычисляем текущую позицию капли
        progress = self.current_animation_index / total_frames
        path_index = int(progress * (len(self.animation_path) - 1))
        self.droplet_pos = self.animation_path[path_index]

        return True

    def move_droplet(self, direction):
        """Запуск движения капли в заданном направлении"""
        if not self.droplet_pos or self.is_animating:
            return False

        path = self.calculate_movement_path(direction)
        if len(path) > 1:
            self.start_animation(path)
            return True
        return False

    def check_win(self):
        """Проверка условия победы"""
        free_cells = sum(1 for row in range(BOARD_SIZE) for col in range(BOARD_SIZE)
                         if self.board[row][col] == 0)
        return len(self.visited) == free_cells

    def draw_info_panel(self):
        """Отрисовка информационной панели"""
        panel_rect = pygame.Rect(0, 0, WINDOW_WIDTH, INFO_HEIGHT)
        pygame.draw.rect(self.screen, GRAY, panel_rect)
        pygame.draw.line(self.screen, GRAY, (0, INFO_HEIGHT), (WINDOW_WIDTH, INFO_HEIGHT), 2)

        if not self.droplet_pos:
            instruction = self.small_font.render("Кликните на свободную клетку для начала", True, BLACK)
            self.screen.blit(instruction, (25, 10))
        else:
            # Счетчик ходов
            moves_text = self.small_font.render(f"Ходы: {self.moves}", True, BLACK)
            self.screen.blit(moves_text, (10, 10))

            # Прогресс
            free_cells = sum(1 for row in range(BOARD_SIZE) for col in range(BOARD_SIZE)
                             if self.board[row][col] == 0)
            visited_count = len(self.visited)
            progress = f"Клетки: {visited_count}/{free_cells}"
            progress_text = self.small_font.render(progress, True, BLACK)
            self.screen.blit(progress_text, (120, 10))

            # Уровень
            level_text = self.small_font.render(f"Уровень: {self.current_level + 1}/{self.total_levels}", True, BLACK)
            self.screen.blit(level_text, (WINDOW_WIDTH - 100, 10))

            # Индикатор завершения
            if visited_count == free_cells:
                complete_text = self.small_font.render("ВСЕ КЛЕТКИ ПОСЕЩЕНЫ!", True, GREEN)
                self.screen.blit(complete_text, (WINDOW_WIDTH - 300, 26))
            elif self.is_animating:
                moving_text = self.small_font.render("Движение...", True, DARK_GRAY)
                self.screen.blit(moving_text, (WINDOW_WIDTH - 250, 26))

    def draw_grid(self):
        """Отрисовка игровой сетки"""
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, INFO_HEIGHT), (x, WINDOW_HEIGHT))
        for y in range(INFO_HEIGHT, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WINDOW_WIDTH, y))

    def draw_board(self):
        """Отрисовка игрового поля"""
        self.screen.fill(WHITE)

        # Отрисовка информационной панели
        self.draw_info_panel()

        # Отрисовка препятствий
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] == 1:  # Препятствие
                    pygame.draw.rect(self.screen, RED,
                                     (col * CELL_SIZE,
                                      row * CELL_SIZE + INFO_HEIGHT,
                                      CELL_SIZE, CELL_SIZE))

        # Отрисовка сетки
        self.draw_grid()

        # Отрисовка следа капли
        for row, col in self.visited:
            pygame.draw.rect(self.screen, LIGHT_BLUE,
                             (col * CELL_SIZE,
                              row * CELL_SIZE + INFO_HEIGHT,
                              CELL_SIZE, CELL_SIZE))

        # Отрисовка капли (если выбрана)
        if self.droplet_pos:
            row, col = self.droplet_pos
            pygame.draw.circle(self.screen, BLUE,
                               (col * CELL_SIZE + CELL_SIZE // 2,
                                row * CELL_SIZE + INFO_HEIGHT + CELL_SIZE // 2),
                               CELL_SIZE // 3)

        # Проверка победы
        if self.droplet_pos and self.check_win() and not self.is_animating:
            win_text = self.font.render("ПОБЕДА! Нажмите ПРОБЕЛ для след. уровня", True, GREEN)
            text_rect = win_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            pygame.draw.rect(self.screen, WHITE, text_rect.inflate(20, 10))
            pygame.draw.rect(self.screen, GREEN, text_rect.inflate(20, 10), 2)
            self.screen.blit(win_text, text_rect)

        pygame.display.flip()

    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE and self.check_win() and not self.is_animating:
                    # Переход к следующему уровню
                    self.load_level(self.current_level + 1)
                elif self.droplet_pos and not self.check_win() and not self.is_animating:
                    # Обработка стрелок
                    if event.key == pygame.K_UP:
                        self.move_droplet((-1, 0))
                    elif event.key == pygame.K_DOWN:
                        self.move_droplet((1, 0))
                    elif event.key == pygame.K_LEFT:
                        self.move_droplet((0, -1))
                    elif event.key == pygame.K_RIGHT:
                        self.move_droplet((0, 1))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    if not self.droplet_pos and not self.is_animating:  # Если капля еще не выбрана
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
            self.update_animation()
            self.draw_board()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = DropletGame()
    game.run()
