import sys as _sys

def resource_path(rel):
    """PyInstaller exe 또는 일반 실행 모두에서 올바른 리소스 경로 반환."""
    if getattr(_sys, "frozen", False):
        base = _sys._MEIPASS
    else:
        base = _sys.path[0]   # main.py 기준 실행 디렉토리
    import os as _os
    return _os.path.join(base, rel)

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


# ── 버튼/UI 효과음 (종류별) ───────────────────────────────────────
# 버튼 종류마다 다른 소리를 쓸 수 있다. 호출: play_click("confirm") 등.
# 종류 → 파일 매핑은 아래 한 곳(SFX_FILES)에서만 관리하면 된다.
#   - 파일이 없으면 _FALLBACK("click")로 대체 재생한다.
#   - 같은 파일을 여러 종류가 공유해도 된다(파일은 한 번만 로드/캐시).
import os as _os

_SFX_DIR = _os.path.join("assets", "ui")
SFX_FILES = {
    "click":   "click.wav",    # 기본 (일반 버튼/항목 선택)
    "confirm": "confirm.wav",  # 확인/시작/구매완료 등 긍정 확정
    "cancel":  "cancel.wav",   # 취소/뒤로
    "buy":     "buy.wav",      # 구매/획득
}
_FALLBACK = "click"            # 해당 종류 파일이 없을 때 대체할 종류

_sfx_cache   = {}              # 파일명 → pygame.mixer.Sound (또는 None)

def _load_sfx(kind):
    """종류에 맞는 Sound 를 로드(캐시). 없으면 _FALLBACK 으로 대체, 그것도 없으면 None."""
    fname = SFX_FILES.get(kind) or SFX_FILES.get(_FALLBACK)
    if fname in _sfx_cache:
        snd = _sfx_cache[fname]
        if snd is not None:
            return snd
        # 이 파일이 없었음 → 대체 종류 시도
        fb = SFX_FILES.get(_FALLBACK)
        return _sfx_cache.get(fb) if fb else None
    path = _os.path.join(_SFX_DIR, fname)
    snd = None
    try:
        if _os.path.exists(path):
            snd = pygame.mixer.Sound(path)
    except Exception:
        snd = None
    _sfx_cache[fname] = snd
    if snd is None and kind != _FALLBACK:
        return _load_sfx(_FALLBACK)
    return snd

def play_click(kind="click"):
    """버튼/UI 클릭 효과음 1회 재생. kind 로 소리 종류를 고른다.
    종류: 'click'(기본) / 'confirm'(확인) / 'cancel'(취소) / 'buy'(구매).
    믹서가 없거나 파일이 없으면 조용히 무시(또는 기본음으로 대체)한다."""
    try:
        if not pygame.mixer.get_init():
            return
        snd = _load_sfx(kind)
        if snd is None:
            return
        vol = max(0.0, min(1.0, settings.get("sfx_vol", 80) / 100.0))
        snd.set_volume(vol)
        ch = pygame.mixer.find_channel(True)
        if ch:
            ch.play(snd)
        else:
            snd.play()
    except Exception:
        pass


# ── 화면별 배경음악(BGM) ──────────────────────────────────────────
# 화면 키 → BGM 파일 매핑 (한 곳에서만 관리).
#   - 값이 None 이면 "그 화면에서는 BGM 을 끈다".
#   - 키가 매핑에 없으면 "현재 재생 중인 BGM 을 그대로 둔다"(건드리지 않음).
#     → 전투('battle')는 자체적으로 음악을 제어하므로 여기 넣지 않는다.
#   - 같은 트랙이 이미 재생 중이면 다시 로드하지 않는다(끊김 방지).
SCREEN_BGM = {
    "title":         _os.path.join("assets", "bgm", "title.wav"),          # 메인 타이틀
    "map":           _os.path.join("assets", "bgm", "map.wav"),            # 구역(노드 선택지)
    "region_select": _os.path.join("assets", "bgm", "region_select.wav"), # 구역 선택
}

_current_bgm = None     # 현재 재생 중인 BGM 파일 경로 (None=없음)

def update_bgm(screen_key, region=None):
    """현재 화면에 맞는 BGM 으로 전환한다. 매 프레임 호출해도 안전하다.
    - 매핑에 없는 화면 키는 무시(현재 BGM 유지) → 전투 등 자체 제어 화면 보호.
    - 같은 곡이면 재로드하지 않는다.
    - screen_key == "map" 이고 region 이 주어지면, 구역별 OST(REGION_BGM)를
      먼저 시도하고 없으면 공통 map 트랙으로 폴백한다."""
    global _current_bgm
    if screen_key not in SCREEN_BGM:
        return
    target = SCREEN_BGM[screen_key]
    if screen_key == "map" and region is not None:
        from data import run_data
        region_track = run_data.region_bgm_path(region)
        if region_track is not None:
            target = region_track
    if target == _current_bgm:
        # 같은 곡: 음량만 설정 반영
        try:
            if target is not None and pygame.mixer.get_init():
                pygame.mixer.music.set_volume(settings.get("bgm_vol", 70) / 100.0)
        except Exception:
            pass
        return
    try:
        if not pygame.mixer.get_init():
            return
        if target is None:
            pygame.mixer.music.stop()
            _current_bgm = None
            return
        if not _os.path.exists(target):
            # 파일이 없으면 조용히 무시(곡 전환만 기록해 반복 시도 방지)
            _current_bgm = target
            return
        pygame.mixer.music.load(target)
        pygame.mixer.music.set_volume(settings.get("bgm_vol", 70) / 100.0)
        pygame.mixer.music.play(-1)
        _current_bgm = target
    except Exception:
        pass

def reset_bgm_state():
    """전투 등 외부에서 음악을 직접 제어한 뒤, BGM 상태를 '미지정'으로 되돌린다.
    이렇게 하면 다음 화면 진입 때 update_bgm 이 곡을 다시 깔아준다."""
    global _current_bgm
    _current_bgm = None


def _render_outlined(font, text, color, outline_color, outline_w):
    """글자에 외곽선을 두른 Surface 반환."""
    base = font.render(text, True, color)
    if outline_w <= 0:
        return base
    ow = outline_w
    w, h = base.get_width(), base.get_height()
    surf = pygame.Surface((w + ow*2, h + ow*2), pygame.SRCALPHA)
    outline_img = font.render(text, True, outline_color)
    # 8방향 + 대각선으로 외곽선 깔기
    offsets = []
    for dx in range(-ow, ow+1):
        for dy in range(-ow, ow+1):
            if dx == 0 and dy == 0:
                continue
            if dx*dx + dy*dy <= ow*ow + 1:
                offsets.append((dx, dy))
    for dx, dy in offsets:
        surf.blit(outline_img, (ow + dx, ow + dy))
    surf.blit(base, (ow, ow))
    return surf


def draw_text(surf, text, font, color, cx, cy, outline=None, outline_w=2):
    if outline is not None:
        img = _render_outlined(font, text, color, outline, outline_w)
    else:
        img = font.render(text, True, color)
    surf.blit(img, img.get_rect(center=(cx, cy)))


def draw_text_fit(surf, text, font, color, cx, cy, max_w, outline=None, outline_w=2):
    """렌더한 글자가 max_w(px)를 넘으면 그 폭에 맞게 줄여서 그린다. (글자 튀어나옴 방지)"""
    if outline is not None:
        img = _render_outlined(font, text, color, outline, outline_w)
    else:
        img = font.render(text, True, color)
    w = img.get_width()
    if w > max_w and w > 0:
        h = max(1, int(img.get_height() * (max_w / w)))
        img = pygame.transform.smoothscale(img, (int(max_w), h))
    surf.blit(img, img.get_rect(center=(cx, cy)))


def draw_text_left(surf, text, font, color, x, cy, outline=None, outline_w=2):
    if outline is not None:
        img = _render_outlined(font, text, color, outline, outline_w)
    else:
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