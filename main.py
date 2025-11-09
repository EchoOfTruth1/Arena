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
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# --- Load Assets ---
arena_bg = pygame.image.load("arena.png").convert()
arena_bg = pygame.transform.scale(arena_bg, (WIDTH, HEIGHT))
menu_music = "menu.mp3"
game_music = "arena.mp3"

# --- Font ---
ui_font = pygame.font.SysFont(None, 36)
title_font = pygame.font.SysFont(None, 72)

# --- Functions ---
def play_music(file):
    pygame.mixer.music.stop()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play(-1)

def main_menu():
    play_music(menu_music)
    menu_running = True
    while menu_running:
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        # Menu buttons
        start_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 60, 300, 50)
        quit_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 20, 300, 50)

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

        if mouse_click[0]:
            if start_rect.collidepoint(mouse_pos):
                menu_running = False
            if quit_rect.collidepoint(mouse_pos):
                pygame.quit()
                sys.exit()

        pygame.display.flip()
        clock.tick(60)

def game_over_screen(final_score):
    play_music(menu_music)
    over_running = True
    font_large = pygame.font.SysFont(None, 72)
    font_small = pygame.font.SysFont(None, 36)

    while over_running:
        screen.fill(BLACK)
        # Game Over text
        text = font_large.render("GAME OVER", True, RED)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 70))

        # Final Score
        score_text = font_small.render(f"Final Score: {final_score}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))

        # Instructions
        restart_text = font_small.render("Press [R] to Restart", True, WHITE)
        quit_text = font_small.render("Press [Q] to Quit", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 40))
        screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 80))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            over_running = False
            main_game()  # Restart game
        if keys[pygame.K_q]:
            pygame.quit()
            sys.exit()

        pygame.display.flip()
        clock.tick(60)

def main_game():
    play_music(game_music)

    # --- Player Setup ---
    player = pygame.Rect(WIDTH // 2, HEIGHT - 150, 20, 20)
    player_speed = 5
    player_max_health = 3
    lives = player_max_health
    healing_potions = 0

    # --- Invincibility ---
    invincibility_timer = 0
    invincibility_duration = 30

    # --- Attack Setup ---
    attack_active = 0
    attack_radius = 50
    attack_active_time = 5
    attack_cooldown = 0
    attack_cooldown_max = 50

    # --- Spawner Setup (continuous spawn) ---
    spawners = [
        {"pos": pygame.Vector2(WIDTH*0.05, 310), "timer": 0, "cooldown": 120},
        {"pos": pygame.Vector2(WIDTH*0.5, 60), "timer": 0, "cooldown": 120},
        {"pos": pygame.Vector2(WIDTH*0.95, 310), "timer": 0, "cooldown": 120},
    ]

    upgrade_door = pygame.Rect(WIDTH//2 - 50, HEIGHT - 80, 100, 20)
    enemy_list = []
    enemy_speed = 2
    in_upgrade_room = False
    upgrade_room_activated = False
    score = 0

    running = True
    while running:
        screen.blit(arena_bg, (0,0))
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # --- Invincibility ---
        if invincibility_timer > 0:
            invincibility_timer -= 1

        if not in_upgrade_room:
            # --- Player Movement ---
            if keys[pygame.K_a]: player.x -= player_speed
            if keys[pygame.K_d]: player.x += player_speed
            if keys[pygame.K_w]: player.y -= player_speed
            if keys[pygame.K_s]: player.y += player_speed

            # --- Attack ---
            if attack_cooldown > 0: attack_cooldown -= 1
            if mouse_buttons[0] and attack_cooldown == 0:
                attack_active = attack_active_time
                attack_cooldown = attack_cooldown_max
            if attack_active > 0: attack_active -= 1

            # --- Boundaries ---
            player.x = max(0, min(WIDTH - player.width, player.x))
            player.y = max(0, min(HEIGHT - player.height, player.y))

            # --- Continuous Enemy Spawning ---
            for spawner in spawners:
                spawner["timer"] += 1
                if spawner["timer"] >= spawner["cooldown"]:
                    spawner["timer"] = 0
                    new_enemy = pygame.Rect(spawner["pos"].x, spawner["pos"].y, 40, 40)
                    if not any(new_enemy.colliderect(e) for e in enemy_list):
                        enemy_list.append(new_enemy)

            # --- Enemy Movement & Collision ---
            for i, enemy in enumerate(enemy_list):
                # Move towards player
                if player.x > enemy.x: enemy.x += enemy_speed
                if player.x < enemy.x: enemy.x -= enemy_speed
                if player.y > enemy.y: enemy.y += enemy_speed
                if player.y < enemy.y: enemy.y -= enemy_speed

                # Avoid overlapping other enemies
                for j, other in enumerate(enemy_list):
                    if i != j and enemy.colliderect(other):
                        if enemy.x < other.x: enemy.x -= 1
                        if enemy.x > other.x: enemy.x += 1
                        if enemy.y < other.y: enemy.y -= 1
                        if enemy.y > other.y: enemy.y += 1

            # --- Player Collision ---
            enemies_to_remove = []
            for enemy in enemy_list:
                if enemy.colliderect(player) and invincibility_timer == 0:
                    lives -= 1
                    invincibility_timer = invincibility_duration
                    enemies_to_remove.append(enemy)
            for enemy in enemies_to_remove:
                enemy_list.remove(enemy)

            if lives <= 0:
                game_over_screen(score)
                return

            # --- Attack Damage ---
            if attack_active > 0:
                attack_hitbox = pygame.Rect(player.centerx - attack_radius, player.centery - attack_radius, attack_radius*2, attack_radius*2)
                for enemy in enemy_list[:]:
                    if attack_hitbox.colliderect(enemy):
                        enemy_list.remove(enemy)
                        score += 10

            # --- Upgrade Room ---
            if player.colliderect(upgrade_door):
                if not upgrade_room_activated:
                    in_upgrade_room = True
                    upgrade_room_activated = True
            else:
                upgrade_room_activated = False

            # --- Healing Potions ---
            if keys[pygame.K_e] and healing_potions > 0 and lives < player_max_health:
                lives += 1
                healing_potions -= 1

        else:
            # --- Upgrade Room UI ---
            screen.fill((40,40,60))
            font = pygame.font.SysFont(None,50)
            upgrades = [
                {"name":"Max Health +1","cost":50},
                {"name":"Attack Radius +10","cost":30},
                {"name":"Speed +1","cost":40},
                {"name":"Healing Potion +1","cost":20}
            ]
            button_width, button_height, start_y, gap = 400, 60, 150, 80
            for i, upgrade in enumerate(upgrades):
                button_rect = pygame.Rect(WIDTH//2 - button_width//2, start_y + i*gap, button_width, button_height)
                color = (0,200,0) if score >= upgrade["cost"] else (100,100,100)
                if button_rect.collidepoint(mouse_pos):
                    color = (0,255,0) if score >= upgrade["cost"] else (150,150,150)
                    if mouse_buttons[0] and score >= upgrade["cost"]:
                        if i==0: player_max_health += 1
                        elif i==1: attack_radius += 10
                        elif i==2: player_speed += 1
                        elif i==3: healing_potions += 1
                        score -= upgrade["cost"]
                pygame.draw.rect(screen,color,button_rect)
                text = font.render(f"{upgrade['name']} - {upgrade['cost']} pts", True, WHITE)
                screen.blit(text,(button_rect.centerx - text.get_width()//2, button_rect.centery - text.get_height()//2))
            exit_text = font.render("Press [E] to Exit", True, WHITE)
            screen.blit(exit_text,(WIDTH//2 - exit_text.get_width()//2, HEIGHT-100))
            if keys[pygame.K_e]:
                in_upgrade_room = False

        # --- Drawing ---
        if not in_upgrade_room:
            # Background
            screen.blit(arena_bg,(0,0))
            # Player
            pygame.draw.circle(screen,(0,255,0),(player.centerx,player.centery),player.width//2)
            # Attack
            if attack_active > 0:
                pygame.draw.circle(screen,(0,150,255),(player.centerx,player.centery),attack_radius,2)
            # Enemies
            for enemy in enemy_list:
                pygame.draw.circle(screen,(255,0,0),(enemy.centerx,enemy.centery),20)
            # Score
            score_text = ui_font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text,(20,20))
            # Health bar
            pygame.draw.rect(screen,(100,0,0),(20,60,100,10))
            health_ratio = max(0,min(1,lives/player_max_health))
            pygame.draw.rect(screen,(0,255,0),(20,60,100*health_ratio,10))
            # Healing potions
            pygame.draw.circle(screen,BLUE,(WIDTH-50,HEIGHT-50),20)
            potion_text = ui_font.render(str(healing_potions),True,WHITE)
            screen.blit(potion_text,(WIDTH-50 - potion_text.get_width()//2, HEIGHT-50 - potion_text.get_height()//2))

        pygame.display.flip()
        clock.tick(60)

# --- Start Game ---
main_menu()
main_game()
pygame.quit()
