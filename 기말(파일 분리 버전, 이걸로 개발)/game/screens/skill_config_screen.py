import pygame
import os
import sys as _sys
_sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from utils import *
from run_state import RUN

PANEL_BG = (245, 245, 245)
DIV      = (210, 210, 210)
EQUIP_BG = (225, 240, 225)   # 장착됨
OWN_BG   = (238, 238, 238)
HOVER    = (250, 245, 220)
FULL_COL = (180, 60, 60)

MAX_EQUIP = 10


class SkillConfigScreen:
    """스킬 배치 화면. 보유 스킬을 장착/해제 (최대 10).
    좌: 장착 스킬, 우: 미장착 보유 스킬. 클릭으로 토글.
    반환값: "back"
    """

    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.hover_side = None   # ("eq", i) or ("own", i)
        self.scroll_eq = 0
        self.scroll_own = 0

    # ── 보유/장착 목록 ────────────────────────────────────────────
    def _equipped(self):
        return RUN.skills_equipped

    def _unequipped(self):
        """보유 중 장착 안 된 스킬 (객체 동일성으로 구분)."""
        eq = RUN.skills_equipped
        return [s for s in RUN.skills_owned if s not in eq]

    # ── 영역 ──────────────────────────────────────────────────────
    def _back_rect(self):
        return pygame.Rect(int(self.W*0.03), int(self.H*0.04), 90, 32)

    def _col_x(self, side):
        # side: "eq"(좌) / "own"(우)
        return int(self.W*0.27) if side == "eq" else int(self.W*0.73)

    def _list_top(self):
        return int(self.H*0.24)

    def _list_bottom(self):
        return int(self.H*0.92)

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
            if event.key == pygame.K_ESCAPE:
                return "back"
        elif event.type == pygame.MOUSEWHEEL:
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
            # 장착 목록 클릭 → 해제
            eq = self._equipped()
            for i in range(len(eq)):
                if self._item_rect("eq", i).collidepoint(event.pos):
                    play_click()
                    self._unequip(eq[i])
                    return None
            # 미장착 목록 클릭 → 장착
            un = self._unequipped()
            for i in range(len(un)):
                if self._item_rect("own", i).collidepoint(event.pos):
                    play_click()
                    self._equip(un[i])
                    return None
        return None

    def _equip(self, skill):
        if len(RUN.skills_equipped) >= MAX_EQUIP:
            return  # 가득 참
        if skill not in RUN.skills_equipped:
            RUN.skills_equipped.append(skill)
            RUN.save_skills()   # 장착 구성 영구 저장

    def _unequip(self, skill):
        if skill in RUN.skills_equipped:
            RUN.skills_equipped.remove(skill)
            RUN.save_skills()   # 장착 구성 영구 저장

    def update(self, dt):
        pass

    # ── 그리기 ────────────────────────────────────────────────────
    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        draw_text(surf, "스킬 배치", self.fonts["title"], BLACK, W//2, int(H*0.07))

        br = self._back_rect()
        pygame.draw.rect(surf, BLACK, br, 1)
        draw_text(surf, "◀ 뒤로", self.fonts["hint"], BLACK, br.centerx, br.centery)

        # 구분선
        pygame.draw.line(surf, DIV, (W//2, int(H*0.18)), (W//2, int(H*0.92)), 1)

        eq = self._equipped()
        un = self._unequipped()

        # 좌측 헤더: 장착 (개수/최대)
        eq_col = FULL_COL if len(eq) >= MAX_EQUIP else (40,120,60)
        draw_text(surf, f"장착 스킬  {len(eq)} / {MAX_EQUIP}", self.fonts["menu"], eq_col,
                  self._col_x("eq"), int(H*0.16))
        draw_text(surf, "클릭하면 해제", self.fonts["small"], GRAY, self._col_x("eq"), int(H*0.205))

        # 우측 헤더: 미장착
        draw_text(surf, "보유 스킬 (미장착)", self.fonts["menu"], BLACK,
                  self._col_x("own"), int(H*0.16))
        draw_text(surf, "클릭하면 장착", self.fonts["small"], GRAY, self._col_x("own"), int(H*0.205))

        # 클리핑 영역 (스크롤 시 헤더/하단 침범 방지)
        clip = pygame.Rect(0, self._list_top()-2, W, self._list_bottom()-self._list_top()+4)
        surf.set_clip(clip)
        # 좌측 목록
        if not eq:
            draw_text(surf, "(장착된 스킬 없음)", self.fonts["hint"], GRAY,
                      self._col_x("eq"), self._list_top()+int(H*0.05))
        for i, s in enumerate(eq):
            self._draw_skill_row("eq", i, s)

        # 우측 목록
        if not un:
            draw_text(surf, "(모든 스킬을 장착함)", self.fonts["hint"], GRAY,
                      self._col_x("own"), self._list_top()+int(H*0.05))
        for i, s in enumerate(un):
            self._draw_skill_row("own", i, s)
        surf.set_clip(None)

    def _draw_skill_row(self, side, i, skill):
        surf = self.screen
        r = self._item_rect(side, i)
        if r.bottom < self._list_top() or r.top > self._list_bottom():
            return
        hovered = self.hover_side == (side, i)
        bg = HOVER if hovered else (EQUIP_BG if side == "eq" else OWN_BG)
        pygame.draw.rect(surf, bg, r, border_radius=8)
        pygame.draw.rect(surf, BLACK, r, 2, border_radius=8)
        # 이름
        draw_text_left(surf, skill["name"], self.fonts["hint_bold"], BLACK,
                       r.x + int(self.W*0.02), r.y + int(r.height*0.32))
        # 정보
        info = f"위력 {skill['power']} · {skill['type']}"
        if skill.get("hits", 1) > 1:
            info += f" · {skill['hits']}회"
        if skill.get("count", "단일") != "단일":
            info += f" · {skill['count']}"
        if "회복" in skill.get("tags", []):
            info += " · 회복"
        if "필중" in skill.get("tags", []):
            info += " · 필중"
        draw_text_left(surf, info, self.fonts["small"], GRAY_D,
                       r.x + int(self.W*0.02), r.y + int(r.height*0.68))