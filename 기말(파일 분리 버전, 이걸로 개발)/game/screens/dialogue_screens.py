import pygame
from utils import *


# ══════════════════════════════════════════════════════════════════
#   대화 화면 (미구현)
# ══════════════════════════════════════════════════════════════════
class DialogueScreen:
    """대화 화면 - 스테이지 대화 표시용"""
    
    def __init__(self, screen, W, H, fonts, stage_id):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.stage_id = stage_id
        # TODO: stage_data에서 대화 내용 로드
    
    def handle_event(self, event):
        # TODO: 대화 진행 로직
        return None
    
    def update(self, dt):
        pass
    
    def draw(self):
        self.screen.fill(WHITE)
        draw_text(self.screen, "대화 화면 (미구현)", self.fonts["title"], BLACK,
                  self.W // 2, self.H // 2)