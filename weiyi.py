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
        print(f"Score {new_score} nicht hoch genug für Top 5.")
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
    print(f"Score {new_score} in Top 5 gespeichert.")

# -------- Spiel Setup --------
pygame.init()
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Best Athletism")

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

clock = pygame.time.Clock()
fps = 60
font = pygame.font.SysFont(None, 40)

boden_height = 50
jump_speed = 15
gravity = 1

# Spielzustand zurücksetzen
def reset_game():
    spieler = pygame.Rect(100, HEIGHT - boden_height - 40, 40, 40)
    is_jumping = False
    velocity_y = 0
    obstacles = []
    obstacle_timer = 0
    score = 0
    score_timer = 0
    speedineeedthis = 10
    game_over = False
    return spieler, is_jumping, velocity_y, obstacles, obstacle_timer, score, score_timer, speedineeedthis, game_over

spieler, is_jumping, velocity_y, obstacles, obstacle_timer, score, score_timer, speedineeedthis, game_over = reset_game()

conn, c = init_db()

running = True
while running:
    screen.fill(WHITE)
    pygame.draw.rect(screen, GREEN, (0, HEIGHT - boden_height, WIDTH, boden_height))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                # Reset nur bei Game Over
                spieler, is_jumping, velocity_y, obstacles, obstacle_timer, score, score_timer, speedineeedthis, game_over = reset_game()

    keys = pygame.key.get_pressed()

    if not game_over:
        # Spieler springt
        if keys[pygame.K_SPACE] and not is_jumping:
            is_jumping = True
            jump_sound = pygame.mixer.Sound("jumpSound.mp3")
            jump_sound.set_volume(10) 
            jump_sound.play(0)
            velocity_y = -jump_speed

        if is_jumping:
            spieler.y += velocity_y
            velocity_y += gravity
            if spieler.y >= HEIGHT - boden_height - spieler.height:
                spieler.y = HEIGHT - boden_height - spieler.height
                is_jumping = False
                velocity_y = 0

        # Gegner erzeugen
        obstacle_timer += clock.get_time()
        if obstacle_timer > 1000:
            obstacle_timer = 0
            new_obstacle = pygame.Rect(WIDTH, HEIGHT - boden_height - 40, 40, 40)
            obstacles.append(new_obstacle)

        # Gegner bewegen & zeichnen
        for obstacle in obstacles[:]:
            obstacle.x -= speedineeedthis
            pygame.draw.rect(screen, BLACK, obstacle)
            if obstacle.right < 0:
                obstacles.remove(obstacle)
                speedineeedthis = random.randint(20, 35)  # Neue Geschwindigkeit bei Hindernis entfernt

        # Kollision prüfen
        for obstacle in obstacles:
            if spieler.colliderect(obstacle):
                game_over = True
                print("Game Over! Dein Score:", score)
                cheer_sound = pygame.mixer.Sound("losing.wav")
                cheer_sound.set_volume(10) 
                cheer_sound.play(0)
                save_score_insert(conn, c, score)
                

        # Punkte pro Sekunde erhöhen
        score_timer += clock.get_time()
        if score_timer >= 1000:
            score += 1
            score_timer = 0

    # Anzeigen
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    pygame.draw.rect(screen, BLUE, spieler)

    if game_over:
   
        game_over_text = font.render("Game Over! Drücke 'R' zum Neustarten.", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
conn.close()
