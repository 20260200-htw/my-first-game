import pygame
import os
import sys as _sys
_sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
import save_data
from utils import *
from data.characters_data import ALLY_DEFS

PANEL_BG = (245, 245, 245)
BAR_BG   = (210, 210, 210)
BAR_EXP  = ( 80, 160, 255)
BTN_UP   = ( 60, 180,  80)
BTN_DN   = (200,  60,  60)
BTN_DIS  = (180, 180, 180)
DIV      = (200, 200, 200)


def _exp_to_next(level):
    return level * 100


def _left_pts(g):
    """좌측 포인트 (물리/마법): 레벨 2부터 지급, 레벨당 2포인트"""
    if g["level"] < 2:
        return 0
    base = (g["level"] - 1) * 2
    used = (g["phys_level"] - 1) + (g["magic_level"] - 1)
    return base - used


def _right_pts(g):
    """우측 포인트 (스탯): 레벨 2부터 지급, 레벨당 3포인트"""
    if g["level"] < 2:
        return 0
    base = (g["level"] - 1) * 3
    used = g["hp_bonus"] + g["spd_bonus"] + g["deal_bonus"] + g["take_bonus"]
    return base - used


class GrowthScreen:
    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self._img_cache = {}
        self.g = dict(save_data.get_growth("주인공"))
        for k, v in [("level",1),("exp",0),("phys_level",1),("magic_level",1),
                     ("hp_bonus",0),("spd_bonus",0),("deal_bonus",0),("take_bonus",0)]:
            self.g.setdefault(k, v)

    # ── 이미지 ────────────────────────────────────────────────────
    def _img(self):
        path = ALLY_DEFS["주인공"].get("sprite", "assets/MC/main_character_B.png")
        if path in self._img_cache:
            return self._img_cache[path]
        if os.path.exists(path):
            try:
                raw = pygame.image.load(path).convert_alpha()
                size = int(self.H * 0.40)
                img  = pygame.transform.smoothscale(raw, (size, size))
                self._img_cache[path] = img
                return img
            except Exception:
                pass
        return None

    # ── 파생 스탯 ─────────────────────────────────────────────────
    def _hp(self):     return ALLY_DEFS["주인공"]["hp_max"] + self.g["hp_bonus"] * 10
    def _speed(self):  return ALLY_DEFS["주인공"]["speed"]  + self.g["spd_bonus"] // 5
    def _deal(self):   return self.g["deal_bonus"] // 5
    def _take(self):   return self.g["take_bonus"] // 5

    # ── 버튼 Rect ─────────────────────────────────────────────────
    def _btn(self, cx, cy, w=34, h=26):
        return pygame.Rect(cx - w//2, cy - h//2, w, h)

    def _back_rect(self):
        return pygame.Rect(int(self.W*0.03), int(self.H*0.04), 90, 32)

    def _skill_rect(self):
        W, H = self.W, self.H
        return pygame.Rect(int(W*0.54), int(H*0.82), int(W*0.38), 36)

    # ── 이벤트 ────────────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._save(); return "back"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._click(event.pos)
        return None

    def _click(self, pos):
        W, H = self.W, self.H
        g = self.g
        lp = _left_pts(g)
        rp = _right_pts(g)

        if self._back_rect().collidepoint(pos):
            self._save(); return "back"
        if self._skill_rect().collidepoint(pos):
            return "skill_config"

        # 좌측: 물리/마법 레벨
        rows_l = [
            (int(H*0.72), "phys_level"),
            (int(H*0.83), "magic_level"),
        ]
        up_x  = int(W*0.30)
        dn_x  = int(W*0.40)
        for cy, key in rows_l:
            if self._btn(up_x, cy).collidepoint(pos) and lp > 0:
                g[key] += 1
            if self._btn(dn_x, cy).collidepoint(pos) and g[key] > 1:
                g[key] -= 1

        # 우측: 스탯
        rows_r = [
            (int(H*0.28), "hp_bonus"),
            (int(H*0.42), "spd_bonus"),
            (int(H*0.56), "deal_bonus"),
            (int(H*0.70), "take_bonus"),
        ]
        up_rx = int(W*0.76)
        dn_rx = int(W*0.86)
        for cy, key in rows_r:
            if self._btn(up_rx, cy).collidepoint(pos) and rp > 0:
                g[key] += 1
            if self._btn(dn_rx, cy).collidepoint(pos) and g[key] > 0:
                g[key] -= 1

        self._save()
        return None

    def _save(self):
        save_data.set_growth(self.g, "주인공")

    def update(self, dt): pass

    # ── 그리기 ────────────────────────────────────────────────────
    def draw(self):
        W, H = self.W, self.H
        surf  = self.screen
        g     = self.g
        lp    = _left_pts(g)
        rp    = _right_pts(g)
        surf.fill(WHITE)

        # 제목
        draw_text(surf, "성장", self.fonts["title"], BLACK, W//2, int(H*0.07))

        # 뒤로가기
        br = self._back_rect()
        pygame.draw.rect(surf, BLACK, br, 1)
        draw_text(surf, "◀ 뒤로", self.fonts["hint"], BLACK, br.centerx, br.centery)

        # 중앙 구분선
        pygame.draw.line(surf, DIV, (W//2, int(H*0.13)), (W//2, int(H*0.92)), 1)

        # ══ 좌측 ════════════════════════════════════════════════
        lx   = int(W*0.25)
        img  = self._img()
        isz  = int(H*0.40)
        ir   = pygame.Rect(lx - isz//2, int(H*0.06), isz, isz)
        if img:
            surf.blit(img, ir)
        else:
            pygame.draw.rect(surf, PANEL_BG, ir)
            pygame.draw.rect(surf, DIV, ir, 2)

        # 레벨
        lv_y = int(H*0.50)
        draw_text(surf, f"Lv. {g['level']}", self.fonts["menu"], BLACK, lx, lv_y)

        # 경험치 바
        exp_y = int(H*0.555)
        bw    = int(W*0.36)
        bh    = 12
        bx    = lx - bw//2
        need  = _exp_to_next(g["level"])
        ratio = min(1.0, g["exp"]/need) if need else 0
        pygame.draw.rect(surf, BAR_BG, (bx, exp_y, bw, bh), border_radius=3)
        if ratio > 0:
            pygame.draw.rect(surf, BAR_EXP, (bx, exp_y, int(bw*ratio), bh), border_radius=3)
        pygame.draw.rect(surf, DIV, (bx, exp_y, bw, bh), 1, border_radius=3)
        draw_text(surf, f"EXP {g['exp']} / {need}", self.fonts["hint"], GRAY_D, lx, exp_y+bh+11)

        # 남은 포인트 (좌측)
        pt_col = (180,40,40) if lp == 0 else (30,130,60)
        draw_text(surf, f"남은 포인트  {lp}", self.fonts["hint"], pt_col, lx, int(H*0.615))

        # 물리 / 마법 레벨
        rows_l = [
            (int(H*0.72), "물리 레벨", "phys_level"),
            (int(H*0.83), "마법 레벨", "magic_level"),
        ]
        lbl_x = int(W*0.07)
        val_x = int(W*0.35)
        up_x  = int(W*0.30)
        dn_x  = int(W*0.40)
        for cy, lbl, key in rows_l:
            draw_text_left(surf, lbl, self.fonts["hint"], BLACK, lbl_x, cy)
            draw_text(surf, str(g[key]), self.fonts["menu"], BLACK, val_x, cy)
            self._updown(surf, up_x, dn_x, cy, lp > 0, g[key] > 1)

        # ══ 우측 ════════════════════════════════════════════════
        lbl_rx = int(W*0.53)
        val_rx = int(W*0.93)
        up_rx  = int(W*0.76)
        dn_rx  = int(W*0.86)

        # 남은 포인트 (우측)
        rpt_col = (180,40,40) if rp == 0 else (30,130,60)
        draw_text(surf, f"남은 포인트  {rp}", self.fonts["hint"], rpt_col, int(W*0.73), int(H*0.17))

        rows_r = [
            (int(H*0.28), "체력",          f"{self._hp():,}",    "hp_bonus",   "(1당 HP +10)"),
            (int(H*0.42), "속도",          str(self._speed()),   "spd_bonus",  "(5당 +1)"),
            (int(H*0.56), "가하는 피해",   f"+{self._deal()}%",  "deal_bonus", "(5당 +1%)"),
            (int(H*0.70), "받는 피해 감소",f"-{self._take()}%",  "take_bonus", "(5당 +1%)"),
        ]
        for cy, lbl, val, key, hint in rows_r:
            draw_text_left(surf, lbl,  self.fonts["menu"], BLACK,  lbl_rx, cy)
            draw_text_left(surf, hint, self.fonts["hint"], GRAY_D, lbl_rx, cy+int(H*0.038))
            draw_text(surf, val, self.fonts["menu"], BLACK, val_rx, cy)
            self._updown(surf, up_rx, dn_rx, cy, rp > 0, g[key] > 0)

        # 스킬 설정
        sr = self._skill_rect()
        pygame.draw.rect(surf, PANEL_BG, sr, border_radius=5)
        pygame.draw.rect(surf, DIV,      sr, 1, border_radius=5)
        draw_text(surf, "스킬  [설정]  (미구현)", self.fonts["menu"], GRAY_D, sr.centerx, sr.centery)

    def _updown(self, surf, up_cx, dn_cx, cy, can_up, can_dn):
        for cx, lbl, active in [(up_cx,"▲",can_up),(dn_cx,"▼",can_dn)]:
            r   = self._btn(cx, cy)
            col = BTN_UP if (active and lbl=="▲") else BTN_DN if (active and lbl=="▼") else BTN_DIS
            pygame.draw.rect(surf, col, r, border_radius=3)
            draw_text(surf, lbl, self.fonts["hint"], WHITE, r.centerx, r.centery)