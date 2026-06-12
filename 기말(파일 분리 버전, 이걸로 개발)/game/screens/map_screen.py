import pygame
import os
import sys as _sys
_sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from utils import *
from run_state import RUN
from data import run_data

NODE_STYLE = {
    run_data.NODE_START:  {"color": (120, 170, 120), "label": "시작"},
    run_data.NODE_MID:    {"color": (210, 140, 90),  "label": "중간"},
    run_data.NODE_BATTLE: {"color": (200, 90, 90),  "label": "전투"},
    run_data.NODE_ELITE:  {"color": (170, 70, 160), "label": "엘리트"},
    run_data.NODE_EVENT:  {"color": (90, 150, 200), "label": "이벤트"},
    run_data.NODE_REWARD: {"color": (90, 180, 110), "label": "보상"},
    run_data.NODE_SHOP:   {"color": (210, 170, 60), "label": "상점"},
    run_data.NODE_BOSS:   {"color": (120, 40, 40),  "label": "보스"},
    run_data.NODE_MAW:    {"color": (40, 20, 60),   "label": "마왕"},
}

LINE_COL  = (205, 205, 205)
LINE_OPEN = (90, 160, 230)   # 진입 가능한 경로 강조
DONE_COL  = (150, 150, 150)
CUR_RING  = (60, 140, 220)
REACH_RING= (90, 200, 120)


class MapScreen:
    """분기 노드맵. 진입 가능한 노드만 클릭 가능.
    반환값:
      ("node", (layer, col), 노드타입) — 노드 진입
      "menu" — 정비 화면
      "back" — 나가기(디버그)
    """

    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.hover = None  # (layer, col)

    # ── 좌표 ──────────────────────────────────────────────────────
    def _node_rect(self, layer, col):
        W, H = self.W, self.H
        nL = len(RUN.layers)
        margin_x = int(W * 0.06)
        usable_x = W - margin_x * 2
        x = margin_x + int(usable_x * (layer / max(1, nL - 1)))
        # 세로 배치: 해당 층 노드 개수에 맞춰 균등
        row = RUN.layers[layer]
        nC = len(row)
        cy0 = int(H * 0.30)
        cy1 = int(H * 0.72)
        if nC == 1:
            y = (cy0 + cy1) // 2
        else:
            y = cy0 + int((cy1 - cy0) * (col / (nC - 1)))
        # 층이 많으면(13단계) 반지름 축소
        rad = int(min(W, H) * 0.040)
        if nL >= 10:
            rad = int(min(W, H) * 0.030)
        return pygame.Rect(x - rad, y - rad, rad * 2, rad * 2)

    def _menu_rect(self):
        W, H = self.W, self.H
        return pygame.Rect(int(W*0.03), int(H*0.04), int(W*0.12), int(H*0.06))

    def _reachable(self):
        return RUN.reachable_next()

    # ── 이벤트 ────────────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
        elif event.type == pygame.MOUSEMOTION:
            self.hover = None
            for (l, c) in self._reachable():
                if self._node_rect(l, c).collidepoint(event.pos):
                    self.hover = (l, c); break
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._menu_rect().collidepoint(event.pos):
                return "menu"
            for (l, c) in self._reachable():
                if self._node_rect(l, c).collidepoint(event.pos):
                    play_click()
                    ntype = RUN.enter_node(l, c)
                    return ("node", (l, c), ntype)
        return None

    def update(self, dt):
        pass

    # ── 그리기 ────────────────────────────────────────────────────
    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        seg = RUN.segment
        region = RUN.region or "-"
        seg_label = "마왕성" if seg >= run_data.FINAL_SEGMENT else f"{seg}구간 · {region}"
        draw_text(surf, seg_label, self.fonts["title"], BLACK, W // 2, int(H * 0.12))

        # 자원
        import save_data
        g = save_data.get_growth("주인공")
        draw_text_left(surf, f"Lv.{g['level']}", self.fonts["hint_bold"], BLACK, int(W*0.18), int(H*0.06))
        draw_text_left(surf, f"골드 {RUN.gold}", self.fonts["hint_bold"], (200,160,40), int(W*0.30), int(H*0.06))
        draw_text_left(surf, f"HP {RUN.hp_cur}/{RUN.hp_max}", self.fonts["hint_bold"], (200,60,60), int(W*0.44), int(H*0.06))
        if g.get("basic_point",0) or g.get("extra_point",0):
            draw_text_left(surf, "미분배 포인트 있음", self.fonts["small"], (40,120,60), int(W*0.62), int(H*0.06))

        mr = self._menu_rect()
        pygame.draw.rect(surf, BLACK, mr, 1, border_radius=5)
        draw_text(surf, "정비", self.fonts["hint"], BLACK, mr.centerx, mr.centery)

        reachable = set(self._reachable())

        # 연결선
        for li in range(len(RUN.layers) - 1):
            for ci, node in enumerate(RUN.layers[li]):
                a = self._node_rect(li, ci).center
                for ec in node["edges"]:
                    b = self._node_rect(li + 1, ec).center
                    # 현재 위치에서 나가는 간선이면 강조
                    is_open = (RUN.cur_layer == li and RUN.cur_col == ci)
                    pygame.draw.line(surf, LINE_OPEN if is_open else LINE_COL, a, b,
                                     5 if is_open else 3)

        # 노드
        for li, row in enumerate(RUN.layers):
            for ci, node in enumerate(row):
                r = self._node_rect(li, ci)
                style = NODE_STYLE.get(node["type"], NODE_STYLE[run_data.NODE_BATTLE])
                is_cur = (li == RUN.cur_layer and ci == RUN.cur_col)
                is_done = (li < RUN.cur_layer)
                is_reach = (li, ci) in reachable
                col = DONE_COL if (is_done and not is_cur) else style["color"]
                pygame.draw.circle(surf, col, r.center, r.width // 2)
                pygame.draw.circle(surf, BLACK, r.center, r.width // 2, 2)
                if is_cur:
                    pygame.draw.circle(surf, CUR_RING, r.center, r.width // 2 + 6, 4)
                elif is_reach:
                    ring = REACH_RING if self.hover != (li, ci) else (255, 210, 80)
                    pygame.draw.circle(surf, ring, r.center, r.width // 2 + 6, 4)
                draw_text(surf, style["label"], self.fonts["small_bold"], WHITE, r.centerx, r.centery)

        # 안내
        if reachable:
            draw_text(surf, "다음 노드를 선택하세요.", self.fonts["menu"], BLACK, W//2, int(H*0.85))