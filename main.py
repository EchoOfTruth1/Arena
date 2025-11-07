import pygame
import random

pygame.init()

# Set up display and clock
clock = pygame.time.Clock()
WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arena Gladiator")

font = pygame.font.SysFont("comicsans", 40)

# Variables
score = 0
enemies = []

# Player setup
player_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
player_speed = 5
player_size = 10
attack_radius = 40
attack_cooldown = 0
attack_cooldown_max = 30  # frames
attack_active_time = 5  # frames
attack_active = 0

# Enemy setup
enemy_size = 10
enemy_speed = 3
spawn_timer = 0
spawn_delay = 60  # frames

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # === INPUT HANDLING ===
    keys = pygame.key.get_pressed()
    move = pygame.Vector2(0, 0)
    if keys[pygame.K_w]: move.y -= 1
    if keys[pygame.K_s]: move.y += 1
    if keys[pygame.K_a]: move.x -= 1
    if keys[pygame.K_d]: move.x += 1
    if move.length() > 0:
        move = move.normalize() * player_speed
        player_pos += move

    # === SPAWN ENEMIES ===
    spawn_timer += 1
    if spawn_timer >= spawn_delay:
        spawn_timer = 0
        enemies.append(pygame.Vector2(random.randint(0, WIDTH), random.randint(0, HEIGHT)))

    # === MOVE ENEMIES ===
    for i, enemy in enumerate(enemies):
        direction = player_pos - enemy
        if direction.length() > 0:
            direction = direction.normalize() * enemy_speed
            enemies[i] += direction

    # === ATTACK SYSTEM ===
    if pygame.mouse.get_pressed()[0] and attack_cooldown <= 0:
        attack_active = attack_active_time
        attack_cooldown = attack_cooldown_max  # reset cooldown

    if attack_active > 0:
        attack_active -= 1
        for i in range(len(enemies) - 1, -1, -1):  # iterate backward to safely delete
            if (enemies[i] - player_pos).length() < attack_radius + player_size:
                del enemies[i]
                score += 1

    if attack_cooldown > 0:
        attack_cooldown -= 1

    # === DRAWING ===
    screen.fill((20, 20, 30))
    pygame.draw.circle(screen, (0, 255, 0), player_pos, player_size)

    # draw attack circle when active
    if attack_active > 0:
        pygame.draw.circle(screen, (0, 150, 255), player_pos, attack_radius, 2)

    for enemy in enemies:
        pygame.draw.circle(screen, (255, 0, 0), enemy, enemy_size)

    # score text
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (20, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
