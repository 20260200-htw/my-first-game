import pygame
import os
from utils import *


class DialogueScreen:
    """스테이지 다이얼로그 화면.
    cuts: [{background, cutscene, characters:[{sprite,x,y,scale}], affiliation, speaker, text}, ...]
    cutscene: 배경과 같은 크기(풀스크린)로 배경 위에 얹는 이미지 (해당 컷에만).
    sound: 대사 출력 효과음 경로 (컷마다 지정 가능).
    sound_volume: 대사 효과음 음량 0.0~1.0 (컷마다 지정 가능, 기본 1.0).
    대사/이름/소속이 모두 없어도 하나의 컷으로 취급되어 클릭으로 넘어간다.
    background 는 컷마다 지정 가능 (같은 대화 중에도 변경됨).
    종료 시 handle_event 가 "done" 을 반환 → 호출측에서 전투/클리어 처리.
    """
    SEC_PER_CHAR = 0.05   # 한 글자당 출력에 걸리는 시간(초)

    def __init__(self, screen, W, H, fonts, cuts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.cuts = cuts or []
        self.idx = 0
        self.elapsed = 0.0        # 현재 컷 경과 시간(초)
        self._sprite_cache = {}
        self._wrap_cache = {}
        self._bg_cache = {}
        self._snd_cache = {}
        self._last_typed = 0      # 직전 프레임까지 출력된 글자 수 (효과음용)
        self.SOUND_EVERY = 1      # 몇 글자마다 효과음 재생할지 (1=매 글자)

    # ── 리소스 ────────────────────────────────────────────────
    def _load_bg(self, path):
        """배경 이미지를 화면 크기에 맞춰 로드 (없으면 None)"""
        if not path:
            return None
        if path in self._bg_cache:
            return self._bg_cache[path]
        if not os.path.exists(path):
            self._bg_cache[path] = None
            return None
        try:
            raw = pygame.image.load(path).convert()
            img = pygame.transform.smoothscale(raw, (self.W, self.H))
            self._bg_cache[path] = img
            return img
        except Exception:
            self._bg_cache[path] = None
            return None

    def _play_text_sound(self):
        """현재 컷의 대사 효과음 1회 재생 (cut['sound']).
        항상 새 채널을 찾아 재생하므로 이전 재생과 겹치거나 무시되지 않는다."""
        cut = self._cut()
        if not cut:
            return
        path = cut.get("sound", "")
        if not path or not os.path.exists(path):
            return
        try:
            snd = self._snd_cache.get(path)
            if snd is None:
                snd = pygame.mixer.Sound(path)
                self._snd_cache[path] = snd
            # 컷별 음량 (0.0~1.0, 기본 1.0)
            vol = cut.get("sound_volume", 1.0)
            try:
                vol = max(0.0, min(1.0, float(vol)))
            except (TypeError, ValueError):
                vol = 1.0
            snd.set_volume(vol)
            # 빈 채널을 찾아 재생 — 채널이 없으면 가장 오래된 것 강제 사용
            ch = pygame.mixer.find_channel(True)
            if ch:
                ch.set_volume(vol)
                ch.play(snd)
        except Exception:
            pass

    def _load_sprite(self, path, scale):
        """scale: story_data에서 지정한 값.
        해상도 대응을 위해 화면 높이(H) 기준 비율로 해석한다.
        예) scale=0.5 → 스프라이트 높이 = H * 0.5
        캐시 키에 H를 포함해 해상도 변경 시 재생성된다."""
        if not path:
            return None
        key = (path, round(scale, 4), self.H)
        if key in self._sprite_cache:
            return self._sprite_cache[key]
        if not os.path.exists(path):
            self._sprite_cache[key] = None
            return None
        try:
            raw = pygame.image.load(path).convert_alpha()
            # scale을 화면 높이 비율로 해석
            target_h = max(1, int(self.H * scale))
            ratio    = target_h / raw.get_height()
            target_w = max(1, int(raw.get_width() * ratio))
            img = pygame.transform.smoothscale(raw, (target_w, target_h))
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

    def _current_bg_path(self):
        """현재 컷까지 거슬러 올라가 마지막으로 지정된 배경 경로.
        한 번 설정하면 다음에 바뀌기 전까지 계속 유지된다."""
        path = ""
        for i in range(min(self.idx, len(self.cuts) - 1), -1, -1):
            bg = self.cuts[i].get("background")
            if bg:
                return bg
        return path

    def _full_text(self):
        c = self._cut()
        return c.get("text", "") if c else ""

    def _typed_len(self):
        """현재까지 출력되어야 할 글자 수 (글자당 SEC_PER_CHAR 초)"""
        return int(self.elapsed / self.SEC_PER_CHAR)

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
                self.elapsed = len(self._full_text()) * self.SEC_PER_CHAR + 0.001
                self._last_typed = len(self._full_text())
            else:
                # 완성 상태 → 다음 컷
                self.idx += 1
                self.elapsed = 0.0
                self._last_typed = 0
                if self.idx >= len(self.cuts):
                    return "done"
        return None

    def update(self, dt):
        """dt: ms. elapsed 누적 후 실제 타이핑된 글자 수를 계산해 효과음을 재생.
        draw() 호출 전에 상태를 확정하므로 렌더링과 사운드 타이밍이 일치한다."""
        self.elapsed += dt / 1000.0

        text = self._full_text()
        typed_now = min(self._typed_len(), len(text))
        if typed_now > self._last_typed:
            # SOUND_EVERY 간격마다 1회 재생 (기본 1 = 매 글자)
            for i in range(self._last_typed, typed_now):
                ch = text[i] if i < len(text) else ""
                if ch.strip() and (i % max(1, self.SOUND_EVERY) == 0):
                    self._play_text_sound()
                    break   # 한 update 호출당 최대 1회
            self._last_typed = typed_now

    # ── 그리기 ───────────────────────────────────────────────
    def draw(self):
        W, H = self.W, self.H
        surf = self.screen

        cut = self._cut()
        if cut is None:
            surf.fill((20, 20, 28))
            return

        # 배경: 한 번 지정하면 다음에 바꾸기 전까지 계속 유지. 없으면 단색.
        bg = self._load_bg(self._current_bg_path())
        if bg:
            surf.blit(bg, (0, 0))
        else:
            surf.fill((20, 20, 28))

        # 컷신: 배경과 같은 크기(풀스크린)로 배경 위에 얹음 (해당 컷에만)
        cs = self._load_bg(cut.get("cutscene", ""))
        if cs:
            surf.blit(cs, (0, 0))

        # 캐릭터 스프라이트 (추가 순서대로, midbottom 기준 x,y 배치)
        for ch in cut.get("characters", []):
            img = self._load_sprite(ch.get("sprite", ""), ch.get("scale", 1.0))
            if img:
                cx = int(ch.get("x", 0.5) * W)
                cy = int(ch.get("y", 0.6) * H)
                rect = img.get_rect(midbottom=(cx, cy))
                surf.blit(img, rect)

        # ── 하단 대화창 ──────────────────────────────────────
        # 이름/소속/대사가 모두 없으면 대화창 자체를 그리지 않음 (순수 컷신)
        if not (cut.get("text") or cut.get("speaker") or cut.get("affiliation")):
            return
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
        # 효과음은 update() 에서 처리되므로 draw() 에서는 렌더링만 담당한다.
        text = self._full_text()
        typed_now = min(self._typed_len(), len(text))
        shown = text[:typed_now]
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