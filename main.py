import pygame
import random

pygame.init()

# --- Setup ---
WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arena Gladiator")
clock = pygame.time.Clock()
font = pygame.font.SysFont("comicsans", 40)

# --- Arena Map ---
# 0 = empty floor
# 1 = wall
# 2 = enemy spawn point
arena_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

TILE_SIZE = 50
spawn_tiles = [(x, y) for y, row in enumerate(arena_map)
               for x, t in enumerate(row) if t == 2]

# --- Player Variables ---
player_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
player_speed = 5
player_size = 12
player_health = 5
player_max_health = 5

# --- Attack Variables ---
attack_radius = 40
attack_active = 0
attack_active_time = 5
attack_cooldown = 0
attack_cooldown_max = 30

# --- Enemy Variables ---
enemies = []
enemy_size = 10
enemy_speed = 3
spawn_timer = 0
spawn_delay = 60

# --- Score ---
score = 0

# --- Helper Function for Wall Collision ---
def is_wall(pos):
    x_tile = int(pos.x // TILE_SIZE)
    y_tile = int(pos.y // TILE_SIZE)
    if 0 <= y_tile < len(arena_map) and 0 <= x_tile < len(arena_map[0]):
        return arena_map[y_tile][x_tile] == 1
    return False

# --- Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Input / Movement ---
    keys = pygame.key.get_pressed()
    move = pygame.Vector2(0, 0)
    if keys[pygame.K_w]: move.y -= 1
    if keys[pygame.K_s]: move.y += 1
    if keys[pygame.K_a]: move.x -= 1
    if keys[pygame.K_d]: move.x += 1

    if move.length() > 0:
        move = move.normalize() * player_speed
        new_pos = player_pos + move
        if not is_wall(new_pos):
            player_pos = new_pos

    # --- Spawn Enemies at Spawn Tiles ---
    spawn_timer += 1
    if spawn_timer >= spawn_delay:
        spawn_timer = 0
        spawn_x, spawn_y = random.choice(spawn_tiles)
        enemies.append(pygame.Vector2(spawn_x * TILE_SIZE + TILE_SIZE // 2,
                                      spawn_y * TILE_SIZE + TILE_SIZE // 2))

    # --- Move Enemies ---
    for i, enemy in enumerate(enemies):
        direction = player_pos - enemy
        if direction.length() > 0:
            direction = direction.normalize() * enemy_speed
            new_enemy_pos = enemy + direction
            if not is_wall(new_enemy_pos):
                enemies[i] = new_enemy_pos

    # --- Enemy Collisions (Damage Player) ---
    for i in range(len(enemies) - 1, -1, -1):
        if (enemies[i] - player_pos).length() < player_size + enemy_size:
            player_health -= 1
            enemies.pop(i)

    # --- Attack System ---
    if pygame.mouse.get_pressed()[0] and attack_cooldown <= 0:
        attack_active = attack_active_time
        attack_cooldown = attack_cooldown_max

    if attack_active > 0:
        attack_active -= 1
        for i in range(len(enemies) - 1, -1, -1):
            if (enemies[i] - player_pos).length() < attack_radius + player_size:
                enemies.pop(i)
                score += 1

    if attack_cooldown > 0:
        attack_cooldown -= 1

    # --- Game Over Check ---
    if player_health <= 0:
        running = False
        break

    # --- Drawing ---
    screen.fill((20, 20, 30))

    # Draw Arena Walls
    for y, row in enumerate(arena_map):
        for x, tile in enumerate(row):
            if tile == 1:
                pygame.draw.rect(screen, (50, 50, 50),
                                 (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # Player
    pygame.draw.circle(screen, (0, 255, 0), player_pos, player_size)

    # Attack Hitbox Visual
    if attack_active > 0:
        pygame.draw.circle(screen, (0, 150, 255), player_pos, attack_radius, 2)

    # Enemies
    for enemy in enemies:
        pygame.draw.circle(screen, (255, 0, 0), enemy, enemy_size)

    # Score
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (20, 20))

    # Player Health Bar
    pygame.draw.rect(screen, (100, 0, 0), (20, 630, 100, 10))
    pygame.draw.rect(screen, (0, 255, 0), (20, 630, 100 * (player_health / player_max_health), 10))

    pygame.display.flip()
    clock.tick(60)

# --- Game Over Screen ---
game_over = True
while game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = False

    screen.fill((20, 20, 30))
    game_over_text = font.render("GAME OVER", True, (255, 0, 0))
    score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))

    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
