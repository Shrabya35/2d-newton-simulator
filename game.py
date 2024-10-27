import time
from pygame import mixer
import pygame, sys
from pygame.locals import *
import os
import random
import math

pygame.init()

# Initialize mixer and load music
mixer.init()
mixer.music.load("data/bg.mp3")
mixer.music.play(-1)

# Load sound effects
death = pygame.mixer.Sound("data/over.mp3")
sponge = pygame.mixer.Sound("data/sponge.mp3")
score_sound = pygame.mixer.Sound("data/score.mp3")
coco = pygame.mixer.Sound("data/minus.mp3")
miss = pygame.mixer.Sound("data/miss.mp3")
missMax =  pygame.mixer.Sound("data/missMax.mp3")
# Set up display
DISPLAY = pygame.display.set_mode((1080, 650))
pygame.display.set_caption('2D Newton Simulator')
sky = (135, 206, 235)
FPS = 24
highscore = 0

# Load and scale images
background = pygame.transform.scale(pygame.image.load(os.path.join('data', 'bg.jpg')), (1080, 650))
bg_img = pygame.transform.scale(pygame.image.load(os.path.join('data', 'bg.png')), (1080, 410))
box_img = pygame.transform.scale(pygame.image.load(os.path.join('data', 'box.png')), (100, 250))
apple_img = pygame.transform.scale(pygame.image.load(os.path.join('data', 'apple.png')), (50, 50))
coco_img = pygame.transform.scale(pygame.image.load(os.path.join('data', 'coco.png')), (70, 50))
boss = pygame.transform.scale(pygame.image.load(os.path.join('data', 'boss.png')), (100, 120))
warn = pygame.transform.scale(pygame.image.load(os.path.join('data', 'warn.png')), (50, 60))
logo = pygame.transform.scale(pygame.image.load(os.path.join('data', 'logo.png')), (450, 70))

# Function to display the main menu
def main_menu():
    while True:
        title_font = pygame.font.Font(pygame.font.get_default_font(), 60)
        menu_font = pygame.font.Font(pygame.font.get_default_font(), 20)

        title = title_font.render("2D Newton Simulator", True, (0, 0, 0))
        play_text = menu_font.render("Press ENTER to Play", True, (44, 14, 82))
        return_text = menu_font.render("Press ESC to Quit", True, (44, 14, 82))

        title_rect = title.get_rect(center=((DISPLAY.get_width() // 2) + 100, 285))
        play_rect = play_text.get_rect(center=(DISPLAY.get_width() // 2, 365))
        return_rect = return_text.get_rect(center=(DISPLAY.get_width() // 2, 400))

        DISPLAY.blit(background, (0, 0))
        DISPLAY.blit(logo, title_rect)
        DISPLAY.blit(play_text, play_rect)
        DISPLAY.blit(return_text, return_rect)
        DISPLAY.blit(box_img, (980, 400))
        DISPLAY.blit(boss, (-20, 540))
        DISPLAY.blit(apple_img, (1000, 350))
        

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:  
                    game_loop()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:  
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

def over_menu(reason,score):
     time.sleep(1) 
     global highscore
     while True:
        if score > highscore:
            highscore = score
        
        title_font = pygame.font.Font(pygame.font.get_default_font(), 50)
        menu_font = pygame.font.Font(pygame.font.get_default_font(), 20)
        if reason == 0:
            title = title_font.render("Newton was hit hard by a Coconut", True, (255, 215, 0))
        elif reason == 1:
            title = title_font.render("Newton was Traumatized by Spongebob", True, (255, 215, 0))
        elif reason == 2:
            title = title_font.render("Maximum apple wasted", True, (255, 215, 0))
        
        play_text = menu_font.render("Press ENTER to Play again", True, (44, 14, 82))
        return_text = menu_font.render("Press ESC to Quit", True, (44, 14, 82))
        score_text =  menu_font.render("Score: " + str(score), True, (44, 14, 82))
        high_score_text =  menu_font.render("Highscore: " + str(highscore), True, (44, 14, 82))
        
        title_rect = title.get_rect(center=(DISPLAY.get_width() // 2, 285))
        play_rect = play_text.get_rect(center=(DISPLAY.get_width() // 2, 365))
        return_rect = return_text.get_rect(center=(DISPLAY.get_width() // 2, 400))
        score_rect = score_text.get_rect(center=((DISPLAY.get_width() // 2)-100, 20))
        high_score_rect = score_text.get_rect(center=((DISPLAY.get_width() // 2)+100, 20))

        DISPLAY.blit(background, (0, 0))
        DISPLAY.blit(title, title_rect)
        DISPLAY.blit(play_text, play_rect)
        DISPLAY.blit(return_text, return_rect)
        DISPLAY.blit(score_text, score_rect)
        DISPLAY.blit(high_score_text, high_score_rect)


        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:  # Start the game on Enter
                    game_loop()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:  
                    pygame.quit()
                    sys.exit()

        mixer.music.unpause() 
        pygame.display.update()

# In-game loop
def game_loop():
    # Set initial positions and speeds
    b_x = random.randint(50, 800)
    b_y = 1200
    x = 600
    y = 375
    player_speed = 10
    a_x = random.randint(50, 800)
    a_y = 0
    c_x = random.randint(50, 800)
    c_y = 0
    c_x1 = random.randint(50, 800)
    c_y1 = 0
    apple_speed = 5
    coco_speed = 5
    score = 0
    missScore = 0
    speed = 1
    time_elapsed = 0
    acceleration_time = 10
    speed_increase = 1 
    max_speed = 20
    

    # Initialize fonts
    font = pygame.font.Font(pygame.font.get_default_font(), 25)
    font2 = pygame.font.Font(pygame.font.get_default_font(), 20)
    font3 = pygame.font.Font(pygame.font.get_default_font(), 17)

    # Define collision detection using Rects
    def collide(rect1, rect2):
        return rect1.colliderect(rect2)

    blink_interval = 500  # milliseconds
    last_blink_time = pygame.time.get_ticks()
    visible = True
    clock = pygame.time.Clock()
    
    while True:
        # Update positions
        delta_time = clock.tick(60) / 1000
        time_elapsed += delta_time
        if time_elapsed >= acceleration_time:
            time_elapsed = 0 
            if speed < max_speed:
                speed += speed_increase
        
        coco_speed += speed * delta_time
        apple_speed += speed * delta_time
        player_speed += speed * delta_time

        b_y -= coco_speed
        if b_y < 0:
            b_x = random.randint(50, 800)
            b_y = 1200
        c_y += coco_speed
        if c_y > 600:
            c_x = random.randint(50, 800)
            c_y = -25
        c_y1 += coco_speed
        if c_y1 > 600:
            c_x1 = random.randint(50, 800)
            c_y1 = -25
        a_y += apple_speed
        if a_y > 600:
            a_x = random.randint(50, 800)
            a_y = -25
            missScore += 1
            miss.play()

        current_time = pygame.time.get_ticks()
        if current_time - last_blink_time >= blink_interval:
            visible = not visible  
            last_blink_time = current_time 

        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # Player movement
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_LEFT]:
            x -= player_speed
        elif pressed[pygame.K_RIGHT]:
            x += player_speed
        elif pressed[pygame.K_ESCAPE]:
            pygame.quit()
        
        if score < 0:
            mixer.music.pause()
            death.play()
            time.sleep(5)
            reason = 0
            over_menu(reason,score)
        
        if missScore >= 15:
            mixer.music.pause()
            missMax.play()
            time.sleep(4)
            reason = 2
            over_menu(reason,score)



        # Boundary checks
        x = max(0, min(x, 980))  # Keep the player within screen bounds

        # Create Rects for collision detection
        player_rect = pygame.Rect(x, y, box_img.get_width(), box_img.get_height())
        apple_rect = pygame.Rect(a_x, a_y, apple_img.get_width(), apple_img.get_height())
        coco_rect = pygame.Rect(c_x, c_y, coco_img.get_width(), coco_img.get_height())
        coco_rect2 = pygame.Rect(c_x1, c_y1, coco_img.get_width(), coco_img.get_height())
        boss_rect = pygame.Rect(b_x, b_y, boss.get_width(), boss.get_height())
        small_player_rect = player_rect.inflate(-player_rect.width // 3, -player_rect.height // 3)
        small_apple_rect = apple_rect.inflate(-apple_rect.width // 3, -apple_rect.height // 3)
        small_coco_rect = coco_rect.inflate(-coco_rect.width // 3, -coco_rect.height // 3)
        small_coco_rect2 = coco_rect2.inflate(-coco_rect2.width // 3, -coco_rect2.height // 3)
        small_boss_rect = boss_rect.inflate(-boss_rect.width // 3, -boss_rect.height // 3)

        # Collision detection
        if collide(small_player_rect, small_coco_rect):
            score -= 2
            coco.play()
            c_x = random.randint(50, 800)
            c_y = -25
        if collide(small_player_rect, small_apple_rect):
            score += 1
            score_sound.play()
            a_x = random.randint(50, 800)
            a_y = -25
        if collide(small_player_rect, small_coco_rect2):
            score -= 2
            coco.play()
            c_x1 = random.randint(50, 800)
            c_y1 = -25
               
        if collide(small_player_rect, small_boss_rect):
            mixer.music.pause()
            sponge.play()
            time.sleep(4)
            reason = 1
            over_menu(reason,score)
        
        # Render
        DISPLAY.blit(background, (0, 0))
        DISPLAY.blit(boss, (b_x, b_y))
        DISPLAY.blit(bg_img, (0, 270))
        if visible and b_y > 620:
            DISPLAY.blit(warn, (b_x, 550))
        DISPLAY.blit(apple_img, (a_x, a_y))
        DISPLAY.blit(coco_img, (c_x, c_y))
        DISPLAY.blit(coco_img, (c_x1, c_y1))
        DISPLAY.blit(box_img, (x, y))

        # Display score and rules
        scoreText = font.render("Gravity found: " + str(score), True, (255, 215, 0))
        missText = font.render("Apple Missed: " + str(missScore), True, (255, 215, 0))
        rules = font2.render("Rules", True, (0, 255, 255))
        rule1 = font3.render("- touch apple = +1", True, (0, 200, 200))
        rule2 = font3.render("- touch Coconut= -2", True, (0, 200, 200))
        rule3 = font3.render("- Spongebob = death", True, (0, 200, 200))
        rule4 = font3.render("- miss limit = 15", True, (0, 200, 200))
        
        DISPLAY.blit(scoreText, (30, 20))
        DISPLAY.blit(missText, (30,50))
        DISPLAY.blit(rules, (960, 20))
        DISPLAY.blit(rule1, (900, 40))
        DISPLAY.blit(rule2, (900, 55))
        DISPLAY.blit(rule3, (900, 70))
        DISPLAY.blit(rule4, (900, 85))

        # Draw rectangles for debug
        # pygame.draw.rect(DISPLAY, (255, 0, 0), player_rect, 2)  
        # pygame.draw.rect(DISPLAY, (0, 255, 0), apple_rect, 2)   
        # pygame.draw.rect(DISPLAY, (0, 0, 255), coco_rect, 2)    
        # pygame.draw.rect(DISPLAY, (255, 255, 0), coco_rect2, 2) 
        # pygame.draw.rect(DISPLAY, (255, 0, 255), boss_rect, 2) 
        # pygame.draw.rect(DISPLAY, (255, 0, 0), small_player_rect, 2)  # Red outline for player
        # pygame.draw.rect(DISPLAY, (0, 255, 0), small_apple_rect, 2)   # Green outline for apple
        # pygame.draw.rect(DISPLAY, (0, 0, 255), small_coco_rect, 2)    # Blue outline for first coconut
        # pygame.draw.rect(DISPLAY, (255, 255, 0), small_coco_rect2, 2) # Yellow outline for second coconut
        # pygame.draw.rect(DISPLAY, (255, 0, 255), small_boss_rect, 2) 

        pygame.display.update()
        clock.tick(FPS)

# Start the game by showing the main menu
main_menu()

