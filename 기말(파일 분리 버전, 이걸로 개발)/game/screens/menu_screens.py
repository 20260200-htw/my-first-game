import pygame
import os
from utils import *

# ══════════════════════════════════════════════════════════════════
#   타이틀 화면
# ══════════════════════════════════════════════════════════════════
class TitleScreen:
    ITEMS = ["게임 시작", "아카이브", "설정", "데이터 초기화", "게임 종료"]

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
        return ["start", "gallery", "settings", "reset", "quit"][self.selected]

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
    ITEMS = ["스토리", "돌아가기"]

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
        return ["story", "back"][self.selected]

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
#   데이터 초기화 확인 다이얼로그 (5번 연속 확인)
# ══════════════════════════════════════════════════════════════════
class ResetConfirmDialog:
    """데이터 초기화 전 5번 연속으로 확인하는 다이얼로그.
    단계마다 메시지가 바뀌고, 5번째에 '예'를 눌러야 초기화 실행.
    handle_event 반환값: "done"(초기화 완료) | "cancel" | None"""

    _MESSAGES = [
        "정말 데이터를 초기화하시겠습니까?",
        "진짜요? 모든 진행 상황이 삭제됩니다.",
        "되돌릴 수 없습니다. 정말 계속하시겠습니까?",
        "마지막 경고입니다. 계속하시겠습니까?",
        "최종 확인: 데이터를 초기화합니다.",
    ]

    def __init__(self, screen, W, H, fonts):
        self.screen  = screen
        self.W, self.H = W, H
        self.fonts   = fonts
        self.step    = 0   # 0~4
        self.selected = 1  # 0=예, 1=아니오 (기본: 아니오)

    def _btn_rects(self):
        W, H = self.W, self.H
        dw = int(W * 0.38)
        dh = int(H * 0.22)
        dx = (W - dw) // 2
        dy = (H - dh) // 2
        bw = int(dw * 0.28)
        bh = int(dh * 0.30)
        gap = int(dw * 0.06)
        by = dy + dh - bh - int(dh * 0.12)
        return [
            pygame.Rect(W // 2 - bw - gap, by, bw, bh),  # 예
            pygame.Rect(W // 2 + gap,      by, bw, bh),  # 아니오
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                self.selected ^= 1
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self._confirm(self.selected == 0)
            elif event.key == pygame.K_ESCAPE:
                return "cancel"
        elif event.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self._btn_rects()):
                if r.collidepoint(event.pos):
                    self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self._btn_rects()):
                if r.collidepoint(event.pos):
                    return self._confirm(i == 0)
        return None

    def _confirm(self, yes):
        if not yes:
            return "cancel"
        self.step += 1
        self.selected = 1  # 다음 단계마다 '아니오'로 리셋
        if self.step >= len(self._MESSAGES):
            import save_data
            save_data.reset()
            return "done"
        return None  # 다음 단계로

    def update(self, dt): pass

    def draw(self):
        W, H = self.W, self.H
        surf  = self.screen

        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 140))
        surf.blit(dim, (0, 0))

        dw = int(W * 0.38)
        dh = int(H * 0.22)
        dx, dy = (W - dw) // 2, (H - dh) // 2
        pygame.draw.rect(surf, WHITE, (dx, dy, dw, dh), border_radius=8)
        pygame.draw.rect(surf, (180, 40, 40), (dx, dy, dw, dh), 2, border_radius=8)

        # 단계 표시
        step_txt = f"({self.step + 1} / {len(self._MESSAGES)})"
        draw_text(surf, step_txt, self.fonts["hint"], GRAY_D, W // 2, dy + int(dh * 0.18))
        draw_text(surf, self._MESSAGES[self.step], self.fonts["menu"], BLACK,
                  W // 2, dy + int(dh * 0.45))

        for i, (r, label) in enumerate(zip(self._btn_rects(), ["예", "아니오"])):
            if i == self.selected:
                bg = (180, 40, 40) if i == 0 else BLACK
                pygame.draw.rect(surf, bg, r, border_radius=4)
                draw_text(surf, label, self.fonts["menu"], WHITE, r.centerx, r.centery)
            else:
                pygame.draw.rect(surf, WHITE, r, border_radius=4)
                pygame.draw.rect(surf, BLACK, r, 1, border_radius=4)
                draw_text(surf, label, self.fonts["menu"], BLACK, r.centerx, r.centery)


# ══════════════════════════════════════════════════════════════════
#   폰트
# ══════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════
#   전투 선택 화면  (가로 일자 나열 + 드래그/방향키 이동)
# ══════════════════════════════════════════════════════════════════
class BattleSelectScreen:
    """스테이지를 가로 일렬로 배치하고 마우스 좌클릭 드래그 또는
    좌우 방향키로 1칸씩 이동, Enter/더블클릭으로 선택하는 화면."""

    # 카드 크기·간격 (화면 비율)
    _CARD_W_RATIO  = 0.18   # 카드 너비
    _CARD_H_RATIO  = 0.28   # 카드 높이
    _GAP_RATIO     = 0.03   # 카드 사이 간격
    _CENTER_Y      = 0.50   # 카드 중심 Y (화면 비율)

    # 드래그 판정 임계값(px): 이 이상 움직여야 드래그로 간주
    _DRAG_THRESHOLD = 8

    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        from data.battle_presets import BATTLE_PRESETS
        self.presets = list(BATTLE_PRESETS.items())
        self.selected = 0           # 현재 포커스 인덱스

        # 스크롤: 중심 카드의 X 오프셋 (픽셀, 애니메이션용)
        self._scroll_x   = 0.0     # 현재 렌더 오프셋
        self._target_x   = 0.0     # 목표 오프셋 (키/드래그 후 설정)
        self._anim_speed = 12.0    # lerp 속도 (초당 배율)

        # 드래그 상태
        self._drag_active  = False
        self._drag_start_x = 0
        self._drag_origin  = 0.0   # 드래그 시작 시점의 _scroll_x

    # ── 내부 계산 ──────────────────────────────────────────────────
    def _card_w(self):  return int(self.W * self._CARD_W_RATIO)
    def _card_h(self):  return int(self.H * self._CARD_H_RATIO)
    def _gap(self):     return int(self.W * self._GAP_RATIO)
    def _stride(self):  return self._card_w() + self._gap()

    def _center_x_for(self, idx):
        """인덱스 idx 카드가 화면 중앙에 오려면 필요한 scroll_x."""
        return idx * self._stride()

    def _snap_to(self, idx):
        """idx 카드를 중앙으로 부드럽게 이동."""
        self.selected  = max(0, min(len(self.presets) - 1, idx))
        self._target_x = self._center_x_for(self.selected)

    def _card_rect(self, idx):
        """현재 scroll_x 기준 idx 카드의 화면 Rect."""
        cw, ch = self._card_w(), self._card_h()
        cy = int(self.H * self._CENTER_Y)
        base_cx = self.W // 2 + idx * self._stride() - int(self._scroll_x)
        return pygame.Rect(base_cx - cw // 2, cy - ch // 2, cw, ch)

    def _idx_at(self, mx, my):
        """(mx, my) 위치의 카드 인덱스 반환. 없으면 None."""
        for i in range(len(self.presets)):
            if self._card_rect(i).collidepoint(mx, my):
                return i
        return None

    # ── 이벤트 ────────────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self._snap_to(self.selected - 1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._snap_to(self.selected + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                return ("start", self.presets[self.selected][1])

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._drag_active  = True
            self._drag_start_x = event.pos[0]
            self._drag_origin  = self._scroll_x

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._drag_active:
                drag_dist = abs(event.pos[0] - self._drag_start_x)
                self._drag_active = False

                if drag_dist < self._DRAG_THRESHOLD:
                    # 클릭으로 판정: 해당 카드 선택/실행
                    idx = self._idx_at(*event.pos)
                    if idx is not None:
                        if idx == self.selected:
                            return ("start", self.presets[self.selected][1])
                        else:
                            self._snap_to(idx)
                else:
                    # 드래그 끝: 가장 가까운 카드로 스냅
                    raw_idx = self._scroll_x / self._stride()
                    nearest = int(round(raw_idx))
                    self._snap_to(nearest)

        elif event.type == pygame.MOUSEMOTION:
            if self._drag_active:
                dx = event.pos[0] - self._drag_start_x
                self._scroll_x = self._drag_origin - dx
                # 범위 클램프 (약간의 과주행 허용)
                lo = -self._stride() * 0.4
                hi = self._center_x_for(len(self.presets) - 1) + self._stride() * 0.4
                self._scroll_x = max(lo, min(hi, self._scroll_x))

        return None

    # ── 업데이트 (애니메이션) ──────────────────────────────────────
    def update(self, dt):
        if not self._drag_active:
            # _scroll_x → _target_x 부드러운 보간
            diff = self._target_x - self._scroll_x
            t = min(1.0, self._anim_speed * dt / 1000.0)
            self._scroll_x += diff * t

    # ── 그리기 ────────────────────────────────────────────────────
    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        draw_text(surf, "전투 선택", self.fonts["title"], BLACK, W // 2, int(H * 0.12))

        cw, ch = self._card_w(), self._card_h()
        n = len(self.presets)

        for i, (key, preset) in enumerate(self.presets):
            r = self._card_rect(i)

            # 화면 밖 카드는 건너뜀
            if r.right < 0 or r.left > W:
                continue

            is_sel = (i == self.selected)

            # 카드 배경
            if is_sel:
                pygame.draw.rect(surf, BLACK, r, border_radius=8)
                text_col = WHITE
                border_col = BLACK
            else:
                pygame.draw.rect(surf, WHITE, r, border_radius=8)
                pygame.draw.rect(surf, BLACK, r, 2, border_radius=8)
                text_col = BLACK
                border_col = BLACK

            # 스테이지 번호
            num_font = self.fonts.get("title", self.fonts["menu"])
            draw_text(surf, str(i + 1), num_font, text_col, r.centerx, r.centery - int(H * 0.04))

            # 스테이지 제목 (긴 이름 줄바꿈 대신 중앙 표시)
            title = preset["title"]
            draw_text(surf, title, self.fonts["hint"], text_col, r.centerx, r.centery + int(H * 0.04))

        # 좌우 화살표 힌트
        arrow_y = int(H * self._CENTER_Y)
        arrow_margin = int(W * 0.03)
        if self.selected > 0:
            draw_text(surf, "◀", self.fonts["menu"], GRAY_D, arrow_margin, arrow_y)
        if self.selected < n - 1:
            draw_text(surf, "▶", self.fonts["menu"], GRAY_D, W - arrow_margin, arrow_y)

        # 페이지 표시 (● 도트)
        dot_y = int(H * 0.82)
        dot_r = max(4, int(W * 0.006))
        dot_gap = dot_r * 3
        total_dot_w = n * dot_gap - dot_gap
        dot_x0 = W // 2 - total_dot_w // 2
        for i in range(n):
            col = BLACK if i == self.selected else GRAY
            pygame.draw.circle(surf, col, (dot_x0 + i * dot_gap, dot_y), dot_r)

        # 안내 텍스트
        draw_text(surf, "← → : 이동   Enter : 선택   ESC : 뒤로", self.fonts["hint"], GRAY_D, W // 2, int(H * 0.92))