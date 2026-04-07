import pygame
import random
import sys
import base64
import io

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

# ── Walk 스프라이트 시트 Base64 (이동 중 애니메이션) ───────────
WALK_B64 = "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"
WALK_FRAME_W  = 96
WALK_FRAME_H  = 84
WALK_COLS     = 8
WALK_COUNT    = 8
WALK_DELAY    = 100   # ms per frame

# ── Idle 스프라이트 시트 Base64 (정지 중 애니메이션) ───────────
IDLE_B64 = "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"
IDLE_FRAME_W  = 96
IDLE_FRAME_H  = 84
IDLE_COLS     = 7
IDLE_COUNT    = 7
IDLE_DELAY    = 150   # ms per frame

# 스프라이트 표시 크기 (히트박스와 별개)
SPRITE_DISPLAY_W = 160
SPRITE_DISPLAY_H = int(WALK_FRAME_H * (SPRITE_DISPLAY_W / WALK_FRAME_W))


def load_frames(b64_str, frame_w, frame_h, cols, count):
    sheet_bytes = base64.b64decode(b64_str)
    sheet = pygame.image.load(io.BytesIO(sheet_bytes)).convert_alpha()
    frames = []
    for i in range(count):
        row, col = divmod(i, cols)
        rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
        frames.append(sheet.subsurface(rect))
    return frames


USE_WALK = bool(WALK_B64.strip())
USE_IDLE = bool(IDLE_B64.strip())
USE_SPRITE = USE_WALK or USE_IDLE

if USE_WALK:
    walk_frames = load_frames(WALK_B64, WALK_FRAME_W, WALK_FRAME_H, WALK_COLS, WALK_COUNT)
if USE_IDLE:
    idle_frames = load_frames(IDLE_B64, IDLE_FRAME_W, IDLE_FRAME_H, IDLE_COLS, IDLE_COUNT)

# ── 레벨 설정 ─────────────────────────────────────────────────
LEVELS = [
    {"min_speed": 5, "max_speed": 10, "spawn": 1,  "label": "Lv.1"},
    {"min_speed": 5, "max_speed": 8,  "spawn": 25, "label": "Lv.2"},
    {"min_speed": 7, "max_speed": 12, "spawn": 15, "label": "Lv.3"},
]

PLAYER_W, PLAYER_H = 40, 40
ENEMY_W,  ENEMY_H  = 30, 30


def spawn_enemy(level_cfg):
    y = random.randint(0, HEIGHT - ENEMY_H)
    speed = random.randint(level_cfg["min_speed"], level_cfg["max_speed"])
    return pygame.Rect(WIDTH, y, ENEMY_W, ENEMY_H), speed


def draw_hud(level_cfg, lives, max_lives=50):
    screen.blit(font.render(f"{level_cfg['label']}", True, YELLOW), (10, 40))

    bar_h = 20
    cell_w = 12
    total_w = cell_w * max_lives
    bar_x = WIDTH // 2 - total_w // 2
    bar_y = HEIGHT - 45

    for i in range(max_lives):
        rect = pygame.Rect(bar_x + i * cell_w, bar_y, cell_w - 2, bar_h)
        pygame.draw.rect(screen, RED, rect)

    for i in range(lives):
        rect = pygame.Rect(bar_x + i * cell_w, bar_y, cell_w - 2, bar_h)
        pygame.draw.rect(screen, GREEN, rect)

    label = font_small.render("내 체력:", True, GREEN)
    screen.blit(label, (bar_x - label.get_width() - 10, bar_y + 1))


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
    player = pygame.Rect(60, HEIGHT // 2 - PLAYER_H // 2, PLAYER_W, PLAYER_H)

    enemies = []
    allies = []
    parry_list = []
    lives = 50
    life_timer = 0
    spawn_timer = 0
    level_idx = 0
    level_cfg = LEVELS[level_idx]
    invincible = 0

    # 애니메이션 상태
    frame_index = 0
    frame_timer = 0
    current_anim = "idle"   # "walk" | "idle"
    facing_left = False     # 좌우 반전 여부

    while True:
        dt = clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    lives -= 5
                    if lives <= 0:
                        if game_over_screen():
                            main()
                        return
                    parry_list.append([player.centerx, player.centery, FPS // 4])

        keys = pygame.key.get_pressed()
        moving = False

        if keys[pygame.K_UP]    and player.top    > 0:      player.y -= 5; moving = True
        if keys[pygame.K_DOWN]  and player.bottom < HEIGHT:  player.y += 5; moving = True
        if keys[pygame.K_LEFT]  and player.left   > 0:
            player.x -= 5
            moving = True
            facing_left = True
        if keys[pygame.K_RIGHT] and player.right  < WIDTH:
            player.x += 5
            moving = True
            facing_left = False

        # 애니메이션 전환 (walk ↔ idle)
        new_anim = "walk" if moving else "idle"
        if new_anim != current_anim:
            current_anim = new_anim
            frame_index = 0
            frame_timer = 0

        # 프레임 업데이트
        if USE_SPRITE:
            delay = WALK_DELAY if current_anim == "walk" else IDLE_DELAY
            frame_timer += dt
            if frame_timer >= delay:
                frame_timer = 0
                if current_anim == "walk" and USE_WALK:
                    frame_index = (frame_index + 1) % WALK_COUNT
                elif current_anim == "idle" and USE_IDLE:
                    frame_index = (frame_index + 1) % IDLE_COUNT

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
            pair[0].x -= pair[1]
            if pair[0].right > 0:
                survived.append(pair)
        enemies = survived

        new_allies = []
        for ally in allies:
            ally[0].x += ally[1]
            if ally[0].left < WIDTH:
                new_allies.append(ally)
        allies = new_allies

        new_parry_list = []
        for item in parry_list:
            item[0] = player.centerx
            item[1] = player.centery
            item[2] -= 1

            for pair in enemies[:]:
                if pygame.math.Vector2(item[0] - pair[0].centerx, item[1] - pair[0].centery).length() < 50:
                    allies.append([pair[0].copy(), pair[1]])
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

        # ── 렌더링 ─────────────────────────────────────────────
        screen.fill(GRAY)

        for item in parry_list:
            pygame.draw.circle(screen, WHITE, (item[0], item[1]), 30, 1)

        for ally in allies:
            pygame.draw.rect(screen, BLUE, ally[0])

        # 플레이어 그리기 (무적 중 깜빡임)
        blink = (invincible // 10) % 2 == 0
        if blink:
            if USE_SPRITE:
                # 현재 상태에 맞는 프레임 선택 (없으면 반대 애니메이션으로 대체)
                if current_anim == "walk" and USE_WALK:
                    src = walk_frames[frame_index % WALK_COUNT]
                elif current_anim == "idle" and USE_IDLE:
                    src = idle_frames[frame_index % IDLE_COUNT]
                elif USE_WALK:
                    src = walk_frames[frame_index % WALK_COUNT]
                else:
                    src = idle_frames[frame_index % IDLE_COUNT]

                scaled = pygame.transform.scale(src, (SPRITE_DISPLAY_W, SPRITE_DISPLAY_H))
                if facing_left:
                    scaled = pygame.transform.flip(scaled, True, False)

                draw_x = player.centerx - SPRITE_DISPLAY_W // 2
                draw_y = player.centery - SPRITE_DISPLAY_H // 2
                screen.blit(scaled, (draw_x, draw_y))
            else:
                pygame.draw.rect(screen, BLUE, player)

        for pair in enemies:
            pygame.draw.rect(screen, RED, pair[0])

        draw_hud(level_cfg, lives)
        pygame.display.flip()


main()