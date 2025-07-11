import pygame
import random
import sqlite3

# -------- Datenbank Setup --------
score_place_names = ["Score1", "Score2", "Score3", "Score4", "Score5"]

def init_db():
    conn = sqlite3.connect("highscore.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS highscores (
            player_name TEXT PRIMARY KEY,
            score INTEGER NOT NULL
        )
    ''')
    for name in score_place_names:
        c.execute('SELECT player_name FROM highscores WHERE player_name = ?', (name,))
        if not c.fetchone():
            c.execute('INSERT INTO highscores (player_name, score) VALUES (?, ?)', (name, 0))
    conn.commit()
    return conn, c

def get_all_scores(c):
    c.execute('SELECT player_name, score FROM highscores')
    results = c.fetchall()
    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
    while len(sorted_results) < 5:
        sorted_results.append(("ScoreX", 0))
    return sorted_results[:5]

def save_score_insert(conn, c, new_score):
    scores = get_all_scores(c)
    if new_score <= scores[-1][1]:
        return
    inserted = False
    new_scores = []
    for pname, pscore in scores:
        if not inserted and new_score > pscore:
            new_scores.append(("Score1", new_score))
            inserted = True
        if len(new_scores) < 5:
            new_scores.append((pname, pscore))
    new_scores = new_scores[:5]
    for i, (_, score_val) in enumerate(new_scores):
        fixed_name = score_place_names[i]
        c.execute('UPDATE highscores SET score = ? WHERE player_name = ?', (score_val, fixed_name))
    conn.commit()

# -------- Spiel Setup --------
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hürdenlauf 1")

# Farben
BLACK = (0, 0, 0)

# Uhr & Schrift
clock = pygame.time.Clock()
fps = 60
font = pygame.font.SysFont(None, 40)

# Spielerbilder laden und skalieren
lauf_bilder = [
    pygame.transform.scale(pygame.image.load("Image2.png"), (60, 60)).convert_alpha(),
    pygame.transform.scale(pygame.image.load("Image1.png"), (60, 60)).convert_alpha(),
    pygame.transform.scale(pygame.image.load("Image4.png"), (60, 60)).convert_alpha(),
    pygame.transform.scale(pygame.image.load("Image3.png"), (60, 60)).convert_alpha()
]
sprung_bild = pygame.transform.scale(pygame.image.load("jump.png"), (60, 60)).convert_alpha()
lauf_index = 0
anim_timer = 0
anim_delay = 100

# Hintergrundbild
try:
    background_img = pygame.image.load("scene-running-track.jpg").convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
except:
    background_img = None

# Hindernisbild
try:
    obstacle_img = pygame.image.load("pixilart-drawing.png").convert_alpha()
    obstacle_img = pygame.transform.scale(obstacle_img, (140, 140))
except:
    obstacle_img = None

# Konstanten
boden_height = 50
jump_speed = 15
gravity = 1

# Funktionen
def draw_gradient_rect(surface, rect, start_color, end_color):
    x, y, w, h = rect
    for i in range(w):
        ratio = i / w
        r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (x + i, y), (x + i, y + h - 1))

def reset_game():
    spieler = pygame.Rect(100, HEIGHT - boden_height - 40, 40, 40)
    return spieler, False, 0, [], 0, 0, 0, 10, False

spieler, is_jumping, velocity_y, obstacles, obstacle_timer, score, score_timer, speedineeedthis, game_over = reset_game()
conn, c = init_db()

# Musik
try:
    pygame.mixer.music.load("retro-game-arcade-236133.mp3")
    pygame.mixer.music.set_volume(0.8)
    pygame.mixer.music.play(-1)
except:
    pass

running = True
while running:
    if background_img:
        screen.blit(background_img, (0, 0))
    else:
        screen.fill((135, 206, 235))

    draw_gradient_rect(screen, (0, HEIGHT - boden_height, WIDTH, boden_height), (255, 0, 0), (255, 165, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                spieler, is_jumping, velocity_y, obstacles, obstacle_timer, score, score_timer, speedineeedthis, game_over = reset_game()

    keys = pygame.key.get_pressed()

    if not game_over:
        if keys[pygame.K_SPACE] and not is_jumping:
            is_jumping = True
            try:
                jump_sound = pygame.mixer.Sound("jumpSound.mp3")
                jump_sound.set_volume(1.0)
                jump_sound.play(0)
            except:
                pass
            velocity_y = -jump_speed

        if is_jumping:
            spieler.y += velocity_y
            velocity_y += gravity
            if spieler.y >= HEIGHT - boden_height - spieler.height:
                spieler.y = HEIGHT - boden_height - spieler.height
                is_jumping = False
                velocity_y = 0

        obstacle_timer += clock.get_time()
        if obstacle_timer > 1000:
            obstacle_timer = 0
            obstacles.append(pygame.Rect(WIDTH, HEIGHT - boden_height - 40, 40, 40))

        for obstacle in obstacles[:]:
            obstacle.x -= speedineeedthis
            if obstacle_img:
                screen.blit(obstacle_img, obstacle.topleft)
            else:
                pygame.draw.rect(screen, (255, 0, 0), obstacle)
            if obstacle.right < 0:
                obstacles.remove(obstacle)
                speedineeedthis = random.randint(20, 35)

        for obstacle in obstacles:
            if spieler.colliderect(obstacle):
                game_over = True
                try:
                    cheer_sound = pygame.mixer.Sound("losing.wav")
                    cheer_sound.set_volume(0.5)
                    cheer_sound.play(0)
                except:
                    pass
                save_score_insert(conn, c, score)

        score_timer += clock.get_time()
        if score_timer >= 1000:
            score += 1
            score_timer = 0

        # Animation aktualisieren
        anim_timer += clock.get_time()
        if anim_timer > anim_delay:
            anim_timer = 0
            lauf_index = (lauf_index + 1) % len(lauf_bilder)

    # Spieler zeichnen (animiert)
    if is_jumping:
        screen.blit(sprung_bild, spieler.topleft)
    else:
        screen.blit(lauf_bilder[lauf_index], spieler.topleft)

    # Score anzeigen
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    if game_over:
        text = font.render("Game Over! Drücke 'R' zum Neustarten.", True, (255, 0, 0))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
conn.close()
