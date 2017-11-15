import pygame
import random
from settings import *


pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()

running = True

while running:
 	clock.tick(FPS)
 	for event in pygame.event.get():
 		if event.type == pygame.QUIT:
 			running = False

 	all_sprites.update()

 	screen.fill(BLACK)
 	all_sprites.draw(screen)

 	pygame.display.flip()

pygame.quit()