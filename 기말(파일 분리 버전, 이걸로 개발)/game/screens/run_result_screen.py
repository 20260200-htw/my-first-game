import pygame
import os
import sys as _sys
_sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from utils import *
from run_state import RUN
import save_data


class RunResultScreen:
    """회차 종료 화면.
    success=True 면 마왕 격파(클리어), False 면 전멸(실패).
    반환값: "title" — 타이틀로 복귀
    """

    def __init__(self, screen, W, H, fonts, success):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.success = success
        # 종료 정산: 스킬은 save_data 에 영구 저장됨. 레벨/포인트/아이템은 다음 회차에 초기화.
        g = save_data.get_growth("주인공")
        self.final_level = g.get("level", 1)
        self.skill_count = len(RUN.skills_owned)
        RUN.end_run()

    def _ok_rect(self):
        W, H = self.W, self.H
        bw, bh = int(W*0.20), int(H*0.07)
        return pygame.Rect(W//2 - bw//2, int(H*0.72), bw, bh)

    def handle_event(self, event):
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and
                self._ok_rect().collidepoint(event.pos)):
            play_click(); return "title"
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
            return "title"
        return None

    def update(self, dt):
        pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill((20, 20, 24) if not self.success else (24, 24, 30))

        if self.success:
            draw_text(surf, "마왕 격파!", self.fonts["title"], (255, 220, 90), W//2, int(H*0.30))
            draw_text(surf, "회차를 클리어했습니다.", self.fonts["menu"], WHITE, W//2, int(H*0.40))
        else:
            draw_text(surf, "패배", self.fonts["title"], (220, 80, 80), W//2, int(H*0.30))
            draw_text(surf, "모험이 막을 내렸습니다.", self.fonts["menu"], WHITE, W//2, int(H*0.40))

        draw_text(surf, f"최종 레벨: Lv.{self.final_level}  ·  보유 스킬 {self.skill_count}개",
                  self.fonts["menu"], WHITE, W//2, int(H*0.52))
        draw_text(surf, "레벨과 스킬, 아이템은 다음 회차에도 유지됩니다.",
                  self.fonts["hint"], GRAY, W//2, int(H*0.58))

        ok = self._ok_rect()
        pygame.draw.rect(surf, WHITE, ok, border_radius=8)
        draw_text(surf, "타이틀로", self.fonts["menu"], BLACK, ok.centerx, ok.centery)