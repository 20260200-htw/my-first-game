import pygame
import os
import sys as _sys
_sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from utils import *
from run_state import RUN
from data import run_data

PANEL_BG = (245, 245, 245)
DIV      = (210, 210, 210)
ITEM_BG  = (235, 238, 245)
DESC_COL = (90, 90, 90)
NOTE_COL = (120, 120, 120)


class ItemViewScreen:
    """아이템 화면. 보유(=장착) 아이템 목록을 보여준다.
    아이템은 획득 시 자동 장착되며 장착/해제가 불가능하므로 조작 없이 열람만 한다.
    반환값: "back"
    """

    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.scroll = 0

    # ── 영역 ──────────────────────────────────────────────────────
    def _back_rect(self):
        return pygame.Rect(int(self.W*0.03), int(self.H*0.04), 90, 32)

    def _list_top(self):
        return int(self.H*0.22)

    def _row_h(self):
        return int(self.H*0.11)

    def _row_rect(self, i):
        w   = int(self.W*0.60)
        h   = self._row_h()
        gap = int(self.H*0.02)
        top = self._list_top()
        y   = top + i*(h+gap)
        return pygame.Rect(self.W//2 - w//2, y, w, h)

    # ── 이벤트 ────────────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                return "back"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._back_rect().collidepoint(event.pos):
                play_click("cancel"); return "back"
            # 아이템 행은 클릭해도 아무 동작 없음 (장착/해제 불가)
        return None

    def update(self, dt):
        pass

    # ── 그리기 ────────────────────────────────────────────────────
    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        draw_text(surf, "아이템", self.fonts["title"], BLACK, W//2, int(H*0.07))

        br = self._back_rect()
        pygame.draw.rect(surf, BLACK, br, 1)
        draw_text(surf, "◀ 뒤로", self.fonts["hint"], BLACK, br.centerx, br.centery)

        # 안내 문구
        draw_text(surf, "획득 시 자동으로 장착되며, 해제할 수 없습니다.",
                  self.fonts["hint"], NOTE_COL, W//2, int(H*0.155))

        if not RUN.items:
            draw_text(surf, "보유한 아이템이 없습니다.",
                      self.fonts["menu"], GRAY, W//2, int(H*0.45))
            return

        for i, key in enumerate(RUN.items):
            it = run_data.ITEMS.get(key, {"name": key, "desc": ""})
            r  = self._row_rect(i)
            pygame.draw.rect(surf, ITEM_BG, r, border_radius=8)
            pygame.draw.rect(surf, DIV, r, 1, border_radius=8)
            # 이름
            draw_text_left(surf, it["name"], self.fonts["menu"], BLACK,
                           r.x + int(W*0.025), r.centery - int(H*0.022))
            # 효과 설명
            draw_text_left(surf, it.get("desc", ""), self.fonts["small"], DESC_COL,
                           r.x + int(W*0.025), r.centery + int(H*0.022))