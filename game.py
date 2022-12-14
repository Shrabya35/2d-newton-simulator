import time
from pygame import mixer
import pygame, sys
from pygame.locals import *
import os
import random
import math

pygame.init()


mixer.init()
mixer.music.load("data/bg.mp3")
mixer.music.play(-1)

#variables 


death = pygame.mixer.Sound("data/over.mp3")
ten = pygame.mixer.Sound("data/10.mp3")
sponge = pygame.mixer.Sound("data/sponge.mp3")
score_sound = pygame.mixer.Sound("data/score.mp3")
coco = pygame.mixer.Sound("data/minus.mp3")
miss = pygame.mixer.Sound("data/miss.mp3")


DISPLAY = pygame.display.set_mode((1080, 650))
pygame.display.set_caption('2D Newton Simulator')
sky = (135, 206, 235)
black = (0, 0, 0)
color2 = (0,10,100)
FPS = 24


bg_img = pygame.image.load(os.path.join('data', 'bg.png'))
bg_img = pygame.transform.scale(bg_img, (1080, 410))
box_img = pygame.image.load(os.path.join('data', 'box.png'))
box_img = pygame.transform.scale(box_img, (300, 300))
apple_img = pygame.image.load(os.path.join('data', 'apple.png'))
apple_img = pygame.transform.scale(apple_img, (100, 80))
coco_img = pygame.image.load(os.path.join('data', 'coco.png'))
coco_img = pygame.transform.scale(coco_img, (70, 50))
coco_img2 = pygame.image.load(os.path.join('data', 'coco.png'))
coco_img2 = pygame.transform.scale(coco_img, (70, 50))
boss = pygame.image.load(os.path.join('data', 'boss.png'))
boss = pygame.transform.scale(boss, (190, 150))


b_x = random.randint(50, 800)
b_y = 1200
x = 300
y = 345
a_x = random.randint(50, 800)
a_y = 0
c_x = random.randint(50, 800)
c_y = 0
c_x1 = random.randint(50, 800)
c_y1 = 0
apple_speed = 10
coco_speed = 8
score = 0


font = pygame.font.Font(pygame.font.get_default_font(), 25)
font2 = pygame.font.Font(pygame.font.get_default_font(), 20)
font3 = pygame.font.Font(pygame.font.get_default_font(), 17)

#collision detection
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
def collide3(x, y, c_x1, c_y1):
    distance3 = math.sqrt(math.pow(x-c_x1, 2) + (math.pow(y-c_y1, 2)))
    if distance3 < 80:
        return True
    else:
        return False

def collide4(x, y, b_x, b_y):
    distance4 = math.sqrt(math.pow(x-b_x, 2) + (math.pow(y-b_y, 2)))
    if distance4 < 80:
        return True
    else:
        return False


#in-game loop
while True:



    b_y = b_y - coco_speed
    if b_y < 0:
        b_x = random.randint(50, 800)
        b_y = 1200
    c_y = c_y + coco_speed
    if c_y > 550:
        c_x = random.randint(50, 800)
        c_y = -25
    c_y1 = c_y1 + coco_speed
    if c_y1 > 550:
        c_x1 = random.randint(50, 800)
        c_y1 = -25

    a_y = a_y + apple_speed
    if a_y > 550:
        a_x = random.randint(50, 800)
        a_y = -25
        miss.play()



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
        if score < 0:
            mixer.music.pause()
            death.play()
            time.sleep(5)
            pygame.quit()


       #boundary set
        if x <= -40:
            x = -40
        elif x >= 800:
            x = 800


        #text 
        text = font.render("Gravity found: " + str(score), True, black)
        text2 = font2.render("Rules", True, color2)
        text3 = font3.render("- Watch apple = +1", True, color2)
        text4 = font3.render("- Watch Coconut= -2", True, color2)
        text5 = font3.render("- Dont Watch Spongebob", True, color2)

        #collision 
        collision2 = collide2(x, y, c_x, c_y)
        if collision2:
            c_x = random.randint(50, 800)
            c_y = -25
            score = score -2
            coco.play()
        collision = collide(x, y, a_x, a_y)
        if collision:
            a_x = random.randint(50, 800)
            a_y = -25
            score = score +1
            score_sound.play()
        collision3 = collide3(x, y, c_x1, c_y1)
        if collision3:
            c_x1 = random.randint(50, 800)
            c_y1 = -25
            score = score -2
            coco.play()

        collision4 = collide4(x, y, b_x, b_y)
        if collision4:
            mixer.music.pause()
            sponge.play()
            time.sleep(4)
            pygame.quit()






        #game exit
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            

    DISPLAY.fill(sky)
    DISPLAY.blit(boss, (b_x, b_y))
    DISPLAY.blit(bg_img, (0, 245))
    DISPLAY.blit(apple_img, (a_x, a_y))
    DISPLAY.blit(coco_img, (c_x, c_y))
    DISPLAY.blit(coco_img2, (c_x1, c_y1))
    DISPLAY.blit(box_img, (x, y))
    DISPLAY.blit(text, (30, 20))
    DISPLAY.blit(text2, (940, 20))
    DISPLAY.blit(text3, (870, 40))
    DISPLAY.blit(text4, (870, 55))
    DISPLAY.blit(text5, (870, 70))


    pygame.display.update()
