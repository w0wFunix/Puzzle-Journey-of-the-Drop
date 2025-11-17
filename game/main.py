import pygame
import sys
import math
import random
# Инициализация Pygame
pygame.init()

# Константы
BOARD_SIZE = 5
CELL_SIZE = 100
INFO_HEIGHT = 50
WINDOW_WIDTH = BOARD_SIZE * CELL_SIZE
WINDOW_HEIGHT = BOARD_SIZE * CELL_SIZE + INFO_HEIGHT
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
LIGHT_GRAY = (230, 230, 230)
BLUE = (65, 105, 225)
DARK_BLUE = (30, 70, 180)
RED = (220, 60, 60)
DARK_RED = (180, 30, 30)
LIGHT_BLUE = (135, 206, 250)
GREEN = (60, 180, 75)
DARK_GREEN = (30, 130, 45)
GOLD = (255, 215, 0)
ORANGE = (255, 140, 0)
DARK_ORANGE = (200, 100, 0)

# Предопределенные уровни
LEVELS = [
    # Уровень 1
    [
        [0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0]
    ],
    # Уровень 2
    [
        [0, 0, 0, 1, 1],
        [0, 1, 0, 0, 1],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0]
    ],
    # Уровень 3
    [
        [0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ],
    # Уровень 4
    [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0]
    ],
    # Уровень 5
    [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0]
    ],
    # Уровень 6
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
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 25)
        self.bold_font = pygame.font.Font(None, 36)
        self.win_font =  pygame.font.Font(None, 30)

        # Текущий уровень
        self.current_level = 0
        self.total_levels = len(LEVELS)

        # Игровое поле
        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.droplet_pos = None
        self.visited = set()
        self.moves = 0

        # Анимация движения
        self.is_animating = False
        self.animation_path = []
        self.current_animation_index = 0
        self.animation_speed = 10  # кадров на клетку

        # Эффекты
        self.win_animation_time = 0
        self.game_over = False
        self.game_over_time = 0

        # Загрузка уровня
        self.load_level(self.current_level)

    def load_level(self, level_index):
        """Загрузка уровня по индексу"""
        self.current_level = level_index % self.total_levels
        self.board = [row[:] for row in LEVELS[self.current_level]]
        self.droplet_pos = None
        self.visited = set()
        self.moves = 0
        self.is_animating = False
        self.win_animation_time = 0
        self.game_over = False
        self.game_over_time = 0
        self.cells_to_fill = set()
        self.filling_cells = {}

    def check_game_over(self):
        """Проверка на поражение (игрок в тупике)"""
        if not self.droplet_pos or self.is_animating:
            return False

        free_cells = sum(1 for row in range(BOARD_SIZE) for col in range(BOARD_SIZE)
                         if self.board[row][col] == 0)

        # Если не все клетки посещены, но двигаться некуда
        if len(self.visited) < free_cells:
            row, col = self.droplet_pos

            # Проверяем все направления
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            can_move = False

            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc

                if (BOARD_SIZE > new_row >= 0 == self.board[new_row][new_col] and 0 <= new_col < BOARD_SIZE and
                        (new_row, new_col) not in self.visited):
                    can_move = True
                    break

            return not can_move

        return False

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
        path = [(row, col)]

        while True:
            new_row, new_col = row + dr, col + dc

            if not (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE):
                break
            if self.board[new_row][new_col] == 1:
                break
            if (new_row, new_col) in self.visited:
                break

            row, col = new_row, new_col
            path.append((row, col))

        return path

    def start_animation(self, path):
        """Запуск анимации движения"""
        if len(path) > 1:
            self.is_animating = True
            self.animation_path = path
            self.current_animation_index = 0

            # Определяем клетки для закрашивания (все кроме стартовой)
            self.cells_to_fill = set(path[1:])
            self.filling_cells = {cell: 0 for cell in self.cells_to_fill}

            self.moves += 1

    def update_animation(self):
        """Обновление анимации движения и закрашивания"""
        if not self.is_animating:
            return False

        self.current_animation_index += 1
        total_frames = len(self.animation_path) * self.animation_speed

        # Обновляем прогресс закрашивания для всех клеток пути
        total_progress = self.current_animation_index / total_frames

        for cell in self.cells_to_fill:
            # Клетка начинает закрашиваться, когда капля ее достигает
            cell_index = self.animation_path.index(cell)
            cell_start_progress = cell_index / len(self.animation_path)
            if total_progress >= cell_start_progress:
                cell_progress = (total_progress - cell_start_progress) * 2.0
                self.filling_cells[cell] = min(1.0, cell_progress)

        if self.current_animation_index >= total_frames:
            # Анимация завершена
            self.is_animating = False
            final_pos = self.animation_path[-1]
            self.droplet_pos = final_pos

            # Добавляем все клетки пути в посещенные
            for cell in self.animation_path:
                self.visited.add(cell)

            self.cells_to_fill.clear()
            self.filling_cells.clear()
            return False

        # Обновляем позицию капли
        progress = self.current_animation_index / total_frames
        path_index = min(int(progress * len(self.animation_path)), len(self.animation_path) - 1)
        self.droplet_pos = self.animation_path[path_index]

        return True

    def move_droplet(self, direction):
        """Запуск движения капли в заданном направлении"""
        if not self.droplet_pos or self.is_animating or self.game_over:
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
        # Фон панели с градиентом
        for i in range(INFO_HEIGHT):
            color_value = 200 + (i * 55 // INFO_HEIGHT)
            pygame.draw.line(self.screen, (color_value, color_value, color_value),
                             (0, i), (WINDOW_WIDTH, i))

        pygame.draw.line(self.screen, DARK_BLUE, (0, INFO_HEIGHT), (WINDOW_WIDTH, INFO_HEIGHT), 3)

        if not self.droplet_pos:
            text = self.small_font.render("Кликните на свободную клетку для начала игры", True, DARK_BLUE)
            self.screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, 15))
        else:
            # Счетчик ходов
            moves_text = self.small_font.render(f"Ходы: {self.moves}", True, BLACK)
            self.screen.blit(moves_text, (10, 10))

            # Прогресс
            free_cells = sum(1 for row in range(BOARD_SIZE) for col in range(BOARD_SIZE)
                             if self.board[row][col] == 0)
            visited_count = len(self.visited)
            progress = f"Прогресс: {visited_count}/{free_cells}"
            progress_text = self.small_font.render(progress, True, BLACK)
            self.screen.blit(progress_text, (180, 10))

            # Уровень
            level_text = self.small_font.render(f"Уровень: {self.current_level + 1}/{self.total_levels}", True, BLACK)
            self.screen.blit(level_text, (WINDOW_WIDTH - 120, 10))

            # Индикаторы
            if self.game_over:
                game_over_text = self.small_font.render("ТУПИК! Нажмите R для перезапуска", True, RED)
                self.screen.blit(game_over_text, (WINDOW_WIDTH // 2 - 155, 30))
            elif visited_count == free_cells:
                complete_text = self.small_font.render("ВСЕ КЛЕТКИ ПОСЕЩЕНЫ!", True, GREEN)
                self.screen.blit(complete_text, (WINDOW_WIDTH // 2 - 110, 30))
            elif self.is_animating:
                moving_text = self.small_font.render("Движение...", True, BLUE)
                self.screen.blit(moving_text, (WINDOW_WIDTH // 2 - 40, 30))

    def draw_board(self):
        """Отрисовка игрового поля"""
        # Фон поля
        self.screen.fill(LIGHT_GRAY)

        # Отрисовка информационной панели
        self.draw_info_panel()

        # Отрисовка препятствий с тенью
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] == 1:
                    # Тень
                    pygame.draw.rect(self.screen, DARK_RED,
                                     (col * CELL_SIZE + 3,
                                      row * CELL_SIZE + INFO_HEIGHT + 3,
                                      CELL_SIZE - 6, CELL_SIZE - 6))
                    # Основной блок
                    pygame.draw.rect(self.screen, RED,
                                     (col * CELL_SIZE,
                                      row * CELL_SIZE + INFO_HEIGHT,
                                      CELL_SIZE - 6, CELL_SIZE - 6))
                    # Детали
                    pygame.draw.rect(self.screen, (255, 100, 100),
                                     (col * CELL_SIZE + 10,
                                      row * CELL_SIZE + INFO_HEIGHT + 10,
                                      CELL_SIZE - 20, CELL_SIZE - 20), 2)

        # Отрисовка следа капли с анимацией
        for i, (row, col) in enumerate(self.visited):
            # Плавное изменение цвета следа
            alpha = min(200, 100 + (i % 5) * 20)
            color = (LIGHT_BLUE[0], LIGHT_BLUE[1], LIGHT_BLUE[2])

            pygame.draw.rect(self.screen, color,
                             (col * CELL_SIZE + 2,
                              row * CELL_SIZE + INFO_HEIGHT + 2,
                              CELL_SIZE - 4, CELL_SIZE - 4))

            # Эффект волны при победе
            if self.check_win() and not self.is_animating:
                wave = math.sin(pygame.time.get_ticks() * 0.01 + i * 0.5) * 0.3 + 0.7
                size = int((CELL_SIZE - 4) * wave)
                offset = (CELL_SIZE - 4 - size) // 2
                pygame.draw.rect(self.screen, BLUE,
                                 (col * CELL_SIZE + 2 + offset,
                                  row * CELL_SIZE + INFO_HEIGHT + 2 + offset,
                                  size, size))
        for (row, col), progress in self.filling_cells.items():
            if progress < 1.0:
                # Анимация закрашивания - от центра к краям с эффектом волны
                wave = math.sin(pygame.time.get_ticks() * 0.01) * 0.1 + 1.0
                base_size = int((CELL_SIZE - 4) * progress)
                animated_size = int(base_size * wave)
                offset = (CELL_SIZE - 4 - animated_size) // 2

                # Плавное изменение цвета от белого к голубому
                r = int(LIGHT_BLUE[0] * progress)
                g = int(LIGHT_BLUE[1] * progress)
                c = int(LIGHT_BLUE[2] * progress)
                color = (r, g, c)

                pygame.draw.rect(self.screen, color,
                                 (col * CELL_SIZE + 2 + offset,
                                  row * CELL_SIZE + INFO_HEIGHT + 2 + offset,
                                  animated_size, animated_size))
            else:
                # Полностью закрашенная клетка
                pygame.draw.rect(self.screen, LIGHT_BLUE,
                                 (col * CELL_SIZE + 2,
                                  row * CELL_SIZE + INFO_HEIGHT + 2,
                                  CELL_SIZE - 4, CELL_SIZE - 4))

        # Отрисовка сетки
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, INFO_HEIGHT), (x, WINDOW_HEIGHT), 2)
        for y in range(INFO_HEIGHT, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WINDOW_WIDTH, y), 2)

        # Отрисовка капли с анимацией
        if self.droplet_pos:
            row, col = self.droplet_pos
            center_x = col * CELL_SIZE + CELL_SIZE // 2
            center_y = row * CELL_SIZE + INFO_HEIGHT + CELL_SIZE // 2

            # Пульсация капли
            pulse = math.sin(pygame.time.get_ticks() * 0.01) * 0.1 + 0.9
            radius = int(CELL_SIZE // 3 * pulse)

            # Капля с градиентом
            for i in range(radius, 0, -2):
                alpha = 255 * (i / radius)
                color = (int(BLUE[0] * (i / radius)),
                         int(BLUE[1] * (i / radius)),
                         int(BLUE[2] * (i / radius)))
                pygame.draw.circle(self.screen, color, (center_x, center_y), i)

            # Блик на капле
            pygame.draw.circle(self.screen, (255, 255, 255),
                               (center_x - radius // 3, center_y - radius // 3),
                               radius // 4)

        # Анимация победы
        if self.droplet_pos and self.check_win() and not self.is_animating:
            self.win_animation_time += 1

            # Мигающая надпись
            alpha = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 127 + 128
            win_color = (int(GREEN[0]), int(GREEN[1]), int(GREEN[2]))

            # Разделяем текст на две строки
            win_text1 = self.win_font.render("ПОБЕДА!", True, win_color)
            win_text2 = self.win_font.render("Нажмите ПРОБЕЛ для следующего уровня", True, win_color)

            # Вычисляем общий размер для фона
            text_width = max(win_text1.get_width(), win_text2.get_width()) + 40
            text_height = win_text1.get_height() + win_text2.get_height() + 30

            # Создаем общий прямоугольник для фона
            background_rect = pygame.Rect(0, 0, text_width, text_height)
            background_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

            # Фон надписи (общая рамка)
            pygame.draw.rect(self.screen, (255, 255, 255, 200),
                             background_rect, border_radius=15)
            pygame.draw.rect(self.screen, win_color,
                             background_rect, 3, border_radius=15)

            # Располагаем текст внутри фона
            text1_rect = win_text1.get_rect(center=(WINDOW_WIDTH // 2, background_rect.top + 25))
            text2_rect = win_text2.get_rect(center=(WINDOW_WIDTH // 2, background_rect.top + 47))

            self.screen.blit(win_text1, text1_rect)
            self.screen.blit(win_text2, text2_rect)

            # Эффект хлопушек
            if self.win_animation_time % 10 == 0:
                for _ in range(5):
                    x = random.randint(0, WINDOW_WIDTH)
                    y = random.randint(INFO_HEIGHT, WINDOW_HEIGHT)
                    color = random.choice([GOLD, GREEN, BLUE, RED])
                    pygame.draw.circle(self.screen, color, (x, y), 4)

        # Анимация поражения
        if self.game_over:
            self.game_over_time += 1

            # Пульсация надпись
            pulse = (math.sin(pygame.time.get_ticks() * 0.02) + 1) * 0.3 + 0.7
            game_over_color = (
                min(255, int(RED[0] * pulse)),
                min(255, int(RED[1] * pulse)),
                min(255, int(RED[2] * pulse))
            )

            game_over_text = self.bold_font.render("ТУПИК! Нажмите R для перезапуска", True, game_over_color)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

            # Фон надписи
            pygame.draw.rect(self.screen, (255, 255, 255, 200),
                             text_rect.inflate(30, 20),
                             border_radius=15)
            pygame.draw.rect(self.screen, game_over_color,
                             text_rect.inflate(30, 20),
                             3, border_radius=15)

            self.screen.blit(game_over_text, text_rect)

        pygame.display.flip()


    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:  # Перезапуск уровня
                    self.load_level(self.current_level)
                elif event.key == pygame.K_SPACE and self.check_win() and not self.is_animating:
                    self.load_level(self.current_level + 1)
                elif self.droplet_pos and not self.check_win() and not self.is_animating and not self.game_over:
                    if event.key == pygame.K_UP:
                        self.move_droplet((-1, 0))
                    elif event.key == pygame.K_DOWN:
                        self.move_droplet((1, 0))
                    elif event.key == pygame.K_LEFT:
                        self.move_droplet((0, -1))
                    elif event.key == pygame.K_RIGHT:
                        self.move_droplet((0, 1))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.droplet_pos and not self.is_animating and not self.game_over:
                    cell = self.get_cell_from_mouse(event.pos)
                    if cell and self.board[cell[0]][cell[1]] == 0:
                        self.droplet_pos = cell
                        self.visited.add(cell)

        # Проверка на поражение после обработки событий
        if not self.game_over and not self.is_animating and self.droplet_pos and not self.check_win():
            self.game_over = self.check_game_over()
            if self.game_over:
                self.game_over_time = 0

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
