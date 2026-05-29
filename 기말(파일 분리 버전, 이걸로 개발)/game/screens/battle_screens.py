import pygame
import os
from utils import *
from combatant import Combatant
from data.characters_data import ENEMY_DEFS, ALLY_DEFS
from battle_logic import BattleLogic


# ══════════════════════════════════════════════════════════════════
#   전투 화면
# ══════════════════════════════════════════════════════════════════
class BattleScreen:
    ENEMY_ORDER   = [0, -1, 1, -2, 2]
    ENEMY_SPACING = 0.13
    ALLY_SPACING  = 0.15
    UI_H_RATIO    = 0.3
    
    # 적 위치 설정 (화면 높이 비율)
    BOSS_HEIGHT_RATIO   = 0.6
    NORMAL_HEIGHT_RATIO = 0.45

    # 카메라
    CAM_MOVE_RATIO = 0.25  # 해상도의 25% 추가 이동 가능
    ZOOM_MIN       = 0.5
    ZOOM_MAX       = 1
    ZOOM_STEP      = 0.1

    STATE_MENU   = "menu"
    STATE_SKILL  = "skill"
    STATE_TARGET = "target"
    STATE_ENEMY  = "enemy"
    STATE_ANIM   = "anim"
    STATE_OVER   = "over"

    TAB_NAMES = ["개요", "스킬", "패시브"]

    def __init__(self, screen, W, H, fonts, enemies, allies, enemy_formation="솔캐리_전방", ally_formation="트리오", gap=0.12):
        self.screen  = screen
        self.W, self.H = W, H
        self.fonts   = fonts

        enemy_max_w = int(W * 0.55)
        enemy_max_h = int(H * 0.55)
        ally_max_w  = int(W * 0.5)
        ally_max_h  = int(H * 0.5)

        self.enemies = [Combatant(ENEMY_DEFS[k], W, H, enemy_max_w, enemy_max_h) for k in enemies]
        self.allies  = [Combatant(ALLY_DEFS[k],  W, H, ally_max_w,  ally_max_h)  for k in allies]
        self.enemy_formation = enemy_formation
        self.ally_formation  = ally_formation
        self.gap             = gap  # 양 진영 앞 캐릭터 사이 거리 (화면 비율)

        # ── 배경 로드 (줌 최소(0.75)에서도 화면을 꽉 채우도록) ──
        # zoom_min=0.75일 때도 꽉 채우려면: BG * 0.75 >= W → BG >= W/0.75
        # 카메라 이동 25% 여유까지 포함: BG >= W * (1/0.75 + 0.25) ≈ W * 1.58
        # 여유있게 W * 1.7 사용
        WLD_W = int(W * 2.5)
        WLD_H = int(H * 1)

        self.background = None
        for enemy_name in enemies:
            bg_path = ENEMY_DEFS[enemy_name].get("background")
            if bg_path and os.path.exists(bg_path):
                try:
                    bg_img = pygame.image.load(bg_path).convert()
                    orig_w, orig_h = bg_img.get_size()
                    # 가로를 WLD_W에 맞추고 세로는 비율 유지
                    scale = WLD_W / orig_w
                    self.background = pygame.transform.smoothscale(bg_img, (WLD_W, int(orig_h * scale)))
                    break
                except Exception as e:
                    print(f"배경 로드 실패: {bg_path} - {e}")

        # ── 바닥 로드 ──────────────────────────────────────────────
        self.floor = None
        for enemy_name in enemies:
            floor_path = ENEMY_DEFS[enemy_name].get("floor")
            if floor_path and os.path.exists(floor_path):
                try:
                    floor_img = pygame.image.load(floor_path).convert_alpha()
                    orig_w, orig_h = floor_img.get_size()
                    scale = WLD_W / orig_w
                    self.floor = pygame.transform.smoothscale(floor_img, (WLD_W, int(orig_h * scale)))
                    break
                except Exception as e:
                    print(f"바닥 로드 실패: {floor_path} - {e}")

        # ── 배경음악 재생 ──────────────────────────────────────────
        for enemy_name in enemies:
            bgm_path = ENEMY_DEFS[enemy_name].get("bgm")
            if bgm_path and os.path.exists(bgm_path):
                try:
                    pygame.mixer.music.load(bgm_path)
                    pygame.mixer.music.set_volume(settings["bgm_vol"] / 100.0)
                    pygame.mixer.music.play(-1)
                    break
                except Exception as e:
                    print(f"BGM 로드 실패: {bgm_path} - {e}")

        self.ui_y    = int(H * (1.0 - self.UI_H_RATIO))

        self.state           = self.STATE_MENU
        self.menu_selected   = 0
        self.target_selected = 0
        self.skill_selected  = 0
        self.UI_ITEMS        = ["스킬", "수비", "아이템"]
        self.pending_skill   = None   # 선택한 스킬 (대상 선택 대기)
        self.current_actor   = None

        # 전투 로직
        self.logic = BattleLogic(self.enemies, self.allies)
        self.logic.start_turn()
        self.enemy_timer = 0.0
        self._sync_turn()

        self.inspect_enemy   = None
        self.inspect_ally    = None
        self.inspect_tab     = 0
        self.inspect_sprite  = None
        self.inspect_scroll  = 0
        self._underline_rects = []

        # ── 카메라 ────────────────────────────────────────────────
        self.cam_x    = 0.0
        self.cam_y    = 0.0
        self.zoom     = 1.0
        self.dragging = False
        self.drag_start_mouse = (0, 0)
        self.drag_start_cam   = (0.0, 0.0)

        # ── 스프라이트 캐시 ───────────────────────────────────────
        self._cache_zoom = None
        self._enemy_cache = []
        self._ally_cache  = []

        # ── 비네팅 캐시 (한 번만 생성) ───────────────────────────
        vignette = pygame.Surface((W, H), pygame.SRCALPHA)
        cx, cy = W // 2, H // 2
        max_r = (cx ** 2 + cy ** 2) ** 0.5
        for y in range(0, H, 2):
            for x in range(0, W, 2):
                dx, dy = x - cx, y - cy
                dist = (dx ** 2 + dy ** 2) ** 0.5
                ratio = dist / max_r
                alpha = int(100 * ratio ** 2)
                if alpha > 0:
                    a = min(alpha, 200)
                    vignette.set_at((x, y), (0, 0, 0, a))
                    if x + 1 < W: vignette.set_at((x+1, y), (0, 0, 0, a))
                    if y + 1 < H: vignette.set_at((x, y+1), (0, 0, 0, a))
                    if x+1 < W and y+1 < H: vignette.set_at((x+1, y+1), (0, 0, 0, a))
        self._vignette = vignette
        self._skill_icon_cache = {}
        self.order_expanded = False  # 행동 서열 펼치기
        self._order_btn_rect = None

        # ── 스킬 모션 애니메이션 ──────────────────────────────
        self.anim = None          # 진행 중인 애니메이션 데이터
        self.shake_timer = 0.0    # 카메라 쉐이크 남은 시간
        self.shake_mag   = 0      # 쉐이크 강도
        self.effect_sprite = None # 현재 재생 중인 이펙트
        self.effect_pos    = (0, 0)
        self.effect_timer  = 0.0
        self.effects       = []   # [{img, target, timer}] 다중 이펙트
        self.anim_actor_offset = {}  # {combatant: (dx, dy)} 모션 중 위치 보정

    def _ui_rect(self):
        W, H = self.W, self.H
        ui_h = int(H * self.UI_H_RATIO) - int(H * 0.02)
        ui_w = int(W // 2 * 2 / 3) // 2
        ui_x = W - ui_w - int(W * 0.02)
        return pygame.Rect(ui_x, self.ui_y, ui_w, ui_h)

    def _target_rect(self):
        ui = self._ui_rect()
        return pygame.Rect(ui.left - ui.width, ui.top, ui.width, ui.height)

    def _world_to_screen(self, wx, wy):
        W, H = self.W, self.H
        sx = (wx - W / 2 - self.cam_x) * self.zoom + W / 2
        sy = (wy - H / 2 - self.cam_y) * self.zoom + H / 2
        return int(sx), int(sy)

    def _enemy_sprite_rect(self, i):
        positions = self._enemy_positions()
        if i >= len(positions):
            return None
        ex, ey = positions[i]
        e = self.enemies[i]
        zoom = self.zoom
        sx, sy = self._world_to_screen(ex, ey)
        if e.sprite:
            orig = e.sprite
            if i != 0:
                orig = pygame.transform.smoothscale(orig, (orig.get_width() // 2, orig.get_height() // 2))
            sw = int(orig.get_width() * zoom)
            sh = int(orig.get_height() * zoom)
            full = pygame.Rect(0, 0, sw, sh)
            full.midbottom = (sx, sy)
            ratio = e.defn.get("click_w_ratio", 1.0)
            new_w = int(full.width * ratio)
            return pygame.Rect(full.centerx - new_w // 2, full.top, new_w, full.height)
        size = int(80 * zoom)
        return pygame.Rect(sx - size // 2, sy - size, size, size)

    def _ally_sprite_rect(self, i):
        positions = self._ally_positions()
        if i >= len(positions):
            return None
        ax, ay = positions[i]
        a = self.allies[i]
        zoom = self.zoom
        sx, sy = self._world_to_screen(ax, ay)
        if a.sprite:
            sw = int(a.sprite.get_width() * zoom)
            sh = int(a.sprite.get_height() * zoom)
            full = pygame.Rect(0, 0, sw, sh)
            full.midbottom = (sx, sy)
            ratio = a.defn.get("click_w_ratio", 1.0)
            new_w = int(full.width * ratio)
            return pygame.Rect(full.centerx - new_w // 2, full.top, new_w, full.height)
        size = int(60 * zoom)
        return pygame.Rect(sx - size // 2, sy - size, size, size)

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
            if self.state == self.STATE_ANIM:
                return None  # 모션 중 입력 무시
            if event.key == pygame.K_ESCAPE:
                if self.state in (self.STATE_TARGET, self.STATE_SKILL):
                    pass  # 각 상태에서 개별 처리
                elif self.state in (self.STATE_MENU, self.STATE_OVER, self.STATE_ENEMY):
                    pygame.mixer.music.stop()
                    return "back"
            elif self.state == self.STATE_MENU:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.menu_selected = (self.menu_selected - 1) % len(self.UI_ITEMS)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.menu_selected = (self.menu_selected + 1) % len(self.UI_ITEMS)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if self.UI_ITEMS[self.menu_selected] == "스킬":
                        self.state = self.STATE_SKILL
                        self.skill_selected = 0
                    elif self.UI_ITEMS[self.menu_selected] == "수비":
                        self._do_defend()
            elif self.state == self.STATE_SKILL:
                actor = self.logic.current_actor()
                skills = actor.skills if actor else []
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.skill_selected = (self.skill_selected - 1) % max(1, len(skills))
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.skill_selected = (self.skill_selected + 1) % max(1, len(skills))
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if skills:
                        self.pending_skill = skills[self.skill_selected]
                        self.state = self.STATE_TARGET
                        self.target_selected = 0
                elif event.key == pygame.K_ESCAPE:
                    self.state = self.STATE_MENU
            elif self.state == self.STATE_TARGET:
                pool = self._target_list()
                n = max(1, len(pool))
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.target_selected = (self.target_selected - 1) % n
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.target_selected = (self.target_selected + 1) % n
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._do_attack(self.target_selected)
                elif event.key == pygame.K_ESCAPE:
                    self.state = self.STATE_SKILL

        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            # 카메라 드래그
            if self.dragging:
                dx = (mx - self.drag_start_mouse[0]) / self.zoom
                dy = (my - self.drag_start_mouse[1]) / self.zoom
                max_x = self.W * self.CAM_MOVE_RATIO
                max_y_up   = self.H * 0.25
                max_y_down = self.H * 0.05
                self.cam_x = max(-max_x, min(max_x, self.drag_start_cam[0] - dx))
                self.cam_y = max(-max_y_up, min(max_y_down, self.drag_start_cam[1] - dy))
            # UI 호버 (UI 내부에 마우스가 있을 때만 반응)
            if self.state == self.STATE_MENU:
                ui     = self._ui_rect()
                if ui.collidepoint(mx, my):
                    item_h = ui.height // (len(self.UI_ITEMS) + 1)
                    for i in range(len(self.UI_ITEMS)):
                        cy = ui.top + item_h * (i + 1)
                        if abs(my - cy) < item_h // 2:
                            self.menu_selected = i
            elif self.state == self.STATE_SKILL:
                actor = self.logic.current_actor()
                skills = actor.skills if actor else []
                tr = self._target_rect()
                if tr.collidepoint(mx, my) and skills:
                    slot_h = tr.height // max(5, len(skills))
                    for i in range(len(skills)):
                        slot_rect = pygame.Rect(tr.left, tr.top + i * slot_h, tr.width, slot_h)
                        if slot_rect.collidepoint(mx, my):
                            self.skill_selected = i
            elif self.state == self.STATE_TARGET:
                tr     = self._target_rect()
                if tr.collidepoint(mx, my):
                    pool = self._target_list()
                    slot_h = tr.height // 5
                    for i in range(len(pool)):
                        slot_rect = pygame.Rect(tr.left, tr.top + i * slot_h, tr.width, slot_h)
                        if slot_rect.collidepoint(mx, my):
                            self.target_selected = i

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            ui = self._ui_rect()
            tr = self._target_rect()
            # 행동 서열 펼치기 버튼
            if self._order_btn_rect and self._order_btn_rect.collidepoint(mx, my):
                self.order_expanded = not self.order_expanded
                return None
            on_ui = ui.collidepoint(mx, my) or (self.state in (self.STATE_TARGET, self.STATE_SKILL) and tr.collidepoint(mx, my))
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
            if self.state == self.STATE_MENU and ui.collidepoint(mx, my):
                item_h = ui.height // (len(self.UI_ITEMS) + 1)
                for i in range(len(self.UI_ITEMS)):
                    cy = ui.top + item_h * (i + 1)
                    if abs(my - cy) < item_h // 2:
                        self.menu_selected = i
                        if self.UI_ITEMS[i] == "스킬":
                            self.state = self.STATE_SKILL
                            self.skill_selected = 0
                        elif self.UI_ITEMS[i] == "수비":
                            self._do_defend()
            elif self.state == self.STATE_SKILL and tr.collidepoint(mx, my):
                actor = self.logic.current_actor()
                skills = actor.skills if actor else []
                if skills:
                    slot_h = tr.height // max(5, len(skills))
                    for i in range(len(skills)):
                        slot_rect = pygame.Rect(tr.left, tr.top + i * slot_h, tr.width, slot_h)
                        if slot_rect.collidepoint(mx, my):
                            self.pending_skill = skills[i]
                            self.skill_selected = i
                            self.state = self.STATE_TARGET
                            self.target_selected = 0
            elif self.state == self.STATE_TARGET and tr.collidepoint(mx, my):
                pool = self._target_list()
                slot_h = tr.height // 5
                for i in range(len(pool)):
                    slot_rect = pygame.Rect(tr.left, tr.top + i * slot_h, tr.width, slot_h)
                    if slot_rect.collidepoint(mx, my):
                        self._do_attack(i)
            # UI 아닌 곳 클릭 → 카메라 드래그 시작
            if not on_ui:
                self.dragging = True
                self.drag_start_mouse = (mx, my)
                self.drag_start_cam   = (self.cam_x, self.cam_y)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            # 우클릭: 뒤로 가기 (선택 취소)
            if self.state == self.STATE_TARGET:
                self.state = self.STATE_SKILL
                self.pending_skill = None
            elif self.state == self.STATE_SKILL:
                self.state = self.STATE_MENU

        elif event.type == pygame.MOUSEWHEEL:
            self.zoom = max(self.ZOOM_MIN, min(self.ZOOM_MAX, self.zoom + self.ZOOM_STEP * event.y))

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
            self.zoom = min(self.ZOOM_MAX, self.zoom + self.ZOOM_STEP)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
            self.zoom = max(self.ZOOM_MIN, self.zoom - self.ZOOM_STEP)

        return None

    def _sync_turn(self):
        """현재 행동자에 맞춰 상태 전환"""
        if self.logic.battle_over:
            self.state = self.STATE_OVER
            return
        actor = self.logic.current_actor()
        if actor is None:
            return
        if actor in self.allies and actor.ctype in ("player", "ally"):
            # 아군(플레이어 조작) 턴
            self.state = self.STATE_MENU
            self.menu_selected = 0
            self.current_actor = actor
        else:
            # 적 턴 → 자동 진행
            self.state = self.STATE_ENEMY
            self.enemy_timer = 0.0
            self.current_actor = actor

    def _target_list(self):
        """현재 pending_skill의 진영에 따른 대상 후보 리스트"""
        actor = self.logic.current_actor()
        skill = self.pending_skill
        if actor is None or skill is None:
            return []
        side = skill.get("side", "적")
        if side == "자신":
            return [actor]
        elif side == "아군":
            return [c for c in self.logic.allies_of(actor) if c.hp > 0]
        else:  # 적
            return [c for c in self.logic.enemies_of(actor) if c.hp > 0]

    # 근접 다단히트 모션을 쓰는 스킬
    MELEE_RUSH_SKILLS = {"난무", "쾌속 베기"}

    def _do_attack(self, target_idx):
        """플레이어가 지정한 대상으로 스킬 사용 (적/아군/자신 공통)"""
        actor = self.logic.current_actor()
        if actor is None or self.pending_skill is None:
            return
        skill = self.pending_skill
        pool = self._target_list()
        primary = None
        if 0 <= target_idx < len(pool):
            primary = pool[target_idx]
        elif pool:
            primary = pool[0]

        # 근접 다단히트 모션 스킬이면 애니메이션 시작
        if skill["name"] in self.MELEE_RUSH_SKILLS and primary is not None:
            targets = self.logic.resolve_targets(actor, skill, primary)
            self._start_melee_rush(actor, skill, primary, targets)
            self.pending_skill = None
            return

        # 그 외 즉시 처리
        self.logic.use_skill(actor, skill, primary_target=primary)
        self.pending_skill = None
        self.logic.advance()
        self._sync_turn()

    def _start_melee_rush(self, actor, skill, primary, targets):
        """마리 근접 다단히트 모션 시작"""
        hits = skill.get("hits", 1)
        self.anim = {
            "type":    "melee_rush",
            "actor":   actor,
            "skill":   skill,
            "primary": primary,
            "targets": targets,
            "hits":    hits,
            "hit_done": 0,
            "phase":   "zoom_in",   # zoom_in → approach → (dash → reset)*hits → return
            "timer":   0.0,
        }
        self.state = self.STATE_ANIM
        # 카메라 줌인 목표 저장
        self._anim_cam_start = (self.cam_x, self.cam_y, self.zoom)

    def _anim_actor_offset(self, combatant):
        """모션 중인 actor의 위치 오프셋 (월드 좌표)"""
        a = self.anim
        if not a or a.get("type") != "melee_rush" or a["actor"] is not combatant:
            return (0, 0)
        W, H = self.W, self.H
        # 대상 위치
        primary = a["primary"]
        if primary in self.enemies:
            pi = self.enemies.index(primary)
            tx, ty = self._enemy_positions()[pi]
        else:
            return (0, 0)
        # 마리 원래 위치
        ai = self.allies.index(a["actor"])
        ox0, oy0 = self._ally_positions()[ai]
        # 대상 왼쪽 위치 / 오른쪽(지나간) 위치
        left_x  = tx - int(W * 0.10)
        right_x = tx + int(W * 0.10)
        phase = a["phase"]
        t = a["timer"]
        if phase == "zoom_in":
            return (0, 0)
        elif phase == "approach":
            p = min(1.0, t / self.ANIM_APPROACH)
            cx = ox0 + (left_x - ox0) * p
            cy = oy0 + (ty - oy0) * p
            return (cx - ox0, cy - oy0)
        stationary = a["skill"].get("motion") == "stationary"
        if phase == "dash":
            if stationary:
                # 제자리(대상 왼쪽)에서 공격
                return (left_x - ox0, ty - oy0)
            p = min(1.0, t / self.ANIM_DASH)
            cx = left_x + (right_x - left_x) * p
            return (cx - ox0, ty - oy0)
        elif phase == "reset":
            if stationary:
                return (left_x - ox0, ty - oy0)
            p = min(1.0, t / self.ANIM_RESET)
            cx = right_x + (left_x - right_x) * p
            return (cx - ox0, ty - oy0)
        elif phase == "return":
            start_x = left_x if stationary else right_x
            p = min(1.0, t / self.ANIM_RETURN)
            cx = start_x + (ox0 - start_x) * p
            cy = ty + (oy0 - ty) * p
            return (cx - ox0, cy - oy0)
        return (0, 0)

    def _do_defend(self):
        actor = self.logic.current_actor()
        if actor:
            self.logic.do_defend(actor)
            self.logic.advance()
            self._sync_turn()

    # 모션 단계별 지속시간(ms)
    ANIM_ZOOM_IN  = 200
    ANIM_APPROACH = 250
    ANIM_DASH     = 200
    ANIM_RESET    = 150
    ANIM_RETURN   = 250

    def update(self, dt):
        # 쉐이크 감쇠
        if self.shake_timer > 0:
            self.shake_timer = max(0, self.shake_timer - dt)
        # 이펙트 타이머
        if self.effects:
            for ef in self.effects:
                ef["timer"] = max(0, ef["timer"] - dt)
            self.effects = [ef for ef in self.effects if ef["timer"] > 0]

        # 적 턴 자동 진행
        if self.state == self.STATE_ENEMY:
            self.enemy_timer += dt
            if self.enemy_timer >= 700:
                actor = self.logic.current_actor()
                if actor:
                    self.logic.enemy_action(actor)
                self._sync_turn()
                self.enemy_timer = 0.0

        # 스킬 모션 진행
        elif self.state == self.STATE_ANIM and self.anim:
            self._update_melee_rush(dt)

    def _update_melee_rush(self, dt):
        a = self.anim
        a["timer"] += dt
        phase = a["phase"]

        if phase == "zoom_in":
            if a["timer"] >= self.ANIM_ZOOM_IN:
                a["phase"] = "approach"; a["timer"] = 0.0
        elif phase == "approach":
            if a["timer"] >= self.ANIM_APPROACH:
                a["phase"] = "dash"; a["timer"] = 0.0
        elif phase == "dash":
            # 모션 중간(절반)에 피해 적용 + 쉐이크 + 이펙트
            if not a.get("hit_applied") and a["timer"] >= self.ANIM_DASH * 0.5:
                self.logic.apply_single_hit(a["actor"], a["skill"], a["targets"])
                a["hit_applied"] = True
                a["hit_done"] += 1
                self.shake_timer = 120
                self.shake_mag = int(self.H * 0.012)
                self._play_skill_effect(a["skill"], a["primary"])
            if a["timer"] >= self.ANIM_DASH:
                a["hit_applied"] = False
                if a["hit_done"] >= a["hits"] or self.logic.battle_over:
                    a["phase"] = "return"; a["timer"] = 0.0
                else:
                    a["phase"] = "reset"; a["timer"] = 0.0
        elif phase == "reset":
            if a["timer"] >= self.ANIM_RESET:
                a["phase"] = "dash"; a["timer"] = 0.0
        elif phase == "return":
            if a["timer"] >= self.ANIM_RETURN:
                # 모션 종료 → 다음 캐릭터
                self.anim = None
                self.effects = []
                self.logic.advance()
                self._sync_turn()

    def _load_effect_img(self, path):
        if path and os.path.exists(path):
            try:
                raw = pygame.image.load(path).convert_alpha()
                size = int(self.W * 0.12)
                return pygame.transform.smoothscale(raw, (size, size))
            except Exception:
                return None
        return None

    def _play_skill_effect(self, skill, target):
        self.effects = []
        actor = self.anim["actor"] if self.anim else None
        # 적/대상 이펙트
        tgt_path = skill.get("effect_target", skill.get("effect", skill.get("sprite", "")))
        img = self._load_effect_img(tgt_path)
        if img:
            self.effects.append({"img": img, "target": target, "timer": 200})
        # 마리(자신) 이펙트 (effect_self가 있을 때만)
        self_path = skill.get("effect_self", "")
        img2 = self._load_effect_img(self_path)
        if img2 and actor is not None:
            self.effects.append({"img": img2, "target": actor, "timer": 200})

    def _enemy_positions(self):
        from data.battle_presets import ENEMY_FORMATIONS
        W, H = self.W, self.H
        # 중앙 기준점
        center_x = int(W * 0.5 + W * self.gap)  # 적 진영 앞 기준 x
        center_y = int(H * 0.60)
        step_x   = int(W * 0.10)
        step_y   = int(H * 0.15)

        formation = ENEMY_FORMATIONS.get(self.enemy_formation, ENEMY_FORMATIONS["솔캐리_전방"])
        positions = []
        for i in range(len(self.enemies)):
            if i < len(formation):
                dx, dy = formation[i]
                positions.append((center_x + dx * step_x, center_y + dy * step_y))
            else:
                positions.append((center_x, center_y))
        return positions

    def _ally_positions(self):
        from data.battle_presets import ALLY_FORMATIONS
        W, H = self.W, self.H
        # 중앙 기준점 (적 진영과 대칭)
        center_x = int(W * 0.5 - W * self.gap)  # 아군 진영 앞 기준 x
        center_y = int(H * 0.60)
        step_x   = int(W * 0.10)
        step_y   = int(H * 0.15)

        formation = ALLY_FORMATIONS.get(self.ally_formation, ALLY_FORMATIONS["트리오"])
        positions = []
        for i in range(len(self.allies)):
            if i < len(formation):
                dx, dy = formation[i]
                # 아군은 x축 반전 (왼쪽 방향)
                positions.append((center_x - dx * step_x, center_y + dy * step_y))
            else:
                positions.append((center_x, center_y))
        return positions

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen

        # ── 애니메이션 중 카메라/쉐이크 보정 ─────────────────────
        anim_cam_dx = 0.0
        anim_cam_dy = 0.0
        anim_zoom_mul = 1.0
        if self.state == self.STATE_ANIM and self.anim and self.anim["actor"] in self.allies:
            # 마리의 현재(이동 중) 위치를 카메라가 따라감 + 확대
            ai = self.allies.index(self.anim["actor"])
            ax, ay = self._ally_positions()[ai]
            ox, oy = self._anim_actor_offset(self.anim["actor"])
            ax += ox; ay += oy
            anim_cam_dx = (ax - W / 2)
            anim_cam_dy = (ay - H / 2)
            anim_zoom_mul = 1.4
        # 쉐이크
        shake_x = shake_y = 0
        if self.shake_timer > 0:
            import random as _r
            shake_x = _r.randint(-self.shake_mag, self.shake_mag)
            shake_y = _r.randint(-self.shake_mag, self.shake_mag)

        # 실제 적용 카메라/줌 (원본 보존)
        base_cam_x, base_cam_y, base_zoom = self.cam_x, self.cam_y, self.zoom
        if self.state == self.STATE_ANIM and self.anim:
            # 모션 중: 사용자 줌/카메라 무시, 고정 줌으로 마리만 비춤
            eff_cam_x = anim_cam_dx + shake_x
            eff_cam_y = anim_cam_dy + shake_y
            eff_zoom  = 1.4
        else:
            eff_cam_x = self.cam_x + anim_cam_dx + shake_x
            eff_cam_y = self.cam_y + anim_cam_dy + shake_y
            eff_zoom  = self.zoom * anim_zoom_mul

        zoom = eff_zoom

        # 스프라이트 캐시 갱신 (줌 변경 시에만)
        if self._cache_zoom != zoom:
            self._enemy_cache = []
            for i, e in enumerate(self.enemies):
                if e.sprite_orig and e.sprite:
                    target_w = int(e.sprite.get_width() * zoom)
                    target_h = int(e.sprite.get_height() * zoom)
                    if i != 0:
                        target_w = target_w // 2
                        target_h = target_h // 2
                    self._enemy_cache.append(
                        pygame.transform.smoothscale(e.sprite_orig, (target_w, target_h))
                    )
                else:
                    self._enemy_cache.append(None)
            self._ally_cache = []
            for a in self.allies:
                if a.sprite_orig and a.sprite:
                    target_w = int(a.sprite.get_width() * zoom)
                    target_h = int(a.sprite.get_height() * zoom)
                    orig_flip = pygame.transform.flip(a.sprite_orig, True, False)
                    self._ally_cache.append(
                        pygame.transform.smoothscale(orig_flip, (target_w, target_h))
                    )
                else:
                    self._ally_cache.append(None)
            self._cache_zoom = zoom

        # 화면 → 줌/카메라 적용 좌표 변환
        def to_sx(wx): return int((wx - W / 2 - eff_cam_x) * zoom + W / 2)
        def to_sy(wy): return int((wy - H / 2 - eff_cam_y) * zoom + H / 2)

        # ── 배경 (125% 크기로 로드됨, 줌 1.0 = 화면 꽉 채움) ───
        surf.fill((0, 0, 0))
        if self.background:
            bw, bh = self.background.get_size()
            draw_w = int(bw * zoom)
            draw_h = int(bh * zoom)
            scaled_bg = pygame.transform.smoothscale(self.background, (draw_w, draw_h))
            bx = int(W / 2 - draw_w / 2 - eff_cam_x * zoom)
            by = int(H / 2 - draw_h / 2 - eff_cam_y * zoom)
            surf.blit(scaled_bg, (bx, by))
        else:
            surf.fill(WHITE)

        # ── 바닥 ──────────────────────────────────────────────────
        if self.floor:
            fw, fh = self.floor.get_size()
            draw_w = int(fw * zoom)
            draw_h = int(fh * zoom)
            scaled_floor = pygame.transform.smoothscale(self.floor, (draw_w, draw_h))
            fx = int(W / 2 - draw_w / 2 - eff_cam_x * zoom)
            fy = int(H / 2 - draw_h / 2 - eff_cam_y * zoom)
            surf.blit(scaled_floor, (fx, fy))

        # ── 적 ────────────────────────────────────────────────────
        enemy_pos = self._enemy_positions()
        for i, (e, (ex, ey)) in reversed(list(enumerate(zip(self.enemies, enemy_pos)))):
            if e.hp <= 0:
                continue
            sx = to_sx(ex)
            sy = to_sy(ey)
            spr = self._enemy_cache[i] if i < len(self._enemy_cache) else None
            spr_rect = None
            if spr:
                spr_rect = spr.get_rect(midbottom=(sx, sy))
                surf.blit(spr, spr_rect)
            else:
                size = int(80 * zoom)
                pygame.draw.rect(surf, GRAY, pygame.Rect(sx - size // 2, sy - size, size, size))

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
                # 고정 크기 (줌에만 비례, 스프라이트 크기 무관)
                bw = int(W * 0.08 * zoom)
                bh = max(4, int(H * 0.015 * zoom))
                bx = sx - bw // 2
                by = spr_rect.top - int(H * 0.02 * zoom) if spr_rect else sy - int(H * 0.25 * zoom)
                pygame.draw.rect(surf, GRAY,  (bx, by, bw, bh))
                fill = int(bw * e.hp / e.hp_max)
                pygame.draw.rect(surf, RED,   (bx, by, fill, bh))
                pygame.draw.rect(surf, BLACK, (bx, by, bw, bh), 1)

        # ── 아군 ──────────────────────────────────────────────────
        ally_pos = self._ally_positions()
        for j, (a, (ax, ay)) in reversed(list(enumerate(zip(self.allies, ally_pos)))):
            if a.hp <= 0:
                continue
            # 모션 중인 actor 위치 보정
            ox, oy = self._anim_actor_offset(a)
            ax += ox; ay += oy
            sx = to_sx(ax)
            sy = to_sy(ay)
            spr = self._ally_cache[j] if j < len(self._ally_cache) else None
            if spr:
                r = spr.get_rect(midbottom=(sx, sy))
                surf.blit(spr, r)
                bar_top = r.top - int(H * 0.01 * zoom)
            else:
                size = int(60 * zoom)
                pygame.draw.rect(surf, GRAY, pygame.Rect(sx - size // 2, sy - size, size, size))
                bar_top = sy - int(size + H * 0.01 * zoom)

            bw = int(W * 0.08 * zoom)
            bh = max(4, int(H * 0.015 * zoom))
            bx = sx - bw // 2
            by = bar_top
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

        # ── 스킬 선택 창 ──────────────────────────────────────────
        if self.state == self.STATE_SKILL:
            actor = self.logic.current_actor()
            skills = actor.skills if actor else []
            tr = self._target_rect()
            slot_h = tr.height // max(5, len(skills))
            pygame.draw.rect(surf, WHITE, tr)
            pygame.draw.rect(surf, BLACK, tr, 2)
            for i, sk in enumerate(skills):
                slot_rect = pygame.Rect(tr.left, tr.top + i * slot_h, tr.width, slot_h)
                pygame.draw.line(surf, GRAY, (tr.left, tr.top + i * slot_h), (tr.right, tr.top + i * slot_h), 1)
                sel = (i == self.skill_selected)
                cy = slot_rect.centery
                label = sk['name']
                if sel:
                    pygame.draw.rect(surf, BLACK, slot_rect)
                    draw_text(surf, label, self.fonts["menu"], WHITE, tr.centerx, cy)
                else:
                    draw_text(surf, label, self.fonts["menu"], BLACK, tr.centerx, cy)

            # ── 선택된 스킬 정보 박스 (스킬 선택창 위) ───────────
            if skills and 0 <= self.skill_selected < len(skills):
                sk = skills[self.skill_selected]
                info_h = int(H * 0.16)
                info_rect = pygame.Rect(tr.left, tr.top - info_h - int(H * 0.01), tr.width, info_h)
                pygame.draw.rect(surf, WHITE, info_rect)
                pygame.draw.rect(surf, BLACK, info_rect, 2)
                pad = int(W * 0.008)
                ix = info_rect.left + pad
                iy = info_rect.top + pad
                # 스킬명
                draw_text_left(surf, sk['name'], self.fonts["hint_bold"], BLACK, ix, iy + int(H * 0.015))
                # 위력/유형/대상
                side  = sk.get("side", "")
                count = sk.get("count", "")
                hits  = sk.get("hits", 1)
                hits_str = f"  {hits}회" if hits > 1 else ""
                line2 = f"위력 {sk['power']}  |  {sk['type']}  |  {side} {count}{hits_str}"
                draw_text_left(surf, line2, self.fonts["small_bold"], GRAY_D, ix, iy + int(H * 0.045))
                # 설명 (최대 2줄)
                dy = iy + int(H * 0.072)
                for line in sk.get("desc", [])[:3]:
                    draw_text_left(surf, line, self.fonts["small_bold"], BLACK, ix, dy)
                    dy += int(H * 0.028)

        # ── 대상 선택 창 ──────────────────────────────────────────
        if self.state == self.STATE_TARGET:
            tr     = self._target_rect()
            slot_h = tr.height // 5
            pool   = self._target_list()
            pygame.draw.rect(surf, WHITE, tr)
            pygame.draw.rect(surf, BLACK, tr, 2)
            for i in range(5):
                slot_rect = pygame.Rect(tr.left, tr.top + i * slot_h, tr.width, slot_h)
                pygame.draw.line(surf, GRAY, (tr.left, tr.top + i * slot_h), (tr.right, tr.top + i * slot_h), 1)
                if i < len(pool):
                    e   = pool[i]
                    sel = (i == self.target_selected)
                    cy  = slot_rect.centery
                    if sel:
                        pygame.draw.rect(surf, BLACK, slot_rect)
                        draw_text(surf, e.name, self.fonts["menu"], WHITE, tr.centerx, cy)
                    else:
                        draw_text(surf, e.name, self.fonts["menu"], BLACK, tr.centerx, cy)

        # ── 전투 종료 화면 ───────────────────────────────────────
        if self.state == self.STATE_OVER:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surf.blit(overlay, (0, 0))
            msg = "승리!" if self.logic.winner == "ally" else "패배..."
            color = (255, 230, 100) if self.logic.winner == "ally" else (255, 80, 80)
            draw_text(surf, msg, self.fonts["title"], color, W // 2, H // 2)
            draw_text(surf, "ESC: 나가기", self.fonts["hint"], WHITE, W // 2, H // 2 + int(H * 0.08))

        # ── 스킬 이펙트 스프라이트 ───────────────────────────────
        for ef in self.effects:
            t = ef["target"]
            if t in self.enemies:
                ti = self.enemies.index(t)
                tx, ty = self._enemy_positions()[ti]
            elif t in self.allies:
                ti = self.allies.index(t)
                tx, ty = self._ally_positions()[ti]
                # 마리 모션 중이면 현재 위치 반영
                ox, oy = self._anim_actor_offset(t)
                tx += ox; ty += oy
            else:
                tx, ty = W // 2, H // 2
            esx = to_sx(tx)
            esy = to_sy(ty - int(H * 0.15))
            er = ef["img"].get_rect(center=(esx, esy))
            surf.blit(ef["img"], er)

        # ── 행동 서열 UI (좌측 상단) ─────────────────────────────
        self._draw_turn_order()

        # ── 비네팅 ───────────────────────────────────────────────
        surf.blit(self._vignette, (0, 0))

        # ── 열람 오버레이 ─────────────────────────────────────────
        c = self._inspect_target()
        if c is not None:
            self._draw_inspect_overlay(c)

    def _draw_turn_order(self):
        """좌측 상단 행동 서열 UI (현재 행동자부터 최대 3개 + 턴 종료)"""
        if self.state == self.STATE_OVER:
            return
        W, H = self.W, self.H
        surf = self.screen
        order = self.logic.turn_order
        idx   = self.logic.order_idx
        if not order:
            return

        # 현재 행동자부터 남은 유닛들
        remaining = order[idx:]
        box_w = int(W * 0.16)
        box_h = int(H * 0.07)
        gap   = int(H * 0.012)
        margin_x = int(W * 0.015)
        margin_y = int(H * 0.015)

        slots = []  # (combatant or None for 턴종료)
        if self.order_expanded:
            # 전체 표시
            for c in remaining:
                slots.append(c)
            slots.append(None)  # 턴 종료
        else:
            for c in remaining[:3]:
                slots.append(c)
            if len(slots) < 3:
                slots.append(None)

        for si, c in enumerate(slots):
            bx = margin_x
            by = margin_y + si * (box_h + gap)
            box = pygame.Rect(bx, by, box_w, box_h)

            if c is None:
                # 턴 종료 박스
                s = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
                s.fill((60, 60, 60, 180))
                surf.blit(s, (bx, by))
                pygame.draw.rect(surf, (200, 200, 200), box, 2)
                draw_text(surf, f"{self.logic.turn_count}턴 종료", self.fonts["hint_bold"], WHITE, box.centerx, box.centery)
                continue

            is_ally = c in self.allies
            if is_ally:
                color = (60, 120, 255, 150)
                border = (120, 170, 255)
            else:
                color = (255, 60, 60, 150)
                border = (255, 120, 120)

            s = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            s.fill(color)
            surf.blit(s, (bx, by))
            # 현재 행동자(맨 위) 강조 테두리
            bw = 3 if si == 0 else 1
            pygame.draw.rect(surf, border, box, bw)

            # 프로필 (좌측 정사각)
            prof_size = box_h - int(H * 0.012)
            prof_rect = pygame.Rect(bx + int(H*0.006), by + int(H*0.006), prof_size, prof_size)
            if c.profile:
                pimg = pygame.transform.smoothscale(c.profile, (prof_size, prof_size))
                surf.blit(pimg, prof_rect)
            else:
                pygame.draw.rect(surf, (40, 40, 40), prof_rect)
            pygame.draw.rect(surf, WHITE, prof_rect, 1)

            # 속도 값 | 턴 수
            tx = prof_rect.right + int(W * 0.008)
            draw_text_left(surf, c.name, self.fonts["small_bold"], WHITE, tx, box.centery - int(H*0.015))
            info = f"속도 {c.speed}  |  {self.logic.turn_count}턴"
            draw_text_left(surf, info, self.fonts["small_bold"], WHITE, tx, box.centery + int(H*0.012))

            # 적이면 오른쪽에 사용 예정 스킬 아이콘
            if not is_ally:
                skill = getattr(c, "planned_skill", None)
                icon_size = prof_size
                icon_rect = pygame.Rect(box.right - icon_size - int(H*0.006), by + int(H*0.006), icon_size, icon_size)
                pygame.draw.rect(surf, (30, 30, 30), icon_rect)
                pygame.draw.rect(surf, WHITE, icon_rect, 1)
                if skill:
                    spr_path = skill.get("sprite", "")
                    img = self._skill_icon_cache.get(spr_path)
                    if img is None and spr_path and os.path.exists(spr_path):
                        try:
                            raw = pygame.image.load(spr_path).convert_alpha()
                            img = pygame.transform.smoothscale(raw, (icon_size, icon_size))
                            self._skill_icon_cache[spr_path] = img
                        except Exception:
                            img = None
                    if img:
                        surf.blit(img, icon_rect)

        # ── 펼치기/접기 버튼 (첫 박스 오른쪽) ────────────────────
        btn_w = int(W * 0.025)
        btn_h = box_h
        btn_x = margin_x + box_w + int(W * 0.004)
        btn_y = margin_y
        btn = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        s = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        s.fill((40, 40, 40, 180))
        surf.blit(s, (btn_x, btn_y))
        pygame.draw.rect(surf, (200, 200, 200), btn, 2)
        arrow = "▲" if self.order_expanded else "▼"
        draw_text(surf, arrow, self.fonts["menu"], WHITE, btn.centerx, btn.centery)
        self._order_btn_rect = btn

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
                for li, line in enumerate(c.overview):
                    if line == "":
                        ty += line_h // 2
                    else:
                        if content_rect.top <= ty <= content_rect.bottom:
                            font = self.fonts["hint_bold"] if li == 0 else self.fonts["small_bold"]
                            draw_text_left(surf, line, font, BLACK, tx, ty + line_h // 2)
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
                    side  = skill.get("side", skill.get("target", ""))
                    count = skill.get("count", "")
                    target_str = f"{side} {count}".strip()
                    elements = f"위력 {skill['power']}  |  {skill['type']}  |  {target_str}{hits_str}"
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



# ══════════════════════════════════════════════════════════════════
#   플레이스홀더
# ══════════════════════════════════════════════════════════════════