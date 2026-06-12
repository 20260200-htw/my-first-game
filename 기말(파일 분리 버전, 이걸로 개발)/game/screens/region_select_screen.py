import pygame
import os
import sys as _sys
_sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from utils import *
from run_state import RUN
from data import run_data

CARD_BG   = (238, 238, 238)
CARD_HOV  = (250, 245, 220)
SEL_COL   = (60, 140, 220)
DIV       = (210, 210, 210)


class RegionSelectScreen:
    """구간 시작 시 지역 선택. 직전 지역은 제외.
    반환값: ("region", 지역명) / "back"
    """

    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.regions = RUN.selectable_regions()
        self.hover = None
        self._img_cache = {}

    def _card_rect(self, i):
        W, H = self.W, self.H
        n = len(self.regions)
        cw = int(W * 0.16)
        gap = int(W * 0.03)
        total = n * cw + (n - 1) * gap
        ox = (W - total) // 2
        cy = int(H * 0.30)
        ch = int(H * 0.42)
        x = ox + i * (cw + gap)
        return pygame.Rect(x, cy, cw, ch)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
        elif event.type == pygame.MOUSEMOTION:
            self.hover = None
            for i in range(len(self.regions)):
                if self._card_rect(i).collidepoint(event.pos):
                    self.hover = i
                    break
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, reg in enumerate(self.regions):
                if self._card_rect(i).collidepoint(event.pos):
                    play_click(); return ("region", reg)
        return None

    def update(self, dt):
        pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        seg = RUN.segment + 1
        draw_text(surf, f"{seg}구간 — 지역 선택", self.fonts["title"], BLACK, W // 2, int(H * 0.12))
        draw_text(surf, "탐험할 지역을 선택하세요.", self.fonts["hint"], GRAY_D, W // 2, int(H * 0.19))

        for i, reg in enumerate(self.regions):
            r = self._card_rect(i)
            info = run_data.REGION_INFO[reg]
            bg = CARD_HOV if self.hover == i else CARD_BG
            pygame.draw.rect(surf, bg, r, border_radius=10)
            pygame.draw.rect(surf, (BLACK if self.hover != i else SEL_COL), r,
                             3 if self.hover == i else 2, border_radius=10)
            # 지역 배경 자리 (회색) — 추후 스프라이트
            inner = pygame.Rect(r.x + 10, r.y + 10, r.width - 20, int(r.height * 0.55))
            pygame.draw.rect(surf, (215, 215, 215), inner, border_radius=6)
            draw_text(surf, reg, self.fonts["menu"], GRAY_D, inner.centerx, inner.centery)
            # 이름/설명
            draw_text(surf, info["title"], self.fonts["hint_bold"], BLACK,
                      r.centerx, r.y + int(r.height * 0.72))
            self._draw_desc(info["desc"], r)

        # 직전 지역 안내
        if RUN.last_region:
            draw_text(surf, f"(직전 지역 '{RUN.last_region}'은 선택할 수 없습니다)",
                      self.fonts["small"], GRAY, W // 2, int(H * 0.80))

    def _draw_desc(self, desc, r):
        surf = self.screen
        # 간단히 한 줄
        draw_text(surf, desc, self.fonts["small"], GRAY_D, r.centerx, r.y + int(r.height * 0.85))