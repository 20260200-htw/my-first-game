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
FPS = 165

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

PARRY_SFX_B64   = ""
PLAYER_HIT_B64  = ""
BOSS_ATTACK_B64 = ""
BOSS_HIT_B64    = ""

def load_sound_b64(b64_str, volume=1.0):
    if not b64_str.strip():
        return None
    data = base64.b64decode(b64_str)
    sound = pygame.mixer.Sound(io.BytesIO(data))
    sound.set_volume(volume)
    return sound

parry_sound     = load_sound_b64(PARRY_SFX_B64,   0.25)
parry_fail_sfx  = None
player_hit_sfx  = load_sound_b64(PLAYER_HIT_B64,  0.25)
boss_hit_sfx    = load_sound_b64(BOSS_HIT_B64,    0.25)
boss_attack_sfx = load_sound_b64(BOSS_ATTACK_B64, 1.0)

BGM_VOLUME = 0.1
if os.path.exists("./assets/sounds/game_bgm.mp3"):
    pygame.mixer.music.load("./assets/sounds/game_bgm.mp3")
    pygame.mixer.music.set_volume(BGM_VOLUME)
    pygame.mixer.music.play(-1)

WALK_B64 = ""
WALK_FRAME_W = 96
WALK_FRAME_H = 84
WALK_COLS    = 8
WALK_COUNT   = 8
WALK_DELAY   = 100

IDLE_B64 = ""
IDLE_FRAME_W = 96
IDLE_FRAME_H = 84
IDLE_COLS    = 7
IDLE_COUNT   = 7
IDLE_DELAY   = 150

PARRY_B64 = ""
PARRY_FRAME_W = 96
PARRY_FRAME_H = 84
PARRY_COLS    = 6
PARRY_COUNT   = 6
PARRY_DELAY   = 25

BOSS_B64 = ""
BOSS_FRAME_W = 96
BOSS_FRAME_H = 84
BOSS_COLS    = 7
BOSS_COUNT   = 7
BOSS_DELAY   = 150

BOSS_IDLE_B64 = ""
BOSS_IDLE_FRAME_W = 96
BOSS_IDLE_FRAME_H = 95
BOSS_IDLE_COLS    = 10
BOSS_IDLE_COUNT   = 10
BOSS_IDLE_DELAY   = 150

SPRITE_DISPLAY_W = 160
SPRITE_DISPLAY_H = int(WALK_FRAME_H * (SPRITE_DISPLAY_W / WALK_FRAME_W))

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


USE_WALK      = bool(WALK_B64.strip())
USE_IDLE      = bool(IDLE_B64.strip())
USE_PARRY     = bool(PARRY_B64.strip())
USE_BOSS      = bool(BOSS_B64.strip())
USE_BOSS_IDLE = bool(BOSS_IDLE_B64.strip())
USE_SPRITE    = USE_WALK or USE_IDLE or USE_PARRY

if USE_WALK:
    walk_frames  = load_frames(WALK_B64,  WALK_FRAME_W,  WALK_FRAME_H,  WALK_COLS,  WALK_COUNT)
if USE_IDLE:
    idle_frames  = load_frames(IDLE_B64,  IDLE_FRAME_W,  IDLE_FRAME_H,  IDLE_COLS,  IDLE_COUNT)
if USE_PARRY:
    parry_frames = load_frames(PARRY_B64, PARRY_FRAME_W, PARRY_FRAME_H, PARRY_COLS, PARRY_COUNT)
if USE_BOSS:
    boss_frames  = load_frames(BOSS_B64,  BOSS_FRAME_W,  BOSS_FRAME_H,  BOSS_COLS,  BOSS_COUNT)
if USE_BOSS_IDLE:
    boss_idle_frames = load_frames(BOSS_IDLE_B64, BOSS_IDLE_FRAME_W, BOSS_IDLE_FRAME_H,
                                   BOSS_IDLE_COLS, BOSS_IDLE_COUNT)

PHASES = [
    {"min_speed": 0.0, "max_speed": 0.0, "spawn": 999999, "label": "Phase 0", "boss_speed": 0.0,  "boss_move_interval": 999999, "count": 0},
    {"min_speed": 0.5, "max_speed": 0.5, "spawn": 200,    "label": "Phase 1", "boss_speed": 0.15, "boss_move_interval": 1000,   "count": 1},
    {"min_speed": 0.5, "max_speed": 0.5, "spawn": 150,    "label": "Phase 2", "boss_speed": 0.3,  "boss_move_interval": 500,    "count": 3},
    {"min_speed": 1, "max_speed": 1, "spawn": 50,     "label": "Phase 3", "boss_speed": 0.0,  "boss_move_interval": 500,    "count": 1},
]

INTRO_DURATION_MS = 5000

PLAYER_W, PLAYER_H = 30, 30
ENEMY_W,  ENEMY_H  = 30, 30

BOSS_W, BOSS_H     = 80, 80
BOSS_MAX_HP        = 100
BOSS_HP_BAR_W      = 600
BOSS_HP_BAR_H      = 24
BOSS_COLLISION_DMG = 10

PARRY_COOLDOWN_MS  = 1000


def spawn_enemy(level_cfg, target, boss_rect):
    speed = level_cfg["min_speed"] + random.random() * (level_cfg["max_speed"] - level_cfg["min_speed"])
    fx = float(boss_rect.centerx)
    fy = float(boss_rect.centery)
    rect = pygame.Rect(int(fx), int(fy), ENEMY_W, ENEMY_H)
    target_x = target.centerx + random.randint(-200, 200)
    target_y = target.centery + random.randint(-200, 200)
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


def boss_clear_screen(score):
    screen.fill(GRAY)
    clear_text  = font_big.render("BOSS CLEARED!", True, YELLOW)
    score_text  = font.render(f"SCORE: {score}", True, WHITE)
    restart_text = font.render("R: Restart   Q: Quit", True, WHITE)
    screen.blit(clear_text,   clear_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))
    screen.blit(score_text,   score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    screen.blit(restart_text, restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60)))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return True
                if e.key == pygame.K_q: pygame.quit(); sys.exit()


def main():
    player_fx = float(WIDTH - 60 - PLAYER_W)
    player_fy = float(HEIGHT // 2 - PLAYER_H // 2)
    player = pygame.Rect(int(player_fx), int(player_fy), PLAYER_W, PLAYER_H)
    PLAYER_SPEED = 0.3

    boss_rect = pygame.Rect(40, HEIGHT // 2 - BOSS_H // 2, BOSS_W, BOSS_H)
    boss_fx   = float(boss_rect.x)
    boss_fy   = float(boss_rect.y)
    boss_hp   = BOSS_MAX_HP
    boss_speed = PHASES[0]["boss_speed"]
    boss_vx   = 0.0
    boss_vy   = 0.0
    boss_move_timer    = 0.0
    boss_move_interval = PHASES[0]["boss_move_interval"]

    boss_attacking  = False
    invincible      = 0.0
    INVINCIBLE_MS   = 250
    boss_invincible = 0.0
    BOSS_INVINCIBLE_MS = 250

    enemies = []
    allies  = []
    parry_list = []
    lives = 50
    life_timer    = 0.0
    spawn_timer   = 0.0
    intro_timer   = 0.0
    phase_idx = 0
    level_cfg = PHASES[phase_idx]
    elapsed_time  = 0.0
    parry_cooldown = 0.0
    PARRY_DURATION_MS = 250

    # ── 점수 관련 ─────────────────────────────────────────────
    hit_count = 0   # 보스 공격에 피격된 횟수

    frame_index  = 0
    frame_timer  = 0.0
    current_anim = "idle"
    facing_left  = False
    parry_done   = False

    boss_frame_index      = 0
    boss_frame_timer      = 0.0
    boss_idle_frame_index = 0
    boss_idle_frame_timer = 0.0

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
                    parry_list.append([player.centerx, player.centery, float(PARRY_DURATION_MS)])
                    parry_cooldown = float(PARRY_COOLDOWN_MS)
                    current_anim = "parry"
                    frame_index  = 0
                    frame_timer  = 0.0
                    parry_done   = False

        keys = pygame.key.get_pressed()
        moving = False

        if keys[pygame.K_UP]    and player.top    > 0:
            player_fy -= PLAYER_SPEED * dt; moving = True
        if keys[pygame.K_DOWN]  and player.bottom < HEIGHT:
            player_fy += PLAYER_SPEED * dt; moving = True
        if keys[pygame.K_LEFT]  and player.left   > 0:
            player_fx -= PLAYER_SPEED * dt
            moving = True
            facing_left = True
        if keys[pygame.K_RIGHT] and player.right  < WIDTH:
            player_fx += PLAYER_SPEED * dt
            moving = True
            facing_left = False

        player.x = int(player_fx)
        player.y = int(player_fy)
        if player.left < 0:        player.left = 0;        player_fx = float(player.x)
        if player.right > WIDTH:   player.right = WIDTH;   player_fx = float(player.x)
        if player.top < 0:         player.top = 0;         player_fy = float(player.y)
        if player.bottom > HEIGHT: player.bottom = HEIGHT; player_fy = float(player.y)

        # ── 인트로 페이즈 전환 ────────────────────────────────
        if phase_idx == 0:
            intro_timer += dt
            if intro_timer >= INTRO_DURATION_MS:
                phase_idx = 1
                level_cfg = PHASES[phase_idx]
                boss_speed = level_cfg["boss_speed"]
                boss_move_interval = level_cfg["boss_move_interval"]
                boss_vx = random.choice([-1, 1]) * boss_speed
                boss_vy = random.choice([-1, 1]) * boss_speed

        # ── 플레이어 애니메이션 ──────────────────────────────
        if current_anim == "parry":
            frame_timer += dt
            if frame_timer >= PARRY_DELAY:
                frame_timer = 0.0
                frame_index += 1
                if frame_index >= PARRY_COUNT:
                    parry_done   = True
                    current_anim = "walk" if moving else "idle"
                    frame_index  = 0
                    frame_timer  = 0.0
        else:
            new_anim = "walk" if moving else "idle"
            if new_anim != current_anim:
                current_anim = new_anim
                frame_index  = 0
                frame_timer  = 0.0
            delay = WALK_DELAY if current_anim == "walk" else IDLE_DELAY
            frame_timer += dt
            if frame_timer >= delay:
                frame_timer = 0.0
                if current_anim == "walk" and USE_WALK:
                    frame_index = (frame_index + 1) % WALK_COUNT
                elif current_anim == "idle" and USE_IDLE:
                    frame_index = (frame_index + 1) % IDLE_COUNT

        # ── 보스 attack 애니메이션 ───────────────────────────
        if USE_BOSS:
            boss_frame_timer += dt
            boss_delay = max(1, level_cfg["spawn"] // BOSS_COUNT)
            if boss_frame_timer >= boss_delay:
                boss_frame_timer = 0.0
                boss_frame_index = (boss_frame_index + 1) % BOSS_COUNT

        # ── 보스 idle 애니메이션 ─────────────────────────────
        if USE_BOSS_IDLE:
            boss_idle_frame_timer += dt
            if boss_idle_frame_timer >= BOSS_IDLE_DELAY:
                boss_idle_frame_timer = 0.0
                boss_idle_frame_index = (boss_idle_frame_index + 1) % BOSS_IDLE_COUNT

        # ── 적 스폰 ───────────────────────────────────────────
        if phase_idx != 0:
            spawn_timer += dt
            if spawn_timer >= level_cfg["spawn"]:
                spawn_timer = 0.0
                if not boss_attacking:
                    boss_attacking = True
                    boss_frame_index = 0
                    boss_frame_timer = 0.0
                for _ in range(level_cfg["count"]):
                    rect, vx, vy, fx, fy = spawn_enemy(level_cfg, player, boss_rect)
                    enemies.append([rect, vx, vy, fx, fy])
                if boss_attack_sfx:
                    boss_attack_sfx.play()

        # ── 체력 시간 감소 (1초마다) ─────────────────────────
        life_timer += dt
        if life_timer >= 1000.0:
            life_timer -= 1000.0
            lives -= 1
            if lives <= 0:
                if game_over_screen():
                    main()
                return

        # ── 적 이동 ───────────────────────────────────────────
        survived = []
        for pair in enemies:
            pair[3] += pair[1] * dt
            pair[4] += pair[2] * dt
            pair[0].x = int(pair[3])
            pair[0].y = int(pair[4])
            if pair[0].right > 0 and pair[0].left < WIDTH and pair[0].bottom > 0 and pair[0].top < HEIGHT:
                survived.append(pair)
        enemies = survived

        # ── 반사체 이동 및 보스 피격 판정 ────────────────────
        boss_invincible = max(0.0, boss_invincible - dt)
        new_allies = []
        for ally in allies:
            ally[3] += ally[1] * dt
            ally[4] += ally[2] * dt
            ally[0].x = int(ally[3])
            ally[0].y = int(ally[4])
            if ally[0].colliderect(boss_rect):
                if boss_invincible <= 0:
                    boss_hp -= BOSS_COLLISION_DMG
                    boss_invincible = float(BOSS_INVINCIBLE_MS)
                    if boss_hit_sfx:
                        boss_hit_sfx.play()
                    if boss_hp <= 0:
                        # ── 점수 계산 ─────────────────────────
                        elapsed_sec = elapsed_time / 1000.0
                        raw_score = 100 - (hit_count * 5) - max(0, int(elapsed_sec - 60))
                        score = max(0, raw_score)
                        if boss_clear_screen(score):
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
            item[2] -= dt
            for pair in enemies[:]:
                if pygame.math.Vector2(item[0] - pair[0].centerx,
                                       item[1] - pair[0].centery).length() < 50:
                    to_boss = pygame.math.Vector2(boss_rect.centerx - pair[0].centerx,
                                                  boss_rect.centery - pair[0].centery)
                    if to_boss.length() != 0:
                        to_boss = to_boss.normalize() * 2.0
                    copied = pair[0].copy()
                    allies.append([copied, to_boss.x, to_boss.y, float(copied.x), float(copied.y)])
                    enemies.remove(pair)
                    lives = min(lives + 20, 50)
                    parry_cooldown = 0.0
                    if parry_sound:
                        parry_sound.play()
            if item[2] > 0:
                new_parry_list.append(item)
            else:
                if parry_fail_sfx:
                    parry_fail_sfx.play()
        parry_list = new_parry_list

        # ── 플레이어 피격 판정 ────────────────────────────────
        invincible = max(0.0, invincible - dt)
        if invincible <= 0:
            for pair in enemies[:]:
                if player.colliderect(pair[0]):
                    lives -= 10
                    hit_count += 1          # ← 피격 횟수 누적
                    enemies.remove(pair)
                    invincible = float(INVINCIBLE_MS)
                    if player_hit_sfx:
                        player_hit_sfx.play()
                    if lives <= 0:
                        if game_over_screen():
                            main()
                        return
                    break

        # ── 보스 랜덤 이동 ────────────────────────────────────
        if phase_idx != 0:
            boss_move_timer += dt
            if boss_move_timer >= boss_move_interval:
                boss_move_timer = 0.0
                boss_vx = random.choice([-1, 0, 1]) * boss_speed
                boss_vy = random.choice([-1, 0, 1]) * boss_speed

            boss_fx += boss_vx * dt
            boss_fy += boss_vy * dt
            boss_rect.x = int(boss_fx)
            boss_rect.y = int(boss_fy)

            if boss_rect.left <= 0:
                boss_rect.left = 0;  boss_fx = float(boss_rect.x); boss_vx = abs(boss_vx)
            elif boss_rect.right >= WIDTH:
                boss_rect.right = WIDTH; boss_fx = float(boss_rect.x); boss_vx = -abs(boss_vx)
            if boss_rect.top <= 0:
                boss_rect.top = 0;   boss_fy = float(boss_rect.y); boss_vy = abs(boss_vy)
            elif boss_rect.bottom >= HEIGHT:
                boss_rect.bottom = HEIGHT; boss_fy = float(boss_rect.y); boss_vy = -abs(boss_vy)

        # ── 쿨타임 / 페이즈 갱신 ─────────────────────────────
        parry_cooldown = max(0.0, parry_cooldown - dt)
        elapsed_time += dt

        if phase_idx != 0:
            hp_ratio = boss_hp / BOSS_MAX_HP
            if hp_ratio <= 0.25:
                new_phase = 3
            elif hp_ratio <= 0.75:
                new_phase = 2
            else:
                new_phase = 1
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

        if not boss_attacking and USE_BOSS_IDLE:
            boss_src = boss_idle_frames[boss_idle_frame_index % BOSS_IDLE_COUNT]
            boss_scaled = pygame.transform.scale(boss_src, (BOSS_DISPLAY_W, BOSS_DISPLAY_H))
        elif USE_BOSS:
            boss_src = boss_frames[boss_frame_index % BOSS_COUNT]
            boss_scaled = pygame.transform.scale(boss_src, (BOSS_DISPLAY_W, BOSS_DISPLAY_H))
        else:
            boss_scaled = None

        if boss_scaled:
            if player.centerx < boss_rect.centerx:
                boss_scaled = pygame.transform.flip(boss_scaled, True, False)
            if boss_invincible > 0 and (int(boss_invincible / 50) % 2 == 0):
                pass
            else:
                boss_draw_x = boss_rect.centerx - BOSS_DISPLAY_W // 2
                boss_draw_y = boss_rect.centery - BOSS_DISPLAY_H // 2
                screen.blit(boss_scaled, (boss_draw_x, boss_draw_y))
        else:
            if not (boss_invincible > 0 and (int(boss_invincible / 50) % 2 == 0)):
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
            if not (invincible > 0 and (int(invincible / 50) % 2 == 0)):
                draw_x = player.centerx - SPRITE_DISPLAY_W // 2
                draw_y = player.centery - SPRITE_DISPLAY_H // 2
                screen.blit(scaled, (draw_x, draw_y))
        else:
            if not (invincible > 0 and (int(invincible / 50) % 2 == 0)):
                pygame.draw.rect(screen, BLUE, player)

        for pair in enemies:
            pygame.draw.rect(screen, RED, pair[0])

        draw_hud(level_cfg, lives, parry_cooldown)
        draw_boss_hud(boss_hp)
        draw_parry_cooldown(player, parry_cooldown)
        pygame.display.flip()


main()