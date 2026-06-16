import pygame
import os
import sys as _sys
_sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from utils import *


class IntroScreen:
    """게임 시작 인트로 연출.
    검은 화면에서 페이드 인 → 타이틀 문구 표시 → 페이드 아웃.
    연출이 끝나거나 키/클릭으로 스킵하면 "done" 반환.
    lines: 순차적으로 표시할 (텍스트, 폰트키) 목록.
    """

    FADE_IN   = 700    # 초기 암전에서 밝아지기
    LINE_HOLD = 1400   # 각 문구 표시 시간
    LINE_FADE = 500    # 문구 페이드 인/아웃
    FADE_OUT  = 700    # 마지막 암전

    def __init__(self, screen, W, H, fonts, lines=None):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        # 기본 인트로 문구 (없음 — 페이드만)
        self.lines = lines or []
        self.idx = 0
        self.t = 0.0
        self.phase = "intro_fade"   # intro_fade → line_in → line_hold → line_out → ... → out_fade → done
        self.done = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
            # 스킵
            play_click("confirm")
            return "done"
        return None

    def update(self, dt):
        if self.done:
            return None
        self.t += dt
        if self.phase == "intro_fade":
            if self.t >= self.FADE_IN:
                if not self.lines:
                    self.phase = "out_fade"; self.t = 0.0
                else:
                    self.phase = "line_in"; self.t = 0.0
        elif self.phase == "line_in":
            if self.t >= self.LINE_FADE:
                self.phase = "line_hold"; self.t = 0.0
        elif self.phase == "line_hold":
            if self.t >= self.LINE_HOLD:
                self.phase = "line_out"; self.t = 0.0
        elif self.phase == "line_out":
            if self.t >= self.LINE_FADE:
                self.idx += 1
                if self.idx >= len(self.lines):
                    self.phase = "out_fade"; self.t = 0.0
                else:
                    self.phase = "line_in"; self.t = 0.0
        elif self.phase == "out_fade":
            if self.t >= self.FADE_OUT:
                self.done = True
                return "done"
        return None

    def _line_alpha(self):
        if self.phase == "line_in":
            return min(1.0, self.t / self.LINE_FADE)
        if self.phase == "line_hold":
            return 1.0
        if self.phase == "line_out":
            return max(0.0, 1.0 - self.t / self.LINE_FADE)
        return 0.0

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill((0, 0, 0))
        # 현재 문구
        if self.phase in ("line_in", "line_hold", "line_out") and self.idx < len(self.lines):
            text, fkey = self.lines[self.idx]
            a = self._line_alpha()
            if a > 0:
                font = self.fonts.get(fkey, self.fonts["menu"])
                img = font.render(text, True, (245, 240, 220))
                img = img.copy(); img.set_alpha(int(255 * a))
                surf.blit(img, img.get_rect(center=(W // 2, H // 2)))
        # 하단 스킵 안내 (은은하게)
        hint = self.fonts["small"].render("아무 키나 눌러 건너뛰기", True, (120, 120, 120))
        surf.blit(hint, hint.get_rect(center=(W // 2, int(H * 0.93))))