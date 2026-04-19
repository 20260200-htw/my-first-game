import pygame
import random
import sys
import base64
import io
import os
import math

pygame.init()
pygame.mixer.init()


def get_korean_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0:
            return font
    return pygame.font.SysFont(None, size)


WIDTH,  HEIGHT  = 1920, 1080
MAP_W,  MAP_H   = WIDTH * 10, HEIGHT * 10
FPS = 165

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
BLUE   = (50,  120, 220)
RED    = (220, 50,  50)
YELLOW = (240, 200, 0)
GRAY   = (40,  40,  40)
GREEN  = (0, 255, 0)
ORANGE = (220, 120, 0)
PURPLE = (180, 50, 220)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodger")
clock = pygame.time.Clock()
font_small = get_korean_font(18)
font       = get_korean_font(36)
font_big   = get_korean_font(72)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  타일맵 스프라이트 시트 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TILESET_B64    = ""
TILE_FRAME_W   = 16
TILE_FRAME_H   = 16
TILE_COLS      = 12
TILE_COUNT     = 2
TILE_DISPLAY   = 32

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  타일셋 로드
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USE_TILESET = bool(TILESET_B64.strip())
tile_frames = []

if USE_TILESET:
    _sheet_bytes = base64.b64decode(TILESET_B64)
    _tile_sheet  = pygame.image.load(io.BytesIO(_sheet_bytes)).convert_alpha()
    for _i in range(TILE_COUNT):
        _row, _col = divmod(_i, TILE_COLS)
        _rect = pygame.Rect(_col * TILE_FRAME_W, _row * TILE_FRAME_H,
                            TILE_FRAME_W, TILE_FRAME_H)
        _raw = _tile_sheet.subsurface(_rect)
        tile_frames.append(pygame.transform.scale(_raw, (TILE_DISPLAY, TILE_DISPLAY)))

TILEMAP_COLS = math.ceil(MAP_W / TILE_DISPLAY)
TILEMAP_ROWS = math.ceil(MAP_H / TILE_DISPLAY)

def generate_tilemap():
    return [[random.randint(0, TILE_COUNT - 1)
             for _ in range(TILEMAP_COLS)]
            for _ in range(TILEMAP_ROWS)]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  사운드 Base64 (공란)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PARRY_SFX_B64   = ""
PLAYER_HIT_B64  = ""
BOSS_HIT_B64    = ""
BOSS_ATTACK_B64 = ""

def load_sound_b64(b64_str, volume=1.0):
    if not b64_str.strip():
        return None
    try:
        data  = base64.b64decode(b64_str)
        sound = pygame.mixer.Sound(io.BytesIO(data))
        sound.set_volume(volume)
        return sound
    except Exception as e:
        print(f"사운드 로드 실패: {e}")
        return None

parry_sound     = load_sound_b64(PARRY_SFX_B64,   0.25)
parry_fail_sfx  = None
player_hit_sfx  = load_sound_b64(PLAYER_HIT_B64,  0.25)
boss_hit_sfx    = load_sound_b64(BOSS_HIT_B64,    0.25)
boss_attack_sfx = load_sound_b64(BOSS_ATTACK_B64, 1.0)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BGM_VOLUME = 0.1

TITLE_BGM_PATH    = os.path.join(BASE_DIR, "assets", "sounds", "title_bgm.mp3")
GAME_BGM_PATH     = os.path.join(BASE_DIR, "assets", "sounds", "game_bgm.mp3")
GAMEOVER_BGM_PATH = os.path.join(BASE_DIR, "assets", "sounds", "gameover_bgm.mp3")


def play_bgm(path):
    if not os.path.exists(path):
        return
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(BGM_VOLUME)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"BGM 로드 실패: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  플레이어 스프라이트 Base64 (공란)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  보스 스프라이트 Base64 (공란)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  투사체 스프라이트 Base64 (공란)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 기본 투사체 (보스가 발사하는 일반 탄)
ENEMY_B64        = ""
ENEMY_FRAME_W    = 32
ENEMY_FRAME_H    = 32
ENEMY_COLS       = 4
ENEMY_COUNT      = 4
ENEMY_DELAY      = 100

# 패링 투사체 (플레이어가 튕겨낸 탄)
ALLY_B64         = ""
ALLY_FRAME_W     = 32
ALLY_FRAME_H     = 32
ALLY_COLS        = 4
ALLY_COUNT       = 4
ALLY_DELAY       = 100

# 사각 투사체 (모서리/십자에서 날아오는 대형 탄)
CORNER_BULLET_B64          = ""
CORNER_BULLET_FRAME_W      = 96
CORNER_BULLET_FRAME_H      = 96
CORNER_BULLET_COLS         = 7
CORNER_BULLET_COUNT        = 1
CORNER_BULLET_SPRITE_DELAY = 150

SPRITE_DISPLAY_W = 160
SPRITE_DISPLAY_H = int(WALK_FRAME_H * (SPRITE_DISPLAY_W / WALK_FRAME_W))

BOSS_DISPLAY_W = 200
BOSS_DISPLAY_H = int(BOSS_FRAME_H * (BOSS_DISPLAY_W / BOSS_FRAME_W))

BOSS_IDLE_SHADOW_OFFSET_Y   = 8
BOSS_ATTACK_SHADOW_OFFSET_Y = 40

# 투사체 표시 크기
ENEMY_DISPLAY_W         = 40
ENEMY_DISPLAY_H         = 40
ALLY_DISPLAY_W          = 40
ALLY_DISPLAY_H          = 40
CORNER_BULLET_DISPLAY_W = 200
CORNER_BULLET_DISPLAY_H = 175

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  게임 오버 스프라이트 Base64 (공란)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GAME_OVER_SPRITE_B64       = ""
GAME_OVER_SPRITE_FRAME_W   = 96
GAME_OVER_SPRITE_FRAME_H   = 84
GAME_OVER_SPRITE_COLS      = 12
GAME_OVER_SPRITE_COUNT     = 12
GAME_OVER_SPRITE_DELAY     = 150
GAME_OVER_SPRITE_DISPLAY_W = 200
GAME_OVER_SPRITE_DISPLAY_H = 200


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

USE_ENEMY         = bool(ENEMY_B64.strip())
USE_ALLY          = bool(ALLY_B64.strip())
USE_CORNER_BULLET = bool(CORNER_BULLET_B64.strip())
USE_GAME_OVER_SPRITE = bool(GAME_OVER_SPRITE_B64.strip())

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
if USE_ENEMY:
    enemy_frames = load_frames(ENEMY_B64, ENEMY_FRAME_W, ENEMY_FRAME_H,
                               ENEMY_COLS, ENEMY_COUNT)
if USE_ALLY:
    ally_frames  = load_frames(ALLY_B64,  ALLY_FRAME_W,  ALLY_FRAME_H,
                               ALLY_COLS,  ALLY_COUNT)
if USE_CORNER_BULLET:
    _cb_sheet_bytes = base64.b64decode(CORNER_BULLET_B64)
    _cb_sheet = pygame.image.load(io.BytesIO(_cb_sheet_bytes)).convert_alpha()
    _cb_row, _cb_col = divmod(4, CORNER_BULLET_COLS)
    _cb_rect = pygame.Rect(_cb_col * CORNER_BULLET_FRAME_W, _cb_row * CORNER_BULLET_FRAME_H,
                           CORNER_BULLET_FRAME_W, CORNER_BULLET_FRAME_H)
    corner_bullet_frames = [_cb_sheet.subsurface(_cb_rect)]
if USE_GAME_OVER_SPRITE:
    game_over_sprite_frames = load_frames(
        GAME_OVER_SPRITE_B64,
        GAME_OVER_SPRITE_FRAME_W,
        GAME_OVER_SPRITE_FRAME_H,
        GAME_OVER_SPRITE_COLS,
        GAME_OVER_SPRITE_COUNT,
    )

PHASES = [
    {"min_speed": 0.0,  "max_speed": 0.0,  "spawn": 999999, "label": "Phase 0", "boss_speed": 0.0, "boss_move_interval": 999999, "count": 0},
    {"min_speed": 0.75, "max_speed": 0.75, "spawn": 200,    "label": "Phase 1", "boss_speed": 0.5, "boss_move_interval": 2000,   "count": 1},
    {"min_speed": 0.75, "max_speed": 0.75, "spawn": 100,    "label": "Phase 2", "boss_speed": 0.5, "boss_move_interval": 2000,   "count": 1},
    {"min_speed": 1,    "max_speed": 1,    "spawn": 100,    "label": "Phase 3", "boss_speed": 0.0, "boss_move_interval": 1000,   "count": 0},
]

INTRO_DURATION_MS = 5000

PLAYER_W, PLAYER_H = 30, 30
ENEMY_W,  ENEMY_H  = 30, 30

BOSS_W, BOSS_H     = 80, 80
BOSS_MAX_HP        = 500
BOSS_HP_BAR_W      = 600
BOSS_HP_BAR_H      = 24
BOSS_COLLISION_DMG = 10

PARRY_COOLDOWN_MS  = 250

BOSS_LEASH_X = 1920
BOSS_LEASH_Y = 1080

CORNER_BULLET_SPEED        = 3
CORNER_BULLET_W            = 200
CORNER_BULLET_H            = 200
CORNER_BULLET_INTERVAL_MS  = 5000

PLAYER_HP_BAR_W  = 400
PLAYER_HP_BAR_H  = 24
PLAYER_MAX_HP    = 50
PLAYER_START_HP  = PLAYER_MAX_HP

# 모서리/십자탄 패링 범위 반지름 (판정 로직과 동일한 값)
CORNER_PARRY_RADIUS = 150

# 미리 생성해두는 반투명 노란 원 서피스 (매 프레임 생성 방지)
_CORNER_PARRY_SURF_SIZE = CORNER_PARRY_RADIUS * 2
_corner_parry_surf = pygame.Surface((_CORNER_PARRY_SURF_SIZE, _CORNER_PARRY_SURF_SIZE), pygame.SRCALPHA)
pygame.draw.circle(_corner_parry_surf, (240, 200, 0, 50),
                   (CORNER_PARRY_RADIUS, CORNER_PARRY_RADIUS), CORNER_PARRY_RADIUS, 2)


def world_to_screen(wx, wy, cam_x, cam_y):
    return wx - cam_x, wy - cam_y


def get_camera(player_rect):
    cx = player_rect.centerx - WIDTH  // 2
    cy = player_rect.centery - HEIGHT // 2
    cx = max(0, min(cx, MAP_W - WIDTH))
    cy = max(0, min(cy, MAP_H - HEIGHT))
    return cx, cy


def rect_to_screen(world_rect, cam_x, cam_y):
    return pygame.Rect(world_rect.x - cam_x, world_rect.y - cam_y,
                       world_rect.w, world_rect.h)


def draw_tilemap(map_tiles, cam_x, cam_y):
    if not USE_TILESET:
        return
    col_start = max(0, cam_x // TILE_DISPLAY)
    col_end   = min(TILEMAP_COLS, (cam_x + WIDTH)  // TILE_DISPLAY + 1)
    row_start = max(0, cam_y // TILE_DISPLAY)
    row_end   = min(TILEMAP_ROWS, (cam_y + HEIGHT) // TILE_DISPLAY + 1)
    for row in range(row_start, row_end):
        for col in range(col_start, col_end):
            tile_idx = map_tiles[row][col]
            sx = col * TILE_DISPLAY - cam_x
            sy = row * TILE_DISPLAY - cam_y
            screen.blit(tile_frames[tile_idx], (sx, sy))


def spawn_enemy(level_cfg, target, boss_rect):
    speed = level_cfg["min_speed"] + random.random() * (level_cfg["max_speed"] - level_cfg["min_speed"])
    fx = float(boss_rect.centerx)
    fy = float(boss_rect.centery) + 50
    rect = pygame.Rect(int(fx), int(fy), ENEMY_W, ENEMY_H)
    target_x = target.centerx + random.randint(-200, 200)
    target_y = target.centery + random.randint(-200, 200)
    direction = pygame.math.Vector2(target_x - fx, target_y - fy)
    if direction.length() != 0:
        direction = direction.normalize() * speed
    else:
        direction = pygame.math.Vector2(speed, 0)
    angle = -math.degrees(math.atan2(direction.y, direction.x))
    return rect, direction.x, direction.y, fx, fy, angle


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  투사체 발사: 모서리/십자 교대
#  use_cross=False → 4개 모서리
#  use_cross=True  → 상하좌우 끝 (십자)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def spawn_corner_bullets(player_rect, use_cross=False):
    if use_cross:
        origins = [
            (MAP_W // 2, 0),        # 상단 중앙
            (MAP_W // 2, MAP_H),    # 하단 중앙
            (0,          MAP_H // 2),  # 좌측 중앙
            (MAP_W,      MAP_H // 2),  # 우측 중앙
        ]
    else:
        origins = [
            (0,     0),
            (MAP_W, 0),
            (0,     MAP_H),
            (MAP_W, MAP_H),
        ]

    bullets = []
    for cx, cy in origins:
        fx, fy = float(cx), float(cy)
        direction = pygame.math.Vector2(player_rect.centerx - fx, player_rect.centery - fy)
        if direction.length() != 0:
            direction = direction.normalize() * CORNER_BULLET_SPEED
        else:
            direction = pygame.math.Vector2(CORNER_BULLET_SPEED, 0)
        rect = pygame.Rect(int(fx) - CORNER_BULLET_W // 2,
                           int(fy) - CORNER_BULLET_H // 2,
                           CORNER_BULLET_W, CORNER_BULLET_H)
        angle = -math.degrees(math.atan2(direction.y, direction.x))
        bullets.append([rect, direction.x, direction.y, fx, fy, angle])
    return bullets


def draw_hud(level_cfg, lives, parry_cooldown_ms, max_lives=PLAYER_MAX_HP):
    screen.blit(font.render(f"{level_cfg['label']}", True, YELLOW), (10, 40))
    bar_x = WIDTH // 2 - PLAYER_HP_BAR_W // 2
    bar_y = HEIGHT - 52
    pygame.draw.rect(screen, RED,   (bar_x, bar_y, PLAYER_HP_BAR_W, PLAYER_HP_BAR_H))
    fill_w = int(PLAYER_HP_BAR_W * max(lives, 0) / max_lives)
    pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_w, PLAYER_HP_BAR_H))
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, PLAYER_HP_BAR_W, PLAYER_HP_BAR_H), 2)
    label   = font_small.render("HP", True, GREEN)
    hp_text = font_small.render(f"{max(lives, 0)} / {max_lives}", True, WHITE)
    screen.blit(label,   (bar_x - label.get_width() - 10, bar_y + 3))
    screen.blit(hp_text, (bar_x + PLAYER_HP_BAR_W + 10,   bar_y + 3))


def draw_parry_cooldown(player_screen_rect, parry_cooldown_ms):
    cd_bar_w = 60
    cd_bar_h = 6
    cd_bar_x = player_screen_rect.centerx - cd_bar_w // 2
    cd_bar_y = player_screen_rect.top - 14
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
    label   = font_small.render("BOSS", True, ORANGE)
    hp_text = font_small.render(f"{max(boss_hp, 0)} / {BOSS_MAX_HP}", True, WHITE)
    screen.blit(label,   (bar_x - label.get_width() - 10, bar_y + 3))
    screen.blit(hp_text, (bar_x + BOSS_HP_BAR_W + 10,     bar_y + 3))


def draw_minimap(player, boss_rect, enemies, allies, corner_bullets, cam_x, cam_y):
    MM_W, MM_H = 160, 90
    MM_MARGIN  = 8
    mm_x = WIDTH  - MM_W - MM_MARGIN
    mm_y = MM_MARGIN
    sx = MM_W / MAP_W
    sy = MM_H / MAP_H

    mm_surf = pygame.Surface((MM_W, MM_H), pygame.SRCALPHA)
    mm_surf.fill((0, 0, 0, 140))

    vp_x = int(cam_x * sx); vp_y = int(cam_y * sy)
    vp_w = max(2, int(WIDTH * sx)); vp_h = max(2, int(HEIGHT * sy))
    pygame.draw.rect(mm_surf, (200, 200, 200, 80), (vp_x, vp_y, vp_w, vp_h))

    for pair in enemies:
        pygame.draw.circle(mm_surf, RED,    (int(pair[0].centerx * sx), int(pair[0].centery * sy)), 2)
    for ally in allies:
        pygame.draw.circle(mm_surf, BLUE,   (int(ally[0].centerx * sx), int(ally[0].centery * sy)), 2)
    for cb in corner_bullets:
        pygame.draw.circle(mm_surf, PURPLE, (int(cb[0].centerx * sx),   int(cb[0].centery * sy)),   3)

    pygame.draw.circle(mm_surf, ORANGE, (int(boss_rect.centerx * sx), int(boss_rect.centery * sy)), 4)
    pygame.draw.circle(mm_surf, GREEN,  (int(player.centerx * sx),    int(player.centery * sy)),    3)
    pygame.draw.rect(mm_surf, WHITE, (0, 0, MM_W, MM_H), 1)
    screen.blit(mm_surf, (mm_x, mm_y))


def draw_sprite_shadow(surface, sprite, display_w, display_h, screen_cx, screen_cy,
                       flip_x=False, alpha=100, squish=0.22, offset_y=8):
    shadow = pygame.transform.scale(sprite, (display_w, display_h))
    if flip_x:
        shadow = pygame.transform.flip(shadow, True, False)
    shadow = pygame.transform.flip(shadow, False, True)
    black_layer = pygame.Surface((display_w, display_h), pygame.SRCALPHA)
    black_layer.fill((0, 0, 0, 255))
    shadow.blit(black_layer, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    squished_h = max(1, int(display_h * squish))
    shadow = pygame.transform.scale(shadow, (display_w, squished_h))
    shadow.set_alpha(alpha)
    surface.blit(shadow, (screen_cx - display_w // 2, screen_cy + offset_y))


def draw_rect_shadow(surface, screen_cx, screen_cy, w, h,
                     alpha=100, squish=0.3, offset_y=4):
    ew = w; eh = max(1, int(h * squish))
    s = pygame.Surface((ew, eh), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, alpha), (0, 0, ew, eh))
    surface.blit(s, (screen_cx - ew // 2, screen_cy + offset_y))


def draw_projectile_sprite(surface, frames, frame_index, count,
                            display_w, display_h, screen_cx, screen_cy):
    src = frames[frame_index % count]
    scaled = pygame.transform.scale(src, (display_w, display_h))
    surface.blit(scaled, (screen_cx - display_w // 2, screen_cy - display_h // 2))


def draw_projectile_sprite_rotated(surface, frames, frame_index, count,
                                    display_w, display_h, screen_cx, screen_cy, angle):
    src = frames[frame_index % count]
    scaled = pygame.transform.scale(src, (display_w, display_h))
    rotated = pygame.transform.rotate(scaled, angle)
    rw, rh = rotated.get_size()
    surface.blit(rotated, (screen_cx - rw // 2, screen_cy - rh // 2))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  게임 오버 화면
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def game_over_screen():
    play_bgm(GAMEOVER_BGM_PATH)
    font_title = get_korean_font(96)
    font_menu  = get_korean_font(48)
    font_hint  = get_korean_font(24)

    RETRY_TEXT = "다시 하기"
    QUIT_TEXT  = "종료"

    retry_surf = font_menu.render(RETRY_TEXT, True, WHITE)
    quit_surf  = font_menu.render(QUIT_TEXT,  True, WHITE)
    retry_w, retry_h = retry_surf.get_size()
    quit_w,  quit_h  = quit_surf.get_size()

    # 스프라이트가 있으면 버튼을 살짝 내림
    sprite_area_h = GAME_OVER_SPRITE_DISPLAY_H + 20 if USE_GAME_OVER_SPRITE else 0
    base_y = HEIGHT // 2 - 40 + sprite_area_h // 2

    retry_rect = pygame.Rect(
        WIDTH // 2 - retry_w // 2 - 20,
        base_y,
        retry_w + 40, retry_h + 20,
    )
    quit_rect = pygame.Rect(
        WIDTH // 2 - quit_w // 2 - 20,
        base_y + 90,
        quit_w + 40, quit_h + 20,
    )

    selected = 0

    # 스프라이트 애니메이션 상태
    go_frame_index = 0
    go_frame_timer = 0.0
    last_time = pygame.time.get_ticks()

    while True:
        now = pygame.time.get_ticks()
        dt  = now - last_time
        last_time = now

        mouse_pos = pygame.mouse.get_pos()
        if retry_rect.collidepoint(mouse_pos):
            selected = 0
        elif quit_rect.collidepoint(mouse_pos):
            selected = 1

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_UP, pygame.K_DOWN):
                    selected = 1 - selected
                if e.key == pygame.K_SPACE:
                    if selected == 0:
                        return True
                    else:
                        pygame.quit(); sys.exit()
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if retry_rect.collidepoint(mouse_pos):
                    return True
                if quit_rect.collidepoint(mouse_pos):
                    pygame.quit(); sys.exit()

        # ── 스프라이트 애니메이션 업데이트 ──────────────────
        if USE_GAME_OVER_SPRITE:
            if go_frame_index < GAME_OVER_SPRITE_COUNT - 1:
                go_frame_timer += dt
                if go_frame_timer >= GAME_OVER_SPRITE_DELAY:
                    go_frame_timer = 0.0
                    go_frame_index = min(go_frame_index + 1, GAME_OVER_SPRITE_COUNT - 1)

        # ── 렌더링 ───────────────────────────────────────────
        screen.fill(GRAY)

        # GAME OVER 타이틀 (상단 중앙)
        title_surf = font_title.render("GAME OVER", True, RED)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_surf, title_rect)

        # 구분선
        pygame.draw.line(
            screen, (100, 100, 100),
            (WIDTH // 2 - 300, HEIGHT // 4 + 70),
            (WIDTH // 2 + 300, HEIGHT // 4 + 70), 2,
        )

        # 스프라이트 (있을 때만)
        if USE_GAME_OVER_SPRITE:
            src    = game_over_sprite_frames[go_frame_index]
            scaled = pygame.transform.scale(
                src, (GAME_OVER_SPRITE_DISPLAY_W, GAME_OVER_SPRITE_DISPLAY_H)
            )
            sprite_rect = scaled.get_rect(
                center=(WIDTH // 2,
                        HEIGHT // 4 + 70 + GAME_OVER_SPRITE_DISPLAY_H // 2 + 20)
            )
            screen.blit(scaled, sprite_rect)

        # 다시 하기 버튼
        is_retry_sel = (selected == 0)
        retry_color  = YELLOW if is_retry_sel else (180, 180, 180)
        if is_retry_sel:
            pygame.draw.rect(screen, (70, 70, 70), retry_rect, border_radius=8)
            pygame.draw.rect(screen, YELLOW, retry_rect, 2, border_radius=8)
        retry_render = font_menu.render(RETRY_TEXT, True, retry_color)
        screen.blit(retry_render, retry_render.get_rect(center=retry_rect.center))
        if is_retry_sel:
            cursor = font_menu.render("▶", True, YELLOW)
            screen.blit(cursor, (retry_rect.left - cursor.get_width() - 10,
                                 retry_rect.centery - cursor.get_height() // 2))

        # 종료 버튼
        is_quit_sel = (selected == 1)
        quit_color  = RED if is_quit_sel else (180, 180, 180)
        if is_quit_sel:
            pygame.draw.rect(screen, (70, 70, 70), quit_rect, border_radius=8)
            pygame.draw.rect(screen, RED, quit_rect, 2, border_radius=8)
        quit_render = font_menu.render(QUIT_TEXT, True, quit_color)
        screen.blit(quit_render, quit_render.get_rect(center=quit_rect.center))
        if is_quit_sel:
            cursor = font_menu.render("▶", True, RED)
            screen.blit(cursor, (quit_rect.left - cursor.get_width() - 10,
                                 quit_rect.centery - cursor.get_height() // 2))

        # 조작 힌트
        hint = font_hint.render("↑↓: 선택   SPACE: 확인   ESC: 종료", True, (120, 120, 120))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 40)))

        pygame.display.flip()
        clock.tick(FPS)


def boss_clear_screen(score):
    screen.fill(GRAY)
    for text, color, y in [("BOSS CLEARED!", YELLOW, HEIGHT//2-80),
                            (f"SCORE: {score}", WHITE, HEIGHT//2),
                            ("R: Restart   Q: Quit", WHITE, HEIGHT//2+60)]:
        f = font_big if "CLEARED" in text else font
        surf = f.render(text, True, color)
        screen.blit(surf, surf.get_rect(center=(WIDTH//2, y)))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return True
                if e.key == pygame.K_q: pygame.quit(); sys.exit()


def main():
    play_bgm(GAME_BGM_PATH)
    map_tiles = generate_tilemap()

    player_fx = float(MAP_W // 2 + 400)
    player_fy = float(MAP_H // 2 - PLAYER_H // 2)
    player    = pygame.Rect(int(player_fx), int(player_fy), PLAYER_W, PLAYER_H)
    PLAYER_SPEED = 0.3

    boss_rect = pygame.Rect(MAP_W // 2 - 0, MAP_H // 2 - PLAYER_H // 2 - 55, BOSS_W, BOSS_H)
    boss_fx   = float(boss_rect.x)
    boss_fy   = float(boss_rect.y)
    boss_hp   = BOSS_MAX_HP
    boss_speed = PHASES[0]["boss_speed"]
    boss_vx = boss_vy = 0.0
    boss_move_timer    = 0.0
    boss_move_interval = PHASES[0]["boss_move_interval"]

    boss_attacking  = False
    invincible      = 0.0
    INVINCIBLE_MS   = 250
    boss_invincible = 0.0
    BOSS_INVINCIBLE_MS = 250

    enemies = []; allies = []; parry_list = []
    corner_bullets = []
    corner_bullet_timer    = 0.0
    corner_bullet_use_cross = False  # False=모서리, True=십자 (교대)

    lives = PLAYER_START_HP
    life_timer = 0.0; spawn_timer = 0.0
    intro_timer = 0.0; phase_idx = 0
    level_cfg = PHASES[phase_idx]
    elapsed_time = 0.0; parry_cooldown = 0.0
    PARRY_DURATION_MS = 100
    hit_count = 0; phase3_wave = 0; phase3_rotation = 0.0

    # ── 보스 대사 ─────────────────────────────────────────
    BOSS_DIALOGUE = {
        1: "1페",
        2: "2페",
        3: "3페",
    }
    PHASE0_DIALOGUE = "패링만 하라는 뜻"
    dialogue_text  = ""
    dialogue_timer = 0.0
    font_dialogue  = get_korean_font(24)

    frame_index  = 0; frame_timer  = 0.0
    current_anim = "idle"; facing_left = True; parry_done = False

    boss_frame_index      = 0; boss_frame_timer      = 0.0
    boss_idle_frame_index = 0; boss_idle_frame_timer = 0.0

    enemy_frame_index         = 0; enemy_frame_timer         = 0.0
    ally_frame_index          = 0; ally_frame_timer          = 0.0
    corner_bullet_frame_index = 0; corner_bullet_frame_timer = 0.0

    while True:
        dt = clock.tick(FPS)
        cam_x, cam_y = get_camera(player)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                if e.key == pygame.K_SPACE and parry_cooldown <= 0:
                    lives -= 5
                    if lives <= 0:
                        if game_over_screen(): main()
                        return
                    parry_list.append([player.centerx, player.centery, float(PARRY_DURATION_MS)])
                    parry_cooldown = float(PARRY_COOLDOWN_MS)
                    current_anim = "parry"; frame_index = 0
                    frame_timer = 0.0; parry_done = False

        keys = pygame.key.get_pressed(); moving = False
        if keys[pygame.K_UP]    and player.top    > 0:      player_fy -= PLAYER_SPEED * dt; moving = True
        if keys[pygame.K_DOWN]  and player.bottom < MAP_H:  player_fy += PLAYER_SPEED * dt; moving = True
        if keys[pygame.K_LEFT]  and player.left   > 0:
            player_fx -= PLAYER_SPEED * dt; moving = True; facing_left = True
        if keys[pygame.K_RIGHT] and player.right  < MAP_W:
            player_fx += PLAYER_SPEED * dt; moving = True; facing_left = False

        player.x = int(player_fx); player.y = int(player_fy)
        if player.left   < 0:     player.left   = 0;     player_fx = float(player.x)
        if player.right  > MAP_W: player.right  = MAP_W; player_fx = float(player.x)
        if player.top    < 0:     player.top    = 0;     player_fy = float(player.y)
        if player.bottom > MAP_H: player.bottom = MAP_H; player_fy = float(player.y)

        if phase_idx == 0:
            intro_timer += dt
            if intro_timer >= INTRO_DURATION_MS:
                phase_idx = 1; level_cfg = PHASES[phase_idx]
                boss_speed = level_cfg["boss_speed"]
                boss_move_interval = level_cfg["boss_move_interval"]
                boss_vx = random.choice([-1, 1]) * boss_speed
                boss_vy = random.choice([-1, 1]) * boss_speed
                dialogue_text  = BOSS_DIALOGUE.get(1, "")
                dialogue_timer = 3000.0

        # ── 플레이어 애니메이션 ──────────────────────────────
        if current_anim == "parry":
            frame_timer += dt
            if frame_timer >= PARRY_DELAY:
                frame_timer = 0.0; frame_index += 1
                if frame_index >= PARRY_COUNT:
                    parry_done = True
                    current_anim = "walk" if moving else "idle"
                    frame_index = 0; frame_timer = 0.0
        else:
            new_anim = "walk" if moving else "idle"
            if new_anim != current_anim:
                current_anim = new_anim; frame_index = 0; frame_timer = 0.0
            delay = WALK_DELAY if current_anim == "walk" else IDLE_DELAY
            frame_timer += dt
            if frame_timer >= delay:
                frame_timer = 0.0
                if current_anim == "walk" and USE_WALK:
                    frame_index = (frame_index + 1) % WALK_COUNT
                elif current_anim == "idle" and USE_IDLE:
                    frame_index = (frame_index + 1) % IDLE_COUNT

        # ── 보스 애니메이션 ──────────────────────────────────
        if USE_BOSS:
            boss_frame_timer += dt
            boss_delay = max(1, level_cfg["spawn"] // BOSS_COUNT)
            if boss_frame_timer >= boss_delay:
                boss_frame_timer = 0.0
                boss_frame_index = (boss_frame_index + 1) % BOSS_COUNT

        if USE_BOSS_IDLE:
            boss_idle_frame_timer += dt
            if boss_idle_frame_timer >= BOSS_IDLE_DELAY:
                boss_idle_frame_timer = 0.0
                boss_idle_frame_index = (boss_idle_frame_index + 1) % BOSS_IDLE_COUNT

        # ── 투사체 애니메이션 ────────────────────────────────
        if USE_ENEMY:
            enemy_frame_timer += dt
            if enemy_frame_timer >= ENEMY_DELAY:
                enemy_frame_timer = 0.0
                enemy_frame_index = (enemy_frame_index + 1) % ENEMY_COUNT

        if USE_ALLY:
            ally_frame_timer += dt
            if ally_frame_timer >= ALLY_DELAY:
                ally_frame_timer = 0.0
                ally_frame_index = (ally_frame_index + 1) % ALLY_COUNT

        if USE_CORNER_BULLET:
            corner_bullet_frame_timer += dt
            if corner_bullet_frame_timer >= CORNER_BULLET_SPRITE_DELAY:
                corner_bullet_frame_timer = 0.0
                corner_bullet_frame_index = (corner_bullet_frame_index + 1) % CORNER_BULLET_COUNT

        # ── 스폰 ─────────────────────────────────────────────
        if phase_idx != 0:
            spawn_timer += dt
            if spawn_timer >= level_cfg["spawn"]:
                spawn_timer = 0.0
                if not boss_attacking:
                    boss_attacking = True; boss_frame_index = 0; boss_frame_timer = 0.0
                if phase_idx == 3:
                    offset_deg = phase3_rotation
                    phase3_rotation = (phase3_rotation + 5.0) % 360
                    speed = level_cfg["min_speed"]
                    for i in range(8):
                        angle_rad = math.radians(offset_deg + i * 45.0)
                        rect = pygame.Rect(int(boss_rect.centerx)-ENEMY_W//2,
                                           int(boss_rect.centery)-ENEMY_H//2 +50, ENEMY_W, ENEMY_H)
                        angle_deg = -math.degrees(angle_rad)
                        enemies.append([rect, math.cos(angle_rad)*speed, math.sin(angle_rad)*speed,
                                        float(rect.x), float(rect.y), angle_deg])
                else:
                    for _ in range(level_cfg["count"]):
                        rect, vx, vy, fx, fy, angle = spawn_enemy(level_cfg, player, boss_rect)
                        enemies.append([rect, vx, vy, fx, fy, angle])
                if boss_attack_sfx: boss_attack_sfx.play()

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        #  모서리/십자 교대 발사
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if phase_idx >= 2:
            corner_bullet_timer += dt
            if corner_bullet_timer >= CORNER_BULLET_INTERVAL_MS:
                corner_bullet_timer = 0.0
                corner_bullets.extend(spawn_corner_bullets(player, use_cross=corner_bullet_use_cross))
                corner_bullet_use_cross = not corner_bullet_use_cross

        life_timer += dt
        if life_timer >= 1000.0:
            life_timer -= 1000.0; lives -= 1
            if lives <= 0:
                if game_over_screen(): main()
                return

        survived = []
        for pair in enemies:
            pair[3] += pair[1]*dt; pair[4] += pair[2]*dt
            pair[0].x = int(pair[3]); pair[0].y = int(pair[4])
            if abs(pair[0].centerx-player.centerx)<WIDTH*2 and abs(pair[0].centery-player.centery)<HEIGHT*2:
                survived.append(pair)
        enemies = survived

        survived_cb = []
        for cb in corner_bullets:
            cb[3] += cb[1]*dt; cb[4] += cb[2]*dt
            cb[0].x = int(cb[3]); cb[0].y = int(cb[4])
            if not (abs(cb[0].centerx-player.centerx)<WIDTH*11 and abs(cb[0].centery-player.centery)<HEIGHT*11):
                continue
            if invincible <= 0 and player.colliderect(cb[0]):
                lives -= 20; hit_count += 1; invincible = float(INVINCIBLE_MS)
                if player_hit_sfx: player_hit_sfx.play()
                if lives <= 0:
                    if game_over_screen(): main()
                    return
            survived_cb.append(cb)
        corner_bullets = survived_cb

        boss_invincible = max(0.0, boss_invincible - dt)
        new_allies = []
        for ally in allies:
            ally[3] += ally[1]*dt; ally[4] += ally[2]*dt
            ally[0].x = int(ally[3]); ally[0].y = int(ally[4])
            if ally[0].colliderect(boss_rect):
                if boss_invincible <= 0:
                    boss_hp -= BOSS_COLLISION_DMG; boss_invincible = float(BOSS_INVINCIBLE_MS)
                    if boss_hit_sfx: boss_hit_sfx.play()
                    if boss_hp <= 0:
                        elapsed_sec = elapsed_time / 1000.0
                        score = max(0, 100 - hit_count*5 - max(0, int(elapsed_sec-60)))
                        if boss_clear_screen(score): main()
                        return
                continue
            if ally[0].left<MAP_W and ally[0].right>0 and ally[0].top<MAP_H and ally[0].bottom>0:
                new_allies.append(ally)
        allies = new_allies

        new_parry_list = []
        for item in parry_list:
            item[0] = player.centerx; item[1] = player.centery; item[2] -= dt
            for pair in enemies[:]:
                if pygame.math.Vector2(item[0]-pair[0].centerx, item[1]-pair[0].centery).length() < 50:
                    to_boss = pygame.math.Vector2(boss_rect.centerx-pair[0].centerx,
                                                  boss_rect.centery-pair[0].centery)
                    if to_boss.length() != 0: to_boss = to_boss.normalize() * 5.0
                    copied = pair[0].copy()
                    to_boss_angle = -math.degrees(math.atan2(to_boss.y, to_boss.x))
                    allies.append([copied, to_boss.x, to_boss.y, float(copied.x), float(copied.y), to_boss_angle])
                    enemies.remove(pair)
                    lives = min(lives + 20, PLAYER_MAX_HP)
                    parry_cooldown = 0.0
                    if parry_sound: parry_sound.play()
            for cb in corner_bullets[:]:
                if pygame.math.Vector2(item[0]-cb[0].centerx, item[1]-cb[0].centery).length() < 150:
                    enemies = [p for p in enemies if abs(p[0].centerx-player.centerx)>500 or abs(p[0].centery-player.centery)>500]
                    corner_bullets = [c for c in corner_bullets if abs(c[0].centerx-player.centerx)>500 or abs(c[0].centery-player.centery)>500]
                    lives = min(lives + 20, PLAYER_MAX_HP)
                    parry_cooldown = 0.0
                    if parry_sound: parry_sound.play()
                    break
            if item[2] > 0: new_parry_list.append(item)
            else:
                if parry_fail_sfx: parry_fail_sfx.play()
        parry_list = new_parry_list

        invincible = max(0.0, invincible - dt)
        if invincible <= 0:
            for pair in enemies[:]:
                if player.colliderect(pair[0]):
                    lives -= 10; hit_count += 1; enemies.remove(pair)
                    invincible = float(INVINCIBLE_MS)
                    if player_hit_sfx: player_hit_sfx.play()
                    if lives <= 0:
                        if game_over_screen(): main()
                        return
                    break

        if phase_idx != 0:
            boss_move_timer += dt
            to_player = pygame.math.Vector2(player.centerx-boss_rect.centerx,
                                            player.centery-boss_rect.centery)
            if abs(to_player.x) > BOSS_LEASH_X or abs(to_player.y) > BOSS_LEASH_Y:
                dir_vec = to_player.normalize()
                boss_vx = dir_vec.x * boss_speed; boss_vy = dir_vec.y * boss_speed
            elif boss_move_timer >= boss_move_interval:
                boss_move_timer = 0.0
                boss_vx = random.choice([-1,0,1]) * boss_speed
                boss_vy = random.choice([-1,0,1]) * boss_speed
            boss_fx += boss_vx*dt; boss_fy += boss_vy*dt
            boss_rect.x = int(boss_fx); boss_rect.y = int(boss_fy)
            if boss_rect.left<=0:        boss_rect.left=0;       boss_fx=float(boss_rect.x); boss_vx=abs(boss_vx)
            elif boss_rect.right>=MAP_W: boss_rect.right=MAP_W;  boss_fx=float(boss_rect.x); boss_vx=-abs(boss_vx)
            if boss_rect.top<=0:         boss_rect.top=0;        boss_fy=float(boss_rect.y); boss_vy=abs(boss_vy)
            elif boss_rect.bottom>=MAP_H:boss_rect.bottom=MAP_H; boss_fy=float(boss_rect.y); boss_vy=-abs(boss_vy)

        parry_cooldown = max(0.0, parry_cooldown - dt)
        elapsed_time  += dt

        if phase_idx != 0:
            hp_ratio = boss_hp / BOSS_MAX_HP
            new_phase = 3 if hp_ratio<=0.25 else (2 if hp_ratio<=0.75 else 1)
            if new_phase != phase_idx:
                if new_phase == 2 and phase_idx != 2: corner_bullet_timer = 0.0
                phase_idx = new_phase; level_cfg = PHASES[phase_idx]
                boss_speed = level_cfg["boss_speed"]
                boss_move_interval = level_cfg["boss_move_interval"]
                dialogue_text  = BOSS_DIALOGUE.get(new_phase, "")
                dialogue_timer = 3000.0

        if dialogue_timer > 0:
            dialogue_timer = max(0.0, dialogue_timer - dt)

        # ── 렌더링 ────────────────────────────────────────────
        screen.fill(GRAY)
        draw_tilemap(map_tiles, cam_x, cam_y)

        border_screen = pygame.Rect(-cam_x, -cam_y, MAP_W, MAP_H)
        pygame.draw.rect(screen, (80, 80, 120), border_screen, 3)

        for ally in allies:
            sr = rect_to_screen(ally[0], cam_x, cam_y)
            if USE_ALLY:
                draw_projectile_sprite_rotated(screen, ally_frames, ally_frame_index,
                                               ALLY_COUNT, ALLY_DISPLAY_W, ALLY_DISPLAY_H,
                                               sr.centerx, sr.centery, ally[5])
            else:
                pygame.draw.rect(screen, BLUE, sr)

        for cb in corner_bullets:
            sr = rect_to_screen(cb[0], cam_x, cam_y)
            if USE_CORNER_BULLET:
                src = corner_bullet_frames[corner_bullet_frame_index % CORNER_BULLET_COUNT]
                scaled = pygame.transform.scale(src, (CORNER_BULLET_DISPLAY_W, CORNER_BULLET_DISPLAY_H))
                rotated = pygame.transform.rotate(scaled, cb[5])
                rw, rh = rotated.get_size()
                screen.blit(rotated, (sr.centerx - rw // 2, sr.centery - rh // 2))
            else:
                pygame.draw.rect(screen, PURPLE, sr)

        boss_screen_rect = rect_to_screen(boss_rect, cam_x, cam_y)
        boss_facing_left = (player.centerx < boss_rect.centerx)

        if not boss_attacking and USE_BOSS_IDLE:
            boss_src = boss_idle_frames[boss_idle_frame_index % BOSS_IDLE_COUNT]
            boss_scaled_raw = pygame.transform.scale(boss_src, (BOSS_DISPLAY_W, BOSS_DISPLAY_H))
        elif USE_BOSS:
            boss_src = boss_frames[boss_frame_index % BOSS_COUNT]
            boss_scaled_raw = pygame.transform.scale(boss_src, (BOSS_DISPLAY_W, BOSS_DISPLAY_H))
        else:
            boss_src = None; boss_scaled_raw = None

        if boss_scaled_raw and boss_src:
            shadow_offset_y = (BOSS_ATTACK_SHADOW_OFFSET_Y
                               if boss_attacking
                               else BOSS_IDLE_SHADOW_OFFSET_Y)
            draw_sprite_shadow(screen, boss_src, BOSS_DISPLAY_W, BOSS_DISPLAY_H,
                               boss_screen_rect.centerx, boss_screen_rect.bottom,
                               flip_x=boss_facing_left, alpha=100, squish=0.5,
                               offset_y=shadow_offset_y)
        else:
            draw_rect_shadow(screen, boss_screen_rect.centerx, boss_screen_rect.bottom,
                             BOSS_W, BOSS_H, alpha=100, squish=0.3, offset_y=2)

        if boss_scaled_raw:
            boss_scaled = pygame.transform.flip(boss_scaled_raw, True, False) if boss_facing_left else boss_scaled_raw
            if not (boss_invincible > 0 and (int(boss_invincible/50)%2==0)):
                screen.blit(boss_scaled, (boss_screen_rect.centerx-BOSS_DISPLAY_W//2,
                                          boss_screen_rect.centery-BOSS_DISPLAY_H//2))
        else:
            if not (boss_invincible > 0 and (int(boss_invincible/50)%2==0)):
                pygame.draw.rect(screen, ORANGE, boss_screen_rect)

        player_screen_rect = rect_to_screen(player, cam_x, cam_y)

        if USE_SPRITE:
            if   current_anim == "parry" and USE_PARRY: player_src = parry_frames[min(frame_index, PARRY_COUNT-1)]
            elif current_anim == "walk"  and USE_WALK:  player_src = walk_frames[frame_index % WALK_COUNT]
            elif current_anim == "idle"  and USE_IDLE:  player_src = idle_frames[frame_index % IDLE_COUNT]
            elif USE_WALK:  player_src = walk_frames[frame_index % WALK_COUNT]
            elif USE_IDLE:  player_src = idle_frames[frame_index % IDLE_COUNT]
            else:           player_src = parry_frames[min(frame_index, PARRY_COUNT-1)]

            draw_sprite_shadow(screen, player_src, SPRITE_DISPLAY_W, SPRITE_DISPLAY_H,
                               player_screen_rect.centerx, player_screen_rect.bottom,
                               flip_x=facing_left, alpha=100, squish=0.5, offset_y=-1.5)

            scaled = pygame.transform.scale(player_src, (SPRITE_DISPLAY_W, SPRITE_DISPLAY_H))
            if facing_left: scaled = pygame.transform.flip(scaled, True, False)
            if not (invincible > 0 and (int(invincible/50)%2==0)):
                screen.blit(scaled, (player_screen_rect.centerx-SPRITE_DISPLAY_W//2,
                                     player_screen_rect.centery-SPRITE_DISPLAY_H//2))
        else:
            draw_rect_shadow(screen, player_screen_rect.centerx, player_screen_rect.bottom,
                             PLAYER_W, PLAYER_H, alpha=100, squish=0.4, offset_y=2)
            if not (invincible > 0 and (int(invincible/50)%2==0)):
                pygame.draw.rect(screen, BLUE, player_screen_rect)

        for pair in enemies:
            sr = rect_to_screen(pair[0], cam_x, cam_y)
            if USE_ENEMY:
                draw_projectile_sprite_rotated(screen, enemy_frames, enemy_frame_index,
                                               ENEMY_COUNT, ENEMY_DISPLAY_W, ENEMY_DISPLAY_H,
                                               sr.centerx, sr.centery, pair[5])
            else:
                pygame.draw.rect(screen, RED, sr)

        for item in parry_list:
            sx, sy = world_to_screen(item[0], item[1], cam_x, cam_y)
            screen.blit(_corner_parry_surf, (int(sx) - CORNER_PARRY_RADIUS, int(sy) - CORNER_PARRY_RADIUS))
            pygame.draw.circle(screen, WHITE, (int(sx), int(sy)), 50, 2)

        draw_hud(level_cfg, lives, parry_cooldown)
        draw_boss_hud(boss_hp)
        draw_parry_cooldown(player_screen_rect, parry_cooldown)
        draw_minimap(player, boss_rect, enemies, allies, corner_bullets, cam_x, cam_y)

        # ── 보스 대사 렌더링 ──────────────────────────────────
        if phase_idx == 0:
            line1 = "패링만,"
            line2 = "쓰라는 말"
            s1 = font_dialogue.render(line1, True, WHITE)
            s2 = font_dialogue.render(line2, True, WHITE)
            line_h = s1.get_height()
            gap = 4
            total_h = line_h * 2 + gap
            d_y = boss_screen_rect.top - total_h - 12
            screen.blit(s1, (boss_screen_rect.centerx - s1.get_width() // 2, d_y))
            screen.blit(s2, (boss_screen_rect.centerx - s2.get_width() // 2, d_y + line_h + gap))

        elif dialogue_timer > 0 and dialogue_text:
            alpha = 255
            if dialogue_timer < 1000.0:
                alpha = int(255 * dialogue_timer / 1000.0)
            d_surf = font_dialogue.render(dialogue_text, True, WHITE)
            d_surf.set_alpha(alpha)
            d_x = WIDTH // 2 - d_surf.get_width() // 2
            d_y = BOSS_HP_BAR_H + 16 + 10
            screen.blit(d_surf, (d_x, d_y))

        pygame.display.flip()


def title_screen():
    play_bgm(TITLE_BGM_PATH)
    font_title = get_korean_font(96)
    font_menu  = get_korean_font(48)
    font_hint  = get_korean_font(24)

    TITLE_TEXT = "용사 자격 인정받기"
    START_TEXT = "게임 시작"
    QUIT_TEXT  = "종료"

    start_surf = font_menu.render(START_TEXT, True, WHITE)
    quit_surf  = font_menu.render(QUIT_TEXT,  True, WHITE)
    start_w, start_h = start_surf.get_size()
    quit_w,  quit_h  = quit_surf.get_size()

    start_rect = pygame.Rect(WIDTH // 2 - start_w // 2 - 20,
                             HEIGHT // 2 + 20 - 10,
                             start_w + 40, start_h + 20)
    quit_rect  = pygame.Rect(WIDTH // 2 - quit_w  // 2 - 20,
                             HEIGHT // 2 + 110 - 10,
                             quit_w  + 40, quit_h  + 20)

    selected = 0

    while True:
        mouse_pos = pygame.mouse.get_pos()
        if start_rect.collidepoint(mouse_pos):
            selected = 0
        elif quit_rect.collidepoint(mouse_pos):
            selected = 1

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_UP, pygame.K_DOWN):
                    selected = 1 - selected
                if e.key == pygame.K_SPACE:
                    if selected == 0:
                        return
                    else:
                        pygame.quit(); sys.exit()
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if start_rect.collidepoint(mouse_pos):
                    return
                if quit_rect.collidepoint(mouse_pos):
                    pygame.quit(); sys.exit()

        # ── 렌더링 ──────────────────────────────────────────
        screen.fill(GRAY)

        title_surf = font_title.render(TITLE_TEXT, True, YELLOW)
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 140)))

        pygame.draw.line(screen, (100, 100, 100),
                         (WIDTH // 2 - 300, HEIGHT // 2 - 40),
                         (WIDTH // 2 + 300, HEIGHT // 2 - 40), 2)

        is_start_sel = (selected == 0)
        start_color  = YELLOW if is_start_sel else (180, 180, 180)
        if is_start_sel:
            pygame.draw.rect(screen, (70, 70, 70), start_rect, border_radius=8)
            pygame.draw.rect(screen, YELLOW, start_rect, 2, border_radius=8)
        start_render = font_menu.render(START_TEXT, True, start_color)
        screen.blit(start_render, start_render.get_rect(center=start_rect.center))

        if is_start_sel:
            cursor = font_menu.render("▶", True, YELLOW)
            screen.blit(cursor, (start_rect.left - cursor.get_width() - 10,
                                 start_rect.centery - cursor.get_height() // 2))

        is_quit_sel = (selected == 1)
        quit_color  = RED if is_quit_sel else (180, 180, 180)
        if is_quit_sel:
            pygame.draw.rect(screen, (70, 70, 70), quit_rect, border_radius=8)
            pygame.draw.rect(screen, RED, quit_rect, 2, border_radius=8)
        quit_render = font_menu.render(QUIT_TEXT, True, quit_color)
        screen.blit(quit_render, quit_render.get_rect(center=quit_rect.center))

        if is_quit_sel:
            cursor = font_menu.render("▶", True, RED)
            screen.blit(cursor, (quit_rect.left - cursor.get_width() - 10,
                                 quit_rect.centery - cursor.get_height() // 2))

        hint = font_hint.render("↑↓: 선택   SPACE: 확인   ESC: 종료", True, (120, 120, 120))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 40)))

        pygame.display.flip()
        clock.tick(FPS)


while True:
    title_screen()
    main()