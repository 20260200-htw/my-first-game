import pygame
import random
import sys

pygame.init()


def get_korean_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0:
            return font
    return pygame.font.SysFont(None, size)


WIDTH, HEIGHT = 1280, 720
FPS = 60

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
BLUE   = (50,  120, 220)
RED    = (220, 50,  50)
YELLOW = (240, 200, 0)
GRAY   = (40,  40,  40)
GREEN  = (0, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodger")
clock = pygame.time.Clock()
font_small = get_korean_font(18)
font = get_korean_font(36)
font_big = get_korean_font(72)

LEVELS = [
    {"min_speed": 5, "max_speed": 10, "spawn": 1,  "label": "Lv.1"},
    {"min_speed": 5, "max_speed": 8,  "spawn": 25, "label": "Lv.2"},
    {"min_speed": 7, "max_speed": 12, "spawn": 15, "label": "Lv.3"},
]

PLAYER_W, PLAYER_H = 40, 40
ENEMY_W,  ENEMY_H  = 30, 30

def spawn_enemy(level_cfg):
    x = random.randint(0, WIDTH - ENEMY_W)
    speed = random.randint(level_cfg["min_speed"], level_cfg["max_speed"])
    return pygame.Rect(x, -ENEMY_H, ENEMY_W, ENEMY_H), speed

def draw_hud(level_cfg, lives, max_lives=50):
    screen.blit(font.render(f"{level_cfg['label']}", True, YELLOW), (10, 40))

    bar_w = 30
    bar_h = 12
    bar_x = WIDTH - bar_w - 10
    max_bar_y_start = HEIGHT - bar_h * max_lives - 60
    bar_y_start = HEIGHT - bar_h * lives - 60

    for i in range(max_lives):
        rect = pygame.Rect(bar_x, max_bar_y_start + i * bar_h, bar_w, bar_h)
        pygame.draw.rect(screen, RED, rect)

    for i in range(lives):
        rect = pygame.Rect(bar_x, bar_y_start + i * bar_h, bar_w, bar_h)
        pygame.draw.rect(screen, GREEN, rect)

    screen.blit(font_small.render("내 체력:", True, GREEN), (bar_x - 80, HEIGHT - 80))

def game_over_screen():
    screen.fill(GRAY)

    go_text = font_big.render("GAME OVER", True, RED)
    restart_text = font.render("R: Restart   Q: Quit", True, WHITE)

    screen.blit(go_text,      go_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
    screen.blit(restart_text, restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))

    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return True
                if e.key == pygame.K_q: pygame.quit(); sys.exit()

def main():
    player = pygame.Rect(WIDTH // 2 - PLAYER_W // 2, HEIGHT - 60, PLAYER_W, PLAYER_H)
    enemies = []
    allies = []  # [rect, speed]
    parry_list = []  # [x, y, timer]
    lives = 50
    life_timer = 0
    spawn_timer = 0
    level_idx = 0
    level_cfg = LEVELS[level_idx]
    invincible = 0

    while True:
        clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    lives -= 5
                    parry_list.append([player.centerx, player.centery, FPS // 4])

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]  and player.left  > 0:      player.x -= 5
        if keys[pygame.K_RIGHT] and player.right < WIDTH:   player.x += 5

        spawn_timer += 1
        if spawn_timer >= level_cfg["spawn"]:
            spawn_timer = 0
            rect, speed = spawn_enemy(level_cfg)
            enemies.append([rect, speed])

        life_timer += 1
        if life_timer >= FPS:
            life_timer = 0
            lives -= 1
            if lives <= 0:
                if game_over_screen():
                    main()
                return

        survived = []
        for pair in enemies:
            pair[0].y += pair[1]
            if pair[0].top < HEIGHT:
                survived.append(pair)
        enemies = survived

        # 아군 이동
        new_allies = []
        for ally in allies:
            ally[0].y -= ally[1]
            if ally[0].bottom > 0:
                new_allies.append(ally)
        allies = new_allies

        new_parry_list = []
        for item in parry_list:
            item[0] = player.centerx
            item[1] = player.centery
            item[2] -= 1

            for pair in enemies[:]:
                if pygame.math.Vector2(item[0] - pair[0].centerx, item[1] - pair[0].centery).length() < 50:
                    allies.append([pair[0].copy(), pair[1]])  # 아군으로 전환
                    enemies.remove(pair)
                    lives = min(lives + 20, 50)

            if item[2] > 0:
                new_parry_list.append(item)
        parry_list = new_parry_list

        if invincible > 0:
            invincible -= 1
        else:
            for pair in enemies:
                if player.colliderect(pair[0]):
                    lives -= 10
                    invincible = 90
                    if lives <= 0:
                        if game_over_screen():
                            main()
                        return
                    break

        level_idx = min(len(enemies) // 20, len(LEVELS) - 1)
        level_cfg = LEVELS[level_idx]

        screen.fill(GRAY)

        for item in parry_list:
            pygame.draw.circle(screen, WHITE, (item[0], item[1]), 30, 1)

        for ally in allies:
            pygame.draw.rect(screen, BLUE, ally[0])

        blink = (invincible // 10) % 2 == 0
        if blink:
            pygame.draw.rect(screen, BLUE, player)

        for pair in enemies:
            pygame.draw.rect(screen, RED, pair[0])

        draw_hud(level_cfg, lives)
        pygame.display.flip()

main()