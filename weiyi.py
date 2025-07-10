import pygame
import random
import sqlite3

# -------- Datenbank Setup --------
score_place_names = ["Score1", "Score2", "Score3", "Score4", "Score5"]

def init_db():
    """
    Initialisiert die SQLite-Datenbank für Highscores.
    Erzeugt Tabelle, falls nicht vorhanden, und füllt Platzhalter ein.
    """
    conn = sqlite3.connect("highscore.db")
    c = conn.cursor()
    c.execute('''   
        CREATE TABLE IF NOT EXISTS highscores (
            player_name TEXT PRIMARY KEY,
            score INTEGER NOT NULL
        )
    ''')
    # Initialeinträge anlegen, falls noch nicht vorhanden
    for name in score_place_names:
        c.execute('SELECT player_name FROM highscores WHERE player_name = ?', (name,))
        if not c.fetchone():
            c.execute('INSERT INTO highscores (player_name, score) VALUES (?, ?)', (name, 0))
    conn.commit()
    return conn, c

def get_all_scores(c):
    """
    Holt alle Highscores aus der Datenbank,
    sortiert sie absteigend nach Score,
    gibt die Top 5 zurück.
    """
    c.execute('SELECT player_name, score FROM highscores')
    results = c.fetchall()
    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
    while len(sorted_results) < 5:
        sorted_results.append(("ScoreX", 0))  # Platzhalter wenn weniger als 5 Scores
    return sorted_results[:5]

def save_score_insert(conn, c, new_score):
    """
    Fügt einen neuen Score in die Top 5 ein,
    falls dieser höher als der niedrigste ist.
    Überschreibt dabei den niedrigsten Score.
    """
    scores = get_all_scores(c)
    if new_score <= scores[-1][1]:
        print(f"Score {new_score} nicht hoch genug für Top 5.")
        return
    inserted = False
    new_scores = []
    for pname, pscore in scores:
        if not inserted and new_score > pscore:
            new_scores.append(("Score1", new_score))  # Neuer Score an richtiger Stelle einfügen
            inserted = True
        if len(new_scores) < 5:
            new_scores.append((pname, pscore))
    new_scores = new_scores[:5]  # Nur Top 5 behalten
    for i, (_, score_val) in enumerate(new_scores):
        fixed_name = score_place_names[i]  # Feste Namen der Scoreplätze
        c.execute('UPDATE highscores SET score = ? WHERE player_name = ?', (score_val, fixed_name))
    conn.commit()
    print(f"Score {new_score} in Top 5 gespeichert.")

# -------- Spiel Setup --------
pygame.init()  # Pygame initialisieren

WIDTH, HEIGHT = 1000, 800  # Fenstergröße

screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Fenster erzeugen
pygame.display.set_caption("Hürdenlauf 1")  # Fenstertitel

# Hintergrundbild laden und auf Fenstergröße skalieren mit Fehlerbehandlung
try:
    background_img = pygame.image.load("scene-running-track.jpg").convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
except Exception as e:
    print("Fehler beim Laden des Hintergrundbildes:", e)
    background_img = None  # Kein Bild vorhanden

# Hindernis-Bild laden und skalieren mit Fehlerbehandlung
try:
    obstacle_img = pygame.image.load("pixilart-drawing.png").convert_alpha()
    obstacle_img = pygame.transform.scale(obstacle_img, (140, 140))
except Exception as e:
    print("Fehler beim Laden des Hindernisbildes:", e)
    obstacle_img = None

# Farben als RGB-Tupel
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

clock = pygame.time.Clock()  # Uhr für Framerate
fps = 60  # Ziel-Framerate
font = pygame.font.SysFont(None, 40)  # Schriftart und Größe

boden_height = 50  # Höhe des Bodens am unteren Bildschirmrand
jump_speed = 15   # Absprunggeschwindigkeit
gravity = 1       # Schwerkraft, beschleunigt Fall nach unten

def draw_gradient_rect(surface, rect, start_color, end_color):
    """
    Zeichnet einen horizontalen Farbverlauf (Gradient) in einem Rechteck.
    :param surface: Zieloberfläche (Surface)
    :param rect: Tuple (x, y, Breite, Höhe)
    :param start_color: RGB Startfarbe (links)
    :param end_color: RGB Endfarbe (rechts)
    """
    x, y, w, h = rect
    for i in range(w):
        ratio = i / w  # Verhältnis von 0 bis 1 quer durchs Rechteck
        r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (x + i, y), (x + i, y + h - 1))

def reset_game():
    """
    Setzt den Spielzustand zurück für einen Neustart.
    Erzeugt Spieler, Hindernisse und setzt Variablen auf Anfangswerte.
    """
    spieler = pygame.Rect(100, HEIGHT - boden_height - 40, 40, 40)  # Spieler-Rechteck (Position und Größe)
    is_jumping = False  # Spieler springt gerade nicht
    velocity_y = 0      # Vertikale Geschwindigkeit
    obstacles = []      # Liste der Hindernisse
    obstacle_timer = 0  # Timer für neues Hindernis
    score = 0           # Punktestand
    score_timer = 0     # Timer für Punktezählung
    speedineeedthis = 10  # Geschwindigkeit der Hindernisse (horizontal)
    game_over = False   # Spiel läuft noch
    return spieler, is_jumping, velocity_y, obstacles, obstacle_timer, score, score_timer, speedineeedthis, game_over

# Initiale Spielzustände setzen
spieler, is_jumping, velocity_y, obstacles, obstacle_timer, score, score_timer, speedineeedthis, game_over = reset_game()

# Datenbankverbindung und Cursor holen
conn, c = init_db()

# Hintergrundmusik laden und starten
try:
    pygame.mixer.music.load("retro-game-arcade-236133.mp3")
    pygame.mixer.music.set_volume(0.8)  # Lautstärke anpassen (0 bis 1)
    pygame.mixer.music.play(-1)  # Endlosschleife
except Exception as e:
    print("Fehler beim Laden oder Abspielen der Musik:", e)

running = True
while running:
    # Hintergrund zeichnen (Bild oder Fallback-Farbe)
    if background_img:
        screen.blit(background_img, (0, 0))
    else:
        screen.fill((135, 206, 235))  # Himmelblau als Fallback-Hintergrund

    # Boden mit Farbverlauf von Rot zu Orange zeichnen
    draw_gradient_rect(screen, (0, HEIGHT - boden_height, WIDTH, boden_height), (255, 0, 0), (255, 165, 0))

    # Ereignisse abfragen (z.B. Tastendrücke oder Fenster schließen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # Programm beenden

        if event.type == pygame.KEYDOWN:
            # Neustart wenn 'R' gedrückt und Spiel vorbei
            if event.key == pygame.K_r and game_over:
                spieler, is_jumping, velocity_y, obstacles, obstacle_timer, score, score_timer, speedineeedthis, game_over = reset_game()

    keys = pygame.key.get_pressed()  # Abfrage, welche Tasten aktuell gedrückt sind

    if not game_over:
        # Springen, wenn Leertaste gedrückt & Spieler gerade nicht springt
        if keys[pygame.K_SPACE] and not is_jumping:
            is_jumping = True
            try:
                jump_sound = pygame.mixer.Sound("jumpSound.mp3")  # Sprung-Sound laden
                jump_sound.set_volume(1.0)  # Lautstärke setzen (0-1)
                jump_sound.play(0)         # Abspielen
            except Exception as e:
                print("Fehler beim Abspielen des Sprung-Sounds:", e)
            velocity_y = -jump_speed   # Impuls nach oben

        # Spielerposition bei Sprung aktualisieren
        if is_jumping:
            spieler.y += velocity_y  # Vertikal verschieben
            velocity_y += gravity    # Schwerkraft addieren (Fall beschleunigen)
            # Spieler landet auf Boden (keine Überhöhung)
            if spieler.y >= HEIGHT - boden_height - spieler.height:
                spieler.y = HEIGHT - boden_height - spieler.height
                is_jumping = False
                velocity_y = 0

        # Timer hochzählen und bei >1000ms (1 Sek) neues Hindernis erzeugen
        obstacle_timer += clock.get_time()
        if obstacle_timer > 1000:
            obstacle_timer = 0
            # Hindernis erzeugen ganz rechts, auf Höhe des Bodens minus Spielerhöhe (damit es am Boden steht)
            obstacles.append(pygame.Rect(WIDTH, HEIGHT - boden_height - 40, 40, 40))

        # Alle Hindernisse verschieben und zeichnen
        for obstacle in obstacles[:]:  # Kopie der Liste für sicheres Entfernen
            obstacle.x -= speedineeedthis  # Hindernis bewegt sich nach links
            if obstacle_img:
                screen.blit(obstacle_img, obstacle.topleft)  # Bild zeichnen an Hindernis-Position
            else:
                pygame.draw.rect(screen, (255, 0, 0), obstacle)  # Rotes Rechteck als Ersatz
            if obstacle.right < 0:  # Hindernis außerhalb links entfernen
                obstacles.remove(obstacle)
                speedineeedthis = random.randint(20, 35)  # Neue Geschwindigkeit zufällig setzen

        # Kollisionsprüfung zwischen Spieler und Hindernissen
        for obstacle in obstacles:
            if spieler.colliderect(obstacle):
                game_over = True  # Spiel ist vorbei
                print("Game Over! Dein Score:", score)
                try:
                    cheer_sound = pygame.mixer.Sound("losing.wav")  # Game-over-Sound
                    cheer_sound.set_volume(0.5)
                    cheer_sound.play(0)
                except Exception as e:
                    print("Fehler beim Abspielen des Game-Over-Sounds:", e)
                save_score_insert(conn, c, score)  # Score speichern

        # Score jede Sekunde erhöhen
        score_timer += clock.get_time()
        if score_timer >= 1000:
            score += 1
            score_timer = 0

    # Score-Text rendern und anzeigen
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    # Spieler-Quadrat zeichnen
    pygame.draw.rect(screen, BLUE, spieler)

    # Game-Over Text anzeigen
    if game_over:
        game_over_text = font.render("Game Over! Drücke 'R' zum Neustarten.", True, (255, 0, 0))
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))

    # Bildschirm aktualisieren
    pygame.display.flip()
    clock.tick(fps)  # Auf Ziel-FPS warten

# Pygame beenden und Datenbankverbindung schließen
pygame.quit()
conn.close()
