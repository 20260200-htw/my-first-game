import pygame
import random
import sys
import base64
import io
import os

pygame.init()
pygame.mixer.init()


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
ORANGE = (220, 120, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodger")
clock = pygame.time.Clock()
font_small = get_korean_font(18)
font = get_korean_font(36)
font_big = get_korean_font(72)

# ── 사운드 로드 ───────────────────────────────────────────────
def load_sound(path, volume=1.0):
    if os.path.exists(path):
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        return sound
    return None

parry_sound     = load_sound("./assets/sounds/parry.wav",       0.25)
parry_fail_sfx  = load_sound("./assets/sounds/parry_fail.wav",  1.0) #아직 없
player_hit_sfx  = load_sound("./assets/sounds/player_hit.ogg",  0.25) #아마 다른 걸로 바꿀지도
boss_hit_sfx    = load_sound("./assets/sounds/boss_hit.ogg",    0.25)
boss_attack_sfx = load_sound("./assets/sounds/boss_attack.wav", 1.0)

# ── 배경 음악 ─────────────────────────────────────────────────
BGM_VOLUME = 0.1
if os.path.exists("./assets/sounds/game_bgm.mp3"):
    pygame.mixer.music.load("./assets/sounds/game_bgm.mp3")
    pygame.mixer.music.set_volume(BGM_VOLUME)
    pygame.mixer.music.play(-1)

# ── Walk 스프라이트 시트 Base64 (이동 중 애니메이션) ───────────
WALK_B64 = "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"
WALK_FRAME_W = 96
WALK_FRAME_H = 84
WALK_COLS    = 8
WALK_COUNT   = 8
WALK_DELAY   = 100

# ── Idle 스프라이트 시트 Base64 (정지 중 애니메이션) ───────────
IDLE_B64 = "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"
IDLE_FRAME_W = 96
IDLE_FRAME_H = 84
IDLE_COLS    = 7
IDLE_COUNT   = 7
IDLE_DELAY   = 150

# ── Parry 스프라이트 시트 Base64 (패링 시 1회 재생) ───────────
PARRY_B64 = "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"
PARRY_FRAME_W = 96
PARRY_FRAME_H = 84
PARRY_COLS    = 6
PARRY_COUNT   = 6
PARRY_DELAY   = 80

# ── Boss 스프라이트 시트 Base64 (보스 애니메이션) ───────────────
BOSS_B64 = "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"
BOSS_FRAME_W = 96
BOSS_FRAME_H = 84
BOSS_COLS    = 7
BOSS_COUNT   = 7
BOSS_DELAY   = 150

# 플레이어 스프라이트 표시 크기
SPRITE_DISPLAY_W = 160
SPRITE_DISPLAY_H = int(WALK_FRAME_H * (SPRITE_DISPLAY_W / WALK_FRAME_W))

# 보스 스프라이트 표시 크기
BOSS_DISPLAY_W = 200
BOSS_DISPLAY_H = int(BOSS_FRAME_H * (BOSS_DISPLAY_W / BOSS_FRAME_W))


def load_frames(b64_str, frame_w, frame_h, cols, count):
    sheet_bytes = base64.b64decode(b64_str)
    sheet = pygame.image.load(io.BytesIO(sheet_bytes)).convert_alpha()
    frames = []
    for i in range(count):
        row, col = divmod(i, cols)
        rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
        frames.append(sheet.subsurface(rect))
    return frames


USE_WALK  = bool(WALK_B64.strip())
USE_IDLE  = bool(IDLE_B64.strip())
USE_PARRY = bool(PARRY_B64.strip())
USE_BOSS  = bool(BOSS_B64.strip())
USE_SPRITE = USE_WALK or USE_IDLE or USE_PARRY

if USE_WALK:
    walk_frames  = load_frames(WALK_B64,  WALK_FRAME_W,  WALK_FRAME_H,  WALK_COLS,  WALK_COUNT)
if USE_IDLE:
    idle_frames  = load_frames(IDLE_B64,  IDLE_FRAME_W,  IDLE_FRAME_H,  IDLE_COLS,  IDLE_COUNT)
if USE_PARRY:
    parry_frames = load_frames(PARRY_B64, PARRY_FRAME_W, PARRY_FRAME_H, PARRY_COLS, PARRY_COUNT)
if USE_BOSS:
    boss_frames  = load_frames(BOSS_B64,  BOSS_FRAME_W,  BOSS_FRAME_H,  BOSS_COLS,  BOSS_COUNT)

# ── 페이즈 설정 ───────────────────────────────────────────────
PHASES = [
    {"min_speed": 10, "max_speed": 10, "spawn": 10, "label": "Phase 1", "boss_speed": 2.5, "boss_move_interval": 60},
    {"min_speed": 15, "max_speed": 15, "spawn": 10, "label": "Phase 2", "boss_speed": 5,   "boss_move_interval": 30},
    {"min_speed": 15, "max_speed": 15, "spawn": 5,  "label": "Phase 3", "boss_speed": 15,  "boss_move_interval": 30},
]

PLAYER_W, PLAYER_H = 30, 30
ENEMY_W,  ENEMY_H  = 30, 30

# ── 보스 설정 ─────────────────────────────────────────────────
BOSS_W, BOSS_H     = 80, 80
BOSS_MAX_HP        = 1000
BOSS_HP_BAR_W      = 600
BOSS_HP_BAR_H      = 24
BOSS_COLLISION_DMG = 10

PARRY_COOLDOWN_MS  = 1000


def spawn_enemy(level_cfg, target, boss_rect):
    speed = random.randint(level_cfg["min_speed"], level_cfg["max_speed"])
    fx = float(boss_rect.centerx)
    fy = float(boss_rect.centery)
    rect = pygame.Rect(int(fx), int(fy), ENEMY_W, ENEMY_H)
    target_x = target.centerx + random.randint(-50, 50)
    target_y = target.centery + random.randint(-50, 50)
    direction = pygame.math.Vector2(target_x - fx, target_y - fy)
    if direction.length() != 0:
        direction = direction.normalize() * speed
    else:
        direction = pygame.math.Vector2(speed, 0)
    return rect, direction.x, direction.y, fx, fy


PLAYER_HP_BAR_W = 400
PLAYER_HP_BAR_H = 24
PLAYER_MAX_HP   = 50


def draw_hud(level_cfg, lives, parry_cooldown_ms, max_lives=50):
    screen.blit(font.render(f"{level_cfg['label']}", True, YELLOW), (10, 40))

    bar_x = WIDTH // 2 - PLAYER_HP_BAR_W // 2
    bar_y = HEIGHT - 52

    pygame.draw.rect(screen, RED,   (bar_x, bar_y, PLAYER_HP_BAR_W, PLAYER_HP_BAR_H))
    fill_w = int(PLAYER_HP_BAR_W * max(lives, 0) / max_lives)
    pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_w, PLAYER_HP_BAR_H))
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, PLAYER_HP_BAR_W, PLAYER_HP_BAR_H), 2)

    label = font_small.render("HP", True, GREEN)
    screen.blit(label, (bar_x - label.get_width() - 10, bar_y + 3))

    hp_text = font_small.render(f"{max(lives, 0)} / {max_lives}", True, WHITE)
    screen.blit(hp_text, (bar_x + PLAYER_HP_BAR_W + 10, bar_y + 3))


def draw_parry_cooldown(player, parry_cooldown_ms):
    cd_bar_w = 60
    cd_bar_h = 6
    cd_bar_x = player.centerx - cd_bar_w // 2
    cd_bar_y = player.top - 14
    pygame.draw.rect(screen, (80, 80, 80), (cd_bar_x, cd_bar_y, cd_bar_w, cd_bar_h))
    ratio = 1.0 - min(parry_cooldown_ms, PARRY_COOLDOWN_MS) / PARRY_COOLDOWN_MS
    pygame.draw.rect(screen, WHITE, (cd_bar_x, cd_bar_y, int(cd_bar_w * ratio), cd_bar_h))


def draw_boss_hud(boss_hp):
    bar_x = WIDTH // 2 - BOSS_HP_BAR_W // 2
    bar_y = 16

    pygame.draw.rect(screen, RED,    (bar_x, bar_y, BOSS_HP_BAR_W, BOSS_HP_BAR_H))
    fill_w = int(BOSS_HP_BAR_W * max(boss_hp, 0) / BOSS_MAX_HP)
    pygame.draw.rect(screen, ORANGE, (bar_x, bar_y, fill_w, BOSS_HP_BAR_H))
    pygame.draw.rect(screen, WHITE,  (bar_x, bar_y, BOSS_HP_BAR_W, BOSS_HP_BAR_H), 2)

    label = font_small.render("BOSS", True, ORANGE)
    screen.blit(label, (bar_x - label.get_width() - 10, bar_y + 3))

    hp_text = font_small.render(f"{max(boss_hp, 0)} / {BOSS_MAX_HP}", True, WHITE)
    screen.blit(hp_text, (bar_x + BOSS_HP_BAR_W + 10, bar_y + 3))


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


def boss_clear_screen():
    screen.fill(GRAY)
    clear_text = font_big.render("BOSS CLEARED!", True, YELLOW)
    restart_text = font.render("R: Restart   Q: Quit", True, WHITE)
    screen.blit(clear_text,   clear_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
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
    player = pygame.Rect(WIDTH - 60 - PLAYER_W, HEIGHT // 2 - PLAYER_H // 2, PLAYER_W, PLAYER_H)

    boss_rect = pygame.Rect(40, HEIGHT // 2 - BOSS_H // 2, BOSS_W, BOSS_H)
    boss_hp   = BOSS_MAX_HP
    boss_speed = PHASES[0]["boss_speed"]
    boss_vx   = random.choice([-1, 1]) * boss_speed
    boss_vy   = random.choice([-1, 1]) * boss_speed
    boss_move_timer    = 0
    boss_move_interval = PHASES[0]["boss_move_interval"]

    enemies = []
    allies  = []
    parry_list = []
    lives = 50
    life_timer = 0
    spawn_timer = 0
    phase_idx = 0
    level_cfg = PHASES[phase_idx]
    invincible = 0
    elapsed_time = 0
    parry_cooldown = 0

    # 플레이어 애니메이션 상태
    frame_index  = 0
    frame_timer  = 0
    current_anim = "idle"
    facing_left  = False
    parry_done   = False

    # 보스 애니메이션 상태
    boss_frame_index = 0
    boss_frame_timer = 0

    while True:
        dt = clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE and parry_cooldown <= 0:
                    lives -= 5
                    if lives <= 0:
                        if game_over_screen():
                            main()
                        return
                    parry_list.append([player.centerx, player.centery, FPS // 4])
                    parry_cooldown = PARRY_COOLDOWN_MS
                    current_anim = "parry"
                    frame_index  = 0
                    frame_timer  = 0
                    parry_done   = False

        keys = pygame.key.get_pressed()
        moving = False

        #플레이어 이동속도        
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

        # ── 플레이어 애니메이션 상태 전환 ────────────────────
        if current_anim == "parry":
            frame_timer += dt
            if frame_timer >= PARRY_DELAY:
                frame_timer = 0
                frame_index += 1
                if frame_index >= PARRY_COUNT:
                    parry_done   = True
                    current_anim = "walk" if moving else "idle"
                    frame_index  = 0
                    frame_timer  = 0
        else:
            new_anim = "walk" if moving else "idle"
            if new_anim != current_anim:
                current_anim = new_anim
                frame_index  = 0
                frame_timer  = 0
            delay = WALK_DELAY if current_anim == "walk" else IDLE_DELAY
            frame_timer += dt
            if frame_timer >= delay:
                frame_timer = 0
                if current_anim == "walk" and USE_WALK:
                    frame_index = (frame_index + 1) % WALK_COUNT
                elif current_anim == "idle" and USE_IDLE:
                    frame_index = (frame_index + 1) % IDLE_COUNT

        # ── 보스 애니메이션 업데이트 ─────────────────────────
        if USE_BOSS:
            boss_frame_timer += dt
            boss_delay = max(1, (level_cfg["spawn"] * 1000 // FPS) // BOSS_COUNT)
            if boss_frame_timer >= boss_delay:
                boss_frame_timer = 0
                boss_frame_index = (boss_frame_index + 1) % BOSS_COUNT

        # ── 적 스폰 ───────────────────────────────────────────
        spawn_timer += 1
        if spawn_timer >= level_cfg["spawn"]:
            spawn_timer = 0
            rect, vx, vy, fx, fy = spawn_enemy(level_cfg, player, boss_rect)
            enemies.append([rect, vx, vy, fx, fy])
            if boss_attack_sfx:
                boss_attack_sfx.play()

        # ── 시간 감소 ─────────────────────────────────────────
        life_timer += 1
        if life_timer >= FPS:
            life_timer = 0
            lives -= 1
            if lives <= 0:
                if game_over_screen():
                    main()
                return

        # ── 적 이동 ───────────────────────────────────────────
        survived = []
        for pair in enemies:
            pair[3] += pair[1]
            pair[4] += pair[2]
            pair[0].x = int(pair[3])
            pair[0].y = int(pair[4])
            if pair[0].right > 0 and pair[0].left < WIDTH and pair[0].bottom > 0 and pair[0].top < HEIGHT:
                survived.append(pair)
        enemies = survived

        # ── 반사체 이동 ───────────────────────────────────────
        new_allies = []
        for ally in allies:
            ally[3] += ally[1]
            ally[4] += ally[2]
            ally[0].x = int(ally[3])
            ally[0].y = int(ally[4])
            if ally[0].colliderect(boss_rect):
                boss_hp -= BOSS_COLLISION_DMG
                if boss_hit_sfx:
                    boss_hit_sfx.play()
                if boss_hp <= 0:
                    if boss_clear_screen():
                        main()
                    return
                continue
            if ally[0].left < WIDTH and ally[0].right > 0 and ally[0].top < HEIGHT and ally[0].bottom > 0:
                new_allies.append(ally)
        allies = new_allies

        # ── 패링 판정 ─────────────────────────────────────────
        new_parry_list = []
        for item in parry_list:
            item[0] = player.centerx
            item[1] = player.centery
            item[2] -= 1

            for pair in enemies[:]:
                if pygame.math.Vector2(item[0] - pair[0].centerx,
                                       item[1] - pair[0].centery).length() < 50:
                    to_boss = pygame.math.Vector2(boss_rect.centerx - pair[0].centerx,
                                                  boss_rect.centery - pair[0].centery)
                    if to_boss.length() != 0:
                        to_boss = to_boss.normalize() * 100
                    copied = pair[0].copy()
                    allies.append([copied, to_boss.x, to_boss.y, float(copied.x), float(copied.y)])
                    enemies.remove(pair)
                    lives = min(lives + 20, 50)
                    parry_cooldown = 0
                    if parry_sound:
                        parry_sound.play()

            if item[2] > 0:
                new_parry_list.append(item)
            else:
                # 패링 시간 만료 + 아무것도 못 맞힌 경우 → 실패
                if parry_fail_sfx:
                    parry_fail_sfx.play()
        parry_list = new_parry_list

        # ── 플레이어 피격 판정 ────────────────────────────────
        if invincible > 0:
            invincible -= 1
        else:
            for pair in enemies[:]:
                if player.colliderect(pair[0]):
                    lives -= 10
                    enemies.remove(pair)
                    invincible = FPS // 4
                    if player_hit_sfx:
                        player_hit_sfx.play()
                    if lives <= 0:
                        if game_over_screen():
                            main()
                        return
                    break

        # ── 보스 랜덤 이동 ────────────────────────────────────
        boss_move_timer += 1
        if boss_move_timer >= boss_move_interval:
            boss_move_timer = 0
            boss_vx = random.choice([-1, 0, 1]) * boss_speed
            boss_vy = random.choice([-1, 0, 1]) * boss_speed

        boss_rect.x += boss_vx
        boss_rect.y += boss_vy

        if boss_rect.left <= 0:
            boss_rect.left = 0
            boss_vx = abs(boss_vx)
        elif boss_rect.right >= WIDTH:
            boss_rect.right = WIDTH
            boss_vx = -abs(boss_vx)
        if boss_rect.top <= 0:
            boss_rect.top = 0
            boss_vy = abs(boss_vy)
        elif boss_rect.bottom >= HEIGHT:
            boss_rect.bottom = HEIGHT
            boss_vy = -abs(boss_vy)

        # ── 쿨타임 감소 ───────────────────────────────────────
        parry_cooldown = max(0, parry_cooldown - dt)

        # ── 페이즈 갱신 (보스 체력 기준) ─────────────────────
        elapsed_time += dt
        hp_ratio = boss_hp / BOSS_MAX_HP
        if hp_ratio <= 0.25:
            new_phase = 2
        elif hp_ratio <= 0.75:
            new_phase = 1
        else:
            new_phase = 0
        if new_phase != phase_idx:
            phase_idx = new_phase
            level_cfg = PHASES[phase_idx]
            boss_speed = level_cfg["boss_speed"]
            boss_move_interval = level_cfg["boss_move_interval"]

        # ── 렌더링 ────────────────────────────────────────────
        screen.fill(GRAY)

        for item in parry_list:
            pygame.draw.circle(screen, WHITE, (item[0], item[1]), 50, 1)

        for ally in allies:
            pygame.draw.rect(screen, BLUE, ally[0])

        if USE_BOSS:
            boss_src = boss_frames[boss_frame_index % BOSS_COUNT]
            boss_scaled = pygame.transform.scale(boss_src, (BOSS_DISPLAY_W, BOSS_DISPLAY_H))
            if player.centerx < boss_rect.centerx:
                boss_scaled = pygame.transform.flip(boss_scaled, True, False)
            boss_draw_x = boss_rect.centerx - BOSS_DISPLAY_W // 2
            boss_draw_y = boss_rect.centery - BOSS_DISPLAY_H // 2
            screen.blit(boss_scaled, (boss_draw_x, boss_draw_y))
        else:
            pygame.draw.rect(screen, ORANGE, boss_rect)

        if USE_SPRITE:
            if current_anim == "parry" and USE_PARRY:
                src = parry_frames[min(frame_index, PARRY_COUNT - 1)]
            elif current_anim == "walk" and USE_WALK:
                src = walk_frames[frame_index % WALK_COUNT]
            elif current_anim == "idle" and USE_IDLE:
                src = idle_frames[frame_index % IDLE_COUNT]
            elif USE_WALK:
                src = walk_frames[frame_index % WALK_COUNT]
            elif USE_IDLE:
                src = idle_frames[frame_index % IDLE_COUNT]
            else:
                src = parry_frames[min(frame_index, PARRY_COUNT - 1)]

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

        draw_hud(level_cfg, lives, parry_cooldown)
        draw_boss_hud(boss_hp)
        draw_parry_cooldown(player, parry_cooldown)
        pygame.display.flip()


main()