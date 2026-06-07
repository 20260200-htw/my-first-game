import pygame
import os
import sys as _sys
_sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from utils import *
from run_state import RUN
from data import run_data

CARD_BG  = (238, 238, 238)
CARD_HOV = (250, 245, 220)
SEL_COL  = (60, 140, 220)


class RewardScreen:
    """전투 승리 후 보상 선택.
    kind="skill" 이면 스킬 3택1, "item" 이면 아이템 3택1.
    보스 보상은 special_item 지정 시 확정 지급 + 추가 선택.
    반환값: "done"
    """

    def __init__(self, screen, W, H, fonts, kind="skill", special_item=None, gold=0):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.kind = kind
        self.gold = gold
        self.special_item = special_item  # 보스 확정 드랍 아이템 키
        self._special_given = False
        self.hover = None
        self.taken = False

        if kind == "skill":
            owned = [s["name"] for s in RUN.skills_owned]
            self.choices = run_data.roll_skill_choices(3, owned)
        else:
            self.choices = run_data.roll_item_choices(3, RUN.items)

        # 골드 지급 (보상 진입 시 1회)
        if gold:
            RUN.add_gold(gold)
        # 보스 확정 아이템 지급
        if special_item and special_item not in RUN.items:
            RUN.add_item(special_item)
            self._special_given = True

    def _card_rect(self, i):
        W, H = self.W, self.H
        n = max(1, len(self.choices))
        cw = int(W * 0.20)
        gap = int(W * 0.03)
        total = n * cw + (n - 1) * gap
        ox = (W - total) // 2
        cy = int(H * 0.34)
        ch = int(H * 0.38)
        return pygame.Rect(ox + i*(cw+gap), cy, cw, ch)

    def _skip_rect(self):
        W, H = self.W, self.H
        bw, bh = int(W*0.16), int(H*0.06)
        return pygame.Rect(W//2 - bw//2, int(H*0.82), bw, bh)

    def handle_event(self, event):
        if self.taken:
            return None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "done"  # 건너뛰기
        elif event.type == pygame.MOUSEMOTION:
            self.hover = None
            for i in range(len(self.choices)):
                if self._card_rect(i).collidepoint(event.pos):
                    self.hover = i; break
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._skip_rect().collidepoint(event.pos):
                return "done"
            for i in range(len(self.choices)):
                if self._card_rect(i).collidepoint(event.pos):
                    self._take(i)
                    return "done"
        return None

    def _take(self, i):
        choice = self.choices[i]
        if self.kind == "skill":
            import copy
            RUN.add_skill(copy.deepcopy(choice))
        else:
            RUN.add_item(choice)  # choice 는 아이템 키
        self.taken = True

    def update(self, dt):
        pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        title = "스킬 획득" if self.kind == "skill" else "아이템 획득"
        draw_text(surf, title, self.fonts["title"], BLACK, W//2, int(H*0.12))
        draw_text(surf, "하나를 선택하세요. (ESC: 건너뛰기)", self.fonts["hint"], GRAY_D, W//2, int(H*0.19))

        if self.gold:
            draw_text(surf, f"골드 +{self.gold}", self.fonts["hint_bold"], (200,160,40), W//2, int(H*0.25))
        if self._special_given:
            it = run_data.ITEMS[self.special_item]
            draw_text(surf, f"보스 전리품 획득: {it['name']}", self.fonts["hint_bold"], (170,70,160),
                      W//2, int(H*0.29))

        for i, choice in enumerate(self.choices):
            r = self._card_rect(i)
            bg = CARD_HOV if self.hover == i else CARD_BG
            pygame.draw.rect(surf, bg, r, border_radius=10)
            pygame.draw.rect(surf, (SEL_COL if self.hover==i else BLACK), r,
                             3 if self.hover==i else 2, border_radius=10)
            if self.kind == "skill":
                self._draw_skill(r, choice)
            else:
                self._draw_item(r, choice)

        # 건너뛰기
        sr = self._skip_rect()
        pygame.draw.rect(surf, PANEL := (245,245,245), sr, border_radius=6)
        pygame.draw.rect(surf, GRAY, sr, 1, border_radius=6)
        draw_text(surf, "건너뛰기", self.fonts["hint"], GRAY_D, sr.centerx, sr.centery)

    def _draw_skill(self, r, skill):
        surf = self.screen
        draw_text(surf, skill["name"], self.fonts["menu"], BLACK, r.centerx, r.y + int(r.height*0.16))
        info = f"위력 {skill['power']} | {skill['type']}"
        if skill.get("hits", 1) > 1:
            info += f" | {skill['hits']}회"
        draw_text(surf, info, self.fonts["small_bold"], GRAY_D, r.centerx, r.y + int(r.height*0.34))
        for j, line in enumerate(skill.get("desc", [])):
            draw_text(surf, line, self.fonts["small"], GRAY_D, r.centerx, r.y + int(r.height*(0.50 + j*0.10)))

    def _draw_item(self, r, key):
        surf = self.screen
        it = run_data.ITEMS[key]
        draw_text(surf, it["name"], self.fonts["menu"], BLACK, r.centerx, r.y + int(r.height*0.18))
        # 설명 (여러 줄 대비 단순 1줄)
        draw_text(surf, it["desc"], self.fonts["small"], GRAY_D, r.centerx, r.centery + int(r.height*0.05))
