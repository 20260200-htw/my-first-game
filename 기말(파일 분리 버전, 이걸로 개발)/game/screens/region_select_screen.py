import pygame
import os
import sys as _sys

_sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
)

from utils import *
from run_state import RUN
from data import run_data


CARD_BG  = (238, 238, 238)
CARD_HOV = (250, 245, 220)
SEL_COL  = (60, 140, 220)
DIV      = (210, 210, 210)


class RegionSelectScreen:
    """
    구간 시작 시 지역 선택 화면
    반환값: ("region", 지역명) / "back"
    """

    def __init__(self, screen, W, H, fonts, only_region=None):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts

        self.regions = RUN.selectable_regions()

        if only_region is not None:
            self.regions = [only_region]

        self.hover = None

        # 이미지 캐시: region -> pygame.Surface
        self._img_cache = {}

    # -----------------------------
    # layout
    # -----------------------------
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

    # -----------------------------
    # image handling
    # -----------------------------
    def _load_region_image(self, reg):
        """이미지 1회 로딩"""
        if reg in self._img_cache:
            return self._img_cache[reg]

        info = run_data.REGION_INFO.get(reg, {})
        path = info.get("image")

        if not path:
            # fallback (이미지 없을 때)
            surf = pygame.Surface((200, 200))
            surf.fill((200, 200, 200))
            self._img_cache[reg] = surf
            return surf

        try:
            img = pygame.image.load(path).convert_alpha()
        except Exception:
            img = pygame.Surface((200, 200))
            img.fill((180, 180, 180))

        self._img_cache[reg] = img
        return img

    def _fit_image_cover(self, img, size):
        """카드 영역을 꽉 채우는 cover 방식"""
        iw, ih = img.get_size()
        tw, th = size

        scale = max(tw / iw, th / ih)
        new_size = (int(iw * scale), int(ih * scale))

        img = pygame.transform.smoothscale(img, new_size)

        surf = pygame.Surface(size, pygame.SRCALPHA)
        rect = img.get_rect(center=(tw // 2, th // 2))
        surf.blit(img, rect)

        return surf

    def _get_region_image(self, reg, size):
        """캐시 + resize"""
        img = self._load_region_image(reg)
        return self._fit_image_cover(img, size)

    # -----------------------------
    # input
    # -----------------------------
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
                    play_click()
                    return ("region", reg)

        return None

    def update(self, dt):
        pass

    # -----------------------------
    # draw
    # -----------------------------
    def draw(self):
        W, H = self.W, self.H
        surf = self.screen

        surf.fill(WHITE)

        seg = RUN.segment + 1

        draw_text(
            surf,
            f"{seg}구간 — 지역 선택",
            self.fonts["title"],
            BLACK,
            W // 2,
            int(H * 0.12),
        )

        draw_text(
            surf,
            "탐험할 지역을 선택하세요.",
            self.fonts["hint"],
            GRAY_D,
            W // 2,
            int(H * 0.19),
        )

        for i, reg in enumerate(self.regions):
            r = self._card_rect(i)
            info = run_data.REGION_INFO[reg]

            # 카드 배경
            bg = CARD_HOV if self.hover == i else CARD_BG

            pygame.draw.rect(surf, bg, r, border_radius=10)
            pygame.draw.rect(
                surf,
                SEL_COL if self.hover == i else (0, 0, 0),
                r,
                3 if self.hover == i else 2,
                border_radius=10,
            )

            # -----------------------------
            # 이미지 영역 (기존 회색 박스 대체)
            # -----------------------------
            inner = pygame.Rect(
                r.x + 10,
                r.y + 10,
                r.width - 20,
                int(r.height * 0.55),
            )

            img = self._get_region_image(reg, (inner.width, inner.height))
            surf.blit(img, inner.topleft)

            # 지역 코드명 (작게 표시)
            draw_text(
                surf,
                reg,
                self.fonts["menu"],
                GRAY,
                inner.centerx,
                inner.centery,
            )

            # 제목
            draw_text(
                surf,
                info["title"],
                self.fonts["hint_bold"],
                BLACK,
                r.centerx,
                r.y + int(r.height * 0.72),
            )

            # 설명
            self._draw_desc(info["desc"], r)

        # 이전 지역 제한 안내
        if RUN.last_region:
            draw_text(
                surf,
                f"(직전 지역 '{RUN.last_region}'은 선택할 수 없습니다)",
                self.fonts["small"],
                GRAY,
                W // 2,
                int(H * 0.80),
            )

    def _draw_desc(self, desc, r):
        draw_text(
            self.screen,
            desc,
            self.fonts["small"],
            GRAY_D,
            r.centerx,
            r.y + int(r.height * 0.85),
        )