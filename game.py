import time
import os
import random
import math
import pygame
from pygame import mixer
from pygame.locals import *

pygame.init()
mixer.init()

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 650
FPS = 60
SKY_COLOR = (135, 206, 235)
FONT_COLOR = (255, 215, 0)
RULE_TITLE_COLOR = (0, 255, 255)
RULE_TEXT_COLOR = (0, 200, 200)
MENU_TEXT_COLOR = (44, 14, 82)

# Game settings
PLAYER_SPEED = 10
APPLE_SPEED = 5
COCONUT_SPEED = 5
BOSS_SPEED = 3
MAX_MISSES = 15
ACCELERATION_TIME = 10
SPEED_INCREASE = 0.5
MAX_SPEED = 10

DISPLAY = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('2D Newton Simulator')
clock = pygame.time.Clock()

def load_resources():
    resources = {
        'background': pygame.transform.scale(pygame.image.load(os.path.join('data', 'bg.jpg')), (SCREEN_WIDTH, SCREEN_HEIGHT)),
        'bg_img': pygame.transform.scale(pygame.image.load(os.path.join('data', 'bg.png')), (SCREEN_WIDTH, 410)),
        'box_img': pygame.transform.scale(pygame.image.load(os.path.join('data', 'box.png')), (100, 250)),
        'apple_img': pygame.transform.scale(pygame.image.load(os.path.join('data', 'apple.png')), (50, 50)),
        'coco_img': pygame.transform.scale(pygame.image.load(os.path.join('data', 'coco.png')), (70, 50)),
        'boss': pygame.transform.scale(pygame.image.load(os.path.join('data', 'boss.png')), (100, 120)),
        'warn': pygame.transform.scale(pygame.image.load(os.path.join('data', 'warn.png')), (50, 60)),
        'logo': pygame.transform.scale(pygame.image.load(os.path.join('data', 'logo.png')), (450, 70)),
        'dark_overlay': pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA),
    }
    
    resources['dark_overlay'].fill((0, 0, 0, 100))
    
    mixer.music.load("data/bg.mp3")
    sounds = {
        'death': pygame.mixer.Sound("data/over.mp3"),
        'sponge': pygame.mixer.Sound("data/sponge.mp3"),
        'score': pygame.mixer.Sound("data/score.mp3"),
        'coco': pygame.mixer.Sound("data/minus.mp3"),
        'miss': pygame.mixer.Sound("data/miss.mp3"),
        'missMax': pygame.mixer.Sound("data/missMax.mp3"),
    }
    
    fonts = {
        'title': pygame.font.Font(pygame.font.get_default_font(), 60),
        'menu': pygame.font.Font(pygame.font.get_default_font(), 20),
        'score': pygame.font.Font(pygame.font.get_default_font(), 25),
        'rules_title': pygame.font.Font(pygame.font.get_default_font(), 20),
        'rules_text': pygame.font.Font(pygame.font.get_default_font(), 17),
        'game_over': pygame.font.Font(pygame.font.get_default_font(), 50),
    }
    
    return resources, sounds, fonts

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_particles(self, x, y, color, count=10, speed_range=(1, 3), size_range=(2, 5), life_range=(20, 40), 
                      gravity=0, angle_range=None):
        for _ in range(count):
            if angle_range:
                angle = random.uniform(angle_range[0], angle_range[1])
            else:
                angle = random.uniform(0, 2 * math.pi)
                
            speed = random.uniform(*speed_range)
            size = random.uniform(*size_range)
            life = random.randint(*life_range)
            
            self.particles.append({
                'x': x,
                'y': y,
                'vel_x': math.cos(angle) * speed,
                'vel_y': math.sin(angle) * speed,
                'size': size,
                'color': color,
                'life': life,
                'max_life': life,
                'alpha': 255,
                'gravity': gravity,
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-5, 5)
            })
    
    def update(self):
        for particle in self.particles[:]:
            particle['vel_y'] += particle['gravity']
            
            particle['x'] += particle['vel_x']
            particle['y'] += particle['vel_y']
            
            particle['rotation'] += particle['rotation_speed']
            
            particle['life'] -= 1
            particle['alpha'] = max(0, 255 * (particle['life'] / particle['max_life']))
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        for particle in self.particles:
            color = list(particle['color'])
            if len(color) == 3:
                color.append(int(particle['alpha']))
            else:
                color[3] = int(particle['alpha'])
            
            if particle['size'] < 4:
                pygame.draw.circle(
                    surface, 
                    color, 
                    (int(particle['x']), int(particle['y'])), 
                    max(1, int(particle['size']))
                )
            else:
                size = max(1, int(particle['size']))
                particle_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.rect(
                    particle_surface,
                    color,
                    (0, 0, size*2, size*2),
                    border_radius=int(size/2)
                )
                
                if particle['rotation_speed'] != 0:
                    particle_surface = pygame.transform.rotate(particle_surface, particle['rotation'])
                    
                rect = particle_surface.get_rect(center=(int(particle['x']), int(particle['y'])))
                surface.blit(particle_surface, rect.topleft)

class GameObject:
    def __init__(self, image, x, y, speed=0):
        self.image = image
        self.x = x
        self.y = y
        self.speed = speed
        self.width = image.get_width()
        self.height = image.get_height()
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.small_rect = self.rect.inflate(-self.width // 3, -self.height // 3)
        
    def update_position(self, delta_time=1):
        self.rect.x = self.x
        self.rect.y = self.y
        self.small_rect = self.rect.inflate(-self.width // 3, -self.height // 3)
        
    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))
        
    def collides_with(self, other):
        return self.small_rect.colliderect(other.small_rect)

def main_menu(resources, sounds, fonts):
    mixer.music.play(-1)
    
    pulse_value = 0
    pulse_direction = 1
    pulse_speed = 0.05
    
    float_value = 0
    float_speed = 0.03
    
    particles = ParticleSystem()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    return game_loop(resources, sounds, fonts)
                if event.key == K_ESCAPE:
                    pygame.quit()
                    exit()
        
        pulse_value += pulse_speed * pulse_direction
        if pulse_value >= 1 or pulse_value <= 0:
            pulse_direction *= -1
        
        float_value += float_speed
        
        if random.random() < 0.1:
            particles.add_particles(
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                (255, 215, 0, 100),
                count=1,
                speed_range=(0.5, 1.5),
                size_range=(1, 3),
                life_range=(30, 60)
            )
        
        particles.update()
        
        DISPLAY.blit(resources['background'], (0, 0))
        
        particles.draw(DISPLAY)
        
        logo_rect = resources['logo'].get_rect(center=((SCREEN_WIDTH // 2) + 100, 285))
        
        play_text = fonts['menu'].render("Press ENTER to Play", True, MENU_TEXT_COLOR)
        play_text_pulse = pygame.Surface(play_text.get_size(), pygame.SRCALPHA)
        play_text_pulse.blit(play_text, (0, 0))
        play_text_pulse.set_alpha(int(155 + 100 * abs(math.sin(pulse_value * 3))))
        
        play_rect = play_text.get_rect(center=(SCREEN_WIDTH // 2, 365))
        return_text = fonts['menu'].render("Press ESC to Quit", True, MENU_TEXT_COLOR)
        return_rect = return_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        
        box_y_offset = math.sin(float_value) * 5
        apple_y_offset = math.sin(float_value + 1) * 5
        boss_y_offset = math.sin(float_value + 2) * 3
        
        DISPLAY.blit(resources['logo'], logo_rect)
        DISPLAY.blit(play_text_pulse, play_rect)
        DISPLAY.blit(return_text, return_rect)
        DISPLAY.blit(resources['box_img'], (980, 400 + box_y_offset))
        DISPLAY.blit(resources['boss'], (-20, 540 + boss_y_offset))
        DISPLAY.blit(resources['apple_img'], (1000, 350 + apple_y_offset))
        
        pygame.display.update()
        clock.tick(FPS)

def over_menu(reason, score, highscore, resources, sounds, fonts):
    time.sleep(1)
    
    if score > highscore:
        highscore = score
    
    particles = ParticleSystem()
    
    for _ in range(30):
        particles.add_particles(
            random.randint(0, SCREEN_WIDTH),
            random.randint(0, SCREEN_HEIGHT),
            (255, 0, 0, 150) if reason == 0 else (0, 0, 255, 150),
            count=1,
            life_range=(30, 100)
        )
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    return game_loop(resources, sounds, fonts, highscore)
                if event.key == K_ESCAPE:
                    pygame.quit()
                    exit()
        
        particles.update()
        
        if random.random() < 0.1:
            particles.add_particles(
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                (255, 0, 0, 150) if reason == 0 else (0, 0, 255, 150),
                count=1,
                life_range=(30, 100)
            )
        
        DISPLAY.blit(resources['background'], (0, 0))
        
        particles.draw(DISPLAY)
        
        if reason == 0:
            title = fonts['game_over'].render("Newton was hit hard by a Coconut", True, FONT_COLOR)
        elif reason == 1:
            title = fonts['game_over'].render("Newton was Traumatized by Spongebob", True, FONT_COLOR)
        elif reason == 2:
            title = fonts['game_over'].render("Maximum apple wasted", True, FONT_COLOR)
        
        play_text = fonts['menu'].render("Press ENTER to Play again", True, MENU_TEXT_COLOR)
        return_text = fonts['menu'].render("Press ESC to Quit", True, MENU_TEXT_COLOR)
        score_text = fonts['menu'].render("Score: " + str(score), True, MENU_TEXT_COLOR)
        high_score_text = fonts['menu'].render("Highscore: " + str(highscore), True, MENU_TEXT_COLOR)
        
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 285))
        play_rect = play_text.get_rect(center=(SCREEN_WIDTH // 2, 365))
        return_rect = return_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        score_rect = score_text.get_rect(center=((SCREEN_WIDTH // 2) - 100, 20))
        high_score_rect = high_score_text.get_rect(center=((SCREEN_WIDTH // 2) + 100, 20))
        
        DISPLAY.blit(title, title_rect)
        DISPLAY.blit(play_text, play_rect)
        DISPLAY.blit(return_text, return_rect)
        DISPLAY.blit(score_text, score_rect)
        DISPLAY.blit(high_score_text, high_score_rect)
        
        mixer.music.unpause()
        
        pygame.display.update()
        clock.tick(FPS)

def game_loop(resources, sounds, fonts, highscore=0):
    player = GameObject(resources['box_img'], 600, 375, PLAYER_SPEED)
    apple = GameObject(resources['apple_img'], random.randint(50, 800), 0, APPLE_SPEED)
    coconut1 = GameObject(resources['coco_img'], random.randint(50, 800), 0, COCONUT_SPEED)
    coconut2 = GameObject(resources['coco_img'], random.randint(50, 800), 0, COCONUT_SPEED)
    boss = GameObject(resources['boss'], random.randint(50, 800), 1200, BOSS_SPEED)
    
    apple_particles = ParticleSystem()
    coconut_particles = ParticleSystem()
    boss_particles = ParticleSystem()
    
    score = 0
    miss_score = 0
    speed = 1
    time_elapsed = 0
    
    blink_interval = 500  
    last_blink_time = pygame.time.get_ticks()
    visible = True
    
    shake_amount = 0
    shake_decay = 0.9
    shake_offset_x = 0
    shake_offset_y = 0
    
    mixer.music.stop()
    mixer.music.play(-1)
    
    while True:
        delta_time = clock.tick(FPS) / 1000
        
        if shake_amount > 0.1:
            shake_offset_x = random.uniform(-shake_amount, shake_amount)
            shake_offset_y = random.uniform(-shake_amount, shake_amount)
            shake_amount *= shake_decay
        else:
            shake_offset_x = 0
            shake_offset_y = 0
            shake_amount = 0
        
        time_elapsed += delta_time
        if time_elapsed >= ACCELERATION_TIME:
            time_elapsed = 0
            if speed < MAX_SPEED:
                speed += SPEED_INCREASE
        
        coconut1.speed = COCONUT_SPEED + speed
        coconut2.speed = COCONUT_SPEED + speed
        apple.speed = APPLE_SPEED + speed
        player.speed = PLAYER_SPEED + speed
        
        boss.y -= BOSS_SPEED + (speed * 0.5)
        if boss.y < 0:
            boss.x = random.randint(50, 800)
            boss.y = 1200
            
        boss_approaching = boss.y < 1000 and boss.y > 0 
        boss_entering = boss.y < 800 and boss.y > 600    
        
        coconut1.y += coconut1.speed
        if coconut1.y > SCREEN_HEIGHT:
            coconut1.x = random.randint(50, 800)
            coconut1.y = -25
            coconut_particles.add_particles(
                coconut1.x + coconut1.width // 2, 
                0,
                (139, 69, 19, 150),
                count=5,
                speed_range=(0.5, 1.5),
                size_range=(1, 3),
                life_range=(10, 20)
            )
        
        coconut2.y += coconut2.speed
        if coconut2.y > SCREEN_HEIGHT:
            coconut2.x = random.randint(50, 800)
            coconut2.y = -25
            coconut_particles.add_particles(
                coconut2.x + coconut2.width // 2, 
                0,
                (139, 69, 19, 150),
                count=5,
                speed_range=(0.5, 1.5),
                size_range=(1, 3),
                life_range=(10, 20)
            )
        
        apple.y += apple.speed
        if apple.y > SCREEN_HEIGHT:
            old_apple_x = apple.x
            apple.x = random.randint(50, 800)
            apple.y = -25
            miss_score += 1
            sounds['miss'].play()
            
            apple_particles.add_particles(
                old_apple_x + apple.width // 2,
                SCREEN_HEIGHT - 10,
                (255, 0, 0, 200),
                count=25,
                speed_range=(2, 5),
                size_range=(3, 8),
                life_range=(30, 50)
            )
            
            for i in range(15):
                angle = math.pi * 0.7 + math.pi * 0.6 * random.random()
                speed = random.uniform(2, 7)
                apple_particles.add_particles(
                    old_apple_x + apple.width // 2,
                    SCREEN_HEIGHT - 5,
                    (200, 0, 0, 255),
                    count=1,
                    speed_range=(speed, speed),
                    size_range=(2, 4),
                    life_range=(20, 40),
                    gravity=0.2,
                    angle_range=(math.pi * 0.7, math.pi * 1.3)
                )
            
            apple_particles.add_particles(
                apple.x + apple.width // 2, 
                0,
                (0, 255, 0, 150),
                count=5,
                speed_range=(0.5, 1.5),
                size_range=(1, 3),
                life_range=(10, 20)
            )
        
        current_time = pygame.time.get_ticks()
        if current_time - last_blink_time >= blink_interval:
            visible = not visible
            last_blink_time = current_time
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                exit()
        
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_LEFT]:
            player.x -= player.speed
        elif pressed[pygame.K_RIGHT]:
            player.x += player.speed
        
        player.x = max(0, min(player.x, SCREEN_WIDTH - player.width))
        
        player.update_position()
        apple.update_position()
        coconut1.update_position()
        coconut2.update_position()
        boss.update_position()
        
        if score < 0:
            mixer.music.pause()
            sounds['death'].play()
            time.sleep(3)
            return over_menu(0, score, highscore, resources, sounds, fonts)
        
        if miss_score >= MAX_MISSES:
            mixer.music.pause()
            sounds['missMax'].play()
            time.sleep(3)
            return over_menu(2, score, highscore, resources, sounds, fonts)
        
        if player.collides_with(coconut1):
            collision_x = coconut1.x + coconut1.width // 2
            collision_y = coconut1.y + coconut1.height // 2
            
            score -= 2
            sounds['coco'].play()
            coconut1.x = random.randint(50, 800)
            coconut1.y = -25
            
            coconut_particles.add_particles(
                collision_x,
                collision_y,
                (165, 42, 42, 200),
                count=20,
                speed_range=(2, 5),
                size_range=(3, 8),
                life_range=(20, 40),
                gravity=0.1
            )
            
            for _ in range(5):
                angle = random.uniform(0, 2 * math.pi)
                coconut_particles.add_particles(
                    collision_x,
                    collision_y,
                    (101, 67, 33, 200),
                    count=1,
                    speed_range=(3, 6),
                    size_range=(4, 7),
                    life_range=(30, 50),
                    gravity=0.2
                )
            
            shake_amount = 10
            
            coconut_particles.add_particles(
                coconut1.x + coconut1.width // 2, 
                0,
                (139, 69, 19, 150),
                count=8,
                speed_range=(0.5, 2),
                size_range=(1, 3),
                life_range=(10, 20)
            )
        
        if player.collides_with(coconut2):
            collision_x = coconut2.x + coconut2.width // 2
            collision_y = coconut2.y + coconut2.height // 2
            
            score -= 2
            sounds['coco'].play()
            coconut2.x = random.randint(50, 800)
            coconut2.y = -25
            
            coconut_particles.add_particles(
                collision_x,
                collision_y,
                (165, 42, 42, 200),
                count=20,
                speed_range=(2, 5),
                size_range=(3, 8),
                life_range=(20, 40),
                gravity=0.1
            )
            
            for _ in range(5):
                angle = random.uniform(0, 2 * math.pi)
                coconut_particles.add_particles(
                    collision_x,
                    collision_y,
                    (101, 67, 33, 200),
                    count=1,
                    speed_range=(3, 6),
                    size_range=(4, 7),
                    life_range=(30, 50),
                    gravity=0.2
                )
            
            shake_amount = 10
            
            coconut_particles.add_particles(
                coconut2.x + coconut2.width // 2, 
                0,
                (139, 69, 19, 150),
                count=8,
                speed_range=(0.5, 2),
                size_range=(1, 3),
                life_range=(10, 20)
            )
        
        if player.collides_with(apple):
            collision_x = apple.x + apple.width // 2
            collision_y = apple.y + apple.height // 2
            
            score += 1
            sounds['score'].play()
            apple.x = random.randint(50, 800)
            apple.y = -25
            
            apple_particles.add_particles(
                collision_x,
                collision_y,
                (0, 255, 0, 200),
                count=20,
                speed_range=(2, 5),
                size_range=(3, 8),
                life_range=(20, 40)
            )
            
            for _ in range(10):
                apple_particles.add_particles(
                    collision_x + random.randint(-20, 20),
                    collision_y + random.randint(-20, 20),
                    (255, 255, 100, 200),
                    count=1,
                    speed_range=(0.5, 1),
                    size_range=(1, 3),
                    life_range=(20, 30)
                )
                
            apple_particles.add_particles(
                apple.x + apple.width // 2, 
                0,
                (0, 255, 0, 150),
                count=8,
                speed_range=(0.5, 2),
                size_range=(1, 3),
                life_range=(10, 20)
            )
        
        if player.collides_with(boss):
            for _ in range(50):
                boss_particles.add_particles(
                    player.x + player.width//2,
                    player.y + player.height//2,
                    (255, 255, 0, 200),
                    count=2,
                    speed_range=(3, 8),
                    size_range=(4, 10),
                    life_range=(30, 60)
                )
            
            shake_amount = 30
            
            DISPLAY.fill((255, 255, 255))  # Flash white
            pygame.display.update()
            pygame.time.delay(100)
            
            DISPLAY.blit(resources['background'], (shake_offset_x, shake_offset_y))
            boss_particles.draw(DISPLAY)
            boss.draw(DISPLAY)
            player.draw(DISPLAY)
            pygame.display.update()
            
            # Play sound and transition to game over
            mixer.music.pause()
            sounds['sponge'].play()
            time.sleep(3)
            return over_menu(1, score, highscore, resources, sounds, fonts)
        
        apple_particles.update()
        coconut_particles.update()
        boss_particles.update()
        
        DISPLAY.blit(resources['background'], (shake_offset_x, shake_offset_y))
        
        if boss_approaching:
            darkness_alpha = min(150, int(150 * (1 - (boss.y / 1000))))
            dark_overlay = resources['dark_overlay'].copy()
            dark_overlay.set_alpha(darkness_alpha)
            DISPLAY.blit(dark_overlay, (0, 0))
            
            if random.random() < 0.1 and boss.y < 800:
                for _ in range(3):
                    boss_particles.add_particles(
                        random.randint(0, SCREEN_WIDTH),
                        random.randint(SCREEN_HEIGHT - 100, SCREEN_HEIGHT),
                        (255, 0, 0, 100),
                        count=1,
                        speed_range=(0, 2),
                        size_range=(1, 3),
                        life_range=(40, 80)
                    )
        
        apple_particles.draw(DISPLAY)
        coconut_particles.draw(DISPLAY)
        boss_particles.draw(DISPLAY)
        
        if boss_entering:
            if visible:
                warn_scale = 1.0 + 0.2 * math.sin(pygame.time.get_ticks() / 200)
                warn_img = pygame.transform.scale(
                    resources['warn'],
                    (int(resources['warn'].get_width() * warn_scale),
                     int(resources['warn'].get_height() * warn_scale))
                )
                warn_rect = warn_img.get_rect(center=(boss.x + boss.width//2, 550))
                DISPLAY.blit(warn_img, warn_rect.topleft)
                
                if random.random() < 0.2:
                    boss_particles.add_particles(
                        boss.x + boss.width//2,
                        550,
                        (255, 0, 0, 150),
                        count=3,
                        speed_range=(1, 3),
                        size_range=(2, 4),
                        life_range=(10, 20)
                    )
        
        DISPLAY.blit(resources['bg_img'], (0, 270))
        boss.draw(DISPLAY)
        apple.draw(DISPLAY)
        coconut1.draw(DISPLAY)
        coconut2.draw(DISPLAY)
        player.draw(DISPLAY)
        
        score_text = fonts['score'].render("Gravity found: " + str(score), True, FONT_COLOR)
        miss_text = fonts['score'].render("Apple Missed: " + str(miss_score), True, FONT_COLOR)
        rules_title = fonts['rules_title'].render("Rules", True, RULE_TITLE_COLOR)
        rule1 = fonts['rules_text'].render("- touch apple = +1", True, RULE_TEXT_COLOR)
        rule2 = fonts['rules_text'].render("- touch Coconut= -2", True, RULE_TEXT_COLOR)
        rule3 = fonts['rules_text'].render("- Spongebob = death", True, RULE_TEXT_COLOR)
        rule4 = fonts['rules_text'].render("- miss limit = 15", True, RULE_TEXT_COLOR)
        
        DISPLAY.blit(score_text, (30, 20))
        DISPLAY.blit(miss_text, (30, 50))
        DISPLAY.blit(rules_title, (960, 20))
        DISPLAY.blit(rule1, (900, 40))
        DISPLAY.blit(rule2, (900, 55))
        DISPLAY.blit(rule3, (900, 70))
        DISPLAY.blit(rule4, (900, 85))
        
        # Draw debug collision boxes if needed
        # pygame.draw.rect(DISPLAY, (255, 0, 0), player.small_rect, 2)
        # pygame.draw.rect(DISPLAY, (0, 255, 0), apple.small_rect, 2)
        # pygame.draw.rect(DISPLAY, (0, 0, 255), coconut1.small_rect, 2)
        # pygame.draw.rect(DISPLAY, (255, 255, 0), coconut2.small_rect, 2)
        # pygame.draw.rect(DISPLAY, (255, 0, 255), boss.small_rect, 2)
        
        pygame.display.update()

def main():
    resources, sounds, fonts = load_resources()
    
    main_menu(resources, sounds, fonts)

if __name__ == "__main__":
    main()