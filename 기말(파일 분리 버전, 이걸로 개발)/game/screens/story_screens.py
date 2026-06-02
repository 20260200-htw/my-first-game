import pygame
import os
from utils import *
from data.story_data import STORY


# ══════════════════════════════════════════════════════════════════
#   공통: 직사각형 카드 선택 화면 (이미지 또는 회색 박스+제목)
# ══════════════════════════════════════════════════════════════════
class _CardSelectScreen:
    """카드(직사각형) 목록을 그리드로 보여주고 하나를 고르는 화면.
    items: [(key, label, image_path), ...]
    선택 시 _on_select(key) 가 반환값을 돌려줌."""
    COLS = 5            # 한 줄에 카드 몇 개
    CARD_RATIO = 1.4    # 카드 가로/세로 비율 (가로가 더 긴 직사각형)

    def __init__(self, screen, W, H, fonts, title, items):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.title = title
        self.items = items            # [(key, label, image_path)]
        self.selected = 0
        self._img_cache = {}
        self._layout()

    def _layout(self):
        W, H = self.W, self.H
        n = len(self.items)
        cols = min(self.COLS, max(1, n))
        # 카드 영역 (제목 아래 ~ 하단 여백)
        area_top = int(H * 0.18)
        area_bottom = int(H * 0.90)
        area_left = int(W * 0.06)
        area_right = int(W * 0.94)
        area_w = area_right - area_left
        area_h = area_bottom - area_top
        gap = int(W * 0.015)

        # 카드 폭: 항목이 적어도 COLS 기준 폭을 넘지 않도록 상한 (너무 커지는 것 방지)
        max_card_w = (area_w - gap * (self.COLS - 1)) // self.COLS
        card_w = min(max_card_w, (area_w - gap * (cols - 1)) // cols)
        card_h = int(card_w / self.CARD_RATIO)

        rows = (n + cols - 1) // cols
        # 카드 높이가 영역을 넘으면 높이에 맞춰 축소 (폭도 비율 유지)
        max_total_h = area_h
        total_h = rows * card_h + gap * (rows - 1)
        if total_h > max_total_h:
            card_h = (max_total_h - gap * (rows - 1)) // rows
            card_w = int(card_h * self.CARD_RATIO)

        # 그리드 전체 크기 → area 안에서 중앙 정렬
        grid_w = cols * card_w + gap * (cols - 1)
        grid_h = rows * card_h + gap * (rows - 1)
        ox = area_left + (area_w - grid_w) // 2
        oy = area_top + (area_h - grid_h) // 2

        self.rects = []
        for i in range(n):
            r = i // cols
            c = i % cols
            x = ox + c * (card_w + gap)
            y = oy + r * (card_h + gap)
            self.rects.append(pygame.Rect(x, y, card_w, card_h))
        self.card_w, self.card_h = card_w, card_h
        self.cols = cols

    def _load_img(self, path, size):
        if not path or not os.path.exists(path):
            return None
        key = (path, size)
        if key in self._img_cache:
            return self._img_cache[key]
        try:
            raw = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(raw, size)
            self._img_cache[key] = img
            return img
        except Exception:
            return None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            n = len(self.items)
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected = (self.selected - 1) % n
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected = (self.selected + 1) % n
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - self.cols) % n
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + self.cols) % n
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self._on_select(self.items[self.selected][0])
            elif event.key == pygame.K_ESCAPE:
                return "back"
        elif event.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self.rects):
                if r.collidepoint(event.pos):
                    self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self.rects):
                if r.collidepoint(event.pos):
                    self.selected = i
                    return self._on_select(self.items[i][0])
        return None

    def _on_select(self, key):
        return ("select", key)

    def update(self, dt): pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        draw_text(surf, self.title, self.fonts["title"], BLACK, W // 2, int(H * 0.09))
        draw_text(surf, "ESC: 뒤로", self.fonts["hint"], GRAY_D, int(W * 0.08), int(H * 0.09))

        for i, (key, label, img_path) in enumerate(self.items):
            r = self.rects[i]
            img = self._load_img(img_path, (r.width, r.height))
            if img:
                surf.blit(img, r)
            else:
                pygame.draw.rect(surf, (235, 235, 235), r)
                draw_text(surf, label, self.fonts["menu"], BLACK, r.centerx, r.centery)
            # 선택 테두리
            border = 4 if i == self.selected else 1
            pygame.draw.rect(surf, BLACK, r, border)


# ══════════════════════════════════════════════════════════════════
#   1) 막 선택
# ══════════════════════════════════════════════════════════════════
class ActSelectScreen(_CardSelectScreen):
    def __init__(self, screen, W, H, fonts):
        items = [(k, v.get("title", k), v.get("image", ""))
                 for k, v in STORY.items()]
        super().__init__(screen, W, H, fonts, "메인 스토리", items)

    def _on_select(self, key):
        return ("act", key)


# ══════════════════════════════════════════════════════════════════
#   2) 장 선택
# ══════════════════════════════════════════════════════════════════
class ChapterSelectScreen(_CardSelectScreen):
    def __init__(self, screen, W, H, fonts, act_key):
        self.act_key = act_key
        act = STORY[act_key]
        items = [(k, v.get("title", k), v.get("image", ""))
                 for k, v in act["chapters"].items()]
        super().__init__(screen, W, H, fonts, act.get("title", act_key), items)

    def _on_select(self, key):
        return ("chapter", self.act_key, key)


# ══════════════════════════════════════════════════════════════════
#   3) 스테이지 선택
# ══════════════════════════════════════════════════════════════════
class StageSelectScreen(_CardSelectScreen):
    def __init__(self, screen, W, H, fonts, act_key, chapter_key):
        self.act_key = act_key
        self.chapter_key = chapter_key
        chap = STORY[act_key]["chapters"][chapter_key]
        items = [(k, v.get("title", k), v.get("image", ""))
                 for k, v in chap["stages"].items()]
        super().__init__(screen, W, H, fonts, chap.get("title", chapter_key), items)

    def _on_select(self, key):
        return ("stage", self.act_key, self.chapter_key, key)