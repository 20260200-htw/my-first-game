import pygame
import sys
import ctypes
import os

# ── 해상도 목록 (16:9) ─────────────────────────────────────────────
RESOLUTIONS = [
    (1280, 720),
    (1600, 900),
    (1920, 1080),
    (2560, 1440),
]

WINDOW_MODES = ["창 모드", "전체화면"]
FRAMERATES = [30, 60, 120, 144, 165, 240]

# ── 색상 ──────────────────────────────────────────────────────────
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (180, 180, 180)
GRAY_D = (100, 100, 100)
RED    = (200,  40,  40)
GREEN  = ( 40, 180,  40)

# ── 설정 ──────────────────────────────────────────────────────────
settings = {
    "bgm_vol":    70,
    "sfx_vol":    80,
    "res_index":  0,
    "win_mode":   0,
    "fps_index":  1,
}

MON_W, MON_H = 0, 0


def draw_text(surf, text, font, color, cx, cy):
    img = font.render(text, True, color)
    surf.blit(img, img.get_rect(center=(cx, cy)))


def draw_text_left(surf, text, font, color, x, cy):
    img = font.render(text, True, color)
    surf.blit(img, img.get_rect(midleft=(x, cy)))


def draw_text_left_underline(surf, text, font, color, x, cy):
    """'텍스트' 사이 단어에 밑줄을 그어 렌더링. 밑줄 단어의 rect 리스트와 단어 리스트를 반환."""
    parts = text.split("'")
    cur_x = x
    underline_rects = []  # (rect, word)
    for i, part in enumerate(parts):
        if not part:
            continue
        img = font.render(part, True, color)
        r = img.get_rect(midleft=(cur_x, cy))
        surf.blit(img, r)
        if i % 2 == 1:
            uy = r.bottom - 1
            pygame.draw.line(surf, color, (r.left, uy), (r.right, uy), 1)
            underline_rects.append((r, part))
        cur_x = r.right
    return underline_rects


def move_window_center(W, H):
    try:
        hwnd = pygame.display.get_wm_info()["window"]
        x = (MON_W - W) // 2
        y = (MON_H - H) // 2
        ctypes.windll.user32.MoveWindow(hwnd, x, y, W, H, False)
    except Exception:
        pass


def apply_resolution():
    W, H = RESOLUTIONS[settings["res_index"]]
    W = min(W, MON_W)
    H = min(H, MON_H)
    if settings["win_mode"] == 1:
        screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
    else:
        flags = pygame.NOFRAME if (W >= MON_W or H >= MON_H) else 0
        screen = pygame.display.set_mode((W, H), flags)
        move_window_center(W, H)
    return screen, W, H


# ══════════════════════════════════════════════════════════════════
#   캐릭터 데이터 정의
# ══════════════════════════════════════════════════════════════════
ENEMY_DEFS = {
    "벨라": {
        "title":         "왕국 기사단장",
        "name":          "벨라",
        "type":          "boss",
        "level":         100,
        "phys_level":    100,
        "magic_level":   100,
        "hp_max":        10000,
        "sprite":        "assets/knight_leader.png",
        "sprite_scale":  0.5625,
        "click_w_ratio": 0.5,
        "overview": [
            "벨라 트릭스",
            "",
            "그녀는 중앙 왕국의 기사단장 입니다.",
            "적의를 가지고 싸움을 건 것은 아닌 것으로 보입니다.",
            "",
            "그렇다고 해서 당신을 죽이지 않는다는 보장은 없으니",
            "최선을 다해서 그녀의 의도에 맞춰주는 것을 권장합니다.",
            "",
            "그녀와 싸우는 것은 이 세계에서 할 수 있는",
            "가장 멍청한 짓 중 하나일 것입니다.",
        ],
        "passives": [
            {
                "name": "왕국 기사단장",
                "desc": [
                    "모든 피해로부터 받는 피해가 30% 감소합니다.",
                    "자신이 적에게 가하는 모든 피해가 50% 증가합니다.",
                ]
            },
            {
                "name": "기사단장의 명령",
                "desc": [
                    "이번 전투에서 왕국 기사단이 참전하지 않습니다.",
                    "또한 벨라가 '시험' 을 얻습니다.",
                ]
            },
            {
                "name": "마력 발산 - 지옥불",
                "desc": [
                    "'마력 발산' 상태가 되면 모든 스킬의 최종 위력이 30 증가합니다.",
                    "매 턴이 시작될 때마다 (물리 레벨+마법 레벨)*1 만큼 모든 적에게 마법 피해를 입힙니다.",
                ]
            },
            {
                "name": "지옥불 결계",
                "desc": [
                    "매 턴이 시작될 때마다 보호막을 1000 만큼 얻습니다.",
                    "적에게 피해를 받으면 즉시 파괴되며, 다음 턴이 되기 전까지 보호막을 얻지 않습니다.",
                ]
            },
            {
                "name": "전황 분석",
                "desc": [
                    "매 턴이 시작될 때마다 '전황 분석' 중첩을 1 얻습니다.",
                    "중첩 당 자신이 가하는 모든 피해가 5% 증가합니다.",
                ]
            },
        ],
        "buffs": {
            "시험": {
                "desc": [
                    "자신이 사용하는 모든 스킬의 최종 위력이 50 감소합니다.",
                ]
            },
        },
        "skills": [
            {
                "name":   "찌르기",
                "power":  50,
                "type":   "물리",
                "target": "단일",
                "hits":   1,
                "tags":   ["필중"],
                "sprite": "assets/KL_skills_1.png",
                "desc": [
                    "반드시 주인공을 대상으로 지정함",
                    "대상이 수비 스킬 '방어' 를 사용하였다면 피해량 -50%",
                ]
            },
            {
                "name":   "피하는 것이 좋을 겁니다",
                "power":  80,
                "type":   "물리",
                "target": "단일",
                "hits":   1,
                "tags":   ["필중"],
                "sprite": "assets/KL_skills_2.png",
                "desc": [
                    "반드시 주인공을 대상으로 지정함",
                    "대상이 수비 스킬 '방어' 를 사용하였다면 피해량 +500%",
                    "대상이 수비 스킬 '회피' 를 사용하였다면 최종 위력이 0으로 고정됨",
                ]
            },
            {
                "name":   "이번 건 피할 수 없을 겁니다",
                "power":  30,
                "type":   "물리",
                "target": "5인",
                "hits":   1,
                "tags":   ["난사"],
                "sprite": "assets/KL_skills_3.png",
                "desc": [
                    "수비 스킬 '방어' 를 사용한 대상에게는 피해량 -90%",
                    "수비 스킬 '회피' 를 사용한 대상에게는 '필중' 효과가 함께 적용됨",
                ]
            },
            {
                "name":   "당신들도 예외는 아닙니다",
                "power":  130,
                "type":   "물리",
                "target": "단일",
                "hits":   1,
                "tags":   ["필중"],
                "sprite": "assets/KL_skills_4.png",
                "desc": [
                    "주인공을 제외한 적을 대상으로 지정함",
                    "대상이 '보호막' 을 가지고 있다면 피해를 입히기 전 보호막을 전부 파괴함",
                ]
            },
            {
                "name":   "꿰뚫는 불꽃",
                "power":  300,
                "type":   "마법",
                "target": "5인",
                "hits":   3,
                "tags":   [],
                "sprite": "assets/KL_skills_5.png",
                "desc": [
                    "반드시 주인공을 대상으로 지정함",
                    "대상이 이 스킬로 피해를 받기 전 자신을 공격했다면 해당 스킬을 취소함",
                ]
            },
        ],
    },
}

ALLY_DEFS = {
    "주인공": {
        "name":          "주인공",
        "type":          "player",
        "level":         10,
        "phys_level":    10,
        "magic_level":   10,
        "hp_max":        100,
        "sprite":        "assets/main_character.png",
        "sprite_scale":  0.5,
        "click_w_ratio": 0.4,
    },
    "아우렐리우스": {
        "name":          "아우렐리우스",
        "type":          "ally",
        "level":         88,
        "phys_level":    84,
        "magic_level":   83,
        "hp_max":        6570,
        "sprite":        "assets/super_healer_man.png",
        "sprite_scale":  0.51,
        "click_w_ratio": 0.4,
    },
    "금강": {
        "name":          "금강",
        "type":          "ally",
        "level":         82,
        "phys_level":    86,
        "magic_level":   72,
        "hp_max":        5560,
        "sprite":        "assets/super_fight_girl.png",
        "sprite_scale":  0.5,
        "click_w_ratio": 0.4,
    },
}


# ══════════════════════════════════════════════════════════════════
#   전투 참가자 인스턴스
# ══════════════════════════════════════════════════════════════════
class Combatant:
    def __init__(self, defn, W, H, max_sprite_w, max_sprite_h):
        self.defn        = defn
        self.title       = defn.get("title", "")
        self.name        = defn["name"]
        self.ctype       = defn["type"]
        self.level       = defn.get("level", 1)
        self.phys_level  = defn.get("phys_level", 0)
        self.magic_level = defn.get("magic_level", 0)
        self.hp_max      = defn["hp_max"]
        self.hp          = defn["hp_max"]
        self.overview    = defn.get("overview", [])
        self.passives    = defn.get("passives", [])
        self.buffs       = defn.get("buffs", {})
        self.skills      = defn.get("skills", [])
        self.sprite      = None
        self.sprite_orig = None
        self._load_sprite(defn["sprite"], max_sprite_w, max_sprite_h)

    def _load_sprite(self, path, max_w, max_h):
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                self.sprite_orig = img
                iw, ih = img.get_size()
                # sprite_scale이 있으면 W/H 비율 기준, 없으면 max_w/h 기준
                scale_ratio = self.defn.get("sprite_scale", None)
                if scale_ratio is not None:
                    from pygame import display
                    info = display.Info()
                    W, H = info.current_w, info.current_h
                    sw = int(W * scale_ratio)
                    sh = int(H * scale_ratio)
                    scale = min(sw / iw, sh / ih)
                else:
                    scale = min(max_w / iw, max_h / ih)
                self.sprite = pygame.transform.smoothscale(
                    img, (int(iw * scale), int(ih * scale))
                )
            except Exception:
                self.sprite = None
                self.sprite_orig = None


# ══════════════════════════════════════════════════════════════════
#   도감 데이터
# ══════════════════════════════════════════════════════════════════
COMPENDIUM = {
    "인간": {
        "주인공": {
            "image": "assets/main_character.png",
            "description": [
                "이름: 미정",
                "소속: 미정",
                "설명: 준비 중입니다.",
            ]
        },
        "중앙": {
            "왕국 기사단": {
                "기사단장": {
                    "image": "assets/knight_leader.png",
                    "description": [
                        "이름: 벨라",
                        "나이: 21",
                        "신장: 177cm",
                        "소속: 왕국 기사단",
                        "직위: 기사단장",
                        "설명: 왕국 기사단의 최연소 단장입니다.",
                        "판타지아의 가장 강한 이들 중 하나입니다.",
                        "능력치: LV 100 | P 100 | M 100"
                    ]
                }
            }
        },
        "동부":  None,
        "서부":  None,
        "남부":  None,
        "북부":  None,
    },
    "마족":  None,
    "마물":  None,
}


# ══════════════════════════════════════════════════════════════════
#   타이틀 화면
# ══════════════════════════════════════════════════════════════════
class TitleScreen:
    ITEMS = ["게임 시작", "갤러리", "설정", "게임 종료"]

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

        draw_text(surf, "↑↓  이동     Enter / 클릭  선택",
                  self.fonts["hint"], GRAY_D, W // 2, H - int(H * 0.05))

        pygame.draw.rect(surf, BLACK, self.battle_btn)
        draw_text(surf, "전투 테스트", self.fonts["hint"], WHITE,
                  self.battle_btn.centerx, self.battle_btn.centery)


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

        draw_text(surf, "↑↓  이동     ←→  조절     Esc  돌아가기",
                  self.fonts["hint"], GRAY_D, W // 2, H - int(H * 0.05))


# ══════════════════════════════════════════════════════════════════
#   갤러리 화면
# ══════════════════════════════════════════════════════════════════
class GalleryScreen:
    ITEMS = ["스토리 컷신", "적 도감", "돌아가기"]

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
        return ["cutscene", "compendium", "back"][self.selected]

    def update(self, dt): pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        draw_text(surf, "갤러리", self.fonts["title"], BLACK, W // 2, int(H * 0.2))
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

        draw_text(surf, "↑↓  이동     Enter  선택     Esc  돌아가기",
                  self.fonts["hint"], GRAY_D, W // 2, H - int(H * 0.05))


# ══════════════════════════════════════════════════════════════════
#   적 도감 — 메뉴 화면
# ══════════════════════════════════════════════════════════════════
class CompendiumMenuScreen:
    def __init__(self, screen, W, H, fonts, title, items):
        self.screen   = screen
        self.W, self.H = W, H
        self.fonts    = fonts
        self.title    = title
        self.items    = items
        self.selected = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.items)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.items)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                _, val = self.items[self.selected]
                if val is not None:
                    return ("select", val)
            elif event.key == pygame.K_ESCAPE:
                return ("back", None)
        elif event.type == pygame.MOUSEMOTION:
            _, my = event.pos
            for i in range(len(self.items)):
                if abs(my - self._cy(i)) < 24:
                    self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            _, my = event.pos
            for i, (_, val) in enumerate(self.items):
                if abs(my - self._cy(i)) < 24:
                    self.selected = i
                    if val is not None:
                        return ("select", val)
        return None

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

        for i, (name, val) in enumerate(self.items):
            cy  = self._cy(i)
            sel = (i == self.selected)
            r   = pygame.Rect(W // 2 - 150, cy - 22, 300, 44)
            if sel:
                pygame.draw.rect(surf, BLACK, r)
                draw_text(surf, name, self.fonts["menu"], WHITE, W // 2, cy)
            else:
                draw_text(surf, name, self.fonts["menu"], BLACK, W // 2, cy)

        draw_text(surf, "↑↓  이동     Enter  선택     Esc  돌아가기",
                  self.fonts["hint"], GRAY_D, W // 2, H - int(H * 0.05))


# ══════════════════════════════════════════════════════════════════
#   적 도감 — 상세 화면
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

        img_area_cx = int(W * 0.25)
        img_area_cy = int(H * 0.5)

        if self.image:
            r = self.image.get_rect(center=(img_area_cx, img_area_cy))
            surf.blit(self.image, r)
        else:
            box = pygame.Rect(int(W * 0.05), int(H * 0.15), int(W * 0.38), int(H * 0.7))
            pygame.draw.rect(surf, GRAY, box)
            draw_text(surf, "이미지 없음", self.fonts["menu"], GRAY_D, img_area_cx, img_area_cy)

        pygame.draw.line(surf, BLACK,
            (int(W * 0.45), int(H * 0.1)),
            (int(W * 0.45), int(H * 0.9)), 1)

        desc = self.entry.get("description", [])
        rx   = int(W * 0.5)
        ry   = int(H * 0.25)
        gap  = int(H * 0.07)
        for i, line in enumerate(desc):
            draw_text_left(surf, line, self.fonts["menu"], BLACK, rx, ry + i * gap)

        draw_text(surf, "Esc  돌아가기",
                  self.fonts["hint"], GRAY_D, W // 2, H - int(H * 0.05))


# ══════════════════════════════════════════════════════════════════
#   전투 화면
# ══════════════════════════════════════════════════════════════════
class BattleScreen:
    ENEMY_ORDER   = [0, -1, 1, -2, 2]
    ENEMY_SPACING = 0.13
    ALLY_SPACING  = 0.15
    UI_H_RATIO    = 0.3

    STATE_MENU   = "menu"
    STATE_TARGET = "target"

    TAB_NAMES = ["개요", "스킬", "패시브"]

    def __init__(self, screen, W, H, fonts, enemies, allies):
        self.screen  = screen
        self.W, self.H = W, H
        self.fonts   = fonts

        enemy_max_w = int(W * 0.55)
        enemy_max_h = int(H * 0.55)
        ally_max_w  = int(W * 0.5)
        ally_max_h  = int(H * 0.5)

        self.enemies = [Combatant(ENEMY_DEFS[k], W, H, enemy_max_w, enemy_max_h) for k in enemies]
        self.allies  = [Combatant(ALLY_DEFS[k],  W, H, ally_max_w,  ally_max_h)  for k in allies]

        self.ui_y    = int(H * (1.0 - self.UI_H_RATIO))

        self.state           = self.STATE_MENU
        self.menu_selected   = 0
        self.target_selected = 0
        self.UI_ITEMS        = ["공격", "수비", "아이템"]

        self.inspect_enemy   = None
        self.inspect_ally    = None
        self.inspect_tab     = 0
        self.inspect_sprite  = None
        self.inspect_scroll  = 0
        self._underline_rects = []

    def _ui_rect(self):
        W, H = self.W, self.H
        ui_h = int(H * self.UI_H_RATIO) - int(H * 0.02)
        ui_w = int(W // 2 * 2 / 3) // 2
        ui_x = W - ui_w - int(W * 0.02)
        return pygame.Rect(ui_x, self.ui_y, ui_w, ui_h)

    def _target_rect(self):
        ui = self._ui_rect()
        return pygame.Rect(ui.left - ui.width, ui.top, ui.width, ui.height)

    def _enemy_sprite_rect(self, i):
        positions = self._enemy_positions()
        if i >= len(positions):
            return None
        ex, ey = positions[i]
        e = self.enemies[i]
        H = self.H
        if e.sprite:
            full = e.sprite.get_rect(midbottom=(ex, ey + int(H * 0.08)))
            ratio = e.defn.get("click_w_ratio", 1.0)
            new_w = int(full.width * ratio)
            return pygame.Rect(full.centerx - new_w // 2, full.top, new_w, full.height)
        return pygame.Rect(ex - 40, ey - 80, 80, 80)

    def _ally_sprite_rect(self, i):
        positions = self._ally_positions()
        if i >= len(positions):
            return None
        ax, ay = positions[i]
        a = self.allies[i]
        if a.sprite:
            flipped = pygame.transform.flip(a.sprite, True, False)
            full  = flipped.get_rect(midbottom=(ax, ay))
            ratio = a.defn.get("click_w_ratio", 1.0)
            new_w = int(full.width * ratio)
            return pygame.Rect(full.centerx - new_w // 2, full.top, new_w, full.height)
        return pygame.Rect(ax - 30, ay - 60, 60, 60)

    def _open_inspect(self, combatant):
        self.inspect_enemy  = None
        self.inspect_ally   = None
        self.inspect_tab    = 0
        W, H = self.W, self.H
        if combatant.ctype == "player":
            self.inspect_ally = combatant
        else:
            self.inspect_enemy = combatant
        if combatant.sprite_orig:
            iw, ih   = combatant.sprite_orig.get_size()
            target_h = int(H * 0.9)
            target_w = int(W * 0.48)
            scale    = min(target_w / iw, target_h / ih)
            self.inspect_sprite = pygame.transform.smoothscale(
                combatant.sprite_orig, (int(iw * scale), int(ih * scale))
            )
        else:
            self.inspect_sprite = None

    def _inspect_target(self):
        """현재 열람 중인 Combatant 반환"""
        return self.inspect_enemy or self.inspect_ally

    def _close_inspect(self):
        self.inspect_enemy  = None
        self.inspect_ally   = None
        self.inspect_sprite = None

    def handle_event(self, event):
        if self._inspect_target() is not None:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._close_inspect()
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.inspect_tab = (self.inspect_tab - 1) % len(self.TAB_NAMES)
                    self.inspect_scroll = 0
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.inspect_tab = (self.inspect_tab + 1) % len(self.TAB_NAMES)
                    self.inspect_scroll = 0
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
                scroll_dir = -1 if event.button == 4 else 1
                H = self.H
                W = self.W
                pad         = int(W * 0.02)
                left_w      = int(W * 0.48)
                info_w      = W - pad * 2 - left_w
                tab_total_w = info_w - pad * 2
                tab_w       = tab_total_w // len(self.TAB_NAMES)
                tabs_total_w = tab_w * len(self.TAB_NAMES)
                bar_y       = pad + int(H * 0.22)
                bar_h       = int(H * 0.03)
                tab_y       = bar_y + bar_h + int(H * 0.03)
                tab_h       = int(H * 0.06)
                content_y   = tab_y + tab_h
                content_h   = H - pad * 2 - content_y
                c = self._inspect_target()
                if self.inspect_tab == 2 and c and c.passives:
                    gap_name  = int(H * 0.035)
                    gap_desc  = int(H * 0.03)
                    gap_block = int(H * 0.015)
                    total = int(H * 0.02)
                    for passive in c.passives:
                        total += gap_name + len(passive["desc"]) * gap_desc + gap_block * 2
                    max_scroll = max(0, total - content_h)
                elif self.inspect_tab == 1 and c and c.skills:
                    icon_size = int(H * 0.08)
                    gap_line  = int(H * 0.03)
                    gap_block = int(H * 0.015)
                    total = int(H * 0.02)
                    for skill in c.skills:
                        block_h = max(icon_size, int(icon_size * 0.2) + int(H * 0.033) + int(H * 0.035) + len(skill["desc"]) * gap_line)
                        total += block_h + gap_block * 2
                    max_scroll = max(0, total - content_h)
                elif self.inspect_tab == 0 and c and c.overview:
                    line_h = int(H * 0.04)
                    total  = int(H * 0.025)
                    for line in c.overview:
                        total += line_h // 2 if line == "" else line_h
                    max_scroll = max(0, total - content_h)
                else:
                    max_scroll = 0
                self.inspect_scroll = max(0, min(max_scroll, self.inspect_scroll + scroll_dir * 20))
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                W, H = self.W, self.H
                pad         = int(W * 0.02)
                left_w      = int(W * 0.48)
                info_x      = pad + left_w
                info_w      = W - pad * 2 - left_w
                tab_total_w = info_w - pad * 2
                tab_w       = tab_total_w // len(self.TAB_NAMES)
                bar_y       = pad + int(H * 0.22)
                bar_h       = int(H * 0.03)
                tab_y       = bar_y + bar_h + int(H * 0.03)
                tab_h       = int(H * 0.06)
                if tab_y <= my <= tab_y + tab_h:
                    for ti in range(len(self.TAB_NAMES)):
                        tx = info_x + pad + ti * tab_w
                        if tx <= mx <= tx + tab_w:
                            self.inspect_tab = ti
                            self.inspect_scroll = 0
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == self.STATE_TARGET:
                    self.state = self.STATE_MENU
                else:
                    return "back"
            elif self.state == self.STATE_MENU:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.menu_selected = (self.menu_selected - 1) % len(self.UI_ITEMS)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.menu_selected = (self.menu_selected + 1) % len(self.UI_ITEMS)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if self.UI_ITEMS[self.menu_selected] == "공격":
                        self.state = self.STATE_TARGET
                        self.target_selected = 0
            elif self.state == self.STATE_TARGET:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.target_selected = (self.target_selected - 1) % len(self.enemies)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.target_selected = (self.target_selected + 1) % len(self.enemies)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._do_attack(self.target_selected)
                    self.state = self.STATE_MENU

        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            if self.state == self.STATE_MENU:
                ui     = self._ui_rect()
                item_h = ui.height // (len(self.UI_ITEMS) + 1)
                for i in range(len(self.UI_ITEMS)):
                    cy = ui.top + item_h * (i + 1)
                    if abs(my - cy) < item_h // 2:
                        self.menu_selected = i
            elif self.state == self.STATE_TARGET:
                tr     = self._target_rect()
                slot_h = tr.height // 5
                for i in range(len(self.enemies)):
                    slot_rect = pygame.Rect(tr.left, tr.top + i * slot_h, tr.width, slot_h)
                    if slot_rect.collidepoint(mx, my):
                        self.target_selected = i

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # 적 스프라이트 클릭
            for i in range(len(self.enemies)):
                r = self._enemy_sprite_rect(i)
                if r and r.collidepoint(mx, my):
                    self._open_inspect(self.enemies[i])
                    return None
            # 아군 스프라이트 클릭
            for i in range(len(self.allies)):
                r = self._ally_sprite_rect(i)
                if r and r.collidepoint(mx, my):
                    self._open_inspect(self.allies[i])
                    return None

            if self.state == self.STATE_MENU:
                ui     = self._ui_rect()
                item_h = ui.height // (len(self.UI_ITEMS) + 1)
                for i in range(len(self.UI_ITEMS)):
                    cy = ui.top + item_h * (i + 1)
                    if abs(my - cy) < item_h // 2 and ui.left <= mx <= ui.right:
                        self.menu_selected = i
                        if self.UI_ITEMS[i] == "공격":
                            self.state = self.STATE_TARGET
                            self.target_selected = 0
            elif self.state == self.STATE_TARGET:
                tr     = self._target_rect()
                slot_h = tr.height // 5
                for i in range(len(self.enemies)):
                    slot_rect = pygame.Rect(tr.left, tr.top + i * slot_h, tr.width, slot_h)
                    if slot_rect.collidepoint(mx, my):
                        self._do_attack(i)
                        self.state = self.STATE_MENU

        return None

    def _do_attack(self, target_idx):
        target = self.enemies[target_idx]
        target.hp = max(0, target.hp - 100)

    def update(self, dt): pass

    def _enemy_positions(self):
        W, H    = self.W, self.H
        cx      = W // 2
        area_cy = int(H * 0.6)
        spacing = int(W * self.ENEMY_SPACING)
        positions = []
        for i, e in enumerate(self.enemies):
            offset = self.ENEMY_ORDER[i] * spacing
            positions.append((cx + offset, area_cy))
        return positions

    def _ally_positions(self):
        W, H    = self.W, self.H
        foot_y  = H
        spacing = int(W * self.ALLY_SPACING)
        start_x = int(W * 0.1)
        return [(start_x + i * spacing, foot_y) for i in range(len(self.allies))]

    def _draw_inspect_overlay(self, c):
        """적/아군 공통 열람 오버레이"""
        W, H = self.W, self.H
        surf = self.screen

        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 180))
        surf.blit(dim, (0, 0))

        pad   = int(W * 0.02)
        panel = pygame.Rect(pad, pad, W - pad * 2, H - pad * 2)
        pygame.draw.rect(surf, WHITE, panel)
        pygame.draw.rect(surf, BLACK, panel, 2)

        left_w = int(W * 0.48)
        info_x = pad + left_w
        info_w = panel.width - left_w

        # 좌측 스프라이트
        if self.inspect_sprite:
            sr = self.inspect_sprite.get_rect(midbottom=(pad + left_w // 2, panel.bottom - pad))
            surf.blit(self.inspect_sprite, sr)

        # 이름 / 스탯
        name_y = pad + int(H * 0.09)
        stat_y = pad + int(H * 0.17)
        bar_y  = pad + int(H * 0.22)

        name_str = f"{c.name}"
        stat_str = f"LV.{c.level}   P {c.phys_level}   M {c.magic_level}"
        draw_text_left(surf, name_str, self.fonts["title"], BLACK, info_x + pad, name_y)
        draw_text_left(surf, stat_str, self.fonts["menu"],  BLACK, info_x + pad, stat_y)

        # 체력바
        tab_total_w  = info_w - pad * 2
        tab_w        = tab_total_w // len(self.TAB_NAMES)
        tabs_total_w = tab_w * len(self.TAB_NAMES)
        bar_w = tabs_total_w
        bar_h = int(H * 0.03)
        bar_x = info_x + pad
        bar_color = GREEN if c.ctype == "player" else RED
        pygame.draw.rect(surf, GRAY,      (bar_x, bar_y, bar_w, bar_h))
        fill = int(bar_w * c.hp / c.hp_max)
        pygame.draw.rect(surf, bar_color, (bar_x, bar_y, fill, bar_h))
        pygame.draw.rect(surf, BLACK,     (bar_x, bar_y, bar_w, bar_h), 2)
        hp_str = f"{c.hp} / {c.hp_max}"
        draw_text(surf, hp_str, self.fonts["hint"], BLACK,
                  bar_x + bar_w // 2, bar_y + bar_h // 2)

        # 탭
        tab_y = bar_y + bar_h + int(H * 0.03)
        tab_h = int(H * 0.06)
        for ti, tname in enumerate(self.TAB_NAMES):
            tx   = info_x + pad + ti * tab_w
            trec = pygame.Rect(tx, tab_y, tab_w, tab_h)
            if ti == self.inspect_tab:
                pygame.draw.rect(surf, BLACK, trec)
                draw_text(surf, tname, self.fonts["menu"], WHITE, trec.centerx, trec.centery)
            else:
                pygame.draw.rect(surf, WHITE, trec)
                pygame.draw.rect(surf, BLACK, trec, 1)
                draw_text(surf, tname, self.fonts["menu"], BLACK, trec.centerx, trec.centery)

        # 탭 내용
        content_y    = tab_y + tab_h
        content_rect = pygame.Rect(info_x + pad, content_y,
                                   tabs_total_w, panel.bottom - pad - content_y)
        pygame.draw.rect(surf, WHITE, content_rect)
        pygame.draw.rect(surf, BLACK, content_rect, 1)

        if self.inspect_tab == 0:
            if c.overview:
                line_h = int(H * 0.04)
                tx = content_rect.left + int(W * 0.015)
                ty = content_rect.top + int(H * 0.025) - self.inspect_scroll
                old_clip = surf.get_clip()
                surf.set_clip(content_rect)
                for line in c.overview:
                    if line == "":
                        ty += line_h // 2
                    else:
                        if content_rect.top <= ty <= content_rect.bottom:
                            draw_text_left(surf, line, self.fonts["hint_bold"], BLACK, tx, ty + line_h // 2)
                        ty += line_h
                surf.set_clip(old_clip)
            else:
                draw_text(surf, "준비 중입니다.", self.fonts["menu"], GRAY_D,
                          content_rect.centerx, content_rect.centery)
        elif self.inspect_tab == 1:
            if c.skills:
                icon_size   = int(H * 0.08)
                gap_line    = int(H * 0.03)
                gap_block   = int(H * 0.015)
                tx          = content_rect.left + int(W * 0.015)
                ty          = content_rect.top + int(H * 0.02) - self.inspect_scroll
                old_clip    = surf.get_clip()
                surf.set_clip(content_rect)
                for si, skill in enumerate(c.skills):
                    # 아이콘 사각형 + 스프라이트
                    icon_rect = pygame.Rect(tx, ty, icon_size, icon_size)
                    if content_rect.top <= ty + icon_size <= content_rect.bottom or content_rect.top <= ty <= content_rect.bottom:
                        pygame.draw.rect(surf, GRAY,  icon_rect)
                        pygame.draw.rect(surf, BLACK, icon_rect, 1)
                        spr_path = skill.get("sprite", "")
                        if os.path.exists(spr_path):
                            try:
                                spr_img = pygame.image.load(spr_path).convert_alpha()
                                iw, ih  = spr_img.get_size()
                                scale   = min(icon_size / iw, icon_size / ih)
                                spr_img = pygame.transform.smoothscale(spr_img, (int(iw * scale), int(ih * scale)))
                                spr_r   = spr_img.get_rect(center=icon_rect.center)
                                surf.blit(spr_img, spr_r)
                            except Exception:
                                pass

                    # 스킬명 + 위력/유형 한 줄
                    info_x  = tx + icon_size + int(W * 0.01)
                    name_y  = ty + int(icon_size * 0.2)
                    tags_str = "  |  ".join(f"'{t}'" for t in skill["tags"]) if skill["tags"] else ""
                    hits_str = f"  |  {skill['hits']}회" if skill["hits"] > 1 else ""
                    elements = f"위력 {skill['power']}  |  {skill['type']}  |  {skill['target']}{hits_str}"
                    if tags_str:
                        elements += f"  |  {tags_str}"
                    if content_rect.top <= name_y <= content_rect.bottom:
                        draw_text_left(surf, skill['name'], self.fonts["hint_bold"], BLACK, info_x, name_y)
                    elem_y = name_y + int(H * 0.033)
                    if content_rect.top <= elem_y <= content_rect.bottom:
                        draw_text_left_underline(surf, elements, self.fonts["small_bold"], BLACK, info_x, elem_y)

                    # 설명
                    desc_y = name_y + int(H * 0.033) + int(H * 0.035)
                    for line in skill["desc"]:
                        if content_rect.top <= desc_y <= content_rect.bottom:
                            draw_text_left_underline(surf, line, self.fonts["small_bold"], BLACK, info_x, desc_y)
                        desc_y += gap_line

                    block_h = max(icon_size, int(icon_size * 0.2) + int(H * 0.033) + int(H * 0.035) + len(skill["desc"]) * gap_line)
                    ty += block_h + gap_block

                    # 구분선 (마지막 제외)
                    if si < len(c.skills) - 1:
                        if content_rect.top <= ty <= content_rect.bottom:
                            pygame.draw.line(surf, GRAY,
                                (content_rect.left + int(W * 0.01), ty),
                                (content_rect.right - int(W * 0.01), ty), 1)
                        ty += gap_block
                surf.set_clip(old_clip)
            else:
                draw_text(surf, "준비 중입니다.", self.fonts["menu"], GRAY_D,
                          content_rect.centerx, content_rect.centery)
        elif self.inspect_tab == 2:
            if c.passives:
                tx         = content_rect.left + int(W * 0.015)
                ty         = content_rect.top + int(H * 0.02) - self.inspect_scroll
                gap_name   = int(H * 0.035)
                gap_desc   = int(H * 0.03)
                gap_block  = int(H * 0.015)
                old_clip   = surf.get_clip()
                surf.set_clip(content_rect)
                self._underline_rects = []
                for pi, passive in enumerate(c.passives):
                    if content_rect.top <= ty <= content_rect.bottom:
                        draw_text_left(surf, f"<{passive['name']}>", self.fonts["hint_bold"], BLACK, tx, ty + gap_name // 2)
                    ty += gap_name
                    for line in passive["desc"]:
                        if content_rect.top <= ty <= content_rect.bottom:
                            if line == "":
                                ty += gap_desc // 2
                                continue
                            rects = draw_text_left_underline(surf, line, self.fonts["small_bold"], BLACK, tx, ty + gap_desc // 2)
                            for r, word in rects:
                                self._underline_rects.append((r, word, c))
                        ty += gap_desc
                    ty += gap_block
                    # 마지막 패시브엔 구분선 없음
                    if pi < len(c.passives) - 1:
                        if content_rect.top <= ty <= content_rect.bottom:
                            pygame.draw.line(surf, GRAY,
                                (content_rect.left + int(W * 0.01), ty),
                                (content_rect.right - int(W * 0.01), ty), 1)
                        ty += gap_block
                surf.set_clip(old_clip)
            else:
                draw_text(surf, "준비 중입니다.", self.fonts["menu"], GRAY_D,
                          content_rect.centerx, content_rect.centery)


    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        # ── 적 ────────────────────────────────────────────────────
        enemy_pos = self._enemy_positions()
        for i, (e, (ex, ey)) in enumerate(zip(self.enemies, enemy_pos)):
            if e.sprite:
                r = e.sprite.get_rect(midbottom=(ex, ey + int(H * 0.08)))
                surf.blit(e.sprite, r)
            else:
                pygame.draw.rect(surf, GRAY, pygame.Rect(ex - 40, ey - 80, 80, 80))

            if e.ctype == "boss":
                bw = int(W * 0.55)
                bh = int(H * 0.035)
                bx = (W - bw) // 2
                by = int(H * 0.03)
                pygame.draw.rect(surf, GRAY,  (bx, by, bw, bh))
                fill = int(bw * e.hp / e.hp_max)
                pygame.draw.rect(surf, RED,   (bx, by, fill, bh))
                pygame.draw.rect(surf, BLACK, (bx, by, bw, bh), 2)
                draw_text(surf, e.title, self.fonts["hint"], BLACK, W // 2, by + bh + int(H * 0.025))
                draw_text(surf, e.name,  self.fonts["menu"], BLACK, W // 2, by + bh + int(H * 0.065))
            else:
                bw = int(W * 0.1)
                bh = int(H * 0.018)
                bx = ex - bw // 2
                by = ey - int(H * 0.22)
                pygame.draw.rect(surf, GRAY,  (bx, by, bw, bh))
                fill = int(bw * e.hp / e.hp_max)
                pygame.draw.rect(surf, RED,   (bx, by, fill, bh))
                pygame.draw.rect(surf, BLACK, (bx, by, bw, bh), 1)

        # ── 아군 ──────────────────────────────────────────────────
        ally_pos = self._ally_positions()
        for a, (ax, ay) in zip(self.allies, ally_pos):
            if a.sprite:
                flipped = pygame.transform.flip(a.sprite, True, False)
                r = flipped.get_rect(midbottom=(ax, ay))
                surf.blit(flipped, r)
            else:
                pygame.draw.rect(surf, GRAY, pygame.Rect(ax - 30, ay - 60, 60, 60))

            bw = int(W * 0.09)
            bh = int(H * 0.018)
            bx = ax - bw // 2
            by = ay - int(H * 0.04)
            pygame.draw.rect(surf, GRAY,  (bx, by, bw, bh))
            fill = int(bw * a.hp / a.hp_max)
            pygame.draw.rect(surf, GREEN, (bx, by, fill, bh))
            pygame.draw.rect(surf, BLACK, (bx, by, bw, bh), 1)

        # ── 행동 메뉴 UI ──────────────────────────────────────────
        ui     = self._ui_rect()
        item_h = ui.height // (len(self.UI_ITEMS) + 1)
        pygame.draw.rect(surf, WHITE, ui)
        pygame.draw.rect(surf, BLACK, ui, 2)
        for i, item in enumerate(self.UI_ITEMS):
            cy  = ui.top + item_h * (i + 1)
            sel = (i == self.menu_selected)
            r   = pygame.Rect(ui.left + 4, cy - item_h // 2 + 2, ui.width - 8, item_h - 4)
            if sel and self.state == self.STATE_MENU:
                pygame.draw.rect(surf, BLACK, r)
                draw_text(surf, item, self.fonts["menu"], WHITE, ui.centerx, cy)
            else:
                draw_text(surf, item, self.fonts["menu"], BLACK, ui.centerx, cy)

        # ── 대상 선택 창 ──────────────────────────────────────────
        if self.state == self.STATE_TARGET:
            tr     = self._target_rect()
            slot_h = tr.height // 5
            pygame.draw.rect(surf, WHITE, tr)
            pygame.draw.rect(surf, BLACK, tr, 2)
            for i in range(5):
                slot_rect = pygame.Rect(tr.left, tr.top + i * slot_h, tr.width, slot_h)
                pygame.draw.line(surf, GRAY, (tr.left, tr.top + i * slot_h), (tr.right, tr.top + i * slot_h), 1)
                if i < len(self.enemies):
                    e   = self.enemies[i]
                    sel = (i == self.target_selected)
                    cy  = slot_rect.centery
                    if sel:
                        pygame.draw.rect(surf, BLACK, slot_rect)
                        draw_text(surf, e.name, self.fonts["menu"], WHITE, tr.centerx, cy)
                    else:
                        draw_text(surf, e.name, self.fonts["menu"], BLACK, tr.centerx, cy)

        # ── 열람 오버레이 ─────────────────────────────────────────
        c = self._inspect_target()
        if c is not None:
            self._draw_inspect_overlay(c)

        draw_text(surf, "Esc  돌아가기",
                  self.fonts["hint"], GRAY_D, W // 2, H - int(H * 0.02))


# ══════════════════════════════════════════════════════════════════
#   플레이스홀더
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
def load_fonts(H):
    def f(size):  return pygame.font.SysFont("malgungothic,nanumgothic,malgun gothic,gulim,sans-serif", size, bold=False)
    def fb(size): return pygame.font.SysFont("malgungothic,nanumgothic,malgun gothic,gulim,sans-serif", size, bold=True)
    return {
        "title":      fb(int(H * 0.08)),
        "menu":       fb(int(H * 0.038)),
        "hint":       f(int(H * 0.022)),
        "hint_bold":  fb(int(H * 0.022)),
        "small_bold": fb(int(H * 0.016)),
    }


# ══════════════════════════════════════════════════════════════════
#   메인 루프
# ══════════════════════════════════════════════════════════════════
def main():
    global MON_W, MON_H
    pygame.init()
    pygame.display.set_caption("뻔하디 뻔한 JRPG")

    info = pygame.display.Info()
    MON_W, MON_H = info.current_w, info.current_h

    screen, W, H = apply_resolution()
    fonts  = load_fonts(H)
    clock  = pygame.time.Clock()

    title        = TitleScreen(screen, W, H, fonts)
    current      = "title"
    overlay      = None
    quit_dlg     = None
    placeholder  = None
    settings_sc  = None
    gallery_sc   = None
    battle_sc    = None

    comp_stack   = []

    def push_comp(screen_obj):
        comp_stack.append(screen_obj)

    def pop_comp():
        if comp_stack:
            comp_stack.pop()

    def comp_top():
        return comp_stack[-1] if comp_stack else None

    while True:
        dt = clock.tick(FRAMERATES[settings["fps_index"]])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if overlay == "quit":
                r = quit_dlg.handle_event(event)
                if r == "yes":  pygame.quit(); sys.exit()
                elif r == "no": overlay = None
                continue

            if current == "compendium" and comp_stack:
                top = comp_top()
                r   = top.handle_event(event)

                if isinstance(top, CompendiumDetailScreen):
                    if r == "back":
                        pop_comp()
                        if not comp_stack:
                            current = "gallery"

                elif isinstance(top, CompendiumMenuScreen):
                    if r is None:
                        pass
                    elif r[0] == "back":
                        pop_comp()
                        if not comp_stack:
                            current = "gallery"
                    elif r[0] == "select":
                        val  = r[1]
                        name = top.items[top.selected][0]
                        if isinstance(val, dict) and "image" in val:
                            push_comp(CompendiumDetailScreen(screen, W, H, fonts, val))
                        elif isinstance(val, dict):
                            items = [(k, v) for k, v in val.items()]
                            push_comp(CompendiumMenuScreen(screen, W, H, fonts, name, items))
                        elif val is None:
                            pass
                continue

            if current == "title":
                a = title.handle_event(event)
                if a == "quit":
                    quit_dlg = QuitDialog(screen, W, H, fonts)
                    overlay  = "quit"
                elif a == "settings":
                    settings_sc = SettingsScreen(screen, W, H, fonts)
                    current = "settings"
                elif a == "gallery":
                    gallery_sc = GalleryScreen(screen, W, H, fonts)
                    current = "gallery"
                elif a == "start":
                    placeholder = PlaceholderScreen(screen, W, H, fonts, "게임 시작")
                    current = "placeholder"
                elif a == "battle_test":
                    battle_sc = BattleScreen(screen, W, H, fonts,
                                             enemies=["벨라"],
                                             allies=["주인공", "아우렐리우스", "금강"])
                    current = "battle"

            elif current == "settings":
                r = settings_sc.handle_event(event)
                if r == "back":
                    screen, W, H = apply_resolution()
                    fonts  = load_fonts(H)
                    title  = TitleScreen(screen, W, H, fonts)
                    current = "title"

            elif current == "gallery":
                r = gallery_sc.handle_event(event)
                if r == "back":
                    current = "title"
                elif r == "cutscene":
                    placeholder = PlaceholderScreen(screen, W, H, fonts, "스토리 컷신")
                    current = "placeholder"
                elif r == "compendium":
                    comp_stack.clear()
                    top_items = [(k, v) for k, v in COMPENDIUM.items()]
                    push_comp(CompendiumMenuScreen(screen, W, H, fonts, "적 도감", top_items))
                    current = "compendium"

            elif current == "battle":
                r = battle_sc.handle_event(event)
                if r == "back":
                    current = "title"

            elif current == "placeholder":
                r = placeholder.handle_event(event)
                if r == "back":
                    current = "title"

        if current == "title":          title.update(dt)
        elif current == "settings":     settings_sc.update(dt)
        elif current == "gallery":      gallery_sc.update(dt)
        elif current == "compendium" and comp_stack:
                                        comp_top().update(dt)
        elif current == "battle":       battle_sc.update(dt)
        elif current == "placeholder":  placeholder.update(dt)
        if overlay == "quit":           quit_dlg.update(dt)

        if current == "title":          title.draw()
        elif current == "settings":     settings_sc.draw()
        elif current == "gallery":      gallery_sc.draw()
        elif current == "compendium" and comp_stack:
                                        comp_top().draw()
        elif current == "battle":       battle_sc.draw()
        elif current == "placeholder":  placeholder.draw()
        if overlay == "quit":           quit_dlg.draw()

        pygame.display.flip()


if __name__ == "__main__":
    main()