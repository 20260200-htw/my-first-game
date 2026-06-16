import pygame
import os
import sys as _sys
_sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from utils import *
from run_state import RUN
from data import run_data

DIV      = (210, 210, 210)
EQUIP_BG = (225, 240, 225)   # 장착됨
OWN_BG   = (238, 238, 238)
HOVER    = (250, 245, 220)
FULL_COL = (180, 60, 60)
SYN_COL  = (150, 90, 40)


class ItemViewScreen:
    """아이템 장착 화면. 보유 아이템을 장착/해제 (최대 10).
    좌: 장착 아이템, 우: 미장착 보유 아이템. 클릭으로 토글. 마우스 휠로 스크롤.
    하단에 완성된 시너지 표시. 반환값: "back"
    """

    MAX_EQUIP = 10

    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.hover_side = None
        self.scroll_eq = 0
        self.scroll_own = 0

    # ── 목록 ──────────────────────────────────────────────────────
    def _equipped(self):
        return list(RUN.items_equipped)

    def _unequipped(self):
        return [k for k in RUN.items if k not in RUN.items_equipped]

    # ── 영역 ──────────────────────────────────────────────────────
    def _back_rect(self):
        return pygame.Rect(int(self.W*0.03), int(self.H*0.04), 90, 32)

    def _col_x(self, side):
        return int(self.W*0.27) if side == "eq" else int(self.W*0.73)

    def _list_top(self):
        return int(self.H*0.24)

    def _list_bottom(self):
        return int(self.H*0.84)   # 하단 시너지 영역 위까지

    def _row_h(self):
        return int(self.H*0.085)

    def _scroll_of(self, side):
        return self.scroll_eq if side == "eq" else self.scroll_own

    def _item_rect(self, side, i):
        cx = self._col_x(side)
        w  = int(self.W*0.40)
        h  = self._row_h()
        gap = int(self.H*0.018)
        top = self._list_top() - self._scroll_of(side)
        y = top + i*(h+gap)
        return pygame.Rect(cx - w//2, y, w, h)

    def _max_scroll(self, side):
        n = len(self._equipped()) if side == "eq" else len(self._unequipped())
        h = self._row_h(); gap = int(self.H*0.018)
        content = n*(h+gap)
        view = self._list_bottom() - self._list_top()
        return max(0, content - view)

    # ── 이벤트 ────────────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                play_click("cancel"); return "back"
        elif event.type == pygame.MOUSEWHEEL:
            # 마우스가 올라가 있는 열을 스크롤 (없으면 좌측 기본)
            mx, _my = pygame.mouse.get_pos()
            side = "eq" if mx < self.W // 2 else "own"
            step = int(self.H*0.05)
            if side == "eq":
                self.scroll_eq = max(0, min(self._max_scroll("eq"),
                                            self.scroll_eq - event.y * step))
            else:
                self.scroll_own = max(0, min(self._max_scroll("own"),
                                             self.scroll_own - event.y * step))
        elif event.type == pygame.MOUSEMOTION:
            self.hover_side = None
            for i in range(len(self._equipped())):
                if self._item_rect("eq", i).collidepoint(event.pos):
                    self.hover_side = ("eq", i); break
            if not self.hover_side:
                for i in range(len(self._unequipped())):
                    if self._item_rect("own", i).collidepoint(event.pos):
                        self.hover_side = ("own", i); break
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._back_rect().collidepoint(event.pos):
                play_click("cancel"); return "back"
            eq = self._equipped()
            for i in range(len(eq)):
                if self._item_rect("eq", i).collidepoint(event.pos):
                    play_click(); RUN.unequip_item(eq[i]); return None
            un = self._unequipped()
            for i in range(len(un)):
                if self._item_rect("own", i).collidepoint(event.pos):
                    play_click(); RUN.equip_item(un[i]); return None
        return None

    def update(self, dt):
        pass

    # ── 그리기 ────────────────────────────────────────────────────
    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        draw_text(surf, "아이템 장착", self.fonts["title"], BLACK, W//2, int(H*0.07))

        br = self._back_rect()
        pygame.draw.rect(surf, BLACK, br, 1)
        draw_text(surf, "◀ 뒤로", self.fonts["hint"], BLACK, br.centerx, br.centery)

        pygame.draw.line(surf, DIV, (W//2, int(H*0.18)), (W//2, self._list_bottom()), 1)

        eq = self._equipped()
        un = self._unequipped()

        eq_col = FULL_COL if len(eq) >= self.MAX_EQUIP else (40,120,60)
        draw_text(surf, f"장착 아이템  {len(eq)} / {self.MAX_EQUIP}", self.fonts["menu"], eq_col,
                  self._col_x("eq"), int(H*0.16))
        draw_text(surf, "클릭하면 해제", self.fonts["small"], GRAY, self._col_x("eq"), int(H*0.205))

        draw_text(surf, "보유 아이템 (미장착)", self.fonts["menu"], BLACK,
                  self._col_x("own"), int(H*0.16))
        draw_text(surf, "클릭하면 장착", self.fonts["small"], GRAY, self._col_x("own"), int(H*0.205))

        # 클리핑 영역 (목록 밖으로 안 나가게)
        clip = pygame.Rect(0, self._list_top()-2, W, self._list_bottom()-self._list_top()+4)
        surf.set_clip(clip)
        if not eq:
            draw_text(surf, "(장착된 아이템 없음)", self.fonts["hint"], GRAY,
                      self._col_x("eq"), self._list_top()+int(H*0.05))
        for i, k in enumerate(eq):
            self._draw_item_row("eq", i, k)
        if not un:
            draw_text(surf, "(모든 아이템을 장착함)", self.fonts["hint"], GRAY,
                      self._col_x("own"), self._list_top()+int(H*0.05))
        for i, k in enumerate(un):
            self._draw_item_row("own", i, k)
        surf.set_clip(None)

        # 하단: 완성된 시너지
        syns = RUN.active_synergies()
        sy = int(H*0.875)
        if syns:
            draw_text(surf, "발동 중인 시너지", self.fonts["hint_bold"], SYN_COL, W//2, sy)
            for j, name in enumerate(syns[:2]):
                desc = run_data.SYNERGIES[name]["desc"]
                draw_text_fit(surf, f"★ {desc}", self.fonts["small"], SYN_COL,
                              W//2, sy + int(H*0.035) + j*int(H*0.03), W*0.92)
        else:
            draw_text(surf, "시너지 아이템을 모두 장착하면 추가 효과가 발동합니다.",
                      self.fonts["small"], GRAY, W//2, sy)

    def _draw_item_row(self, side, i, key):
        surf = self.screen
        r = self._item_rect(side, i)
        if r.bottom < self._list_top() or r.top > self._list_bottom():
            return
        it = run_data.ITEMS.get(key, {"name": key, "desc": ""})
        hovered = self.hover_side == (side, i)
        bg = HOVER if hovered else (EQUIP_BG if side == "eq" else OWN_BG)
        pygame.draw.rect(surf, bg, r, border_radius=8)
        pygame.draw.rect(surf, BLACK, r, 2, border_radius=8)
        draw_text_left(surf, it["name"], self.fonts["hint_bold"], BLACK,
                       r.x + int(self.W*0.02), r.y + int(r.height*0.32))
        draw_text_left(surf, it.get("desc", ""), self.fonts["small"], GRAY_D,
                       r.x + int(self.W*0.02), r.y + int(r.height*0.68))
