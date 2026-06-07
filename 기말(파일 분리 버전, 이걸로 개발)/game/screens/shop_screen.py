import pygame
import os
import sys as _sys
_sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from utils import *
from run_state import RUN
from data import run_data

CARD_BG  = (238, 238, 238)
SOLD_BG  = (210, 210, 210)
DIV      = (210, 210, 210)


class ShopScreen:
    """상점: 스킬/아이템/회복 구매. 골드 사용.
    반환값: "done"
    """

    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.hover = None

        # 판매 목록 구성: 스킬 2 + 아이템 2 + 회복 1
        owned = [s["name"] for s in RUN.skills_owned]
        skills = run_data.roll_skill_choices(2, owned)
        items  = run_data.roll_item_choices(2, RUN.items)
        self.entries = []
        for s in skills:
            self.entries.append({"type": "skill", "data": s,
                                 "price": run_data.SHOP_PRICE["skill"], "sold": False})
        for k in items:
            self.entries.append({"type": "item", "data": k,
                                 "price": run_data.SHOP_PRICE["item"], "sold": False})
        self.entries.append({"type": "heal", "data": None,
                             "price": run_data.SHOP_PRICE["heal"], "sold": False})

    def _entry_rect(self, i):
        W, H = self.W, self.H
        cols = len(self.entries)
        cw = int(W * 0.15)
        gap = int(W * 0.02)
        total = cols*cw + (cols-1)*gap
        ox = (W - total)//2
        cy = int(H * 0.32)
        ch = int(H * 0.40)
        return pygame.Rect(ox + i*(cw+gap), cy, cw, ch)

    def _buy_rect(self, i):
        r = self._entry_rect(i)
        bw, bh = int(r.width*0.8), int(self.H*0.05)
        return pygame.Rect(r.centerx - bw//2, r.bottom - bh - int(self.H*0.02), bw, bh)

    def _leave_rect(self):
        W, H = self.W, self.H
        bw, bh = int(W*0.16), int(H*0.06)
        return pygame.Rect(W - bw - int(W*0.04), H - bh - int(H*0.05), bw, bh)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "done"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._leave_rect().collidepoint(event.pos):
                return "done"
            for i, e in enumerate(self.entries):
                if e["sold"]:
                    continue
                if self._buy_rect(i).collidepoint(event.pos):
                    self._buy(i)
                    return None
        return None

    def _buy(self, i):
        e = self.entries[i]
        if RUN.gold < e["price"]:
            return
        if e["type"] == "heal":
            RUN.spend_gold(e["price"])
            RUN.heal(run_data.SHOP_HEAL_PCT)
            e["sold"] = True
        elif e["type"] == "skill":
            RUN.spend_gold(e["price"])
            import copy
            RUN.add_skill(copy.deepcopy(e["data"]))
            e["sold"] = True
        elif e["type"] == "item":
            if e["data"] in RUN.items:
                return
            RUN.spend_gold(e["price"])
            RUN.add_item(e["data"])
            e["sold"] = True

    def update(self, dt):
        pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        draw_text(surf, "상점", self.fonts["title"], BLACK, W//2, int(H*0.12))
        draw_text_left(surf, f"보유 골드: {RUN.gold}", self.fonts["hint_bold"], (200,160,40),
                       int(W*0.10), int(H*0.20))
        draw_text_left(surf, f"HP {RUN.hp_cur}/{RUN.hp_max}", self.fonts["hint_bold"], (200,60,60),
                       int(W*0.30), int(H*0.20))

        for i, e in enumerate(self.entries):
            r = self._entry_rect(i)
            bg = SOLD_BG if e["sold"] else CARD_BG
            pygame.draw.rect(surf, bg, r, border_radius=10)
            pygame.draw.rect(surf, BLACK, r, 2, border_radius=10)
            self._draw_entry(r, e, i)

        # 나가기
        lr = self._leave_rect()
        pygame.draw.rect(surf, BLACK, lr, border_radius=6)
        draw_text(surf, "나가기", self.fonts["menu"], WHITE, lr.centerx, lr.centery)

    def _draw_entry(self, r, e, i):
        surf = self.screen
        # 종류 헤더
        head = {"skill": "스킬", "item": "아이템", "heal": "회복"}[e["type"]]
        draw_text(surf, head, self.fonts["small_bold"], GRAY_D, r.centerx, r.y + int(r.height*0.08))

        if e["type"] == "skill":
            s = e["data"]
            draw_text(surf, s["name"], self.fonts["hint_bold"], BLACK, r.centerx, r.y + int(r.height*0.24))
            info = f"위력 {s['power']} | {s['type']}"
            if s.get("hits",1) > 1: info += f" | {s['hits']}회"
            draw_text(surf, info, self.fonts["small"], GRAY_D, r.centerx, r.y + int(r.height*0.38))
        elif e["type"] == "item":
            it = run_data.ITEMS[e["data"]]
            draw_text(surf, it["name"], self.fonts["hint_bold"], BLACK, r.centerx, r.y + int(r.height*0.24))
            draw_text(surf, it["desc"], self.fonts["small"], GRAY_D, r.centerx, r.y + int(r.height*0.42))
        else:
            draw_text(surf, f"체력 {run_data.SHOP_HEAL_PCT}% 회복", self.fonts["hint_bold"], BLACK,
                      r.centerx, r.y + int(r.height*0.30))

        # 구매 버튼
        br = self._buy_rect(i)
        if e["sold"]:
            pygame.draw.rect(surf, GRAY, br, border_radius=5)
            draw_text(surf, "구매 완료", self.fonts["small"], WHITE, br.centerx, br.centery)
        else:
            can = RUN.gold >= e["price"]
            pygame.draw.rect(surf, (BLACK if can else (200,200,200)), br, border_radius=5)
            draw_text(surf, f"{e['price']} G", self.fonts["small_bold"],
                      (WHITE if can else (150,150,150)), br.centerx, br.centery)
