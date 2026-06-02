import pygame
from utils import *


class LoadingScreen:
    """스테이지 진입 시 검은 로딩 화면. 일정 시간 후 done.
    (추후 꾸밀 예정 — 지금은 검은 화면 + 최소 표시)"""
    DURATION = 0.6   # 초

    def __init__(self, screen, W, H, fonts, label=""):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.label = label
        self.elapsed = 0.0

    def handle_event(self, event):
        return None

    def update(self, dt):
        self.elapsed += dt / 1000.0
        if self.elapsed >= self.DURATION:
            return "done"
        return None

    def draw(self):
        self.screen.fill(BLACK)
