import pygame
import os
import sys as _sys
# PyInstaller(_MEIPASS) 또는 일반 실행 모두 대응
_sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import save_data
from utils import *
from data.story_data import STORY


# ══════════════════════════════════════════════════════════════════
#   공통: 카드 선택 화면 (가로 일자 나열 + 드래그/방향키 이동)
# ══════════════════════════════════════════════════════════════════
class _CardSelectScreen:
    """카드를 가로 한 줄로 배치하고 좌우 방향키 또는 마우스
    좌클릭 드래그로 이동, Enter/클릭으로 선택하는 공통 화면.
    items: [(key, label, image_path), ...]"""

    CARD_W_RATIO  = 0.20    # 카드 너비 (화면 폭 비율)
    CARD_H_RATIO  = 0.50    # 카드 높이 (화면 높이 비율)
    GAP_RATIO     = 0.025   # 카드 사이 간격
    CENTER_Y      = 0.55    # 카드 중심 Y
    DRAG_THRESH   = 8       # 드래그 판정 임계값 (px)
    ANIM_SPEED    = 14.0    # 슬라이드 보간 속도

    def __init__(self, screen, W, H, fonts, title, items):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.title = title
        self.items = items
        self.selected = 0
        self._img_cache = {}

        self._scroll_x   = 0.0
        self._target_x   = 0.0
        self._drag_active  = False
        self._drag_start_x = 0
        self._drag_origin  = 0.0

    # ── 치수 ──────────────────────────────────────────────────────
    def _cw(self):     return int(self.W * self.CARD_W_RATIO)
    def _ch(self):     return int(self.H * self.CARD_H_RATIO)
    def _gap(self):    return int(self.W * self.GAP_RATIO)
    def _stride(self): return self._cw() + self._gap()

    def _target_for(self, idx):
        return idx * self._stride()

    def _snap_to(self, idx):
        n = len(self.items)
        self.selected = max(0, min(n - 1, idx))
        self._target_x = self._target_for(self.selected)

    def _card_rect(self, idx):
        cw, ch = self._cw(), self._ch()
        cy = int(self.H * self.CENTER_Y)
        cx = self.W // 2 + idx * self._stride() - int(self._scroll_x)
        return pygame.Rect(cx - cw // 2, cy - ch // 2, cw, ch)

    def _idx_at(self, mx, my):
        for i in range(len(self.items)):
            if self._card_rect(i).collidepoint(mx, my):
                return i
        return None

    # ── 이미지 ────────────────────────────────────────────────────
    def _load_img(self, path, size):
        if not path or not os.path.exists(path):
            return None
        key = (path, size)
        if key in self._img_cache:
            return self._img_cache[key]
        try:
            raw = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(raw, size)
            self._img_cache[key] = img
            return img
        except Exception:
            return None

    # ── 이벤트 ────────────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self._snap_to(self.selected - 1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._snap_to(self.selected + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if not self._is_locked(self.items[self.selected][0]):
                    return self._on_select(self.items[self.selected][0])

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._drag_active  = True
            self._drag_start_x = event.pos[0]
            self._drag_origin  = self._scroll_x

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._drag_active:
                dist = abs(event.pos[0] - self._drag_start_x)
                self._drag_active = False
                if dist < self.DRAG_THRESH:
                    idx = self._idx_at(*event.pos)
                    if idx is not None:
                        if self._is_locked(self.items[idx][0]):
                            self._snap_to(idx)   # 포커스만 이동, 진입 불가
                        elif idx == self.selected:
                            return self._on_select(self.items[idx][0])
                        else:
                            self._snap_to(idx)
                else:
                    nearest = int(round(self._scroll_x / self._stride()))
                    self._snap_to(nearest)

        elif event.type == pygame.MOUSEMOTION:
            if self._drag_active:
                dx = event.pos[0] - self._drag_start_x
                raw = self._drag_origin - dx
                n = len(self.items)
                lo = -self._stride() * 0.4
                hi = self._target_for(n - 1) + self._stride() * 0.4
                self._scroll_x = max(lo, min(hi, raw))

        return None

    def _on_select(self, key):
        return ("select", key)

    def _is_locked(self, key):
        """서브클래스에서 오버라이드. True면 잠긴 카드."""
        return False

    # ── 업데이트 ──────────────────────────────────────────────────
    def update(self, dt):
        if not self._drag_active:
            diff = self._target_x - self._scroll_x
            t = min(1.0, self.ANIM_SPEED * dt / 1000.0)
            self._scroll_x += diff * t

    # ── 그리기 ────────────────────────────────────────────────────
    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        draw_text(surf, self.title, self.fonts["title"], BLACK, W // 2, int(H * 0.09))
        draw_text(surf, "ESC: 뒤로", self.fonts["hint"], GRAY_D, int(W * 0.08), int(H * 0.09))

        n = len(self.items)
        cw, ch = self._cw(), self._ch()

        for i, (key, label, img_path) in enumerate(self.items):
            r = self._card_rect(i)
            if r.right < 0 or r.left > W:
                continue

            locked = self._is_locked(key)
            img = self._load_img(img_path, (r.width, r.height))
            if locked:
                # 잠긴 카드: 어두운 회색 + 자물쇠
                pygame.draw.rect(surf, (160, 160, 160), r, border_radius=6)
                draw_text(surf, "🔒", self.fonts["menu"], (80, 80, 80), r.centerx, r.centery)
            elif img:
                surf.blit(img, r)
            else:
                pygame.draw.rect(surf, (235, 235, 235), r, border_radius=6)
                draw_text(surf, label, self.fonts["menu"], BLACK, r.centerx, r.centery)

            border = 4 if i == self.selected else 1
            col = (120, 120, 120) if locked else BLACK
            pygame.draw.rect(surf, col, r, border, border_radius=6)

        # 좌우 화살표
        cy = int(H * self.CENTER_Y)
        margin = int(W * 0.025)
        if self.selected > 0:
            draw_text(surf, "◀", self.fonts["menu"], GRAY_D, margin, cy)
        if self.selected < n - 1:
            draw_text(surf, "▶", self.fonts["menu"], GRAY_D, W - margin, cy)

        # 하단 도트 인디케이터
        dot_y = int(H * 0.87)
        dr = max(4, int(W * 0.005))
        dg = dr * 3
        dot_x0 = W // 2 - (n * dg - dg) // 2
        for i in range(n):
            col = BLACK if i == self.selected else GRAY
            pygame.draw.circle(surf, col, (dot_x0 + i * dg, dot_y), dr)

        pass  # 키 가이드 없음


# ══════════════════════════════════════════════════════════════════
#   1) 막 선택
# ══════════════════════════════════════════════════════════════════
class ActSelectScreen(_CardSelectScreen):
    def __init__(self, screen, W, H, fonts):
        items = [(k, v.get("title", k), v.get("image", ""))
                 for k, v in STORY.items()]
        super().__init__(screen, W, H, fonts, "메인 스토리", items)

    def _is_locked(self, key):
        return not save_data.is_act_unlocked(key)

    def _on_select(self, key):
        return ("act", key)


# ══════════════════════════════════════════════════════════════════
#   1-5) 막 내부 메뉴 (스토리/탐험/성장/편성/모집/돌아가기)
# ══════════════════════════════════════════════════════════════════
class ActMenuScreen:
    """막을 선택한 뒤 나타나는 메뉴 화면."""
    ITEMS = ["스토리", "탐험", "성장", "편성", "모집", "돌아가기"]

    def __init__(self, screen, W, H, fonts, act_key):
        self.screen  = screen
        self.W, self.H = W, H
        self.fonts   = fonts
        self.act_key = act_key
        self.selected = 0
        self._build_rects()

    def _build_rects(self):
        W, H = self.W, self.H
        gap = int(H * 0.075)
        start_y = int(H * 0.28)
        menu_cx = int(W * 0.25)
        self.rects = [
            pygame.Rect(menu_cx - 160, start_y + i * gap - 22, 320, 44)
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
            elif event.key == pygame.K_ESCAPE:
                return "back"
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
        actions = ["story", "explore", "growth", "formation", "recruit", "back"]
        return actions[self.selected]

    def update(self, dt): pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        # 제목: 우측 영역 중앙
        title_cx = int(W * 0.68)
        act_title = STORY.get(self.act_key, {}).get("title", self.act_key)
        draw_text(surf, act_title, self.fonts["title"], BLACK, title_cx, int(H * 0.40))

        # 메뉴: 좌측 영역
        gap = int(H * 0.075)
        start_y = int(H * 0.28)
        menu_cx = int(W * 0.25)
        for i, item in enumerate(self.ITEMS):
            cy = start_y + i * gap
            r  = self.rects[i]
            if i == self.selected:
                pygame.draw.rect(surf, BLACK, r)
                draw_text(surf, item, self.fonts["menu"], WHITE, menu_cx, cy)
            else:
                draw_text(surf, item, self.fonts["menu"], BLACK, menu_cx, cy)

        # 구분선 (메뉴와 제목 사이)
        pygame.draw.line(surf, GRAY, (int(W * 0.45), int(H * 0.15)), (int(W * 0.45), int(H * 0.85)), 1)


# ══════════════════════════════════════════════════════════════════
#   2) 장 선택
# ══════════════════════════════════════════════════════════════════
class ChapterSelectScreen(_CardSelectScreen):
    def __init__(self, screen, W, H, fonts, act_key):
        self.act_key = act_key
        act = STORY[act_key]
        items = [(k, v.get("title", k), v.get("image", ""))
                 for k, v in act["chapters"].items()]
        super().__init__(screen, W, H, fonts, act.get("title", act_key), items)

    def _is_locked(self, key):
        return not save_data.is_chapter_unlocked(self.act_key, key)

    def _on_select(self, key):
        return ("chapter", self.act_key, key)


# ══════════════════════════════════════════════════════════════════
#   3) 스테이지 선택
# ══════════════════════════════════════════════════════════════════
class StageSelectScreen(_CardSelectScreen):
    def __init__(self, screen, W, H, fonts, act_key, chapter_key):
        self.act_key = act_key
        self.chapter_key = chapter_key
        chap = STORY[act_key]["chapters"][chapter_key]
        items = [(k, v.get("title", k), v.get("image", ""))
                 for k, v in chap["stages"].items()]
        super().__init__(screen, W, H, fonts, chap.get("title", chapter_key), items)

    def _is_locked(self, key):
        return not save_data.is_stage_unlocked(self.act_key, self.chapter_key, key)

    def _on_select(self, key):
        return ("stage", self.act_key, self.chapter_key, key)