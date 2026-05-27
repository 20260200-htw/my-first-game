import pygame
import os
from utils import *

# ══════════════════════════════════════════════════════════════════
#   타이틀 화면
# ══════════════════════════════════════════════════════════════════
class TitleScreen:
    ITEMS = ["게임 시작", "아카이브", "설정", "게임 종료"]

    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.selected = 0

        gap = int(H * 0.08)
        start_y = H // 2
        self.rects = [
            pygame.Rect(W // 2 - 150, start_y + i * gap - 22, 300, 44)
            for i in range(len(self.ITEMS))
        ]
        self.battle_btn = pygame.Rect(W - int(W * 0.18), H - int(H * 0.1), int(W * 0.15), int(H * 0.06))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.ITEMS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.ITEMS)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self._action()
        elif event.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self.rects):
                if r.collidepoint(event.pos):
                    self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.battle_btn.collidepoint(event.pos):
                return "battle_test"
            for i, r in enumerate(self.rects):
                if r.collidepoint(event.pos):
                    self.selected = i
                    return self._action()
        return None

    def _action(self):
        return ["start", "gallery", "settings", "quit"][self.selected]

    def update(self, dt): pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        draw_text(surf, "뻔하디 뻔한 JRPG", self.fonts["title"], BLACK, W // 2, int(H * 0.3))
        pygame.draw.line(surf, BLACK, (W // 2 - 150, int(H * 0.42)), (W // 2 + 150, int(H * 0.42)), 1)

        gap = int(H * 0.08)
        start_y = H // 2
        for i, item in enumerate(self.ITEMS):
            cy = start_y + i * gap
            r  = self.rects[i]
            if i == self.selected:
                pygame.draw.rect(surf, BLACK, r)
                draw_text(surf, item, self.fonts["menu"], WHITE, W // 2, cy)
            else:
                draw_text(surf, item, self.fonts["menu"], BLACK, W // 2, cy)


        pygame.draw.rect(surf, BLACK, self.battle_btn)
        draw_text(surf, "전투 테스트", self.fonts["hint"], WHITE,
                  self.battle_btn.centerx, self.battle_btn.centery)


# ══════════════════════════════════════════════════════════════════
#   게임 시작 화면
# ══════════════════════════════════════════════════════════════════
class GameStartScreen:
    ITEMS = ["스토리", "탐험", "돌아가기"]

    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.selected = 0

        gap = int(H * 0.08)
        start_y = H // 2
        self.rects = [
            pygame.Rect(W // 2 - 150, start_y + i * gap - 22, 300, 44)
            for i in range(len(self.ITEMS))
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.ITEMS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.ITEMS)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self._action()
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
                    return self._action()
        return None

    def _action(self):
        return ["story", "explore", "back"][self.selected]

    def update(self, dt): pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        draw_text(surf, "게임 시작", self.fonts["title"], BLACK, W // 2, int(H * 0.3))
        pygame.draw.line(surf, BLACK, (W // 2 - 150, int(H * 0.42)), (W // 2 + 150, int(H * 0.42)), 1)

        gap = int(H * 0.08)
        start_y = H // 2
        for i, item in enumerate(self.ITEMS):
            cy = start_y + i * gap
            r  = self.rects[i]
            if i == self.selected:
                pygame.draw.rect(surf, BLACK, r)
                draw_text(surf, item, self.fonts["menu"], WHITE, W // 2, cy)
            else:
                draw_text(surf, item, self.fonts["menu"], BLACK, W // 2, cy)


# ══════════════════════════════════════════════════════════════════
#   설정 화면
# ══════════════════════════════════════════════════════════════════
class SettingsScreen:
    ITEMS = ["BGM 볼륨", "효과음 볼륨", "창 모드", "해상도", "프레임", "돌아가기"]

    LABEL_GAP_RATIO = 0.15
    HOLD_DELAY      = 400
    HOLD_REPEAT     = 80

    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.selected = 0
        self._held_key  = None
        self._held_dir  = 0
        self._held_time = 0.0

    def handle_event(self, event):
        last = len(self.ITEMS) - 1
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.ITEMS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.ITEMS)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self._adjust(-1)
                self._held_key  = event.key
                self._held_dir  = -1
                self._held_time = self.HOLD_DELAY
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._adjust(1)
                self._held_key  = event.key
                self._held_dir  = 1
                self._held_time = self.HOLD_DELAY
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.selected == last:
                    return "back"
            elif event.key == pygame.K_ESCAPE:
                return "back"
        elif event.type == pygame.KEYUP:
            if event.key == self._held_key:
                self._held_key = None
                self._held_dir = 0
        elif event.type == pygame.MOUSEMOTION:
            _, my = event.pos
            for i in range(len(self.ITEMS)):
                if abs(my - self._cy(i)) < 24:
                    self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i in range(len(self.ITEMS)):
                if abs(my - self._cy(i)) < 24:
                    self.selected = i
                    if i == last:
                        return "back"
                    if i in (0, 1):
                        sx  = self.W // 2 + int(self.W * self.LABEL_GAP_RATIO)
                        sw  = int(self.W * 0.15)
                        slx = sx - sw // 2
                        if slx <= mx <= slx + sw:
                            raw = int((mx - slx) / sw * 100)
                            val = round(raw / 10) * 10
                            if i == 0: settings["bgm_vol"] = max(0, min(100, val))
                            else:      settings["sfx_vol"] = max(0, min(100, val))
                    else:
                        self._adjust(1)
        return None

    def update(self, dt):
        if self._held_key is None:
            return
        self._held_time -= dt
        if self._held_time <= 0:
            self._adjust(self._held_dir)
            self._held_time = self.HOLD_REPEAT

    def _cy(self, i):
        return int(self.H * 0.3) + i * int(self.H * 0.1)

    def _adjust(self, d):
        if self.selected == 0:
            settings["bgm_vol"]   = max(0, min(100, settings["bgm_vol"] + d * 10))
        elif self.selected == 1:
            settings["sfx_vol"]   = max(0, min(100, settings["sfx_vol"] + d * 10))
        elif self.selected == 2:
            settings["win_mode"]  = (settings["win_mode"] + d) % len(WINDOW_MODES)
        elif self.selected == 3:
            settings["res_index"] = (settings["res_index"] + d) % len(RESOLUTIONS)
        elif self.selected == 4:
            settings["fps_index"] = (settings["fps_index"] + d) % len(FRAMERATES)

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        bx = int(W * 0.2)
        by = int(H * 0.08)
        bw = int(W * 0.6)
        bh = int(H * 0.84)
        pygame.draw.rect(surf, WHITE, (bx, by, bw, bh))
        pygame.draw.rect(surf, BLACK, (bx, by, bw, bh), 2)

        draw_text(surf, "설정", self.fonts["title"], BLACK, W // 2, int(H * 0.17))
        pygame.draw.line(surf, BLACK, (bx + int(bw * 0.1), int(H * 0.26)), (bx + int(bw * 0.9), int(H * 0.26)), 1)

        lx  = W // 2 - int(W * self.LABEL_GAP_RATIO)
        sx  = W // 2 + int(W * self.LABEL_GAP_RATIO)
        sw  = int(W * 0.15)
        slx = sx - sw // 2

        for i, label in enumerate(self.ITEMS):
            cy  = self._cy(i)
            sel = (i == self.selected)

            if i < len(self.ITEMS) - 1:
                draw_text(surf, label, self.fonts["menu"], BLACK, lx, cy)

            if i in (0, 1):
                vol = settings["bgm_vol"] if i == 0 else settings["sfx_vol"]
                pygame.draw.rect(surf, GRAY,  (slx, cy - 4, sw, 8))
                pygame.draw.rect(surf, BLACK, (slx, cy - 4, int(sw * vol / 100), 8))
                if sel:
                    draw_text(surf, "◀", self.fonts["hint"], BLACK, slx - 14, cy)
                    draw_text(surf, "▶", self.fonts["hint"], BLACK, slx + sw + 14, cy)
            elif i == 2:
                val_str = WINDOW_MODES[settings["win_mode"]]
                if sel:
                    draw_text(surf, "◀", self.fonts["hint"], BLACK, slx - 14, cy)
                    draw_text(surf, val_str, self.fonts["menu"], BLACK, sx, cy)
                    draw_text(surf, "▶", self.fonts["hint"], BLACK, slx + sw + 14, cy)
                else:
                    draw_text(surf, val_str, self.fonts["menu"], GRAY_D, sx, cy)
            elif i == 3:
                rw, rh  = RESOLUTIONS[settings["res_index"]]
                res_str = f"{rw} × {rh}"
                if sel:
                    draw_text(surf, "◀", self.fonts["hint"], BLACK, slx - 14, cy)
                    draw_text(surf, res_str, self.fonts["menu"], BLACK, sx, cy)
                    draw_text(surf, "▶", self.fonts["hint"], BLACK, slx + sw + 14, cy)
                else:
                    draw_text(surf, res_str, self.fonts["menu"], GRAY_D, sx, cy)
            elif i == 4:
                fps_str = f"{FRAMERATES[settings['fps_index']]} FPS"
                if sel:
                    draw_text(surf, "◀", self.fonts["hint"], BLACK, slx - 14, cy)
                    draw_text(surf, fps_str, self.fonts["menu"], BLACK, sx, cy)
                    draw_text(surf, "▶", self.fonts["hint"], BLACK, slx + sw + 14, cy)
                else:
                    draw_text(surf, fps_str, self.fonts["menu"], GRAY_D, sx, cy)
            elif i == len(self.ITEMS) - 1:
                draw_text(surf, label, self.fonts["menu"], BLACK if sel else GRAY_D, W // 2, cy)



# ══════════════════════════════════════════════════════════════════
#   갤러리 화면
# ══════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════
#   갤러리(아카이브) 화면
# ══════════════════════════════════════════════════════════════════
class GalleryScreen:
    ITEMS = ["용어", "도감", "돌아가기"]

    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.selected = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.ITEMS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.ITEMS)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self._action()
            elif event.key == pygame.K_ESCAPE:
                return "back"
        elif event.type == pygame.MOUSEMOTION:
            _, my = event.pos
            for i in range(len(self.ITEMS)):
                if abs(my - self._cy(i)) < 24:
                    self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            _, my = event.pos
            for i in range(len(self.ITEMS)):
                if abs(my - self._cy(i)) < 24:
                    self.selected = i
                    return self._action()
        return None

    def _cy(self, i):
        return int(self.H * 0.35) + i * int(self.H * 0.1)

    def _action(self):
        return ["glossary", "compendium", "back"][self.selected]

    def update(self, dt): pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        draw_text(surf, "아카이브", self.fonts["title"], BLACK, W // 2, int(H * 0.2))
        pygame.draw.line(surf, BLACK, (W // 2 - 150, int(H * 0.3)), (W // 2 + 150, int(H * 0.3)), 1)

        for i, item in enumerate(self.ITEMS):
            cy  = self._cy(i)
            sel = (i == self.selected)
            r   = pygame.Rect(W // 2 - 150, cy - 22, 300, 44)
            if sel:
                pygame.draw.rect(surf, BLACK, r)
                draw_text(surf, item, self.fonts["menu"], WHITE, W // 2, cy)
            else:
                draw_text(surf, item, self.fonts["menu"], BLACK, W // 2, cy)



# ══════════════════════════════════════════════════════════════════
#   적 도감 — 메뉴 화면
# ══════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════
#   도감 메뉴 화면
# ══════════════════════════════════════════════════════════════════
class CompendiumMenuScreen:
    def __init__(self, screen, W, H, fonts, title, items):
        self.screen   = screen
        self.W, self.H = W, H
        self.fonts    = fonts
        self.title    = title
        self.items    = items
        self.selected = 0
        self.scroll   = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.items)
                self._clamp_scroll()
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.items)
                self._clamp_scroll()
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                _, val = self.items[self.selected]
                if val is not None:
                    return ("select", val)
            elif event.key == pygame.K_ESCAPE:
                return ("back", None)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
            if event.button == 4:
                self.scroll = max(0, self.scroll - 1)
            else:
                max_scroll = max(0, len(self.items) - self._visible_count())
                self.scroll = min(max_scroll, self.scroll + 1)
        elif event.type == pygame.MOUSEMOTION:
            _, my = event.pos
            for i in range(len(self.items)):
                if abs(my - self._cy(i)) < 24:
                    self.selected = i + self.scroll
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            _, my = event.pos
            for i in range(self._visible_count()):
                idx = i + self.scroll
                if idx >= len(self.items):
                    break
                if abs(my - self._cy(i)) < 24:
                    self.selected = idx
                    _, val = self.items[idx]
                    if val is not None:
                        return ("select", val)
        return None

    def _visible_count(self):
        gap = int(self.H * 0.09)
        start = int(self.H * 0.35)
        return max(1, (self.H - start - int(self.H * 0.1)) // gap)

    def _clamp_scroll(self):
        vis = self._visible_count()
        if self.selected < self.scroll:
            self.scroll = self.selected
        elif self.selected >= self.scroll + vis:
            self.scroll = self.selected - vis + 1
        self.scroll = max(0, self.scroll)

    def _cy(self, i):
        start = int(self.H * 0.35)
        gap   = int(self.H * 0.09)
        return start + i * gap

    def update(self, dt): pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        draw_text(surf, self.title, self.fonts["title"], BLACK, W // 2, int(H * 0.2))
        pygame.draw.line(surf, BLACK, (W // 2 - 150, int(H * 0.3)), (W // 2 + 150, int(H * 0.3)), 1)

        vis = self._visible_count()
        for i in range(vis):
            idx = i + self.scroll
            if idx >= len(self.items):
                break
            name, val = self.items[idx]
            cy  = self._cy(i)
            sel = (idx == self.selected)
            r   = pygame.Rect(W // 2 - 150, cy - 22, 300, 44)
            if sel:
                pygame.draw.rect(surf, BLACK, r)
                draw_text(surf, name, self.fonts["menu"], WHITE, W // 2, cy)
            else:
                draw_text(surf, name, self.fonts["menu"], BLACK, W // 2, cy)



# ══════════════════════════════════════════════════════════════════
#   적 도감 — 상세 화면
# ══════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════
#   도감 상세 화면
# ══════════════════════════════════════════════════════════════════
class CompendiumDetailScreen:
    def __init__(self, screen, W, H, fonts, entry):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts  = fonts
        self.entry  = entry
        self.image  = None
        self._load_image()

    def _load_image(self):
        path = self.entry.get("image", "")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                max_w = int(self.W * 0.35)
                max_h = int(self.H * 0.7)
                iw, ih = img.get_size()
                scale = min(max_w / iw, max_h / ih)
                self.image = pygame.transform.smoothscale(
                    img, (int(iw * scale), int(ih * scale))
                )
            except Exception:
                self.image = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
        return None

    def update(self, dt): pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        cx = W // 2
        gap = int(W * 0.04)

        # 구분선
        pygame.draw.line(surf, BLACK, (cx, int(H * 0.1)), (cx, int(H * 0.9)), 1)

        # 스프라이트 (구분선 왼쪽, 오른쪽 끝이 구분선에서 gap만큼)
        if self.image:
            r = self.image.get_rect(midright=(cx - gap, H // 2))
            surf.blit(self.image, r)
        else:
            box_w = int(W * 0.35)
            box_h = int(H * 0.7)
            box = pygame.Rect(cx - gap - box_w, (H - box_h) // 2, box_w, box_h)
            pygame.draw.rect(surf, GRAY, box)
            draw_text(surf, "이미지 없음", self.fonts["menu"], GRAY_D, box.centerx, box.centery)

        # 텍스트 (구분선 오른쪽, 왼쪽 끝이 구분선에서 gap만큼)
        desc = self.entry.get("description", [])
        tx      = cx + gap
        line_gap = int(H * 0.07)
        total_h  = len(desc) * line_gap
        ty       = H // 2 - total_h // 2
        for line in desc:
            draw_text_left(surf, line, self.fonts["hint_bold"], BLACK, tx, ty)
            ty += line_gap





# ══════════════════════════════════════════════════════════════════
#   용어 상세 화면
# ══════════════════════════════════════════════════════════════════
class GlossaryDetailScreen:
    def __init__(self, screen, W, H, fonts, entry):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts  = fonts
        self.entry  = entry
        self.image  = None
        self._load_image()

    def _load_image(self):
        path = self.entry.get("image", "")
        if path and os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                max_w = int(self.W * 0.3)
                max_h = int(self.H * 0.35)
                iw, ih = img.get_size()
                scale = min(max_w / iw, max_h / ih)
                self.image = pygame.transform.smoothscale(
                    img, (int(iw * scale), int(ih * scale))
                )
            except Exception:
                self.image = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
        return None

    def update(self, dt): pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        desc = self.entry.get("description", [])
        name = desc[0] if desc else ""
        lines = [l for l in desc[2:] if l != ""] if len(desc) > 2 else []

        # 전체 블록 높이 계산
        img_h    = self.image.get_height() + int(H * 0.04) if self.image else int(H * 0.04)
        name_h   = int(H * 0.07)
        desc_h   = len(lines) * int(H * 0.05)
        total_h  = img_h + name_h + desc_h
        cy       = H // 2 - total_h // 2

        # 이미지
        if self.image:
            ir = self.image.get_rect(midtop=(W // 2, cy))
            surf.blit(self.image, ir)
            cy = ir.bottom + int(H * 0.04)
        else:
            cy += int(H * 0.04)

        # 용어 이름
        draw_text(surf, name, self.fonts["menu"], BLACK, W // 2, cy)
        cy += name_h

        # 설명
        for line in lines:
            draw_text(surf, line, self.fonts["hint_bold"], BLACK, W // 2, cy)
            cy += int(H * 0.05)



# ══════════════════════════════════════════════════════════════════
#   전투 화면
# ══════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════
#   준비중 화면
# ══════════════════════════════════════════════════════════════════
class PlaceholderScreen:
    def __init__(self, screen, W, H, fonts, label):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.label = label

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN: return "back"
        return None

    def update(self, dt): pass

    def draw(self):
        W, H = self.W, self.H
        self.screen.fill(WHITE)
        draw_text(self.screen, self.label,             self.fonts["title"], BLACK,  W // 2, int(H * 0.45))
        draw_text(self.screen, "준비 중입니다.",         self.fonts["menu"],  GRAY_D, W // 2, int(H * 0.55))
        draw_text(self.screen, "아무 키나 눌러 돌아가기", self.fonts["hint"],  GRAY,   W // 2, int(H * 0.62))


# ══════════════════════════════════════════════════════════════════
#   종료 다이얼로그
# ══════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════
#   종료 확인창
# ══════════════════════════════════════════════════════════════════
class QuitDialog:
    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.selected = 1

    def _btn_rects(self):
        W, H = self.W, self.H
        dw = int(W * 0.28)
        dh = int(H * 0.18)
        dx = (W - dw) // 2
        dy = (H - dh) // 2
        bw = int(dw * 0.3)
        bh = int(dh * 0.35)
        gap = int(dw * 0.05)
        by = dy + dh - bh - int(dh * 0.12)
        return [
            pygame.Rect(W // 2 - bw - gap, by, bw, bh),
            pygame.Rect(W // 2 + gap,      by, bw, bh),
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                self.selected ^= 1
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return "yes" if self.selected == 0 else "no"
            elif event.key == pygame.K_ESCAPE:
                return "no"
        elif event.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self._btn_rects()):
                if r.collidepoint(event.pos): self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self._btn_rects()):
                if r.collidepoint(event.pos):
                    return "yes" if i == 0 else "no"
        return None

    def update(self, dt): pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen

        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 120))
        surf.blit(dim, (0, 0))

        dw = int(W * 0.28)
        dh = int(H * 0.18)
        dx, dy = (W - dw) // 2, (H - dh) // 2
        pygame.draw.rect(surf, WHITE, (dx, dy, dw, dh))
        pygame.draw.rect(surf, BLACK, (dx, dy, dw, dh), 2)

        draw_text(surf, "정말 종료하시겠습니까?", self.fonts["menu"], BLACK, W // 2, dy + int(dh * 0.3))

        for i, (r, label) in enumerate(zip(self._btn_rects(), ["예", "아니오"])):
            if i == self.selected:
                pygame.draw.rect(surf, BLACK, r)
                draw_text(surf, label, self.fonts["menu"], WHITE, r.centerx, r.centery)
            else:
                pygame.draw.rect(surf, WHITE, r)
                pygame.draw.rect(surf, BLACK, r, 1)
                draw_text(surf, label, self.fonts["menu"], BLACK, r.centerx, r.centery)


# ══════════════════════════════════════════════════════════════════
#   폰트
# ══════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════
#   전투 선택 화면
# ══════════════════════════════════════════════════════════════════
class BattleSelectScreen:
    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        from data.battle_presets import BATTLE_PRESETS
        self.presets = list(BATTLE_PRESETS.items())
        self.selected = 0
        self.scroll = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.selected = max(0, self.selected - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = min(len(self.presets) - 1, self.selected + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return ("start", self.presets[self.selected][1])
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, r in enumerate(self._item_rects()):
                if r.collidepoint(mx, my):
                    if i == self.selected:
                        return ("start", self.presets[i][1])
                    self.selected = i
        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for i, r in enumerate(self._item_rects()):
                if r.collidepoint(mx, my):
                    self.selected = i
        return None

    def _item_rects(self):
        W, H = self.W, self.H
        item_h = int(H * 0.07)
        start_y = int(H * 0.15)
        rects = []
        for i in range(len(self.presets)):
            r = pygame.Rect(int(W * 0.2), start_y + i * item_h, int(W * 0.6), item_h - 4)
            rects.append(r)
        return rects

    def update(self, dt):
        pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)
        draw_text(surf, "전투 선택", self.fonts["title"], BLACK, W // 2, int(H * 0.08))

        for i, (key, preset) in enumerate(self.presets):
            r = self._item_rects()[i]
            if i == self.selected:
                pygame.draw.rect(surf, BLACK, r)
                draw_text(surf, preset["title"], self.fonts["menu"], WHITE, r.centerx, r.centery)
            else:
                pygame.draw.rect(surf, WHITE, r)
                pygame.draw.rect(surf, BLACK, r, 1)
                draw_text(surf, preset["title"], self.fonts["menu"], BLACK, r.centerx, r.centery)

        draw_text(surf, "ESC: 뒤로", self.fonts["hint"], GRAY_D, W // 2, int(H * 0.93))