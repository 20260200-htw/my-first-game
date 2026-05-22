import pygame
import sys
import ctypes
import os

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


# ══════════════════════════════════════════════════════════════════
#   도감 데이터
# ══════════════════════════════════════════════════════════════════
COMPENDIUM = {
    "인간": {
        "주인공": {
            "image": "assets/main_character.png",
            "description": [
                "이름: 미정",
                "소속: 미정",
                "설명: 준비 중입니다.",
            ]
        },
        "중앙": {
            "왕국 기사단": {
                "기사단장": {
                    "image": "assets/knight_leader.png",
                    "description": [
                        "이름: 미정",
                        "소속: 왕국 기사단",
                        "직위: 기사단장",
                        "설명: 왕국 기사단의 단장입니다.",
                        "아직 젊지만 실력은 확실한 강자입니다.",
                        "레벨 100 | 물리 레벨 100 | 마력 레벨 100"
                    ]
                }
            }
        },
        "동부":  None,
        "서부":  None,
        "남부":  None,
        "북부":  None,
    },
    "마족":  None,
    "마물":  None,
}


# ══════════════════════════════════════════════════════════════════
#   타이틀 화면
# ══════════════════════════════════════════════════════════════════
class TitleScreen:
    ITEMS = ["게임 시작", "갤러리", "설정", "게임 종료"]

    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.selected = 0

        gap = int(H * 0.08)
        start_y = H // 2
        self.rects = [
            pygame.Rect(W // 2 - 150, start_y + i * gap - 22, 300, 44)
            for i in range(len(self.ITEMS))
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.ITEMS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.ITEMS)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self._action()
        elif event.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self.rects):
                if r.collidepoint(event.pos):
                    self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self.rects):
                if r.collidepoint(event.pos):
                    self.selected = i
                    return self._action()
        return None

    def _action(self):
        return ["start", "gallery", "settings", "quit"][self.selected]

    def update(self, dt): pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        draw_text(surf, "뻔하디 뻔한 JRPG", self.fonts["title"], BLACK, W // 2, int(H * 0.3))
        pygame.draw.line(surf, BLACK, (W // 2 - 150, int(H * 0.42)), (W // 2 + 150, int(H * 0.42)), 1)

        gap = int(H * 0.08)
        start_y = H // 2
        for i, item in enumerate(self.ITEMS):
            cy = start_y + i * gap
            r  = self.rects[i]
            if i == self.selected:
                pygame.draw.rect(surf, BLACK, r)
                draw_text(surf, item, self.fonts["menu"], WHITE, W // 2, cy)
            else:
                draw_text(surf, item, self.fonts["menu"], BLACK, W // 2, cy)

        draw_text(surf, "↑↓  이동     Enter / 클릭  선택",
                  self.fonts["hint"], GRAY_D, W // 2, H - int(H * 0.05))


# ══════════════════════════════════════════════════════════════════
#   설정 화면
# ══════════════════════════════════════════════════════════════════
class SettingsScreen:
    ITEMS = ["BGM 볼륨", "효과음 볼륨", "창 모드", "해상도", "프레임", "돌아가기"]

    LABEL_GAP_RATIO = 0.15
    HOLD_DELAY      = 400
    HOLD_REPEAT     = 80

    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.selected = 0
        self._held_key  = None
        self._held_dir  = 0
        self._held_time = 0.0

    def handle_event(self, event):
        last = len(self.ITEMS) - 1
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.ITEMS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.ITEMS)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self._adjust(-1)
                self._held_key  = event.key
                self._held_dir  = -1
                self._held_time = self.HOLD_DELAY
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._adjust(1)
                self._held_key  = event.key
                self._held_dir  = 1
                self._held_time = self.HOLD_DELAY
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.selected == last:
                    return "back"
            elif event.key == pygame.K_ESCAPE:
                return "back"
        elif event.type == pygame.KEYUP:
            if event.key == self._held_key:
                self._held_key = None
                self._held_dir = 0
        elif event.type == pygame.MOUSEMOTION:
            _, my = event.pos
            for i in range(len(self.ITEMS)):
                if abs(my - self._cy(i)) < 24:
                    self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i in range(len(self.ITEMS)):
                if abs(my - self._cy(i)) < 24:
                    self.selected = i
                    if i == last:
                        return "back"
                    if i in (0, 1):
                        sx  = self.W // 2 + int(self.W * self.LABEL_GAP_RATIO)
                        sw  = int(self.W * 0.15)
                        slx = sx - sw // 2
                        if slx <= mx <= slx + sw:
                            raw = int((mx - slx) / sw * 100)
                            val = round(raw / 10) * 10
                            if i == 0: settings["bgm_vol"] = max(0, min(100, val))
                            else:      settings["sfx_vol"] = max(0, min(100, val))
                    else:
                        self._adjust(1)
        return None

    def update(self, dt):
        if self._held_key is None:
            return
        self._held_time -= dt
        if self._held_time <= 0:
            self._adjust(self._held_dir)
            self._held_time = self.HOLD_REPEAT

    def _cy(self, i):
        return int(self.H * 0.3) + i * int(self.H * 0.1)

    def _adjust(self, d):
        if self.selected == 0:
            settings["bgm_vol"]   = max(0, min(100, settings["bgm_vol"] + d * 10))
        elif self.selected == 1:
            settings["sfx_vol"]   = max(0, min(100, settings["sfx_vol"] + d * 10))
        elif self.selected == 2:
            settings["win_mode"]  = (settings["win_mode"] + d) % len(WINDOW_MODES)
        elif self.selected == 3:
            settings["res_index"] = (settings["res_index"] + d) % len(RESOLUTIONS)
        elif self.selected == 4:
            settings["fps_index"] = (settings["fps_index"] + d) % len(FRAMERATES)

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        bx = int(W * 0.2)
        by = int(H * 0.08)
        bw = int(W * 0.6)
        bh = int(H * 0.84)
        pygame.draw.rect(surf, WHITE, (bx, by, bw, bh))
        pygame.draw.rect(surf, BLACK, (bx, by, bw, bh), 2)

        draw_text(surf, "설정", self.fonts["title"], BLACK, W // 2, int(H * 0.17))
        pygame.draw.line(surf, BLACK, (bx + int(bw * 0.1), int(H * 0.26)), (bx + int(bw * 0.9), int(H * 0.26)), 1)

        lx  = W // 2 - int(W * self.LABEL_GAP_RATIO)
        sx  = W // 2 + int(W * self.LABEL_GAP_RATIO)
        sw  = int(W * 0.15)
        slx = sx - sw // 2

        for i, label in enumerate(self.ITEMS):
            cy  = self._cy(i)
            sel = (i == self.selected)

            if i < len(self.ITEMS) - 1:
                draw_text(surf, label, self.fonts["menu"], BLACK, lx, cy)

            if i in (0, 1):
                vol = settings["bgm_vol"] if i == 0 else settings["sfx_vol"]
                pygame.draw.rect(surf, GRAY,  (slx, cy - 4, sw, 8))
                pygame.draw.rect(surf, BLACK, (slx, cy - 4, int(sw * vol / 100), 8))
                if sel:
                    draw_text(surf, "◀", self.fonts["hint"], BLACK, slx - 14, cy)
                    draw_text(surf, "▶", self.fonts["hint"], BLACK, slx + sw + 14, cy)
            elif i == 2:
                val_str = WINDOW_MODES[settings["win_mode"]]
                if sel:
                    draw_text(surf, "◀", self.fonts["hint"], BLACK, slx - 14, cy)
                    draw_text(surf, val_str, self.fonts["menu"], BLACK, sx, cy)
                    draw_text(surf, "▶", self.fonts["hint"], BLACK, slx + sw + 14, cy)
                else:
                    draw_text(surf, val_str, self.fonts["menu"], GRAY_D, sx, cy)
            elif i == 3:
                rw, rh  = RESOLUTIONS[settings["res_index"]]
                res_str = f"{rw} × {rh}"
                if sel:
                    draw_text(surf, "◀", self.fonts["hint"], BLACK, slx - 14, cy)
                    draw_text(surf, res_str, self.fonts["menu"], BLACK, sx, cy)
                    draw_text(surf, "▶", self.fonts["hint"], BLACK, slx + sw + 14, cy)
                else:
                    draw_text(surf, res_str, self.fonts["menu"], GRAY_D, sx, cy)
            elif i == 4:
                fps_str = f"{FRAMERATES[settings['fps_index']]} FPS"
                if sel:
                    draw_text(surf, "◀", self.fonts["hint"], BLACK, slx - 14, cy)
                    draw_text(surf, fps_str, self.fonts["menu"], BLACK, sx, cy)
                    draw_text(surf, "▶", self.fonts["hint"], BLACK, slx + sw + 14, cy)
                else:
                    draw_text(surf, fps_str, self.fonts["menu"], GRAY_D, sx, cy)
            elif i == len(self.ITEMS) - 1:
                draw_text(surf, label, self.fonts["menu"], BLACK if sel else GRAY_D, W // 2, cy)

        draw_text(surf, "↑↓  이동     ←→  조절     Esc  돌아가기",
                  self.fonts["hint"], GRAY_D, W // 2, H - int(H * 0.05))


# ══════════════════════════════════════════════════════════════════
#   갤러리 화면
# ══════════════════════════════════════════════════════════════════
class GalleryScreen:
    ITEMS = ["스토리 컷신", "적 도감", "돌아가기"]

    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.selected = 0

    def handle_event(self, event):
        last = len(self.ITEMS) - 1
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.ITEMS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.ITEMS)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self._action()
            elif event.key == pygame.K_ESCAPE:
                return "back"
        elif event.type == pygame.MOUSEMOTION:
            _, my = event.pos
            for i in range(len(self.ITEMS)):
                if abs(my - self._cy(i)) < 24:
                    self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            _, my = event.pos
            for i in range(len(self.ITEMS)):
                if abs(my - self._cy(i)) < 24:
                    self.selected = i
                    return self._action()
        return None

    def _cy(self, i):
        return int(self.H * 0.35) + i * int(self.H * 0.1)

    def _action(self):
        return ["cutscene", "compendium", "back"][self.selected]

    def update(self, dt): pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        draw_text(surf, "갤러리", self.fonts["title"], BLACK, W // 2, int(H * 0.2))
        pygame.draw.line(surf, BLACK, (W // 2 - 150, int(H * 0.3)), (W // 2 + 150, int(H * 0.3)), 1)

        for i, item in enumerate(self.ITEMS):
            cy  = self._cy(i)
            sel = (i == self.selected)
            r   = pygame.Rect(W // 2 - 150, cy - 22, 300, 44)
            if sel:
                pygame.draw.rect(surf, BLACK, r)
                draw_text(surf, item, self.fonts["menu"], WHITE, W // 2, cy)
            else:
                draw_text(surf, item, self.fonts["menu"], BLACK, W // 2, cy)

        draw_text(surf, "↑↓  이동     Enter  선택     Esc  돌아가기",
                  self.fonts["hint"], GRAY_D, W // 2, H - int(H * 0.05))


# ══════════════════════════════════════════════════════════════════
#   적 도감 — 메뉴 화면 (공통 베이스)
# ══════════════════════════════════════════════════════════════════
class CompendiumMenuScreen:
    """항목 목록을 보여주는 범용 메뉴."""

    def __init__(self, screen, W, H, fonts, title, items):
        self.screen   = screen
        self.W, self.H = W, H
        self.fonts    = fonts
        self.title    = title
        self.items    = items
        self.selected = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.items)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.items)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                _, val = self.items[self.selected]
                if val is not None:
                    return ("select", val)
            elif event.key == pygame.K_ESCAPE:
                return ("back", None)
        elif event.type == pygame.MOUSEMOTION:
            _, my = event.pos
            for i in range(len(self.items)):
                if abs(my - self._cy(i)) < 24:
                    self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            _, my = event.pos
            for i, (_, val) in enumerate(self.items):
                if abs(my - self._cy(i)) < 24:
                    self.selected = i
                    if val is not None:
                        return ("select", val)
        return None

    def _cy(self, i):
        start = int(self.H * 0.35)
        gap   = int(self.H * 0.09)
        return start + i * gap

    def update(self, dt): pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        draw_text(surf, self.title, self.fonts["title"], BLACK, W // 2, int(H * 0.2))
        pygame.draw.line(surf, BLACK, (W // 2 - 150, int(H * 0.3)), (W // 2 + 150, int(H * 0.3)), 1)

        for i, (name, val) in enumerate(self.items):
            cy  = self._cy(i)
            sel = (i == self.selected)
            r   = pygame.Rect(W // 2 - 150, cy - 22, 300, 44)
            if sel:
                pygame.draw.rect(surf, BLACK, r)
                draw_text(surf, name, self.fonts["menu"], WHITE, W // 2, cy)
            else:
                draw_text(surf, name, self.fonts["menu"], BLACK, W // 2, cy)

        draw_text(surf, "↑↓  이동     Enter  선택     Esc  돌아가기",
                  self.fonts["hint"], GRAY_D, W // 2, H - int(H * 0.05))


# ══════════════════════════════════════════════════════════════════
#   적 도감 — 상세 화면
# ══════════════════════════════════════════════════════════════════
class CompendiumDetailScreen:
    """이미지(좌) + 설명(우) 레이아웃"""

    def __init__(self, screen, W, H, fonts, entry):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts  = fonts
        self.entry  = entry
        self.image  = None
        self._load_image()

    def _load_image(self):
        path = self.entry.get("image", "")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                max_w = int(self.W * 0.35)
                max_h = int(self.H * 0.7)
                iw, ih = img.get_size()
                scale = min(max_w / iw, max_h / ih)
                self.image = pygame.transform.smoothscale(
                    img, (int(iw * scale), int(ih * scale))
                )
            except Exception:
                self.image = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return "back"
        return None

    def update(self, dt): pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        img_area_cx = int(W * 0.25)
        img_area_cy = int(H * 0.5)

        if self.image:
            r = self.image.get_rect(center=(img_area_cx, img_area_cy))
            surf.blit(self.image, r)
        else:
            box = pygame.Rect(int(W * 0.05), int(H * 0.15), int(W * 0.38), int(H * 0.7))
            pygame.draw.rect(surf, GRAY, box)
            draw_text(surf, "이미지 없음", self.fonts["menu"], GRAY_D, img_area_cx, img_area_cy)

        pygame.draw.line(surf, BLACK,
            (int(W * 0.45), int(H * 0.1)),
            (int(W * 0.45), int(H * 0.9)), 1)

        desc = self.entry.get("description", [])
        rx   = int(W * 0.5)
        ry   = int(H * 0.25)
        gap  = int(H * 0.07)
        for i, line in enumerate(desc):
            draw_text_left(surf, line, self.fonts["menu"], BLACK, rx, ry + i * gap)

        draw_text(surf, "Esc / 클릭  돌아가기",
                  self.fonts["hint"], GRAY_D, W // 2, H - int(H * 0.05))


# ══════════════════════════════════════════════════════════════════
#   플레이스홀더
# ══════════════════════════════════════════════════════════════════
class PlaceholderScreen:
    def __init__(self, screen, W, H, fonts, label):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.label = label

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:         return "back"
        if event.type == pygame.MOUSEBUTTONDOWN: return "back"
        return None

    def update(self, dt): pass

    def draw(self):
        W, H = self.W, self.H
        self.screen.fill(WHITE)
        draw_text(self.screen, self.label,             self.fonts["title"], BLACK,  W // 2, int(H * 0.45))
        draw_text(self.screen, "준비 중입니다.",         self.fonts["menu"],  GRAY_D, W // 2, int(H * 0.55))
        draw_text(self.screen, "아무 키나 눌러 돌아가기", self.fonts["hint"],  GRAY,   W // 2, int(H * 0.62))


# ══════════════════════════════════════════════════════════════════
#   종료 다이얼로그
# ══════════════════════════════════════════════════════════════════
class QuitDialog:
    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.selected = 1

    def _btn_rects(self):
        W, H = self.W, self.H
        dw = int(W * 0.28)
        dh = int(H * 0.18)
        dx = (W - dw) // 2
        dy = (H - dh) // 2
        bw = int(dw * 0.3)
        bh = int(dh * 0.35)
        gap = int(dw * 0.05)
        by = dy + dh - bh - int(dh * 0.12)
        return [
            pygame.Rect(W // 2 - bw - gap, by, bw, bh),
            pygame.Rect(W // 2 + gap,      by, bw, bh),
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                self.selected ^= 1
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return "yes" if self.selected == 0 else "no"
            elif event.key == pygame.K_ESCAPE:
                return "no"
        elif event.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self._btn_rects()):
                if r.collidepoint(event.pos): self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self._btn_rects()):
                if r.collidepoint(event.pos):
                    return "yes" if i == 0 else "no"
        return None

    def update(self, dt): pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen

        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 120))
        surf.blit(dim, (0, 0))

        dw = int(W * 0.28)
        dh = int(H * 0.18)
        dx, dy = (W - dw) // 2, (H - dh) // 2
        pygame.draw.rect(surf, WHITE, (dx, dy, dw, dh))
        pygame.draw.rect(surf, BLACK, (dx, dy, dw, dh), 2)

        draw_text(surf, "정말 종료하시겠습니까?", self.fonts["menu"], BLACK, W // 2, dy + int(dh * 0.3))

        for i, (r, label) in enumerate(zip(self._btn_rects(), ["예", "아니오"])):
            if i == self.selected:
                pygame.draw.rect(surf, BLACK, r)
                draw_text(surf, label, self.fonts["menu"], WHITE, r.centerx, r.centery)
            else:
                pygame.draw.rect(surf, WHITE, r)
                pygame.draw.rect(surf, BLACK, r, 1)
                draw_text(surf, label, self.fonts["menu"], BLACK, r.centerx, r.centery)


# ══════════════════════════════════════════════════════════════════
#   폰트
# ══════════════════════════════════════════════════════════════════
def load_fonts(H):
    def f(size):  return pygame.font.SysFont("malgungothic,nanumgothic,malgun gothic,gulim,sans-serif", size, bold=False)
    def fb(size): return pygame.font.SysFont("malgungothic,nanumgothic,malgun gothic,gulim,sans-serif", size, bold=True)
    return {
        "title": fb(int(H * 0.08)),
        "menu":  fb(int(H * 0.038)),
        "hint":  f(int(H * 0.022)),
    }


# ══════════════════════════════════════════════════════════════════
#   메인 루프
# ══════════════════════════════════════════════════════════════════
def main():
    global MON_W, MON_H
    pygame.init()
    pygame.display.set_caption("뻔하디 뻔한 JRPG")

    info = pygame.display.Info()
    MON_W, MON_H = info.current_w, info.current_h

    screen, W, H = apply_resolution()
    fonts  = load_fonts(H)
    clock  = pygame.time.Clock()

    title        = TitleScreen(screen, W, H, fonts)
    current      = "title"
    overlay      = None
    quit_dlg     = None
    placeholder  = None
    settings_sc  = None
    gallery_sc   = None

    comp_stack   = []

    def push_comp(screen_obj):
        comp_stack.append(screen_obj)

    def pop_comp():
        if comp_stack:
            comp_stack.pop()

    def comp_top():
        return comp_stack[-1] if comp_stack else None

    while True:
        dt = clock.tick(FRAMERATES[settings["fps_index"]])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if overlay == "quit":
                r = quit_dlg.handle_event(event)
                if r == "yes":  pygame.quit(); sys.exit()
                elif r == "no": overlay = None
                continue

            if current == "compendium" and comp_stack:
                top = comp_top()
                r   = top.handle_event(event)

                if isinstance(top, CompendiumDetailScreen):
                    if r == "back":
                        pop_comp()
                        if not comp_stack:
                            current = "gallery"

                elif isinstance(top, CompendiumMenuScreen):
                    if r is None:
                        pass
                    elif r[0] == "back":
                        pop_comp()
                        if not comp_stack:
                            current = "gallery"
                    elif r[0] == "select":
                        val  = r[1]
                        name = top.items[top.selected][0]  # 선택한 항목 이름
                        if isinstance(val, dict) and "image" in val:
                            push_comp(CompendiumDetailScreen(screen, W, H, fonts, val))
                        elif isinstance(val, dict):
                            items = [(k, v) for k, v in val.items()]
                            push_comp(CompendiumMenuScreen(screen, W, H, fonts, name, items))
                        elif val is None:
                            pass
                continue

            if current == "title":
                a = title.handle_event(event)
                if a == "quit":
                    quit_dlg = QuitDialog(screen, W, H, fonts)
                    overlay  = "quit"
                elif a == "settings":
                    settings_sc = SettingsScreen(screen, W, H, fonts)
                    current = "settings"
                elif a == "gallery":
                    gallery_sc = GalleryScreen(screen, W, H, fonts)
                    current = "gallery"
                elif a == "start":
                    placeholder = PlaceholderScreen(screen, W, H, fonts, "게임 시작")
                    current = "placeholder"

            elif current == "settings":
                r = settings_sc.handle_event(event)
                if r == "back":
                    screen, W, H = apply_resolution()
                    fonts  = load_fonts(H)
                    title  = TitleScreen(screen, W, H, fonts)
                    current = "title"

            elif current == "gallery":
                r = gallery_sc.handle_event(event)
                if r == "back":
                    current = "title"
                elif r == "cutscene":
                    placeholder = PlaceholderScreen(screen, W, H, fonts, "스토리 컷신")
                    current = "placeholder"
                elif r == "compendium":
                    comp_stack.clear()
                    top_items = [(k, v) for k, v in COMPENDIUM.items()]
                    push_comp(CompendiumMenuScreen(screen, W, H, fonts, "적 도감", top_items))
                    current = "compendium"

            elif current == "placeholder":
                r = placeholder.handle_event(event)
                if r == "back":
                    current = "title"

        if current == "title":          title.update(dt)
        elif current == "settings":     settings_sc.update(dt)
        elif current == "gallery":      gallery_sc.update(dt)
        elif current == "compendium" and comp_stack:
                                        comp_top().update(dt)
        elif current == "placeholder":  placeholder.update(dt)
        if overlay == "quit":           quit_dlg.update(dt)

        if current == "title":          title.draw()
        elif current == "settings":     settings_sc.draw()
        elif current == "gallery":      gallery_sc.draw()
        elif current == "compendium" and comp_stack:
                                        comp_top().draw()
        elif current == "placeholder":  placeholder.draw()
        if overlay == "quit":           quit_dlg.draw()

        pygame.display.flip()


if __name__ == "__main__":
    main()