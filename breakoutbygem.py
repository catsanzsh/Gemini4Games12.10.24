import pygame
import sys
import numpy as np

# --- Constants ---
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 10
BALL_RADIUS = 10
BRICK_WIDTH, BRICK_HEIGHT = 75, 20
FPS = 60
SAMPLE_RATE = 44100

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# --- Initialize Pygame ---
pygame.init()
pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2)  # Initialize Pygame Mixer for stereo
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# --- Sound Generation Functions ---
def generate_sine_wave(frequency, duration, amplitude):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave

def generate_impact_sound(base_frequency, duration, amplitude):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    decay = np.exp(-8 * t)  # Adjust decay for different impact sounds
    wave = amplitude * decay * np.sin(2 * np.pi * base_frequency * t)
    return wave

def play_sound(wave):
    # Normalize to 16-bit range and convert to int16
    audio = (wave * 32767 / np.max(np.abs(wave))).astype(np.int16)

    # Reshape the audio array for stereo playback
    audio = np.repeat(audio.reshape(len(audio), 1), 2, axis=1)

    sound = pygame.sndarray.make_sound(audio)
    sound.play()

# --- Paddle Class ---
class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = 0  # Set initial speed to 0
        self.friction = 0.85 #Friction/deceleration factor

    def move(self, direction):
        if direction == "LEFT" and self.rect.left > 0:
            self.speed = -8
        elif direction == "RIGHT" and self.rect.right < WIDTH:
            self.speed = 8
        else:
            # Apply friction to slow down the paddle gradually
            self.speed *= self.friction
            if abs(self.speed) < 0.1:
                self.speed = 0

        self.rect.x += self.speed

        # Prevent the paddle from going off-screen
        if self.rect.left < 0:
            self.rect.left = 0
            self.speed = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.speed = 0

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

# --- Ball Class ---
class Ball:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BALL_RADIUS * 2, BALL_RADIUS * 2)
        self.speed_x = 5
        self.speed_y = -5

    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

    def bounce(self, paddle=None):
        if self.rect.top <= 0:
            self.speed_y *= -1
            play_sound(generate_sine_wave(440, 0.1, 0.5))  # Wall bounce sound
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.speed_x *= -1
            play_sound(generate_sine_wave(440, 0.1, 0.5))  # Wall bounce sound
        if paddle and self.rect.colliderect(paddle.rect):
            self.speed_y *= -1
            # Paddle hit sound (higher frequency)
            play_sound(generate_impact_sound(600, 0.1, 0.5))

    def draw(self):
        pygame.draw.circle(screen, RED, self.rect.center, BALL_RADIUS)

# --- Brick Class ---
class Brick:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.color = color

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)

# --- Functions ---

def create_bricks():
    bricks = []
    for row in range(5):
        for col in range(WIDTH // BRICK_WIDTH):
            x = col * BRICK_WIDTH
            y = row * BRICK_HEIGHT + 50  # Offset from the top
            color = YELLOW if row < 2 else GREEN
            bricks.append(Brick(x, y, color))
    return bricks

def display_text(text, color, y, size=36):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, y))
    screen.blit(text_surface, text_rect)

def main_menu():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "GAME"
                elif event.key == pygame.K_c:
                    return "CREDITS"
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        screen.fill(BLACK)
        display_text("Breakout", WHITE, HEIGHT // 3)
        display_text("Press SPACE to Play", WHITE, HEIGHT // 2)
        display_text("Press C for Credits", WHITE, HEIGHT // 2 + 50)
        pygame.display.update()
        clock.tick(FPS)

def credits():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "MENU"

        screen.fill(BLACK)
        display_text("Credits", WHITE, HEIGHT // 3)
        display_text("Game made by [Your Name]", WHITE, HEIGHT // 2)
        display_text("Press ESC to return", WHITE, HEIGHT // 2 + 50)
        pygame.display.update()
        clock.tick(FPS)

def game_over(score):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "GAME"
                elif event.key == pygame.K_ESCAPE:
                    return "MENU"

        screen.fill(BLACK)
        display_text("Game Over", RED, HEIGHT // 3, size=50)
        display_text(f"Your Score: {score}", WHITE, HEIGHT // 2)
        display_text("Press SPACE to Play Again", WHITE, HEIGHT // 2 + 50)
        display_text("Press ESC for Main Menu", WHITE, HEIGHT // 2 + 100)
        pygame.display.update()
        clock.tick(FPS)

def game():
    paddle = Paddle(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - 50)
    ball = Ball(WIDTH // 2, HEIGHT // 2)
    bricks = create_bricks()
    score = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Paddle Movement
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    paddle.move("LEFT")
                elif event.key == pygame.K_RIGHT:
                    paddle.move("RIGHT")
            elif event.type == pygame.KEYUP:
                # Stop accelerating when key is released
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    paddle.move("NONE")

        # --- Game Logic Update (at 60 FPS) ---
        paddle.move("NONE")  # Update paddle position based on inertia
        ball.move()
        ball.bounce(paddle)

        # Brick Collisions
        for brick in bricks:
            if ball.rect.colliderect(brick.rect):
                ball.speed_y *= -1
                bricks.remove(brick)
                score += 10
                # Brick hit sound (lower frequency)
                play_sound(generate_impact_sound(300, 0.05, 0.5))

        # Game Over Check
        if ball.rect.bottom >= HEIGHT:
            play_sound(generate_sine_wave(220, 0.5, 0.5))  # Game over sound
            return "GAME_OVER", score

        # --- Drawing ---
        screen.fill(BLACK)
        paddle.draw()
        ball.draw()
        for brick in bricks:
            brick.draw()

        # Display Score
        display_text(f"Score: {score}", WHITE, 30, 20)

        pygame.display.update()
        clock.tick(FPS)

# --- Main Loop ---
current_state = "MENU"
score = 0

while True:
    if current_state == "MENU":
        current_state = main_menu()
    elif current_state == "CREDITS":
        current_state = credits()
    elif current_state == "GAME":
        current_state, score = game()
    elif current_state == "GAME_OVER":
        current_state = game_over(score)
