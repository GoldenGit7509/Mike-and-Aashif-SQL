import pygame
import sqlite3
import sys

# Fixed placeholder names for the 5 score slots
score_place_names = ["Score1", "Score2", "Score3", "Score4", "Score5"]

def init_db():
    # Connect to SQLite database (file: highscore.db)
    conn = sqlite3.connect("highscore.db")
    c = conn.cursor()
    # Create table if not exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS highscores (
            player_name TEXT PRIMARY KEY,
            score INTEGER NOT NULL
        )
    ''')
    conn.commit()

    # Insert entries if not exist with score 0
    for name in score_place_names:
        c.execute('SELECT player_name FROM highscores WHERE player_name = ?', (name,))
        if not c.fetchone():
            c.execute('INSERT INTO highscores (player_name, score) VALUES (?, ?)', (name, 0))
    conn.commit()
    return conn, c

def get_all_scores(c):
    # Get all scores ordered descending by score
    c.execute('SELECT player_name, score FROM highscores')
    results = c.fetchall()
    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)

    # If less than 5 entries, pad with dummy zero scores (won't be saved!)
    while len(sorted_results) < 5:
        sorted_results.append(("ScoreX", 0))
    return sorted_results[:5]

def save_score_insert(conn, c, new_score):
    scores = get_all_scores(c)

    if not scores:
        # DB empty, insert first score
        c.execute('UPDATE highscores SET score = ? WHERE player_name = ?', (new_score, score_place_names[0]))
        conn.commit()
        print(f"Score {new_score} inserted as first score (empty DB).")
        return

    while len(scores) < 5:
        scores.append(("ScoreX", 0))

    if new_score <= scores[-1][1]:
        print(f"Score {new_score} not high enough for top 5.")
        return

    inserted = False
    new_scores = []

    for pname, pscore in scores:
        if not inserted and new_score > pscore:
            new_scores.append(("Score1", new_score))  # name will be reassigned below
            inserted = True
        if len(new_scores) < 5:
            new_scores.append((pname, pscore))

    if len(new_scores) < 5:
        new_scores.append(scores[-1])

    new_scores = new_scores[:5]

    # Update DB: assign scores to fixed placeholders Score1..Score5
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

font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

conn, c = init_db()

# Load local editable score (from Score1 slot)
c.execute('SELECT score FROM highscores WHERE player_name = ?', ("Score1",))
result = c.fetchone()
player_score = result[0] if result else 0

clock = pygame.time.Clock()
running = True

while running:
    screen.fill((30, 30, 30))

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

    # Display local score
    score_text = font.render(f"Current Score: {player_score}", True, (255, 255, 255))
    screen.blit(score_text, (20, 20))

    # Display top 5 scores
    all_scores = get_all_scores(c)
    header = font.render("Top 5 Scores:", True, (255, 215, 0))
    screen.blit(header, (20, 60))

    y = 100
    for i, (name, score) in enumerate(all_scores, start=1):
        text = small_font.render(f"{i}. {name} - {score}", True, (255, 215, 0))
        screen.blit(text, (40, y))
        y += 30

    # Controls info
    info_text = small_font.render(
        "Space: +10 points | M: -10 points | S: Save score | R: Reset all scores",
        True, (200, 200, 200)
    )
    screen.blit(info_text, (20, 440))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
conn.close()
sys.exit() 