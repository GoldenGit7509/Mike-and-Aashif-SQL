import pygame
import sqlite3
import sys

# Platzhalter für Score-Slots
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
    conn.commit()
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
        print(f"Score {new_score} not high enough for top 5.")
        return
    inserted = False
    new_scores = []
    for pname, pscore in scores:
        if not inserted and new_score > pscore:
            new_scores.append(("Score1", new_score))
            inserted = True
        if len(new_scores) < 5:
            new_scores.append((pname, pscore))
    if len(new_scores) < 5:
        new_scores.append(scores[-1])
    new_scores = new_scores[:5]
    for i, (_, score_val) in enumerate(new_scores):
        fixed_name = score_place_names[i]
        c.execute('UPDATE highscores SET score = ? WHERE player_name = ?', (score_val, fixed_name))
    conn.commit()
    print(f"Score {new_score} inserted into top 5.")

def reset_all_scores(conn, c):
    c.execute('UPDATE highscores SET score = 0')
    conn.commit()
    print("All scores reset to 0.")

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Jump and Run - Top 5 Scores")

# Schriftarten mit fettem Stil
font = pygame.font.SysFont("arialblack", 40)
small_font = pygame.font.SysFont("arial", 28)
tiny_font = pygame.font.SysFont("arial", 20)

conn, c = init_db()

c.execute('SELECT score FROM highscores WHERE player_name = ?', ("Score1",))
result = c.fetchone()
player_score = result[0] if result else 0

clock = pygame.time.Clock()
running = True

# Farben
BG_COLOR = (18, 18, 18)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)
WHITE = (240, 240, 240)
RED = (220, 50, 50)

# Medaillen-Emojis oder einfache Unicode Symbole (als Ersatz für Icons)
medals = ["🥇", "🥈", "🥉", "🏅", "🏅"]

while running:
    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player_score += 10
                print(f"Local score increased to {player_score} (not saved yet)")
            elif event.key == pygame.K_m:
                player_score = max(player_score - 10, 0)
                print(f"Local score decreased to {player_score} (not saved yet)")
            elif event.key == pygame.K_s:
                save_score_insert(conn, c, player_score)
            elif event.key == pygame.K_r:
                reset_all_scores(conn, c)
                player_score = 0
                print("All scores reset and local score reset to 0.")

    # Titel
    title_surf = font.render("Top 5 Highscores", True, GOLD)
    screen.blit(title_surf, (20, 20))

    # Lokaler Score
    current_score_surf = small_font.render(f"Current Score: {player_score}", True, WHITE)
    screen.blit(current_score_surf, (20, 80))

    # Scores abrufen
    all_scores = get_all_scores(c)

    y_start = 140
    y_gap = 40

    # Alle Scores schön auflisten mit Farbe und Medaillen-Icons
    for i, (name, score) in enumerate(all_scores):
        # Farbe je Platz
        if i == 0:
            color = GOLD
        elif i == 1:
            color = SILVER
        elif i == 2:
            color = BRONZE
        else:
            color = WHITE

        medal = medals[i]
        text_surf = small_font.render(f"{medal}  {i+1}. {name} — {score}", True, color)
        screen.blit(text_surf, (40, y_start + i * y_gap))

    # Steuerungshilfe
    info_text = tiny_font.render(
        "Space: +10 | M: -10 | S: Save Score | R: Reset Scores",
        True, (150, 150, 150)
    )
    screen.blit(info_text, (20, 440))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
conn.close()
sys.exit()