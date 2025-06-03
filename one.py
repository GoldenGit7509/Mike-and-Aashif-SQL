import pygame
import random

# Initialisierung
pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jump and Run")

running = True
while running:

 for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

