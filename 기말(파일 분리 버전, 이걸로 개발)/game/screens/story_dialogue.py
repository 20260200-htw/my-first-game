import pygame
import os
from utils import *


class DialogueScreen:
    """스테이지 다이얼로그 화면.
    cuts: [{characters:[{sprite,x,y,scale}], affiliation, speaker, text}, ...]
    종료 시 handle_event 가 "done" 을 반환 → 호출측에서 전투/클리어 처리.
    """
    TYPE_SPEED = 28.0   # 초당 출력 글자 수

    def __init__(self, screen, W, H, fonts, cuts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.cuts = cuts or []
        self.idx = 0
        self.elapsed = 0.0        # 현재 컷 경과 시간(초)
        self._sprite_cache = {}
        self._wrap_cache = {}

    # ── 리소스 ────────────────────────────────────────────────
    def _load_sprite(self, path, scale):
        if not path:
            return None
        key = (path, round(scale, 3))
        if key in self._sprite_cache:
            return self._sprite_cache[key]
        if not os.path.exists(path):
            self._sprite_cache[key] = None
            return None
        try:
            raw = pygame.image.load(path).convert_alpha()
            w = max(1, int(raw.get_width() * scale))
            h = max(1, int(raw.get_height() * scale))
            img = pygame.transform.smoothscale(raw, (w, h))
            self._sprite_cache[key] = img
            return img
        except Exception:
            self._sprite_cache[key] = None
            return None

    # ── 텍스트 줄바꿈 (폭 기준, 글자 단위) ───────────────────────
    def _wrap(self, text, font, max_w):
        key = (text, max_w)
        if key in self._wrap_cache:
            return self._wrap_cache[key]
        lines = []
        cur = ""
        for ch in text:
            if ch == "\n":
                lines.append(cur)
                cur = ""
                continue
            if font.size(cur + ch)[0] > max_w and cur:
                lines.append(cur)
                cur = ch
            else:
                cur += ch
        lines.append(cur)
        self._wrap_cache[key] = lines
        return lines

    # ── 현재 컷 ──────────────────────────────────────────────
    def _cut(self):
        if 0 <= self.idx < len(self.cuts):
            return self.cuts[self.idx]
        return None

    def _full_text(self):
        c = self._cut()
        return c.get("text", "") if c else ""

    def _typed_len(self):
        """현재까지 출력되어야 할 글자 수"""
        return int(self.elapsed * self.TYPE_SPEED)

    def _is_complete(self):
        return self._typed_len() >= len(self._full_text())

    # ── 입력 ─────────────────────────────────────────────────
    def handle_event(self, event):
        advance = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "done"   # 스킵
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                advance = True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            advance = True

        if advance:
            if not self._is_complete():
                # 타자 진행 중 → 즉시 완성
                self.elapsed = len(self._full_text()) / self.TYPE_SPEED + 0.001
            else:
                # 완성 상태 → 다음 컷
                self.idx += 1
                self.elapsed = 0.0
                if self.idx >= len(self.cuts):
                    return "done"
        return None

    def update(self, dt):
        # dt: ms
        self.elapsed += dt / 1000.0

    # ── 그리기 ───────────────────────────────────────────────
    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill((20, 20, 28))   # 배경 (추후 배경 이미지로 교체 가능)

        cut = self._cut()
        if cut is None:
            return

        # 캐릭터 스프라이트 (추가 순서대로, midbottom 기준 x,y 배치)
        for ch in cut.get("characters", []):
            img = self._load_sprite(ch.get("sprite", ""), ch.get("scale", 1.0))
            if img:
                cx = int(ch.get("x", 0.5) * W)
                cy = int(ch.get("y", 0.6) * H)
                rect = img.get_rect(midbottom=(cx, cy))
                surf.blit(img, rect)

        # ── 하단 대화창 ──────────────────────────────────────
        box_h = int(H * 0.28)
        box_y = H - box_h
        box_margin = int(W * 0.04)
        box_rect = pygame.Rect(box_margin, box_y + int(H * 0.02),
                               W - box_margin * 2, box_h - int(H * 0.04))
        # 반투명 패널
        panel = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 200))
        surf.blit(panel, box_rect.topleft)
        pygame.draw.rect(surf, WHITE, box_rect, 2)

        pad = int(W * 0.02)
        # 소속 (위, 작게) + 이름 (그 아래, 크게) — 대화창 좌측 상단
        affil = cut.get("affiliation", "")
        speaker = cut.get("speaker", "")
        name_x = box_rect.x + pad
        affil_y = box_rect.y + int(H * 0.03)
        name_y  = box_rect.y + int(H * 0.075)
        if affil:
            draw_text_left(surf, affil, self.fonts["hint"], GRAY, name_x, affil_y)
        if speaker:
            draw_text_left(surf, speaker, self.fonts["menu"], WHITE, name_x, name_y)

        # 본문 (타자 효과 + 자동 줄바꿈)
        text = self._full_text()
        shown = text[:self._typed_len()]
        max_w = box_rect.width - pad * 2
        full_lines = self._wrap(text, self.fonts["hint"], max_w)
        # 타자: 누적 글자수로 어디까지 보일지 계산
        budget = len(shown)
        line_y = box_rect.y + int(H * 0.13)
        line_h = int(H * 0.045)
        for ln in full_lines:
            if budget <= 0:
                break
            part = ln[:budget]
            draw_text_left(surf, part, self.fonts["hint"], WHITE, name_x, line_y)
            budget -= len(ln)
            line_y += line_h

        # 진행 표시 (완성 시 ▼)
        if self._is_complete():
            tri = "▼"
            draw_text(surf, tri, self.fonts["hint"], WHITE,
                      box_rect.right - pad, box_rect.bottom - int(H * 0.03))
