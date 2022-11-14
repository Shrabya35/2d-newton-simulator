import pygame, sys
from pygame.locals import *
import os
import random
import math

pygame.init()
DISPLAY = pygame.display.set_mode((1080, 650))
pygame.display.set_caption('2D Newton Simulator')
sky = (135, 206, 235)
black = (0, 0, 0)
color2 = (0,10,100)
FPS = 24
bg_img = pygame.image.load(os.path.join('img', 'bg.png'))
bg_img = pygame.transform.scale(bg_img, (1080, 410))
box_img = pygame.image.load(os.path.join('img', 'box.png'))
box_img = pygame.transform.scale(box_img, (300, 300))
apple_img = pygame.image.load(os.path.join('img', 'apple.png'))
apple_img = pygame.transform.scale(apple_img, (100, 80))
coco_img = pygame.image.load(os.path.join('img', 'coco.png'))
coco_img = pygame.transform.scale(coco_img, (70, 50))
x = 300
y = 345
a_x = random.randint(50, 600)
a_y = 0
c_x = random.randint(50, 600)
c_y = 0
apple_speed = 10
coco_speed = 8
score = 0
font = pygame.font.Font(pygame.font.get_default_font(), 25)
font2 = pygame.font.Font(pygame.font.get_default_font(), 20)
font3 = pygame.font.Font(pygame.font.get_default_font(), 17)


clock = pygame.time.Clock()


def collide(x, y, a_x, a_y):
    distance = math.sqrt(math.pow(x-a_x, 2) + (math.pow(y-a_y, 2)))
    if distance < 80:
        return True
    else:
        return False
def collide2(x, y, c_x, c_y):
    distance2 = math.sqrt(math.pow(x-c_x, 2) + (math.pow(y-c_y, 2)))
    if distance2 < 80:
        return True
    else:
        return False

while True:





    c_y = c_y + coco_speed
    if c_y > 550:
        c_x = random.randint(50, 600)
        c_y = -25


    a_y = a_y + apple_speed
    if a_y > 550:
        a_x = random.randint(50, 600)
        a_y = -25
    clock.tick(FPS)


    for event in pygame.event.get():


     #player movement
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_LEFT]:
            x -= 40
        elif pressed[pygame.K_RIGHT]:
            x += 40
        elif pressed[pygame.K_ESCAPE]:
            pygame.quit()

       #boundary set
        if x <= -40:
            x = -40
        elif x >= 800:
            x = 800
        text = font.render("Gravity found: " + str(score), True, black)
        text2 = font2.render("Rules", True, color2)
        text3 = font3.render("- Watch apple = +1", True, color2)
        text4 = font3.render("- Watch Coconut= -1", True, color2)
        collision2 = collide2(x, y, c_x, c_y)
        if collision2:
            c_x = random.randint(50, 600)
            c_y = -25
            score = score - 1
        collision = collide(x, y, a_x, a_y)
        if collision:
            a_x = random.randint(50, 600)
            a_y = -25
            score = score +1






        #game exit
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    DISPLAY.fill(sky)
    DISPLAY.blit(bg_img, (0, 245))
    DISPLAY.blit(text2, (940, 20))
    DISPLAY.blit(text, (30, 20))
    DISPLAY.blit(text3, (910, 40))
    DISPLAY.blit(text4, (910, 55))
    DISPLAY.blit(apple_img, (a_x, a_y))
    DISPLAY.blit(coco_img, (c_x, c_y))
    DISPLAY.blit(box_img, (x, y))

    pygame.display.update()



