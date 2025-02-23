import pygame
import sys
import random
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Game constants
WIDTH = 400
HEIGHT = 600
GRAVITY = 0.5
FLAP_POWER = -8
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # milliseconds
HIGH_SCORE_FILE = "flappy_high_score.txt"

# Colors
WHITE = (255, 255, 255)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# Load assets
current_dir = os.path.dirname(__file__)
assets_dir = os.path.join(current_dir, 'assets')

try:
    bg_image = pygame.image.load(os.path.join(assets_dir, 'bg.png')).convert()
    base_image = pygame.image.load(os.path.join(assets_dir, 'ground.png')).convert()
    pipe_image = pygame.image.load(os.path.join(assets_dir, 'pipe.png')).convert()
    restart_image = pygame.image.load(os.path.join(assets_dir, 'restart.png')).convert_alpha()
    bird_images = [
        pygame.image.load(os.path.join(assets_dir, 'bird1.png')).convert_alpha(),
        pygame.image.load(os.path.join(assets_dir, 'bird2.png')).convert_alpha(),
        pygame.image.load(os.path.join(assets_dir, 'bird3.png')).convert_alpha()
    ]
    
    # Sounds
    flap_sound = pygame.mixer.Sound(os.path.join(assets_dir, 'flap.wav'))
    hit_sound = pygame.mixer.Sound(os.path.join(assets_dir, 'hit.wav'))
    point_sound = pygame.mixer.Sound(os.path.join(assets_dir, 'point.wav'))
    die_sound = pygame.mixer.Sound(os.path.join(assets_dir, 'die.wav'))
except Exception as e:
    print(f"Error loading assets: {e}")
    sys.exit()

# Scale images
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
base_image = pygame.transform.scale(base_image, (WIDTH, 100))
pipe_image = pygame.transform.scale(pipe_image, (80, HEIGHT))
restart_rect = restart_image.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))

class Bird:
    def __init__(self):
        self.images = bird_images
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect(center=(50, HEIGHT//2))
        self.velocity = 0
        self.animation_time = 0
        
    def jump(self):
        self.velocity = FLAP_POWER
        flap_sound.play()
        
    def update(self):
        self.velocity += GRAVITY
        self.rect.centery += self.velocity
        
        self.animation_time += 1
        if self.animation_time % 5 == 0:
            self.image_index = (self.image_index + 1) % 3
            self.image = self.images[self.image_index]
        
    def draw(self):
        screen.blit(self.image, self.rect)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(150, HEIGHT - 150 - PIPE_GAP)
        self.passed = False
        
    @property
    def top_rect(self):
        return pygame.Rect(self.x, 0, 80, self.gap_y)
    
    @property
    def bottom_rect(self):
        return pygame.Rect(self.x, self.gap_y + PIPE_GAP, 80, HEIGHT - self.gap_y - PIPE_GAP)
    
    def update(self):
        self.x -= 3
        
    def draw(self):
        screen.blit(pygame.transform.flip(pipe_image, False, True), 
                   (self.x, self.gap_y - pipe_image.get_height()))
        screen.blit(pipe_image, (self.x, self.gap_y + PIPE_GAP))


def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, 'r') as f:
            return int(f.read())
    except:
        return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, 'w') as f:
        f.write(str(score))

def draw_text(text, size, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def game_loop():
    bird = Bird()
    base_x = 0
    pipes = []
    score = 0
    high_score = load_high_score()
    game_active = False
    game_over = False
    die_played = False
    spawn_pipe = pygame.USEREVENT
    pygame.time.set_timer(spawn_pipe, PIPE_FREQUENCY)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_over:
                        bird.jump()
                        game_active = True
                    else:
                        return game_loop()
            if event.type == spawn_pipe and game_active:
                pipes.append(Pipe(WIDTH))

        screen.blit(bg_image, (0, 0))

        if game_active and not game_over:
            bird.update()
            for pipe in pipes:
                pipe.update()
                if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                    hit_sound.play()
                    game_over = True
                    game_active = False
                if not pipe.passed and pipe.x + 80 < bird.rect.centerx:
                    pipe.passed = True
                    score += 1
                    point_sound.play()
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)
            pipes = [pipe for pipe in pipes if pipe.x > -80]
            if bird.rect.bottom >= HEIGHT - 100:
                hit_sound.play()
                game_over = True
                game_active = False

        for pipe in pipes:
            pipe.draw()

        base_x -= 1
        if base_x <= -WIDTH:
            base_x = 0
        screen.blit(base_image, (base_x, HEIGHT - 100))
        screen.blit(base_image, (base_x + WIDTH, HEIGHT - 100))
        bird.draw()
        draw_text(f"Score: {score}", 40, WIDTH//2, 50)
        draw_text(f"High Score: {high_score}", 30, WIDTH//2, 90)

        if game_over:
            if not die_played:
                die_sound.play()
                die_played = True
            screen.blit(restart_image, restart_rect)
            draw_text("Game Over! Press SPACE to restart", 30, WIDTH//2, HEIGHT//2)
        
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    game_loop()
