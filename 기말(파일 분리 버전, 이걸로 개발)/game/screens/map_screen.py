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
        self.t = 0.0       # 경과 시간 (정비 버튼 점멸용)
        self._bg = None        # 현재 구역 배경 Surface (없으면 None)
        self._bg_region = None # 배경을 로드한 구역명 (캐시 무효화용)
        self._load_bg()

    # ── 배경 ──────────────────────────────────────────────────────
    def _load_bg(self):
        """현재 구역 배경을 화면 크기에 맞춰 로드(캐시). 없으면 None."""
        region = RUN.region
        if region == self._bg_region and self._bg is not None:
            return
        self._bg_region = region
        self._bg = None
        path = run_data.region_background_path(region)
        if path:
            try:
                img = pygame.image.load(path).convert()
                self._bg = pygame.transform.smoothscale(img, (self.W, self.H))
            except Exception:
                self._bg = None

    # ── 좌측 하단: (이제 하단 중앙에 통합되어 사용 안 함) ──────────
    def _draw_status_panel(self, g):
        pass

    # ── 하단 중앙: 레벨 | 골드 + 체력바 ──────────────────────────
    def _draw_bottom_center(self):
        W, H = self.W, self.H
        surf = self.screen
        import save_data
        g = save_data.get_growth("주인공")
        cx = W // 2
        bar_w = int(W * 0.26)
        bar_h = int(H * 0.034)
        cy = int(H * 0.90)
        # 레벨 | 골드 (체력바 위, 한 줄)
        ty = cy - int(H * 0.045)
        info = f"Lv. {g['level']}   |   골드: {RUN.gold}"
        draw_text(surf, info, self.fonts["hint_bold"], BLACK, cx, ty,
                  outline=WHITE, outline_w=2)
        # 체력바
        bar = pygame.Rect(cx - bar_w // 2, cy, bar_w, bar_h)
        pygame.draw.rect(surf, (60, 60, 60), bar, border_radius=4)
        ratio = 0 if RUN.hp_max <= 0 else max(0.0, min(1.0, RUN.hp_cur / RUN.hp_max))
        fill = pygame.Rect(bar.x, bar.y, int(bar_w * ratio), bar_h)
        if ratio > 0.5:
            hp_col = (90, 190, 90)
        elif ratio > 0.25:
            hp_col = (220, 190, 60)
        else:
            hp_col = (210, 70, 70)
        if fill.width > 0:
            pygame.draw.rect(surf, hp_col, fill, border_radius=4)
        pygame.draw.rect(surf, BLACK, bar, 2, border_radius=4)
        draw_text(surf, f"{RUN.hp_cur} / {RUN.hp_max}", self.fonts["small_bold"], WHITE,
                  bar.centerx, bar.centery, outline=BLACK, outline_w=2)

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
        self.t += dt / 1000.0   # dt 는 ms 단위 → 초로 변환 (점멸 주기 정상화)
        # 구역이 바뀌었으면 배경 갱신
        if RUN.region != self._bg_region:
            self._load_bg()

    # ── 그리기 ────────────────────────────────────────────────────
    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        # 구역 배경 (없으면 흰색)
        if self._bg is not None:
            surf.blit(self._bg, (0, 0))
        else:
            surf.fill(WHITE)

        seg = RUN.segment
        region = RUN.region or "-"
        draw_text(surf, f"{seg}구간", self.fonts["title"], BLACK, W // 2, int(H * 0.09),
                  outline=WHITE, outline_w=3)
        draw_text(surf, region, self.fonts["menu"], BLACK, W // 2, int(H * 0.155),
                  outline=WHITE, outline_w=2)

        import save_data
        g = save_data.get_growth("주인공")
        has_points = bool(g.get("basic_point", 0) or g.get("extra_point", 0))

        # ── 정비 버튼 (미분배 포인트 있으면 천천히 점멸) ──
        mr = self._menu_rect()
        blink = False
        if has_points:
            import math
            # 0~1 사인파로 천천히 점멸 (주기 ≈ 4초)
            pulse = 0.5 + 0.5 * math.sin(self.t * 1.6)
            # 배경을 알림색(노랑)으로 채우고 테두리 강조
            bg_col = (int(255), int(238 - 60*pulse), int(150 - 80*pulse))
            pygame.draw.rect(surf, bg_col, mr, border_radius=5)
            pygame.draw.rect(surf, (200, 150, 30), mr, max(2, int(2 + 3*pulse)), border_radius=5)
            blink = True
        else:
            pygame.draw.rect(surf, WHITE, mr, border_radius=5)
            pygame.draw.rect(surf, BLACK, mr, 1, border_radius=5)
        draw_text(surf, "정비", self.fonts["hint"], BLACK, mr.centerx, mr.centery)
        if has_points:
            # 버튼 우측에 작은 알림 표시 (배경 위 — 흰 외곽선)
            draw_text_left(surf, "● 미분배 포인트", self.fonts["small"], (200, 120, 30),
                           mr.right + int(W*0.01), mr.centery, outline=WHITE, outline_w=2)

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
                rad = r.width // 2
                pygame.draw.circle(surf, col, r.center, rad)
                # 진입 가능/현재 노드: 노드에 딱 붙는 두꺼운 색 링
                if is_cur:
                    pygame.draw.circle(surf, CUR_RING, r.center, rad + 2, 6)
                elif is_reach:
                    ring = REACH_RING if self.hover != (li, ci) else (255, 210, 80)
                    pygame.draw.circle(surf, ring, r.center, rad + 2, 6)
                pygame.draw.circle(surf, BLACK, r.center, rad, 3)
                # 노드 내부 라벨은 외곽선 없이 (요구사항: 노드 내부 제외)
                draw_text(surf, style["label"], self.fonts["small_bold"], WHITE, r.centerx, r.centery)

        # 하단 중앙: 골드 + 체력바 (진입 가능한 노드가 있을 때만 = 회차 진행 중)
        if reachable:
            self._draw_bottom_center()