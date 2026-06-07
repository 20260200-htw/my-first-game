import pygame
import os
import random
import math
import sys as _sys
_sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
import save_data
from utils import *
from data.recruit_data import (
    RECRUIT_POOL, GRADE_INFO, GRADE_ORDER, grade_of, names_by_grade
)

PANEL_BG = (245, 245, 245)
DIV      = (210, 210, 210)
TAB_ON   = (0, 0, 0)
GOLD_COL = (200, 160, 40)
CONTACT_COL = (90, 150, 210)

PULL1_COST  = 10
PULL10_COST = 100
DEBUG_GOLD  = 1000

# 화면 모드(가운데 큰 영역에 표시할 내용)
TAB_RATE     = "rate"      # 확률 및 리스트
TAB_PULL     = "pull"      # 모집(1회/10회)
TAB_EXCHANGE = "exchange"  # 교환


def _roll_one():
    """확률에 따라 한 번 뽑기 → 등급 결정 후 그 등급 풀에서 랜덤 캐릭터."""
    r = random.random()
    acc = 0.0
    chosen_grade = GRADE_ORDER[-1]
    for g in GRADE_ORDER:
        acc += GRADE_INFO[g]["rate"]
        if r <= acc:
            chosen_grade = g
            break
    pool = names_by_grade(chosen_grade)
    return random.choice(pool) if pool else None


def _roll_multi(n):
    """n회 뽑기. 10회면 4급 이상 1개 보장."""
    results = [_roll_one() for _ in range(n)]
    if n >= 10:
        if not any(grade_of(x) <= 4 for x in results if x):
            # 4급 이상 강제 1개 (4급으로)
            idx = random.randrange(len(results))
            pool = names_by_grade(4)
            if pool:
                results[idx] = random.choice(pool)
    return results


class RecruitScreen:
    """모집 화면.
    탭: 확률 / 모집(1·10회) / 교환
    반환값: "back"
    """

    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.tab = TAB_PULL

        # 뽑기 결과 연출 상태
        self.pull_results = []      # 이번에 뽑은 이름 리스트
        self.pull_rewards = []      # 각 결과의 (신규/연락망량) 정보
        self.anim_timer = 0.0
        self.anim_state = None      # None / "spin" / "reveal"
        self.SPIN_TIME = 900        # 카드 회전 시간(ms)
        self.REVEAL_STEP = 130      # reveal 시 카드 1장씩 공개 간격(ms)
        self.revealed_n = 0         # 현재까지 공개된 카드 수
        self.spin_phase = 0.0       # 카드 회전 위상(계속 증가) — 미공개 카드 회전용

        # 교환/리스트 스크롤
        self._scroll_y = 0.0
        self._target_y = 0.0
        self._drag = False
        self._drag_y0 = 0
        self._drag_org = 0.0

        self._img_cache = {}

    # ── 영역 ──────────────────────────────────────────────────────
    def _back_rect(self):
        return pygame.Rect(int(self.W*0.03), int(self.H*0.04), 90, 32)

    def _debug_rect(self):
        W, H = self.W, self.H
        return pygame.Rect(int(W*0.80), int(H*0.05), int(W*0.16), int(H*0.05))

    def _main_area(self):
        W, H = self.W, self.H
        return pygame.Rect(int(W*0.10), int(H*0.15), int(W*0.80), int(H*0.55))

    def _popup_rect(self):
        """결과 팝업 창 영역."""
        W, H = self.W, self.H
        return pygame.Rect(int(W*0.12), int(H*0.14), int(W*0.76), int(H*0.60))

    def _confirm_rect(self):
        """결과 팝업 하단 확인 버튼."""
        W, H = self.W, self.H
        bw, bh = int(W*0.16), int(H*0.055)
        pr = self._popup_rect()
        return pygame.Rect(W//2 - bw//2, pr.bottom - bh - int(H*0.015), bw, bh)

    def _tab_rects(self):
        """하단 탭 3개 (대칭). 가운데 탭은 위/아래로 1회·10회 나뉨."""
        W, H = self.W, self.H
        tw = int(W*0.22)
        th = int(H*0.10)
        y  = int(H*0.78)
        cxs = [int(W*0.22), int(W*0.50), int(W*0.78)]
        return [pygame.Rect(cx - tw//2, y, tw, th) for cx in cxs]

    def _pull1_rect(self):
        r = self._tab_rects()[1]
        return pygame.Rect(r.x, r.y, r.width, r.height//2 - 2)

    def _pull10_rect(self):
        r = self._tab_rects()[1]
        return pygame.Rect(r.x, r.y + r.height//2 + 2, r.width, r.height//2 - 2)

    # ── 이벤트 ────────────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.anim_state == "reveal":
                    # 결과창 닫기
                    self.anim_state = None
                    self.pull_results = []
                    self.pull_rewards = []
                    self.revealed_n = 0
                    return None
                if self.anim_state == "spin":
                    return None
                return "back"

        elif event.type == pygame.MOUSEWHEEL:
            if self.tab in (TAB_RATE, TAB_EXCHANGE):
                self._target_y -= event.y * int(self.H*0.08)
                self._clamp_scroll()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._back_rect().collidepoint(event.pos):
                return "back"
            if self._debug_rect().collidepoint(event.pos):
                save_data.add_gold(DEBUG_GOLD)
                return None
            # 스크롤 가능한 탭이면 드래그 시작
            if self.tab in (TAB_RATE, TAB_EXCHANGE) and self._main_area().collidepoint(event.pos):
                self._drag = True
                self._drag_y0 = event.pos[1]
                self._drag_org = self._scroll_y
            self._handle_click(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._drag = False
            self._target_y = self._scroll_y
            self._clamp_scroll()

        elif event.type == pygame.MOUSEMOTION:
            if self._drag:
                dy = event.pos[1] - self._drag_y0
                self._scroll_y = self._drag_org - dy
                self._target_y = self._scroll_y
                self._clamp_scroll()

        return None

    def _handle_click(self, pos):
        # 결과 팝업이 떠 있으면: 확인 버튼만 처리, 다른 입력 차단
        if self.anim_state == "reveal":
            # 아직 공개 중이면 클릭으로 전부 즉시 공개(스킵)
            if self.revealed_n < len(self.pull_results):
                self.revealed_n = len(self.pull_results)
                return
            if self._confirm_rect().collidepoint(pos):
                self.anim_state = None
                self.pull_results = []
                self.pull_rewards = []
                self.revealed_n = 0
            return
        if self.anim_state == "spin":
            return  # 회전 중 입력 차단

        # 탭 전환
        tabs = self._tab_rects()
        if tabs[0].collidepoint(pos):
            self.tab = TAB_RATE; self._reset_scroll(); return
        if tabs[2].collidepoint(pos):
            self.tab = TAB_EXCHANGE; self._reset_scroll(); return
        # 가운데: 1회 / 10회 (모집 탭일 때만 실제 동작)
        if self._pull1_rect().collidepoint(pos):
            self.tab = TAB_PULL
            if self.anim_state is None:
                self._do_pull(1)
            return
        if self._pull10_rect().collidepoint(pos):
            self.tab = TAB_PULL
            if self.anim_state is None:
                self._do_pull(10)
            return
        # 교환 탭: 캐릭터 교환 클릭
        if self.tab == TAB_EXCHANGE:
            self._handle_exchange_click(pos)

    # ── 뽑기 실행 ─────────────────────────────────────────────────
    def _do_pull(self, n):
        cost = PULL1_COST if n == 1 else PULL10_COST
        if not save_data.spend_gold(cost):
            return  # 골드 부족
        results = _roll_multi(n)
        self.pull_results = results
        self.pull_rewards = []
        for name in results:
            if name is None:
                self.pull_rewards.append(("none", 0))
                continue
            if save_data.is_recruited(name):
                # 중복 → 연락망 지급
                c = GRADE_INFO[grade_of(name)]["dup_contact"]
                save_data.add_contact(c)
                self.pull_rewards.append(("dup", c))
            else:
                save_data.add_recruited(name)
                self.pull_rewards.append(("new", 0))
        self.anim_state = "spin"
        self.anim_timer = 0.0
        self.spin_phase = 0.0
        self.revealed_n = 0

    # ── 교환 ──────────────────────────────────────────────────────
    def _exchange_list(self):
        """교환 가능 캐릭터(1~3급) 중 미보유."""
        out = []
        for g in (1, 2, 3):
            for name in names_by_grade(g):
                if not save_data.is_recruited(name):
                    out.append(name)
        return out

    def _exchange_item_rect(self, i):
        area = self._main_area()
        ih = int(self.H*0.09)
        gap = int(self.H*0.015)
        y = area.y + int(self.H*0.02) + i*(ih+gap) - int(self._scroll_y)
        return pygame.Rect(area.x + int(self.W*0.05), y, area.width - int(self.W*0.10), ih)

    def _handle_exchange_click(self, pos):
        for i, name in enumerate(self._exchange_list()):
            if self._exchange_item_rect(i).collidepoint(pos):
                cost = GRADE_INFO[grade_of(name)]["exchange_cost"]
                if cost and save_data.spend_contact(cost):
                    save_data.add_recruited(name)
                return

    # ── 스크롤 ────────────────────────────────────────────────────
    def _reset_scroll(self):
        self._scroll_y = 0.0
        self._target_y = 0.0

    def _content_h(self):
        if self.tab == TAB_EXCHANGE:
            n = len(self._exchange_list())
            ih = int(self.H*0.09); gap = int(self.H*0.015)
            return max(0, n*(ih+gap) + int(self.H*0.04))
        if self.tab == TAB_RATE:
            return int(self.H*0.70)
        return 0

    def _clamp_scroll(self):
        area = self._main_area()
        mx = max(0, self._content_h() - area.height)
        self._target_y = max(0, min(mx, self._target_y))
        self._scroll_y = max(0, min(mx, self._scroll_y))

    # ── 업데이트 ──────────────────────────────────────────────────
    def update(self, dt):
        diff = self._target_y - self._scroll_y
        if abs(diff) > 0.5:
            self._scroll_y += diff * min(1.0, 14.0*dt/1000.0)
        else:
            self._scroll_y = self._target_y

        if self.anim_state == "spin":
            self.spin_phase += dt
            self.anim_timer += dt
            if self.anim_timer >= self.SPIN_TIME:
                self.anim_state = "reveal"
                self.anim_timer = 0.0
                self.revealed_n = 0
        elif self.anim_state == "reveal":
            self.spin_phase += dt   # 미공개 카드 계속 회전
            n = len(self.pull_results)
            if self.revealed_n < n:
                self.anim_timer += dt
                while self.anim_timer >= self.REVEAL_STEP and self.revealed_n < n:
                    self.anim_timer -= self.REVEAL_STEP
                    self.revealed_n += 1

    # ── 그리기 ────────────────────────────────────────────────────
    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        draw_text(surf, "모집", self.fonts["title"], BLACK, W//2, int(H*0.07))

        br = self._back_rect()
        pygame.draw.rect(surf, BLACK, br, 1)
        draw_text(surf, "◀ 뒤로", self.fonts["hint"], BLACK, br.centerx, br.centery)

        # 재화 표시
        draw_text_left(surf, f"골드 {save_data.get_gold()}", self.fonts["hint_bold"],
                       GOLD_COL, int(W*0.12), int(H*0.075))
        draw_text_left(surf, f"연락망 {save_data.get_contact()}", self.fonts["hint_bold"],
                       CONTACT_COL, int(W*0.30), int(H*0.075))

        # 디버그 충전 버튼
        dr = self._debug_rect()
        pygame.draw.rect(surf, PANEL_BG, dr, border_radius=5)
        pygame.draw.rect(surf, DIV, dr, 1, border_radius=5)
        draw_text(surf, f"[디버그] +{DEBUG_GOLD} 골드", self.fonts["small"], GRAY_D, dr.centerx, dr.centery)

        # 중앙 큰 영역
        area = self._main_area()
        pygame.draw.rect(surf, BLACK, area, 2)

        if self.tab == TAB_PULL:
            self._draw_pull_area(area)
        elif self.tab == TAB_RATE:
            self._draw_rate_area(area)
        elif self.tab == TAB_EXCHANGE:
            self._draw_exchange_area(area)

        # 하단 탭
        self._draw_tabs()

        # 결과 팝업 (spin/reveal 상태) — 최상단 레이어
        if self.anim_state in ("spin", "reveal") and self.pull_results:
            self._draw_result_popup()

    def _draw_result_popup(self):
        """뽑기 연출/결과를 별도 팝업 창에 표시. spin이면 회전, reveal이면 공개+확인버튼."""
        W, H = self.W, self.H
        surf = self.screen
        # 어둡게 덮기
        veil = pygame.Surface((W, H), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 150))
        surf.blit(veil, (0, 0))
        # 창
        pr = self._popup_rect()
        pygame.draw.rect(surf, WHITE, pr, border_radius=10)
        pygame.draw.rect(surf, BLACK, pr, 2, border_radius=10)

        title = "모집 중..." if self.anim_state == "spin" else "모집 결과"
        draw_text(surf, title, self.fonts["menu"], BLACK, pr.centerx, pr.y + int(H*0.045))

        # 카드 영역 (spin/reveal 동일하게 고정 — 확인 버튼 공간 항상 비워둠)
        cr = self._confirm_rect()
        card_area = pygame.Rect(pr.x + int(W*0.02), pr.y + int(H*0.09),
                                pr.width - int(W*0.04),
                                cr.top - int(H*0.015) - (pr.y + int(H*0.09)))

        if self.anim_state == "spin":
            self._draw_spin_cards(card_area)
        else:
            self._draw_reveal(card_area)
            # 모든 카드가 공개된 뒤에만 확인 버튼 표시
            if self.revealed_n >= len(self.pull_results):
                cr = self._confirm_rect()
                pygame.draw.rect(surf, BLACK, cr, border_radius=6)
                draw_text(surf, "확인", self.fonts["menu"], WHITE, cr.centerx, cr.centery)

    def _card_grid(self, area):
        """결과 카드들의 Rect 리스트 계산 (1개=중앙 1장, 그 외=5x2)."""
        n = len(self.pull_results)
        if n <= 1:
            cols, rows = 1, 1
        else:
            cols, rows = 5, 2
        gap = int(self.W * 0.01)
        cw = (area.width - gap*(cols+1)) // cols
        cw = min(cw, int(self.W*0.13))
        ch = min(int(cw * 1.35), (area.height - gap*(rows+1)) // rows)
        total_w = cols*cw + (cols-1)*gap
        total_h = rows*ch + (rows-1)*gap
        ox = area.centerx - total_w//2
        oy = area.centery - total_h//2
        rects = []
        for i in range(n):
            row = i // cols
            col = i % cols
            x = ox + col*(cw+gap)
            y = oy + row*(ch+gap)
            rects.append(pygame.Rect(x, y, cw, ch))
        return rects

    def _draw_spin_cards(self, area):
        """모든 카드 슬롯에서 회전 연출 (spin 상태)."""
        rects = self._card_grid(area)
        for r in rects:
            self._draw_spinning_card(r)

    def _draw_spinning_card(self, r):
        """검회색 카드가 가로로 회전하는 모습 한 장."""
        surf = self.screen
        t = self.spin_phase / 1000.0
        scale = abs(math.cos(t * math.pi * 5))   # 0~1 반복(회전감)
        w = max(2, int(r.width * scale))
        card = pygame.Rect(r.centerx - w//2, r.y, w, r.height)
        pygame.draw.rect(surf, (90, 90, 100), card, border_radius=8)
        pygame.draw.rect(surf, (60, 60, 70), card, 2, border_radius=8)

    # ── 탭 ────────────────────────────────────────────────────────
    def _draw_tabs(self):
        surf = self.screen
        tabs = self._tab_rects()
        # 확률
        self._tab_button(tabs[0], "확률", self.tab == TAB_RATE)
        # 교환
        self._tab_button(tabs[2], "교환", self.tab == TAB_EXCHANGE)
        # 가운데: 1회 / 10회
        r1 = self._pull1_rect()
        r10 = self._pull10_rect()
        self._tab_button(r1,  f"1회 뽑기 ({PULL1_COST})",   False)
        self._tab_button(r10, f"10회 뽑기 ({PULL10_COST})", False)

    def _tab_button(self, r, label, active):
        surf = self.screen
        if active:
            pygame.draw.rect(surf, TAB_ON, r, border_radius=5)
            draw_text(surf, label, self.fonts["menu"], WHITE, r.centerx, r.centery)
        else:
            pygame.draw.rect(surf, WHITE, r, border_radius=5)
            pygame.draw.rect(surf, BLACK, r, 2, border_radius=5)
            draw_text(surf, label, self.fonts["menu"], BLACK, r.centerx, r.centery)

    # ── 모집 결과/연출 ────────────────────────────────────────────
    def _draw_pull_area(self, area):
        surf = self.screen
        # spin/reveal 은 팝업에서 그리므로, 여기서는 안내문만
        draw_text(surf, "모집할 인원을 선택하세요.", self.fonts["menu"], GRAY,
                  area.centerx, area.centery)

    def _draw_spin(self, area):
        """검회색 카드가 빙글빙글 도는 연출."""
        surf = self.screen
        t = self.anim_timer / self.SPIN_TIME
        # 가로 스케일을 사인으로 흔들어 회전처럼 보이게
        cw = int(area.width * 0.14)
        ch = int(area.height * 0.6)
        scale = abs(math.cos(t * math.pi * 6))   # 0~1 반복
        w = max(2, int(cw * scale))
        cx, cy = area.centerx, area.centery
        card = pygame.Rect(cx - w//2, cy - ch//2, w, ch)
        pygame.draw.rect(surf, (90, 90, 100), card, border_radius=8)
        pygame.draw.rect(surf, (60, 60, 70), card, 2, border_radius=8)

    def _draw_reveal(self, area):
        """뽑힌 카드들을 1→N 순서로 한 장씩 공개. 미공개 카드는 뒷면(회색)."""
        surf = self.screen
        rects = self._card_grid(area)
        for i, name in enumerate(self.pull_results):
            if i >= len(rects):
                break
            r = rects[i]
            if i < self.revealed_n:
                # 공개된 카드: 등급색 앞면
                self._draw_result_card(r, name,
                                       self.pull_rewards[i] if i < len(self.pull_rewards) else None)
            else:
                # 미공개 카드: 계속 회전
                self._draw_spinning_card(r)

    def _draw_result_card(self, r, name, reward):
        surf = self.screen
        grade = grade_of(name) if name else 5
        info = GRADE_INFO[grade]
        col = info["color"]
        pygame.draw.rect(surf, col, r, border_radius=8)
        pygame.draw.rect(surf, BLACK, r, 2, border_radius=8)
        # 등급
        draw_text(surf, info["name"], self.fonts["small_bold"], BLACK, r.centerx, r.y + int(r.height*0.12))
        # 이름
        draw_text(surf, name or "-", self.fonts["small"], BLACK, r.centerx, r.centery)
        # 신규/중복
        if reward:
            kind, amt = reward
            if kind == "new":
                draw_text(surf, "NEW", self.fonts["small_bold"], (200,40,40), r.centerx, r.bottom - int(r.height*0.12))
            elif kind == "dup":
                draw_text(surf, f"연락망+{amt}", self.fonts["small"], (40,80,160), r.centerx, r.bottom - int(r.height*0.12))

    # ── 확률 및 리스트 ────────────────────────────────────────────
    def _draw_rate_area(self, area):
        surf = self.screen
        prev = surf.get_clip(); surf.set_clip(area)
        x = area.x + int(self.W*0.04)
        y = area.y + int(self.H*0.03) - int(self._scroll_y)
        line_h = int(self.H*0.05)
        for g in GRADE_ORDER:
            info = GRADE_INFO[g]
            # 색 박스
            box = pygame.Rect(x, y, int(self.W*0.03), int(self.H*0.03))
            pygame.draw.rect(surf, info["color"], box)
            pygame.draw.rect(surf, BLACK, box, 1)
            draw_text_left(surf, f"{info['name']}   {info['rate']*100:.0f}%   "
                                 f"(보유 동료 {len(names_by_grade(g))}명)",
                           self.fonts["hint"], BLACK, x + int(self.W*0.04), box.centery)
            y += line_h
        surf.set_clip(prev)

    # ── 교환 ──────────────────────────────────────────────────────
    def _draw_exchange_area(self, area):
        surf = self.screen
        prev = surf.get_clip(); surf.set_clip(area)
        items = self._exchange_list()
        if not items:
            surf.set_clip(prev)
            draw_text(surf, "교환 가능한 동료가 없습니다.", self.fonts["hint"], GRAY,
                      area.centerx, area.centery)
            return
        for i, name in enumerate(items):
            r = self._exchange_item_rect(i)
            if r.bottom < area.top or r.top > area.bottom:
                continue
            grade = grade_of(name)
            info = GRADE_INFO[grade]
            pygame.draw.rect(surf, PANEL_BG, r, border_radius=5)
            pygame.draw.rect(surf, info["color"], r, 3, border_radius=5)
            draw_text_left(surf, f"{info['name']}  {name}", self.fonts["hint_bold"], BLACK,
                           r.x + int(self.W*0.02), r.centery)
            cost = info["exchange_cost"]
            can = save_data.get_contact() >= (cost or 0)
            cc = (40,120,60) if can else (180,60,60)
            draw_text(surf, f"연락망 {cost}", self.fonts["hint"], cc,
                      r.right - int(self.W*0.07), r.centery)
        surf.set_clip(prev)