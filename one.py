import pygame
import random

pygame.init()
HEIGHT = 800
WIDTH = 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jump and Run")
player = pygame.Rect(100, 300, 40, 40)
BLUE = (0, 0, 255)
clock = pygame.time.Clock()
fps = 60


running = True
while running:

 for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            # Quadrat zeichnen
 pygame.draw.rect(screen, BLUE, player)

    
 pygame.display.flip()

    
 clock.tick(fps)
pygame.quit()


