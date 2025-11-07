import pygame

pygame.init()

# Set up display
WIDTH, HEIGHT = 1000,650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arena Gladiator")

font = pygame.font.SysFont("comicsans", 40)

score = 0
enemies=[]

#player setup
player_pos = [WIDTH//2, HEIGHT//2]
player_speed = 5
player_size = 10

#enemy setup
enemy_size = 10
enemy_speed = 3
spawn timer = 0
spawn delay = 60 # frames

#game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #input handling
    keys = pygame.key.get_pressed()
    move = pygame.Vector2(0, 0)
    if keys[pygame.K_w]: move.y -= 1
    if keys[pygame.K_s]: move.y += 1
    if keys[pygame.K_a]: move.x -= 1
    if keys[pygame.K_d]: move.x += 1
    if move.length() > 0:
        move = move.normalize() * player_speed
        player_pos += move
        

    #spawn enemies
    spawn_timer += 1
    if spawn_timer >= spawn_delay:
        spawn_timer = 0
        enemies.append(pygame.Vector2(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
    
    #move enemies
    for i, enemy in enumenrate(enemies):
        direction = player_pos - enemy
        if direction.length() > 0:
            direction = direction.normalize() * enemy_speed
            enemies[i] += direction
    
    #attacking (left click attack)
    if pygame.mouse.get_pressed()[0]:
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        for i, enemy in enumerate(enemies):
            if (enemy - mouse_pos).length() < 20: # attack radius
                del enemies[i]
                score += 1
                
    #drawing
    screen.fill((20, 20, 30))
    pygame.draw.circle(screen, (0, 255, 0), player_pos, player_size)
    for enemy in enemies:
        pygame.draw.circle(screen, (255, 0, 0), enemy, enemy_size)
        
    #score text
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (20, 20))
    
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()
