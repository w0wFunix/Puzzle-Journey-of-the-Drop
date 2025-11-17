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
DARK_GRAY = (100, 100, 100)


class DropletGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Путешествие капли")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

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

        # Генерация валидных препятствий
        self.generate_valid_obstacles()

    def is_reachable(self, start_pos):
        """Проверка доступности всех клеток"""
        visited = set()
        queue = [start_pos]

        while queue:
            row, col = queue.pop(0)
            if (row, col) in visited:
                continue

            visited.add((row, col))

            # Проверяем всех соседей
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_row, new_col = row + dr, col + dc
                if (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE and
                        self.board[new_row][new_col] == 0 and
                        (new_row, new_col) not in visited):
                    queue.append((new_row, new_col))

        # Считаем количество свободных клеток
        free_cells = sum(1 for row in range(BOARD_SIZE) for col in range(BOARD_SIZE)
                         if self.board[row][col] == 0)

        return len(visited) == free_cells

    def generate_valid_obstacles(self):
        """Генерация препятствий с проверкой доступности всех клеток"""
        max_attempts = 100

        for attempt in range(max_attempts):
            # Сбрасываем поле
            self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

            # Генерация препятствий
            total_cells = BOARD_SIZE * BOARD_SIZE
            obstacle_count = random.randint(2, 4)  # 2-4 препятствия

            obstacles_placed = 0
            while obstacles_placed < obstacle_count:
                row = random.randint(0, BOARD_SIZE - 1)
                col = random.randint(0, BOARD_SIZE - 1)

                if self.board[row][col] == 0:
                    self.board[row][col] = 1
                    obstacles_placed += 1

            # Проверяем доступность из случайной стартовой точки
            free_cells = [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)
                          if self.board[r][c] == 0]
            if free_cells:
                start_pos = random.choice(free_cells)
                if self.is_reachable(start_pos):
                    return  # Успешная генерация

        # Если не удалось сгенерировать за max_attempts, создаем поле без препятствий
        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    def get_cell_from_mouse(self, mouse_pos):
        """Преобразование координат мыши в координаты клетки"""
        x, y = mouse_pos
        col = x // CELL_SIZE
        row = y // CELL_SIZE

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
        if len(path) > 1:  # Если есть куда двигаться то двигаемся
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
        if len(path) > 1:  # Если есть движение
            self.start_animation(path)
            return True
        return False

    def check_win(self):
        """Проверка условия победы"""
        free_cells = sum(1 for row in range(BOARD_SIZE) for col in range(BOARD_SIZE)
                         if self.board[row][col] == 0)
        return len(self.visited) == free_cells

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

        # Отрисовка капли если клетка выбрана
        if self.droplet_pos:
            row, col = self.droplet_pos
            pygame.draw.circle(self.screen, BLUE,
                               (col * CELL_SIZE + CELL_SIZE // 2,
                                row * CELL_SIZE + CELL_SIZE // 2),
                               CELL_SIZE // 3)

        # Отображение информации
        info_y = 5
        if not self.droplet_pos:
            instruction = self.small_font.render("Кликните на свободную клетку для начала", True, DARK_GRAY)
            self.screen.blit(instruction, (5, info_y))
        else:
            moves_text = self.small_font.render(f"Ходы: {self.moves}", True, BLACK)
            self.screen.blit(moves_text, (5, info_y))

            # Прогрессбар
            free_cells = sum(1 for row in range(BOARD_SIZE) for col in range(BOARD_SIZE)
                             if self.board[row][col] == 0)
            progress = f"Прогресс: {len(self.visited)}/{free_cells}"
            progress_text = self.small_font.render(progress, True, BLACK)
            self.screen.blit(progress_text, (WINDOW_SIZE - 120, info_y))

            if self.is_animating:
                moving_text = self.small_font.render("Движение...", True, DARK_GRAY)
                self.screen.blit(moving_text, (WINDOW_SIZE // 2 - 40, info_y))

        # Проверка победы
        if self.droplet_pos and self.check_win() and not self.is_animating:
            win_text = self.font.render("ПОБЕДА!", True, BLUE)
            text_rect = win_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2))
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
        """игровой цикл"""
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
