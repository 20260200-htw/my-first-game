import pygame
import os
import sys as _sys
_sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
import save_data
from utils import *
from data.characters_data import ALLY_DEFS
from data.recruit_data import RECRUIT_POOL

PANEL_BG   = (245, 245, 245)
SLOT_BG    = (235, 235, 235)
SLOT_EMPTY = (248, 248, 248)
DIV        = (210, 210, 210)
HILITE     = (60, 140, 220)


def _char_def(name):
    """캐릭터 정의를 ALLY_DEFS 또는 RECRUIT_POOL 에서 찾는다."""
    if name in ALLY_DEFS:
        return ALLY_DEFS[name]
    return RECRUIT_POOL.get(name, {})


def _char_level(name):
    """캐릭터 레벨. 주인공은 성장 데이터, 동료는 고정값(없으면 1)."""
    if name == "주인공":
        return save_data.get_growth("주인공").get("level", 1)
    return _char_def(name).get("level", 1)


class FormationScreen:
    """편성 화면.
    좌측: 5칸 (1번 주인공 고정, 2~5번 동료)
    우측: 보유 동료 리스트 (휠/드래그 스크롤, 클릭으로 편성/해제)
    반환값: "back"
    """

    MAX_PARTY = 5          # 주인공 포함 최대 인원
    DRAG_THRESH = 8        # 클릭/드래그 구분 임계값(px)

    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self._img_cache = {}

        # 보유 동료 = 모집으로 획득한 동료
        self.owned = save_data.get_recruited()

        # 현재 편성된 동료 (2~5번). 보유하지 않은 이름은 제거.
        self.party = [n for n in save_data.get_party() if n in self.owned]

        # 우측 리스트 스크롤
        self._scroll_y = 0.0
        self._target_y = 0.0
        self._drag_active = False
        self._drag_start_y = 0
        self._drag_origin = 0.0

    # ── 보유 동료 중 편성 안 된 목록 (우측에 표시) ─────────────────
    def _available(self):
        return [n for n in self.owned if n not in self.party]

    # ── 이미지 ────────────────────────────────────────────────────
    def _profile(self, name, size):
        path = _char_def(name).get("profile", "")
        key = (path, size)
        if key in self._img_cache:
            return self._img_cache[key]
        img = None
        if path and os.path.exists(path):
            try:
                raw = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(raw, (size, size))
            except Exception:
                img = None
        self._img_cache[key] = img
        return img

    # ── 좌측 슬롯 Rect ────────────────────────────────────────────
    def _slot_rect(self, idx):
        """idx: 0~4 (0=주인공). 좌측 세로 5칸."""
        W, H = self.W, self.H
        sw = int(W * 0.13)
        sh = int(H * 0.135)
        gap = int(H * 0.018)
        start_y = int(H * 0.18)
        cx = int(W * 0.25)
        y = start_y + idx * (sh + gap)
        return pygame.Rect(cx - sw // 2, y, sw, sh)

    # ── 우측 리스트 Rect ──────────────────────────────────────────
    def _list_area(self):
        """좌측 5칸 전체가 차지하는 세로 범위와 동일하게 맞춘 스크롤 영역."""
        W, H = self.W, self.H
        sh = int(H * 0.135)
        gap = int(H * 0.018)
        start_y = int(H * 0.18)
        total_h = self.MAX_PARTY * sh + (self.MAX_PARTY - 1) * gap
        cx = int(W * 0.75)
        sw = int(W * 0.13)
        return pygame.Rect(cx - sw // 2, start_y, sw, total_h)

    def _list_item_rect(self, i):
        """우측 리스트 i번째 항목 Rect (스크롤 반영). 좌측 칸과 동일 크기."""
        area = self._list_area()
        ih = int(self.H * 0.135)
        gap = int(self.H * 0.018)
        y = area.y + i * (ih + gap) - int(self._scroll_y)
        return pygame.Rect(area.x, y, area.width, ih)

    def _list_content_h(self):
        n = len(self._available())
        ih = int(self.H * 0.135)
        gap = int(self.H * 0.018)
        return max(0, n * (ih + gap) - gap)

    def _clamp_scroll(self):
        area = self._list_area()
        max_scroll = max(0, self._list_content_h() - area.height)
        self._target_y = max(0, min(max_scroll, self._target_y))
        self._scroll_y = max(0, min(max_scroll, self._scroll_y))

    # ── 이벤트 ────────────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._save()
                return "back"

        elif event.type == pygame.MOUSEWHEEL:
            self._target_y -= event.y * int(self.H * 0.08)
            self._clamp_scroll()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 뒤로 버튼
            if self._back_rect().collidepoint(event.pos):
                self._save()
                return "back"
            # 리스트 영역이면 드래그 시작
            if self._list_area().collidepoint(event.pos):
                self._drag_active = True
                self._drag_start_y = event.pos[1]
                self._drag_origin = self._scroll_y
            else:
                self._drag_active = False
                self._handle_click(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._drag_active:
                dist = abs(event.pos[1] - self._drag_start_y)
                self._drag_active = False
                if dist < self.DRAG_THRESH:
                    # 드래그 아닌 클릭 → 리스트 항목 선택
                    self._handle_click(event.pos)
                else:
                    self._target_y = self._scroll_y
                    self._clamp_scroll()

        elif event.type == pygame.MOUSEMOTION:
            if self._drag_active:
                dy = event.pos[1] - self._drag_start_y
                self._scroll_y = self._drag_origin - dy
                self._target_y = self._scroll_y
                self._clamp_scroll()

        return None

    def _handle_click(self, pos):
        # 좌측 슬롯 클릭: 편성된 동료(2~5번)면 해제
        for idx in range(1, self.MAX_PARTY):
            if self._slot_rect(idx).collidepoint(pos):
                slot_i = idx - 1   # party 리스트 인덱스
                if slot_i < len(self.party):
                    # 해제 → 뒤 번호가 앞으로 당겨짐 (리스트라 자동)
                    self.party.pop(slot_i)
                    self._save()
                return

        # 우측 리스트 클릭: 빈 자리가 있으면 편성
        avail = self._available()
        for i, name in enumerate(avail):
            if self._list_item_rect(i).collidepoint(pos):
                if len(self.party) < self.MAX_PARTY - 1:   # 최대 4명
                    self.party.append(name)
                    self._save()
                return

    def _save(self):
        save_data.set_party(self.party)

    def _back_rect(self):
        return pygame.Rect(int(self.W * 0.03), int(self.H * 0.04), 90, 32)

    def update(self, dt):
        # 스크롤 부드러운 보간
        diff = self._target_y - self._scroll_y
        if abs(diff) > 0.5:
            self._scroll_y += diff * min(1.0, 14.0 * dt / 1000.0)
        else:
            self._scroll_y = self._target_y

    # ── 그리기 ────────────────────────────────────────────────────
    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        draw_text(surf, "편성", self.fonts["title"], BLACK, W // 2, int(H * 0.07))

        br = self._back_rect()
        pygame.draw.rect(surf, BLACK, br, 1)
        draw_text(surf, "◀ 뒤로", self.fonts["hint"], BLACK, br.centerx, br.centery)

        # ── 좌측 5칸 ────────────────────────────────────────────
        draw_text(surf, "편성", self.fonts["hint_bold"], GRAY_D, int(W * 0.25), int(H * 0.14))
        for idx in range(self.MAX_PARTY):
            r = self._slot_rect(idx)
            if idx == 0:
                self._draw_unit(r, "주인공", tag="1")
            else:
                slot_i = idx - 1
                if slot_i < len(self.party):
                    self._draw_unit(r, self.party[slot_i], tag=str(idx + 1))
                else:
                    self._draw_empty(r, str(idx + 1))

        # ── 우측 리스트 ─────────────────────────────────────────
        draw_text(surf, "보유 동료", self.fonts["hint_bold"], GRAY_D, int(W * 0.75), int(H * 0.14))
        area = self._list_area()
        prev_clip = surf.get_clip()
        surf.set_clip(area)
        avail = self._available()
        if not avail:
            surf.set_clip(prev_clip)
            draw_text(surf, "보유한 동료가 없습니다.", self.fonts["hint"], GRAY,
                      area.centerx, area.centery)
        else:
            for i, name in enumerate(avail):
                r = self._list_item_rect(i)
                if r.bottom < area.top or r.top > area.bottom:
                    continue
                self._draw_unit(r, name)
            surf.set_clip(prev_clip)

    def _draw_unit(self, r, name, tag=None):
        """프로필 + 이름 + 레벨 카드. (이미지 위, 텍스트 아래로 분리)"""
        surf = self.screen
        pygame.draw.rect(surf, SLOT_BG, r, border_radius=6)
        pygame.draw.rect(surf, BLACK, r, 2, border_radius=6)

        # 이미지 영역: 카드 상단 ~ 62% 높이
        img_size = int(r.height * 0.52)
        img_y = r.y + int(r.height * 0.06)
        img = self._profile(name, img_size)
        if img:
            surf.blit(img, (r.centerx - img_size // 2, img_y))
        else:
            ph = pygame.Rect(r.centerx - img_size // 2, img_y, img_size, img_size)
            pygame.draw.rect(surf, (215, 215, 215), ph)

        # 이름 / 레벨: 이미지 아래 영역
        draw_text(surf, name, self.fonts["small_bold"], BLACK,
                  r.centerx, r.bottom - int(r.height * 0.24))
        draw_text(surf, f"Lv.{_char_level(name)}", self.fonts["small"], GRAY_D,
                  r.centerx, r.bottom - int(r.height * 0.10))

        # 자리 번호 태그
        if tag is not None:
            tr = pygame.Rect(r.x + 4, r.y + 4, 22, 20)
            pygame.draw.rect(surf, BLACK, tr, border_radius=3)
            draw_text(surf, tag, self.fonts["small"], WHITE, tr.centerx, tr.centery)

    def _draw_empty(self, r, tag):
        surf = self.screen
        pygame.draw.rect(surf, SLOT_EMPTY, r, border_radius=6)
        pygame.draw.rect(surf, DIV, r, 1, border_radius=6)
        draw_text(surf, "비어있음", self.fonts["small"], GRAY, r.centerx, r.centery)
        tr = pygame.Rect(r.x + 4, r.y + 4, 22, 20)
        pygame.draw.rect(surf, DIV, tr, border_radius=3)
        draw_text(surf, tag, self.fonts["small"], GRAY_D, tr.centerx, tr.centery)