# 보스 모드 선택 화면 (도전/극한/최종) + 엔딩 크레딧
#
# 잠금 규칙:
#   - 도전보스: 일반 모드(5지역) 1회 이상 클리어 시 오픈
#   - 극한보스: 모든 '구현된' 도전보스 클리어 시 오픈
#   - 최종보스: 모든 '구현된' 극한보스 클리어 시 오픈
#   - 각 보스 칸: 미구현(없음)이면 회색 'NONE', 구현+잠금이면 자물쇠, 구현+해금이면 선택 가능,
#     이미 클리어했으면 'CLEAR' 표시(재도전 가능)

import pygame
from utils import *
import save_data
from data import run_data

TIERS = [("challenge", "도전 보스"), ("extreme", "극한 보스"), ("final", "최종 보스")]


def _tier_unlocked(tier):
    """해당 tier가 열렸는지 (잠금 규칙)."""
    p = save_data.get_progress()
    if tier == "challenge":
        return p.get("normal_cleared", False)
    if tier == "extreme":
        # 구현된 모든 도전보스를 클리어했는가
        need = run_data.implemented_bosses("challenge")
        done = p.get("challenge_cleared", [])
        return bool(need) and all(r in done for r in need)
    if tier == "final":
        need = run_data.implemented_bosses("extreme")
        done = p.get("extreme_cleared", [])
        return bool(need) and all(r in done for r in need)
    return False


class BossSelectScreen:
    """보스 모드 선택. 좌우로 tier 전환, 위아래로 지역 선택, Enter로 진입."""

    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.tier_idx = 0
        self.sel = 0
        # 처음 열린 tier로 자동 이동
        for i, (t, _) in enumerate(TIERS):
            if _tier_unlocked(t):
                self.tier_idx = i
        self._build_rows()

    def _build_rows(self):
        tier = TIERS[self.tier_idx][0]
        defs = run_data.boss_tier_defs(tier)
        if tier == "final":
            order = ["마왕"]
        else:
            order = run_data.BOSS_REGION_ORDER
        self.rows = []
        for region in order:
            bdef = defs.get(region)
            self.rows.append((region, bdef))
        self.sel = min(self.sel, len(self.rows) - 1)

    def _row_rects(self):
        W, H = self.W, self.H
        bw = int(W * 0.5)
        bh = int(H * 0.10)
        bx = W // 2 - bw // 2
        gap = int(H * 0.022)
        top = int(H * 0.30)
        return [pygame.Rect(bx, top + i * (bh + gap), bw, bh) for i in range(len(self.rows))]

    def _row_selectable(self, region, bdef):
        """이 칸이 실제 선택(진입) 가능한가."""
        tier = TIERS[self.tier_idx][0]
        if bdef is None:
            return False               # 미구현
        if not _tier_unlocked(tier):
            return False               # tier 잠김
        return True

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                play_click("cancel"); return "back"
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.tier_idx = (self.tier_idx - 1) % len(TIERS)
                self._build_rows()
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.tier_idx = (self.tier_idx + 1) % len(TIERS)
                self._build_rows()
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel - 1) % len(self.rows)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel + 1) % len(self.rows)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self._try_select()
        elif event.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self._row_rects()):
                if r.collidepoint(event.pos):
                    self.sel = i
            for i, r in enumerate(self._tab_rects()):
                pass
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self._tab_rects()):
                if r.collidepoint(event.pos):
                    self.tier_idx = i; self._build_rows(); return None
            for i, r in enumerate(self._row_rects()):
                if r.collidepoint(event.pos):
                    self.sel = i
                    return self._try_select()
        return None

    def _try_select(self):
        region, bdef = self.rows[self.sel]
        if self._row_selectable(region, bdef):
            play_click("confirm")
            tier = TIERS[self.tier_idx][0]
            return ("boss_start", tier, region)
        play_click("cancel")
        return None

    def _tab_rects(self):
        W, H = self.W, self.H
        tw = int(W * 0.16)
        th = int(H * 0.07)
        gap = int(W * 0.01)
        total = len(TIERS) * tw + (len(TIERS) - 1) * gap
        x0 = W // 2 - total // 2
        y = int(H * 0.16)
        return [pygame.Rect(x0 + i * (tw + gap), y, tw, th) for i in range(len(TIERS))]

    def update(self, dt):
        pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)
        draw_text(surf, "보스 모드", self.fonts["title"], BLACK, W // 2, int(H * 0.08))

        # 탭 (tier)
        for i, (rect, (tkey, tname)) in enumerate(zip(self._tab_rects(), TIERS)):
            unlocked = _tier_unlocked(tkey)
            active = (i == self.tier_idx)
            if active:
                pygame.draw.rect(surf, BLACK, rect)
                col = WHITE
            else:
                pygame.draw.rect(surf, WHITE, rect)
                pygame.draw.rect(surf, BLACK, rect, 2)
                col = BLACK if unlocked else GRAY
            label = tname if unlocked else f"{tname} 🔒"
            draw_text_fit(surf, tname, self.fonts["hint_bold"], col,
                          rect.centerx, rect.centery, rect.width * 0.9)

        tier = TIERS[self.tier_idx][0]
        tier_open = _tier_unlocked(tier)

        # 보스 칸들
        for i, (rect, (region, bdef)) in enumerate(zip(self._row_rects(), self.rows)):
            selected = (i == self.sel)
            selectable = self._row_selectable(region, bdef)
            cleared = bdef is not None and save_data.is_boss_cleared(tier, region)

            if selected and selectable:
                pygame.draw.rect(surf, BLACK, rect)
                name_col = WHITE
                border = None
            else:
                pygame.draw.rect(surf, WHITE, rect)
                pygame.draw.rect(surf, BLACK if selectable else GRAY, rect, 2)
                name_col = BLACK if selectable else GRAY

            # 좌측: 지역명
            label = region if tier != "final" else "마왕"
            draw_text(surf, label, self.fonts["menu"], name_col,
                      rect.x + int(rect.width * 0.18), rect.centery)

            # 우측: 상태
            if bdef is None:
                status = "미구현"
                scol = GRAY
            elif not tier_open:
                status = "잠김"
                scol = GRAY if not selected else WHITE
            elif cleared:
                status = "클리어"
                scol = (90, 150, 90) if not selected else WHITE
            else:
                status = "도전 가능"
                scol = BLACK if not selected else WHITE
            draw_text_fit(surf, status, self.fonts["hint_bold"], scol,
                          rect.right - int(rect.width * 0.18), rect.centery, rect.width * 0.3)

        # 하단 안내
        if not tier_open:
            if tier == "challenge":
                msg = "일반 모드를 클리어하면 열립니다."
            elif tier == "extreme":
                msg = "모든 도전 보스를 클리어하면 열립니다."
            else:
                msg = "모든 극한 보스를 클리어하면 열립니다."
        else:
            msg = "← → 단계 전환   ↑ ↓ 선택   Enter 도전   ESC 뒤로"
        draw_text_fit(surf, msg, self.fonts["hint"], GRAY_D, W // 2, int(H * 0.90), W * 0.9)


class CreditsScreen:
    """엔딩 크레딧. 위로 스크롤. ESC 또는 클릭으로 종료(타이틀 복귀)."""

    LINES = [
        "",
        "",
        "축하합니다!",
        "",
        "마왕을 물리치고",
        "판타지아에 평화가 찾아왔습니다.",
        "",
        "",
        "─────────────",
        "",
        "  제 작  ",
        "",
        "기획 / 개발",
        "당신",
        "",
        "프로그래밍",
        "당신",
        "",
        "그래픽 / 디자인",
        "당신",
        "",
        "스페셜 땡스",
        "이 게임을 플레이한 당신",
        "",
        "",
        "─────────────",
        "",
        "THE END",
        "",
        "",
        "(ESC 를 눌러 타이틀로)",
    ]

    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.scroll = float(H)       # 화면 아래에서 시작
        self.speed = H * 0.06        # 초당 픽셀
        self.done = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
            play_click("cancel"); return "back"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return "back"
        return None

    def update(self, dt):
        self.scroll -= self.speed * dt
        line_h = int(self.H * 0.05)
        total = len(self.LINES) * line_h
        # 끝까지 올라가면 멈춤(맨 아래 안내가 화면 중앙쯤에서 정지)
        if self.scroll < -total + self.H * 0.5:
            self.scroll = -total + self.H * 0.5

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(BLACK)
        line_h = int(H * 0.05)
        for i, line in enumerate(self.LINES):
            y = int(self.scroll) + i * line_h
            if -line_h < y < H + line_h:
                if line in ("THE END", "축하합니다!"):
                    font = self.fonts["title"]
                elif line.startswith("  제") or line in ("기획 / 개발", "프로그래밍",
                                                          "그래픽 / 디자인", "스페셜 땡스"):
                    font = self.fonts["menu"]
                else:
                    font = self.fonts["hint_bold"]
                draw_text_fit(surf, line, font, WHITE, W // 2, y, W * 0.9)