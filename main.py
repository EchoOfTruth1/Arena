import pygame, random, sys

pygame.init()
pygame.mixer.init()  # Initialize the mixer for music

# Load and play background music endlessly
pygame.mixer.music.load("arena.mp3")
pygame.mixer.music.play(-1)  # -1 loops indefinitely

# --- Window Setup ---
WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arena Battle")

clock = pygame.time.Clock()

# --- Colors ---
WHITE = (255, 255, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# --- Player ---
player = pygame.Rect(WIDTH // 2, HEIGHT - 150, 20, 20)
player_speed = 5
score = 0
player_max_health = 3
lives = player_max_health
healing_potions = 0  # Track healing potions

# --- Invincibility ---
invincibility_timer = 0
invincibility_duration = 30  # frames (0.5 seconds at 60 FPS)

# --- Attack Setup ---
attack_active = 0
attack_radius = 50
attack_active_time = 5
attack_cooldown = 0
attack_cooldown_max = 30

# --- Font Setup ---
pygame.font.init()
ui_font = pygame.font.SysFont(None, 36)

import pygame, random, sys

pygame.init()
pygame.mixer.init()

# --- Window Setup ---
WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arena Battle")

clock = pygame.time.Clock()

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
BLUE = (0, 0, 255)

# --- Load Assets ---
arena_bg = pygame.image.load("arena.png").convert()
arena_bg = pygame.transform.scale(arena_bg, (WIDTH, HEIGHT))
pygame.mixer.music.load("arena.mp3")
pygame.mixer.music.play(-1)

# --- Font ---
ui_font = pygame.font.SysFont(None, 48)

# --- Main Menu ---
def main_menu():
    menu_running = True
    while menu_running:
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        # Menu options
        start_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 60, 300, 50)
        quit_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 20, 300, 50)

        # Draw buttons
        pygame.draw.rect(screen, GREEN if start_rect.collidepoint(mouse_pos) else WHITE, start_rect)
        pygame.draw.rect(screen, GREEN if quit_rect.collidepoint(mouse_pos) else WHITE, quit_rect)

        start_text = ui_font.render("Start Game", True, BLACK)
        quit_text = ui_font.render("Quit Game", True, BLACK)
        screen.blit(start_text, (start_rect.centerx - start_text.get_width()//2, start_rect.centery - start_text.get_height()//2))
        screen.blit(quit_text, (quit_rect.centerx - quit_text.get_width()//2, quit_rect.centery - quit_text.get_height()//2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Check clicks
        if mouse_click[0]:
            if start_rect.collidepoint(mouse_pos):
                menu_running = False  # Exit menu and start game
            if quit_rect.collidepoint(mouse_pos):
                pygame.quit()
                sys.exit()

        pygame.display.flip()
        clock.tick(60)

# --- Call Main Menu before starting game ---
main_menu()

# --- Spawner + Upgrade Door Positions ---
spawners = [
    pygame.Vector2(WIDTH * 0.05, 310),
    pygame.Vector2(WIDTH * 0.5, 60),
    pygame.Vector2(WIDTH * 0.95, 310),
]
upgrade_door = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 80, 100, 20)

# --- Enemies ---
enemy_list = []
enemy_speed = 2
spawn_timer = 0
wave = 1
enemies_per_wave = 3
wave_cooldown = 120
in_wave = False
wave_timer = 0

# --- Upgrade Room ---
in_upgrade_room = False
upgrade_room_activated = False  # Tracks if player entered once

# --- Load Arena Background ---
arena_bg = pygame.image.load("arena.png").convert()
arena_bg = pygame.transform.scale(arena_bg, (WIDTH, HEIGHT))

# --- Functions ---
def spawn_wave():
    global in_wave
    in_wave = True
    for _ in range(enemies_per_wave):
        spawn_point = random.choice(spawners)
        enemy = pygame.Rect(spawn_point.x, spawn_point.y, 40, 40)
        enemy_list.append(enemy)

def reset_wave():
    global in_wave, wave_timer, wave, enemies_per_wave
    wave += 1
    enemies_per_wave += 1
    wave_timer = 0
    in_wave = False

# --- Game Loop ---
running = True
while running:
    screen.blit(arena_bg, (0, 0))

    keys = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Decrease invincibility timer
    if invincibility_timer > 0:
        invincibility_timer -= 1

    if not in_upgrade_room:
        # === PLAYER MOVEMENT ===
        if keys[pygame.K_a]:
            player.x -= player_speed
        if keys[pygame.K_d]:
            player.x += player_speed
        if keys[pygame.K_w]:
            player.y -= player_speed
        if keys[pygame.K_s]:
            player.y += player_speed

        # === ATTACK INPUT ===
        if attack_cooldown > 0:
            attack_cooldown -= 1

        if mouse_buttons[0] and attack_cooldown == 0:
            attack_active = attack_active_time
            attack_cooldown = attack_cooldown_max

        # === ATTACK TIMER ===
        if attack_active > 0:
            attack_active -= 1

        # Boundaries
        player.x = max(0, min(WIDTH - player.width, player.x))
        player.y = max(0, min(HEIGHT - player.height, player.y))

        # === WAVE LOGIC ===
        if not in_wave and len(enemy_list) == 0:
            wave_timer += 1
            if wave_timer > wave_cooldown:
                spawn_wave()

        # === ENEMY MOVEMENT ===
        for enemy in enemy_list[:]:
            if player.x > enemy.x:
                enemy.x += enemy_speed
            if player.x < enemy.x:
                enemy.x -= enemy_speed
            if player.y > enemy.y:
                enemy.y += enemy_speed
            if player.y < enemy.y:
                enemy.y -= enemy_speed

        # === ENEMY COLLISION with invincibility ===
        enemies_to_remove = []
        for enemy in enemy_list:
            if enemy.colliderect(player) and invincibility_timer == 0:
                lives -= 1
                invincibility_timer = invincibility_duration
                enemies_to_remove.append(enemy)
        for enemy in enemies_to_remove:
            enemy_list.remove(enemy)

        if lives <= 0:
            running = False

        # === ATTACK DAMAGE ===
        if attack_active > 0:
            attack_hitbox = pygame.Rect(
                player.centerx - attack_radius,
                player.centery - attack_radius,
                attack_radius * 2,
                attack_radius * 2
            )
            for enemy in enemy_list[:]:
                if attack_hitbox.colliderect(enemy):
                    enemy_list.remove(enemy)
                    score += 1

        # === WAVE COMPLETE ===
        if in_wave and len(enemy_list) == 0:
            reset_wave()

        # === UPGRADE ROOM ENTRY ===
        if player.colliderect(upgrade_door):
            if not upgrade_room_activated:
                in_upgrade_room = True
                upgrade_room_activated = True
        else:
            upgrade_room_activated = False

        # === USE HEALING POTION ===
        if keys[pygame.K_e] and healing_potions > 0 and lives < player_max_health:
            lives += 1
            healing_potions -= 1

    else:
        # === UPGRADE ROOM SCREEN ===
        screen.fill((40, 40, 60))
        font = pygame.font.SysFont(None, 50)

        upgrades = [
            {"name": "Max Health +1", "cost": 50},
            {"name": "Attack Radius +10", "cost": 30},
            {"name": "Speed +1", "cost": 40},
            {"name": "Healing Potion +1", "cost": 20}
        ]

        button_width = 400
        button_height = 60
        button_y_start = 150
        button_gap = 80

        for i, upgrade in enumerate(upgrades):
            button_rect = pygame.Rect(
                WIDTH // 2 - button_width // 2,
                button_y_start + i * button_gap,
                button_width,
                button_height
            )
            color = (0, 200, 0) if score >= upgrade["cost"] else (100, 100, 100)
            if button_rect.collidepoint(mouse_pos):
                color = (0, 255, 0) if score >= upgrade["cost"] else (150, 150, 150)
                if mouse_buttons[0] and score >= upgrade["cost"]:
                    if i == 0:
                        player_max_health += 1
                    elif i == 1:
                        attack_radius += 10
                    elif i == 2:
                        player_speed += 1
                    elif i == 3:
                        healing_potions += 1
                    score -= upgrade["cost"]
            pygame.draw.rect(screen, color, button_rect)
            text = font.render(f"{upgrade['name']} - {upgrade['cost']} pts", True, WHITE)
            screen.blit(text, (button_rect.centerx - text.get_width() // 2, button_rect.centery - text.get_height() // 2))

        # Exit Upgrade Room
        exit_text = font.render("Press [E] to Exit", True, WHITE)
        screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT - 100))
        if keys[pygame.K_e]:
            in_upgrade_room = False

    # --- Drawing ---
    if not in_upgrade_room:
        # Background
        screen.blit(arena_bg, (0, 0))

        # Player
        player_pos = (player.centerx, player.centery)
        player_size = player.width // 2
        pygame.draw.circle(screen, (0, 255, 0), player_pos, player_size)

        # Attack Hitbox Visual
        if attack_active > 0:
            pygame.draw.circle(screen, (0, 150, 255), player_pos, attack_radius, 2)

        # Enemies
        enemy_draw_radius = 20
        for enemy in enemy_list:
            enemy_pos = (enemy.centerx, enemy.centery)
            pygame.draw.circle(screen, (255, 0, 0), enemy_pos, enemy_draw_radius)

        # Score
        score_text = ui_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (20, 20))

        # Health bar
        pygame.draw.rect(screen, (100, 0, 0), (20, 60, 100, 10))
        health_ratio = max(0, min(1, lives / player_max_health))
        pygame.draw.rect(screen, (0, 255, 0), (20, 60, 100 * health_ratio, 10))

        # Draw healing potion count
        potion_radius = 20
        potion_x = WIDTH - 50
        potion_y = HEIGHT - 50
        pygame.draw.circle(screen, BLUE, (potion_x, potion_y), potion_radius)
        potion_text = ui_font.render(str(healing_potions), True, WHITE)
        screen.blit(potion_text, (potion_x - potion_text.get_width() // 2, potion_y - potion_text.get_height() // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

pygame.quit()

