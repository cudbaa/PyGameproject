import pygame
import random
import json

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
BLOCK_WIDTH, BLOCK_HEIGHT = 75, 30
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 10
BALL_RADIUS = 10

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = {
    (255, 0, 0): 30,   # Красный - 30 очков
    (0, 255, 0): 20,   # Зеленый - 20 очков
    (0, 0, 255): 10,   # Синий - 10 очков
    (255, 255, 0): 15,  # Желтый - 15 очков
    (255, 165, 0): 25   # Оранжевый - 25 очков
}

# Скины
SKINS = {
    "Скин 1": {
        "ball_color": (255, 0, 0),  # Красный
        "paddle_color": (0, 255, 0)  # Зеленый
    },
    "Скин 2": {
        "ball_color": (0, 0, 255),  # Синий
        "paddle_color": (255, 255, 0)  # Желтый
    },
    "Скин 3": {
        "ball_color": (255, 165, 0),  # Оранжевый
        "paddle_color": (255, 0, 255)  # Розовый
    }
}

# Бонусы
BONUS_TYPES = {
    "life": (255, 255, 0),  # Желтый
    "split": (0, 255, 255),  # Циан
    "expand": (255, 0, 255)   # Магента
}

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Арканоид")

# Загрузка таблицы лидеров
def load_leaderboard():
    try:
        with open('leaderboard.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Сохранение таблицы лидеров
def save_leaderboard(leaderboard):
    with open('leaderboard.json', 'w') as f:
        json.dump(leaderboard, f)

# Класс блока
class Block:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BLOCK_WIDTH, BLOCK_HEIGHT)
        self.color = random.choice(list(COLORS.keys()))
        self.bonus_type = random.choice(list(BONUS_TYPES.keys()) + [None]) if random.random() < 0.4 else None  # 40% шанс на бонус

# Класс платформы
class Paddle:
    def __init__(self, color):
        self.rect = pygame.Rect((WIDTH - PADDLE_WIDTH) // 2, HEIGHT - 50, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.color = color

    def move(self, dx):
        self.rect.x += dx
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > WIDTH - PADDLE_WIDTH:
            self.rect.x = WIDTH - PADDLE_WIDTH

    def expand(self):
        self.rect.width = 150  # Устанавливаем ширину платформы на 150 пикселей

    def reset_size(self):
        self.rect.width = PADDLE_WIDTH  # Сбрасываем размер платформы


# Класс мяча
class Ball:
    def __init__(self, color):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT - 60, BALL_RADIUS * 2, BALL_RADIUS * 2)
        self.dx = random.choice([-4, 4])
        self.dy = -4
        self.color = color
        self.trail = []  # Для эффекта следа

    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        # Добавление следа
        self.trail.append(self.rect.topleft)
        if len(self.trail) > 20:  # Ограничение длины следа
            self.trail.pop(0)

        # Проверка столкновения со стенами
        if self.rect.x <= 0 or self.rect.x >= WIDTH - BALL_RADIUS * 2:
            self.dx *= -1
        if self.rect.y <= 0:
            self.dy *= -1


# Класс бонуса
class Bonus:
    def __init__(self, x, y, bonus_type):
        self.rect = pygame.Rect(x, y, 20, 20)  # Размер бонуса
        self.bonus_type = bonus_type
        self.color = BONUS_TYPES[bonus_type]

    def move(self):
        self.rect.y += 3  # Скорость падения бонуса


# Функция для создания блоков
def create_blocks(rows, cols):
    blocks = []
    for row in range(rows):
        for col in range(cols):
            block_x = col * (BLOCK_WIDTH + 5) + 35
            block_y = row * (BLOCK_HEIGHT + 5) + 50
            blocks.append(Block(block_x, block_y))
    return blocks


# Меню игры
def menu():
    font = pygame.font.Font(None, 74)
    title_text = font.render("Арканоид", True, WHITE)
    play_text = "Играть"
    leaderboard_text = "Таблица лидеров"
    skins_text = "Скины"
    exit_text = "Выход"

    menu_items = [play_text, leaderboard_text, skins_text, exit_text]
    selected = 0

    while True:
        screen.fill(BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

        for i, item in enumerate(menu_items):
            if i == selected:
                item_color = (255, 255, 0)  # Желтый для выделенного элемента
            else:
                item_color = WHITE
            menu_item_text = font.render(item, True, item_color)
            screen.blit(menu_item_text, (WIDTH // 2 - menu_item_text.get_width() // 2, 150 + i * 60))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(menu_items)
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(menu_items)
                elif event.key == pygame.K_RETURN:
                    if selected == 0:
                        return "play"
                    elif selected == 1:
                        return "leaderboard"
                    elif selected == 2:
                        return "skins"
                    elif selected == 3:
                        pygame.quit()
                        return


# Функция для отображения таблицы лидеров
def show_leaderboard():
    leaderboard = load_leaderboard()
    font = pygame.font.Font(None, 36)
    leaderboard.sort(key=lambda x: x['score'], reverse=True)  # Сортировка по убыванию очков

    while True:
        screen.fill(BLACK)
        title_text = font.render("Таблица лидеров", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

        for i, entry in enumerate(leaderboard):
            score_text = font.render(f"{i + 1}. {entry['name']} - {entry['score']}", True, WHITE)
            screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 100 + i * 30))

        back_text = font.render("Назад", True, WHITE)
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return


# Функция для выбора скинов
def choose_skin():
    skins = list(SKINS.keys())
    selected = 0
    font = pygame.font.Font(None, 36)

    while True:
        screen.fill(BLACK)
        title_text = font.render("Выбор скина", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

        for i, skin in enumerate(skins):
            if i == selected:
                item_color = (255, 255, 0)  # Желтый для выделенного элемента
            else:
                item_color = WHITE
            skin_text = font.render(skin, True, item_color)
            screen.blit(skin_text, (WIDTH // 2 - skin_text.get_width() // 2, 100 + i * 40))

        back_text = font.render("Назад", True, WHITE)
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(skins)
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(skins)
                elif event.key == pygame.K_RETURN:
                    return skins[selected]  # Возвращаем выбранный скин
                elif event.key == pygame.K_ESCAPE:
                    return


# Функция для ввода имени игрока
def input_name(score):
    font = pygame.font.Font(None, 36)
    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        color = color_active if active else color_inactive
        screen.fill(BLACK)
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, HEIGHT - 40))

        pygame.display.flip()

class Pause:
    def __init__(self):
        self.paused = False

    def toggle_pause(self):
        self.paused = not self.paused

    def display_pause_menu(self):
        font = pygame.font.Font(None, 74)
        pause_text = font.render("Пауза", True, WHITE)
        resume_text = font.render("Нажмите ESC для продолжения", True, WHITE)

        while self.paused:
            screen.fill(BLACK)
            screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 + 10))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.toggle_pause()  # Возвращаемся в игру

# Главная функция игры
def main(selected_skin):
    clock = pygame.time.Clock()
    skin = SKINS[selected_skin]
    paddle = Paddle(skin["paddle_color"])
    balls = [Ball(skin["ball_color"])]  # Список шариков
    blocks = create_blocks(5, 10)
    bonuses = []
    score = 0
    lives = 3
    pause = Pause()  # Создаем экземпляр класса Pause

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause.toggle_pause()  # Переключаем состояние паузы

        if pause.paused:
            pause.display_pause_menu()  # Отображаем меню паузы
            continue  # Пропускаем остальную часть цикла, пока игра на паузе

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.move(-8)
        if keys[pygame.K_RIGHT]:
            paddle.move(8)

        # Движение всех шариков
        for ball in balls:
            ball.move()

            # Проверка столкновения с платформой
            if ball.rect.colliderect(paddle.rect):
                ball.dy *= -1
                ball.rect.y = paddle.rect.top - BALL_RADIUS * 2

            # Проверка столкновения с блоками
            for block in blocks[:]:
                if ball.rect.colliderect(block.rect):
                    blocks.remove(block)
                    score += COLORS[block.color]  # Добавляем очки за уничтожение блока

                    # Выпадение бонуса
                    if block.bonus_type:
                        bonuses.append(Bonus(block.rect.x + BLOCK_WIDTH // 2 - 10, block.rect.y, block.bonus_type))

                    ball.dy *= -1
                    break

            # Проверка падения мяча
            if ball.rect.y > HEIGHT:
                balls.remove(ball)  # Удаляем падший мяч

        # Проверка на потерю жизни
        if not balls:  # Если все шарики упали
            lives -= 1
            # Создаем новый шарик
            balls.append(Ball(skin["ball_color"]))

            if lives <= 0:
                # Сохраняем результат в таблицу лидеров
                name = input_name(score)
                leaderboard = load_leaderboard()
                leaderboard.append({"name": name, "score": score})
                save_leaderboard(leaderboard)
                return  # Возвращаемся в меню

        # Обработка бонусов
        for bonus in bonuses[:]:
            bonus.move()
            if bonus.rect.colliderect(paddle.rect):
                if bonus.bonus_type == "life":
                    lives += 1
                elif bonus.bonus_type == "split":
                    # Логика раздвоения мяча
                    balls.append(Ball(skin["ball_color"]))  # Добавляем новый шарик
                elif bonus.bonus_type == "expand":
                    paddle.expand()
                    # Возврат платформы в исходное состояние через 10 секунд
                    pygame.time.set_timer(pygame.USEREVENT, 10000)

                bonuses.remove(bonus)
            elif bonus.rect.y > HEIGHT:
                bonuses.remove(bonus)

        # Проверка на возврат платформы в исходное состояние
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                paddle.reset_size()

        # Отрисовка
        screen.fill(BLACK)
        for block in blocks:
            pygame.draw.rect(screen, block.color, block.rect)
        pygame.draw.rect(screen, paddle.color, paddle.rect)

        # Отрисовка всех шариков
        for ball in balls:
            for pos in ball.trail:
                pygame.draw.circle(screen, ball.color, (int(pos[0] + BALL_RADIUS), int(pos[1] + BALL_RADIUS)), 5)
            pygame.draw.ellipse(screen, ball.color, ball.rect)

        # Отрисовка бонусов
        for bonus in bonuses:
            pygame.draw.rect(screen, bonus.color, bonus.rect)

        # Отображение счета и жизней
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(score_text, (10, HEIGHT - 40))
        screen.blit(lives_text, (10, HEIGHT - 80))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

# Функция для выбора уровня
def choose_level():
    levels = ["Уровень 1", "Уровень 2"]
    selected = 0
    font = pygame.font.Font(None, 36)

    while True:
        screen.fill(BLACK)
        title_text = font.render("Выбор уровня", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

        for i, level in enumerate(levels):
            if i == selected:
                item_color = (255, 255, 0)  # Желтый для выделенного элемента
            else:
                item_color = WHITE
            level_text = font.render(level, True, item_color)
            screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, 100 + i * 40))

        back_text = font.render("Назад", True, WHITE)
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(levels)
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(levels)
                elif event.key == pygame.K_RETURN:
                    return selected  # Возвращаем индекс выбранного уровня
                elif event.key == pygame.K_ESCAPE:
                    return

if __name__ == "__main__":
    try:
        while True:
            action = menu()
            if action == "play":
                selected_skin = choose_skin()
                if selected_skin:  # Если выбран скин
                    main(selected_skin)
            elif action == "leaderboard":
                show_leaderboard()
            elif action == "skins":
                choose_skin()
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        pygame.quit()
