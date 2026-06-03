import pygame
import os
import sys as _sys
_sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
import save_data
from utils import *
from data.characters_data import ALLY_DEFS

# ── 색상 ──────────────────────────────────────────────────────────
PANEL_BG   = (245, 245, 245)
BAR_BG     = (210, 210, 210)
BAR_EXP    = ( 80, 160, 255)
BTN_UP     = ( 60, 180,  80)
BTN_DN     = (200,  60,  60)
BTN_DIS    = (180, 180, 180)   # 비활성 버튼
DIVIDER    = (180, 180, 180)


def _exp_to_next(level):
    """레벨업에 필요한 총 경험치."""
    return level * 100


def _remaining_points(g):
    """현재 남은 포인트 = 레벨 × 1.5 − 사용량"""
    base  = int(g["level"] * 1.5)
    used  = (g["phys_level"]  - 1) + (g["magic_level"] - 1)
    return base - used


class GrowthScreen:
    """성장 화면.
    반환값: "back" / "skill_config" (스킬 설정, 미구현)
    """

    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts  = fonts
        self._profile_cache = {}

        # 저장된 성장 데이터 로드
        base = ALLY_DEFS["주인공"]
        self.g = dict(save_data.get_growth("주인공"))

        # 기본값 보정 (저장 없을 때)
        for k, v in [("level",1),("exp",0),("phys_level",1),("magic_level",1),
                     ("hp_bonus",0),("spd_bonus",0),("deal_bonus",0),("take_bonus",0)]:
            self.g.setdefault(k, v)

    # ── 리소스 ────────────────────────────────────────────────────
    def _load_profile(self):
        path = ALLY_DEFS["주인공"].get("profile", "assets/mainB_profile.png")
        if not os.path.exists(path):
            path = ALLY_DEFS["주인공"].get("sprite", "assets/main_character_B.png")
        if path in self._profile_cache:
            return self._profile_cache[path]
        if os.path.exists(path):
            try:
                raw = pygame.image.load(path).convert_alpha()
                size = int(self.H * 0.28)
                img  = pygame.transform.smoothscale(raw, (size, size))
                self._profile_cache[path] = img
                return img
            except Exception:
                pass
        return None

    # ── 파생 스탯 계산 ────────────────────────────────────────────
    def _hp(self):
        return ALLY_DEFS["주인공"]["hp_max"] + self.g["hp_bonus"] * 10

    def _speed(self):
        return ALLY_DEFS["주인공"]["speed"] + self.g["spd_bonus"] // 5

    def _deal_pct(self):
        return self.g["deal_bonus"] // 5

    def _take_pct(self):
        return self.g["take_bonus"] // 5

    # ── 버튼 Rect 빌더 ────────────────────────────────────────────
    def _btn(self, cx, cy, w=36, h=28):
        return pygame.Rect(cx - w // 2, cy - h // 2, w, h)

    # ── 이벤트 ────────────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._save()
                return "back"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._handle_click(event.pos)
        return None

    def _handle_click(self, pos):
        W, H = self.W, self.H
        g = self.g
        pts = _remaining_points(g)

        # ── 뒤로가기 버튼 ──
        if self._back_rect().collidepoint(pos):
            self._save()
            return "back"

        # ── 좌측 패널 버튼들 ──
        # 물리 레벨 UP
        r = self._btn(int(W * 0.18), int(H * 0.55))
        if r.collidepoint(pos) and pts > 0:
            g["phys_level"] += 1

        # 물리 레벨 DOWN
        r = self._btn(int(W * 0.30), int(H * 0.55))
        if r.collidepoint(pos) and g["phys_level"] > 1:
            g["phys_level"] -= 1

        # 마법 레벨 UP
        r = self._btn(int(W * 0.18), int(H * 0.65))
        if r.collidepoint(pos) and pts > 0:
            g["magic_level"] += 1

        # 마법 레벨 DOWN
        r = self._btn(int(W * 0.30), int(H * 0.65))
        if r.collidepoint(pos) and g["magic_level"] > 1:
            g["magic_level"] -= 1

        # ── 우측 패널 버튼들 ──
        rx = int(W * 0.62)
        # 체력 UP / DOWN
        if self._btn(rx,         int(H * 0.30)).collidepoint(pos):
            g["hp_bonus"] += 1
        if self._btn(rx + int(W*0.12), int(H * 0.30)).collidepoint(pos) and g["hp_bonus"] > 0:
            g["hp_bonus"] -= 1

        # 속도 UP / DOWN
        if self._btn(rx,         int(H * 0.42)).collidepoint(pos):
            g["spd_bonus"] += 1
        if self._btn(rx + int(W*0.12), int(H * 0.42)).collidepoint(pos) and g["spd_bonus"] > 0:
            g["spd_bonus"] -= 1

        # 가하는 피해 UP / DOWN
        if self._btn(rx,         int(H * 0.54)).collidepoint(pos):
            g["deal_bonus"] += 1
        if self._btn(rx + int(W*0.12), int(H * 0.54)).collidepoint(pos) and g["deal_bonus"] > 0:
            g["deal_bonus"] -= 1

        # 받는 피해 감소 UP / DOWN
        if self._btn(rx,         int(H * 0.66)).collidepoint(pos):
            g["take_bonus"] += 1
        if self._btn(rx + int(W*0.12), int(H * 0.66)).collidepoint(pos) and g["take_bonus"] > 0:
            g["take_bonus"] -= 1

        # 스킬 설정 버튼
        if self._skill_btn_rect().collidepoint(pos):
            return "skill_config"

        self._save()
        return None

    def _save(self):
        save_data.set_growth(self.g, "주인공")

    def _back_rect(self):
        return pygame.Rect(int(self.W * 0.03), int(self.H * 0.04), 100, 34)

    def _skill_btn_rect(self):
        W, H = self.W, self.H
        return pygame.Rect(int(W * 0.55), int(H * 0.78), int(W * 0.30), 38)

    def update(self, dt): pass

    # ── 그리기 ────────────────────────────────────────────────────
    def draw(self):
        W, H = self.W, self.H
        surf  = self.screen
        g     = self.g
        pts   = _remaining_points(g)
        surf.fill(WHITE)

        # 제목
        draw_text(surf, "성장", self.fonts["title"], BLACK, W // 2, int(H * 0.07))

        # 뒤로가기
        br = self._back_rect()
        pygame.draw.rect(surf, BLACK, br, 1)
        draw_text(surf, "◀ 뒤로", self.fonts["hint"], BLACK, br.centerx, br.centery)

        # 중앙 구분선
        pygame.draw.line(surf, DIVIDER, (W // 2, int(H * 0.14)), (W // 2, int(H * 0.90)), 1)

        # ══ 좌측 패널 ═══════════════════════════════════════════
        lx = int(W * 0.25)   # 좌측 중심 X

        # 프로필 이미지
        img = self._load_profile()
        img_size = int(H * 0.28)
        img_rect = pygame.Rect(lx - img_size // 2, int(H * 0.15), img_size, img_size)
        if img:
            surf.blit(img, img_rect)
        else:
            pygame.draw.rect(surf, PANEL_BG, img_rect)
            pygame.draw.rect(surf, GRAY,     img_rect, 2)
            draw_text(surf, "주인공", self.fonts["menu"], GRAY_D, img_rect.centerx, img_rect.centery)

        # 레벨
        lv_y = int(H * 0.48)
        draw_text(surf, f"Lv. {g['level']}", self.fonts["menu"], BLACK, lx, lv_y)

        # 경험치 바
        exp_y  = int(H * 0.535)
        bar_w  = int(W * 0.38)
        bar_h  = 14
        bar_x  = lx - bar_w // 2
        need   = _exp_to_next(g["level"])
        ratio  = min(1.0, g["exp"] / need) if need > 0 else 0
        pygame.draw.rect(surf, BAR_BG,  (bar_x, exp_y, bar_w, bar_h), border_radius=4)
        if ratio > 0:
            pygame.draw.rect(surf, BAR_EXP, (bar_x, exp_y, int(bar_w * ratio), bar_h), border_radius=4)
        pygame.draw.rect(surf, GRAY,    (bar_x, exp_y, bar_w, bar_h), 1, border_radius=4)
        draw_text(surf, f"EXP  {g['exp']} / {need}", self.fonts["hint"], GRAY_D, lx, exp_y + bar_h + 12)

        # 남은 포인트
        draw_text(surf, f"남은 포인트:  {pts}", self.fonts["menu"],
                  (180, 40, 40) if pts == 0 else BLACK, lx, int(H * 0.615))

        # 물리 레벨
        phy_y = int(H * 0.70)
        draw_text_left(surf, "물리 레벨", self.fonts["hint"], BLACK, int(W * 0.08), phy_y)
        draw_text(surf, str(g["phys_level"]), self.fonts["menu"], BLACK, int(W * 0.24), phy_y)
        self._draw_updown(surf, int(W * 0.18), int(W * 0.30), phy_y,
                          pts > 0, g["phys_level"] > 1)

        # 마법 레벨
        mag_y = int(H * 0.80)
        draw_text_left(surf, "마법 레벨", self.fonts["hint"], BLACK, int(W * 0.08), mag_y)
        draw_text(surf, str(g["magic_level"]), self.fonts["menu"], BLACK, int(W * 0.24), mag_y)
        self._draw_updown(surf, int(W * 0.18), int(W * 0.30), mag_y,
                          pts > 0, g["magic_level"] > 1)

        # ══ 우측 패널 ═══════════════════════════════════════════
        rx  = int(W * 0.62)   # 업 버튼 X
        rx2 = rx + int(W * 0.12)  # 다운 버튼 X
        label_x = int(W * 0.53)
        val_x   = int(W * 0.80)

        rows = [
            (int(H * 0.30), "체력",          f"{self._hp():,}",         "hp_bonus",   True),
            (int(H * 0.42), "속도",          str(self._speed()),         "spd_bonus",  True),
            (int(H * 0.54), "가하는 피해",   f"+{self._deal_pct()}%",    "deal_bonus", True),
            (int(H * 0.66), "받는 피해 감소",f"-{self._take_pct()}%",    "take_bonus", True),
        ]
        cost_hints = ["(1당 HP +10)", "(5당 속도 +1)", "(5당 +1%)", "(5당 +1%)"]

        for (cy, label, val, key, _), hint in zip(rows, cost_hints):
            draw_text_left(surf, label, self.fonts["menu"], BLACK, label_x, cy)
            draw_text_left(surf, hint,  self.fonts["hint"], GRAY_D, label_x, cy + int(H * 0.038))
            draw_text(surf, val, self.fonts["menu"], BLACK, val_x, cy)
            self._draw_updown(surf, rx, rx2, cy, True, g[key] > 0)

        # 스킬 설정 버튼
        sr = self._skill_btn_rect()
        pygame.draw.rect(surf, PANEL_BG, sr, border_radius=6)
        pygame.draw.rect(surf, GRAY,     sr, 1, border_radius=6)
        draw_text(surf, "스킬  [설정]  (미구현)", self.fonts["menu"], GRAY_D, sr.centerx, sr.centery)

    def _draw_updown(self, surf, up_cx, dn_cx, cy, can_up, can_dn):
        """▲ / ▼ 버튼 그리기."""
        for cx, label, active in [(up_cx, "▲", can_up), (dn_cx, "▼", can_dn)]:
            r   = self._btn(cx, cy)
            col = BTN_UP if (active and label == "▲") else BTN_DN if active else BTN_DIS
            pygame.draw.rect(surf, col, r, border_radius=4)
            draw_text(surf, label, self.fonts["hint"], WHITE, r.centerx, r.centery)
