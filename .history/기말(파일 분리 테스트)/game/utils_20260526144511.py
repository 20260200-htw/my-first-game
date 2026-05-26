import pygame
import ctypes

# ── 해상도 목록 (16:9) ─────────────────────────────────────────────
RESOLUTIONS = [
    (1280, 720),
    (1600, 900),
    (1920, 1080),
    (2560, 1440),
]

WINDOW_MODES = ["창 모드", "전체화면"]
FRAMERATES = [30, 60, 120, 144, 165, 240]

# ── 색상 ──────────────────────────────────────────────────────────
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (180, 180, 180)
GRAY_D = (100, 100, 100)
RED    = (200,  40,  40)
GREEN  = ( 40, 180,  40)

# ── 설정 ──────────────────────────────────────────────────────────
settings = {
    "bgm_vol":    70,
    "sfx_vol":    80,
    "res_index":  0,
    "win_mode":   0,
    "fps_index":  1,
}

MON_W, MON_H = 0, 0


def draw_text(surf, text, font, color, cx, cy):
    img = font.render(text, True, color)
    surf.blit(img, img.get_rect(center=(cx, cy)))


def draw_text_left(surf, text, font, color, x, cy):
    img = font.render(text, True, color)
    surf.blit(img, img.get_rect(midleft=(x, cy)))


def draw_text_left_underline(surf, text, font, color, x, cy):
    """'텍스트' 사이 단어에 밑줄을 그어 렌더링. 밑줄 단어의 rect 리스트와 단어 리스트를 반환."""
    parts = text.split("'")
    cur_x = x
    underline_rects = []  # (rect, word)
    for i, part in enumerate(parts):
        if not part:
            continue
        img = font.render(part, True, color)
        r = img.get_rect(midleft=(cur_x, cy))
        surf.blit(img, r)
        if i % 2 == 1:
            uy = r.bottom - 1
            pygame.draw.line(surf, color, (r.left, uy), (r.right, uy), 1)
            underline_rects.append((r, part))
        cur_x = r.right
    return underline_rects


def move_window_center(W, H):
    try:
        hwnd = pygame.display.get_wm_info()["window"]
        x = (MON_W - W) // 2
        y = (MON_H - H) // 2
        ctypes.windll.user32.MoveWindow(hwnd, x, y, W, H, False)
    except Exception:
        pass


def apply_resolution():
    W, H = RESOLUTIONS[settings["res_index"]]
    W = min(W, MON_W)
    H = min(H, MON_H)
    if settings["win_mode"] == 1:
        screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
    else:
        flags = pygame.NOFRAME if (W >= MON_W or H >= MON_H) else 0
        screen = pygame.display.set_mode((W, H), flags)
        move_window_center(W, H)
    return screen, W, H