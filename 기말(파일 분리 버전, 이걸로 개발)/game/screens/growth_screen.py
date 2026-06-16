import pygame
import os
import sys as _sys
_sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
import save_data
from utils import *
from data.characters_data import ALLY_DEFS
from data import run_data
from run_state import RUN

PANEL_BG = (245, 245, 245)
BAR_BG   = (210, 210, 210)
BAR_EXP  = ( 80, 160, 255)
BTN_UP   = ( 60, 180,  80)
BTN_DN   = (200,  60,  60)
BTN_DIS  = (180, 180, 180)
DIV      = (200, 200, 200)
ITEM_BG  = (238, 238, 238)


def _exp_to_next(level):
    return run_data.exp_to_next(level)


def _left_pts(g):
    """좌측 포인트 (물리/마법): 레벨업으로 적립된 미사용 기초 포인트."""
    return g.get("basic_point", 0)


def _right_pts(g):
    """우측 포인트 (스탯): 레벨업으로 적립된 미사용 부가 포인트."""
    return g.get("extra_point", 0)


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
        return pygame.Rect(int(W*0.54), int(H*0.76), int(W*0.38), 36)

    def _item_rect(self):
        """우측 하단 '아이템' 버튼 (스킬 배치 버튼 바로 아래)."""
        W, H = self.W, self.H
        sr = self._skill_rect()
        return pygame.Rect(sr.x, sr.bottom + int(H*0.018), sr.width, sr.height)

    # ── 행/버튼 좌표 (draw 와 click 이 공유하는 단일 기준) ─────────
    def _rows_left(self):
        """좌측: 물리/마법 레벨. [(cy, key)]"""
        H = self.H
        return [
            (int(H*0.72), "phys_level"),
            (int(H*0.83), "magic_level"),
        ]

    def _rows_right(self):
        """우측: 부가 스탯 4종. [(cy, key)]"""
        H = self.H
        return [
            (int(H*0.26), "hp_bonus"),
            (int(H*0.38), "spd_bonus"),
            (int(H*0.50), "deal_bonus"),
            (int(H*0.62), "take_bonus"),
        ]

    def _lr_btn_x(self):
        """좌측 ▲/▼ x좌표."""
        W = self.W
        return int(W*0.30), int(W*0.40)

    def _rr_btn_x(self):
        """우측 ▲/▼ x좌표."""
        W = self.W
        return int(W*0.76), int(W*0.88)

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
            play_click("cancel"); self._save(); return "back"
        if self._skill_rect().collidepoint(pos):
            play_click(); return "skill_config"
        if self._item_rect().collidepoint(pos):
            play_click(); return "item_view"

        # 좌측: 물리/마법 레벨 (기초 포인트 사용)
        up_x, dn_x = self._lr_btn_x()
        for cy, key in self._rows_left():
            if self._btn(up_x, cy).collidepoint(pos) and lp > 0:
                play_click()
                g[key] += 1
                g["basic_point"] = g.get("basic_point", 0) - 1
            if self._btn(dn_x, cy).collidepoint(pos) and g[key] > 1:
                play_click()
                g[key] -= 1
                g["basic_point"] = g.get("basic_point", 0) + 1

        # 우측: 스탯 (부가 포인트 사용)
        up_rx, dn_rx = self._rr_btn_x()
        for cy, key in self._rows_right():
            if self._btn(up_rx, cy).collidepoint(pos) and rp > 0:
                play_click()
                g[key] += 1
                g["extra_point"] = g.get("extra_point", 0) - 1
            if self._btn(dn_rx, cy).collidepoint(pos) and g[key] > 0:
                play_click()
                g[key] -= 1
                g["extra_point"] = g.get("extra_point", 0) + 1

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
        labels_l = {"phys_level": "물리 레벨", "magic_level": "마법 레벨"}
        lbl_x = int(W*0.07)
        val_x = int(W*0.35)
        up_x, dn_x = self._lr_btn_x()
        for cy, key in self._rows_left():
            draw_text_left(surf, labels_l[key], self.fonts["hint"], BLACK, lbl_x, cy)
            draw_text(surf, str(g[key]), self.fonts["menu"], BLACK, val_x, cy)
            self._updown(surf, up_x, dn_x, cy, lp > 0, g[key] > 1)

        # ══ 우측 ════════════════════════════════════════════════
        lbl_rx = int(W*0.53)
        up_rx, dn_rx = self._rr_btn_x()
        val_rx = (up_rx + dn_rx) // 2

        # 남은 포인트 (우측)
        rpt_col = (180,40,40) if rp == 0 else (30,130,60)
        draw_text(surf, f"남은 포인트  {rp}", self.fonts["hint"], rpt_col, int(W*0.73), int(H*0.17))

        meta_r = {
            "hp_bonus":   ("체력",           f"{self._hp():,}",   "(1당 HP +10)"),
            "spd_bonus":  ("속도",           str(self._speed()),  "(5당 +1)"),
            "deal_bonus": ("가하는 피해",    f"+{self._deal()}%", "(5당 +1%)"),
            "take_bonus": ("받는 피해 감소", f"-{self._take()}%", "(5당 +1%)"),
        }
        for cy, key in self._rows_right():
            lbl, val, hint = meta_r[key]
            draw_text_left(surf, lbl,  self.fonts["menu"], BLACK,  lbl_rx, cy)
            draw_text_left(surf, hint, self.fonts["hint"], GRAY_D, lbl_rx, cy+int(H*0.038))
            draw_text(surf, val, self.fonts["menu"], BLACK, val_rx, cy)
            self._updown(surf, up_rx, dn_rx, cy, rp > 0, g[key] > 0)

        # 스킬 배치 버튼
        sr = self._skill_rect()
        pygame.draw.rect(surf, BLACK, sr, border_radius=5)
        eq_n = len(RUN.skills_equipped)
        draw_text(surf, f"스킬 배치  ({eq_n}/10)", self.fonts["menu"], WHITE, sr.centerx, sr.centery)

        # 아이템 버튼 (스킬 배치처럼 전용 화면으로 이동)
        ir = self._item_rect()
        pygame.draw.rect(surf, BLACK, ir, border_radius=5)
        draw_text(surf, f"아이템  ({len(RUN.items)})", self.fonts["menu"], WHITE, ir.centerx, ir.centery)

    def _updown(self, surf, up_cx, dn_cx, cy, can_up, can_dn):
        for cx, lbl, active in [(up_cx,"▲",can_up),(dn_cx,"▼",can_dn)]:
            r   = self._btn(cx, cy)
            col = BTN_UP if (active and lbl=="▲") else BTN_DN if (active and lbl=="▼") else BTN_DIS
            pygame.draw.rect(surf, col, r, border_radius=3)
            draw_text(surf, lbl, self.fonts["hint"], WHITE, r.centerx, r.centery)