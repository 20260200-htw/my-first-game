import pygame
import os
import sys as _sys
_sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
import save_data
from utils import *
from data.explore_data import REGIONS, REGION_LAYOUT, REGION_ORDER, roll_event

PANEL_BG  = (245, 245, 245)
REGION_BG = (220, 220, 220)
LOCK_BG   = (170, 170, 170)
DIV       = (200, 200, 200)
SEL_COL   = (60, 140, 220)

# 진행 단계
PH_NONE     = None
PH_EXPLORING = "exploring"   # "탐험 진행 중" 표시
PH_RESULT    = "result"      # 이벤트 결과 표시

EXPLORE_HOLD = 900   # 탐험 진행 중 표시 시간(ms)


class ExploreScreen:
    """탐험 화면.
    십자 지도에서 구역 선택 → '탐험 시작하기' → 진행 팝업 → 이벤트 결과.
    act_key: 어느 막에서 진입했는지 (구역 해금 판정).
    반환값: "back"
    """

    def __init__(self, screen, W, H, fonts, act_key):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.act_key = act_key

        self.unlocked = save_data.unlocked_explore_regions(act_key)
        self.selected = self.unlocked[0] if self.unlocked else None

        # 진행 팝업 상태
        self.phase = PH_NONE
        self.timer = 0.0
        self.cur_event = None        # 뽑힌 이벤트
        self.result_lines = []       # 결과로 보여줄 텍스트 줄들
        self.dlg_idx = 0             # 텍스트 이벤트 진행 인덱스

    # ── 영역 ──────────────────────────────────────────────────────
    def _back_rect(self):
        return pygame.Rect(int(self.W*0.03), int(self.H*0.04), 90, 32)

    def _start_rect(self):
        """우측 하단 탐험 시작 버튼."""
        W, H = self.W, self.H
        bw, bh = int(W*0.20), int(H*0.07)
        return pygame.Rect(W - bw - int(W*0.04), H - bh - int(H*0.05), bw, bh)

    def _grid_origin(self):
        """십자 지도 그리드 기준 좌표/셀 크기."""
        W, H = self.W, self.H
        cell = int(min(W, H) * 0.18)
        gap  = int(cell * 0.12)
        gw = 3*cell + 2*gap
        gh = 3*cell + 2*gap
        ox = (W - gw)//2
        oy = int(H*0.18)
        return ox, oy, cell, gap

    def _region_rect(self, key):
        col, row = REGION_LAYOUT[key]
        ox, oy, cell, gap = self._grid_origin()
        x = ox + col*(cell+gap)
        y = oy + row*(cell+gap)
        return pygame.Rect(x, y, cell, cell)

    def _region_at(self, pos):
        for key in REGION_ORDER:
            if self._region_rect(key).collidepoint(pos):
                return key
        return None

    # ── 이벤트 ────────────────────────────────────────────────────
    def handle_event(self, event):
        # 진행 팝업이 떠 있으면 팝업 입력만
        if self.phase is not None:
            return self._handle_popup_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._back_rect().collidepoint(event.pos):
                return "back"
            # 구역 선택
            key = self._region_at(event.pos)
            if key and key in self.unlocked:
                self.selected = key
                return None
            # 탐험 시작
            if self._start_rect().collidepoint(event.pos) and self.selected:
                self._start_explore()
        return None

    def _handle_popup_event(self, event):
        click = (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)
        key_ok = (event.type == pygame.KEYDOWN and event.key in (
            pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_ESCAPE))

        if self.phase == PH_EXPLORING:
            return None  # 진행 중엔 입력 무시(시간 경과로 자동 전환)

        if self.phase == PH_RESULT and (click or key_ok):
            # 텍스트 이벤트면 다음 줄, 끝이면 팝업 닫기
            if self.cur_event and self.cur_event.get("kind") == "text":
                if self.dlg_idx + 1 < len(self.cur_event.get("dialogue", [])):
                    self.dlg_idx += 1
                    return None
            # 닫기 → 지도 복귀
            self._close_popup()
        return None

    def _start_explore(self):
        self.phase = PH_EXPLORING
        self.timer = 0.0
        self.cur_event = roll_event(self.selected)
        self.dlg_idx = 0

    def _close_popup(self):
        # 보상 지급(텍스트 이벤트)
        if self.cur_event and self.cur_event.get("reward_gold"):
            save_data.add_gold(self.cur_event["reward_gold"])
        self.phase = PH_NONE
        self.cur_event = None
        self.dlg_idx = 0

    def update(self, dt):
        if self.phase == PH_EXPLORING:
            self.timer += dt
            if self.timer >= EXPLORE_HOLD:
                self.phase = PH_RESULT
                self.timer = 0.0

    # ── 그리기 ────────────────────────────────────────────────────
    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        draw_text(surf, "탐험", self.fonts["title"], BLACK, W//2, int(H*0.07))

        br = self._back_rect()
        pygame.draw.rect(surf, BLACK, br, 1)
        draw_text(surf, "◀ 뒤로", self.fonts["hint"], BLACK, br.centerx, br.centery)

        # 십자 지도
        for key in REGION_ORDER:
            self._draw_region(key)

        # 선택된 구역 정보
        if self.selected:
            reg = REGIONS[self.selected]
            draw_text(surf, reg["title"], self.fonts["menu"], BLACK, W//2, int(H*0.80))
            draw_text(surf, reg["desc"], self.fonts["hint"], GRAY_D, W//2, int(H*0.85))

        # 탐험 시작 버튼
        sr = self._start_rect()
        can = self.selected is not None
        if can:
            pygame.draw.rect(surf, BLACK, sr, border_radius=6)
            draw_text(surf, "탐험 시작하기", self.fonts["menu"], WHITE, sr.centerx, sr.centery)
        else:
            pygame.draw.rect(surf, PANEL_BG, sr, border_radius=6)
            pygame.draw.rect(surf, DIV, sr, 1, border_radius=6)
            draw_text(surf, "구역을 선택하세요", self.fonts["hint"], GRAY, sr.centerx, sr.centery)

        # 진행 팝업
        if self.phase is not None:
            self._draw_popup()

    def _draw_region(self, key):
        surf = self.screen
        r = self._region_rect(key)
        unlocked = key in self.unlocked
        # TODO: 구역 배경 스프라이트 (현재 회색)
        if unlocked:
            pygame.draw.rect(surf, REGION_BG, r, border_radius=8)
        else:
            pygame.draw.rect(surf, LOCK_BG, r, border_radius=8)
        # 선택 테두리
        if key == self.selected and unlocked:
            pygame.draw.rect(surf, SEL_COL, r, 4, border_radius=8)
        else:
            pygame.draw.rect(surf, BLACK, r, 2, border_radius=8)
        # 라벨
        if unlocked:
            draw_text(surf, REGIONS[key]["title"].replace(" 구역",""),
                      self.fonts["menu"], BLACK, r.centerx, r.centery)
        else:
            draw_text(surf, "🔒", self.fonts["menu"], (90,90,90), r.centerx, r.centery)

    def _draw_popup(self):
        W, H = self.W, self.H
        surf = self.screen
        # 어둡게
        veil = pygame.Surface((W, H), pygame.SRCALPHA)
        veil.fill((0,0,0,150))
        surf.blit(veil, (0,0))
        pr = pygame.Rect(int(W*0.12), int(H*0.16), int(W*0.76), int(H*0.60))
        # TODO: 뒤에 구역 스프라이트 배경 (현재 흰 창)
        pygame.draw.rect(surf, WHITE, pr, border_radius=10)
        pygame.draw.rect(surf, BLACK, pr, 2, border_radius=10)

        if self.phase == PH_EXPLORING:
            draw_text(surf, "탐험 진행 중...", self.fonts["title"], BLACK, pr.centerx, pr.centery)
            return

        # 결과
        ev = self.cur_event
        if ev is None:
            draw_text(surf, "아무 일도 없었다.", self.fonts["menu"], BLACK, pr.centerx, pr.centery)
        elif ev["kind"] == "battle":
            draw_text(surf, "전투 발생!", self.fonts["title"], (180,40,40), pr.centerx, pr.centery - int(H*0.04))
            pool = ev.get("enemy_pools", [])
            if pool:
                draw_text(surf, pool[0], self.fonts["menu"], BLACK, pr.centerx, pr.centery + int(H*0.04))
        elif ev["kind"] == "text":
            dlg = ev.get("dialogue", [])
            if dlg:
                line = dlg[min(self.dlg_idx, len(dlg)-1)]
                draw_text(surf, line.get("speaker",""), self.fonts["hint_bold"], GRAY_D,
                          pr.centerx, pr.y + int(H*0.10))
                draw_text(surf, line.get("text",""), self.fonts["menu"], BLACK,
                          pr.centerx, pr.centery)

        # 안내 (확인)
        draw_text(surf, "클릭하여 계속", self.fonts["hint"], GRAY,
                  pr.centerx, pr.bottom - int(H*0.05))
