import pygame
import random


pygame.init()
HEIGHT = 800
WIDTH = 1000

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jump and Run")


BLUE = (0, 0, 255)
WHITE = (255, 255, 255)


spieler = pygame.Rect(100, 300, 40, 40)
spieler_speed = 5





clock = pygame.time.Clock()
fps = 60


running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

   
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        spieler.x -= spieler_speed
    if keys[pygame.K_RIGHT]:
        spieler.x += spieler_speed
    



    
    pygame.draw.rect(screen, BLUE, spieler)
    

    
    pygame.display.flip()
    clock.tick(fps)

pygame.quit()



