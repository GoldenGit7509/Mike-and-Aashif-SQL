import pygame
import random

pygame.init()
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The best athletes")
#Sounds
cheer_sound = pygame.mixer.Sound("crowd_cheering.mp3")
cheer_sound.set_volume(0.3) 
cheer_sound.play(-1)  

# Farben
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)

#  FPS
clock = pygame.time.Clock()
fps = 60

# Punktesystem
score = 0
score_timer = 0
font = pygame.font.SysFont(None, 40)

# Spieler
spieler = pygame.Rect(100, 670, 40, 80)
is_jumping = False
jump_speed = 15
gravity = 1
velocity_y = 0

# Boden
boden_height = 50

# "gegner"
obstacles = []
obstacle_timer = 0
obstacle_interval = 1000
speedineeedthis = 10

running = True
while running:
    screen.fill(WHITE)
    pygame.draw.rect(screen, GREEN, (0, HEIGHT - boden_height, WIDTH, boden_height))  # Boden

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Spieler movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and not is_jumping:
        is_jumping = True
        velocity_y = -jump_speed

    # Sprung
    if is_jumping:
        spieler.y += velocity_y
        velocity_y += gravity
        if spieler.y >= HEIGHT - boden_height - spieler.height:
            spieler.y = HEIGHT - boden_height - spieler.height
            is_jumping = False
            velocity_y = 0

    # "gegener" erzeugen
    obstacle_timer += clock.get_time()
    if obstacle_timer > obstacle_interval:
        obstacle_timer = 0
        new_obstacle = pygame.Rect(WIDTH, HEIGHT - boden_height - 40, 40, 40)
        obstacles.append(new_obstacle)

    # "gegner" bewegen und zeichnen
    for obstacle in obstacles[:]:
        obstacle.x -= speedineeedthis
        print(obstacle.x)
        pygame.draw.rect(screen, BLACK, obstacle)
        if obstacle.right < 0:
            obstacles.remove(obstacle)
            speedineeedthis = random.randint(20,35)

    # collisiion
    for obstacle in obstacles:
        if spieler.colliderect(obstacle):
            running = False

    # Punkte erhöhen pro Sekunde
    score_timer += clock.get_time()
    if score_timer >= 1000:  # 1000 ms = 1 Sekunde
        score += 1
        score_timer = 0
    

    

        
        
     

    # Punktestand anzeigen
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    # Spieler zeichnen
    pygame.draw.rect(screen, BLUE, spieler)

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()


            