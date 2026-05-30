import pygame
import os
from utils import *
from combatant import Combatant
from data.characters_data import ENEMY_DEFS, ALLY_DEFS
from battle_logic import BattleLogic


# ══════════════════════════════════════════════════════════════════
#   전투 화면
# ══════════════════════════════════════════════════════════════════
from screens.battle_anim import BattleAnimMixin
from screens.battle_draw import BattleDrawMixin


class BattleScreen(BattleAnimMixin, BattleDrawMixin):
    ENEMY_ORDER   = [0, -1, 1, -2, 2]
    ENEMY_SPACING = 0.13
    ALLY_SPACING  = 0.15
    UI_H_RATIO    = 0.3
    BOSS_HEIGHT_RATIO   = 0.6
    NORMAL_HEIGHT_RATIO = 0.45
    CAM_MOVE_RATIO = 0.25  # 해상도의 25% 추가 이동 가능
    ZOOM_MIN       = 0.5
    ZOOM_MAX       = 1
    ZOOM_STEP      = 0.1
    STATE_MENU   = "menu"
    STATE_SKILL  = "skill"
    STATE_TARGET = "target"
    STATE_ENEMY  = "enemy"
    STATE_ANIM   = "anim"
    STATE_ROLL   = "roll"
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
        self._exec_pending   = None

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
        self._bg_cache    = None
        self._floor_cache = None
        self._last_zoom   = None

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
        self._sound_cache = {}      # 스킬 효과음 캐시
        self._effect_img_cache = {} # 이펙트 이미지 캐시
        self.order_expanded = False  # 행동 서열 펼치기
        self._disp_cam_x = 0.0
        self._disp_cam_y = 0.0
        self._disp_zoom  = 1.0
        self._returning  = False
        self._order_btn_rect = None

        # ── 스킬 모션 애니메이션 ──────────────────────────────
        self.anim = None          # 진행 중인 애니메이션 데이터
        self.shake_timer = 0.0    # 카메라 쉐이크 남은 시간
        self.shake_mag   = 0      # 쉐이크 강도
        self.effect_sprite = None # 현재 재생 중인 이펙트
        self.effect_pos    = (0, 0)
        self.effect_timer  = 0.0
        self.effects       = []   # [{img, target, timer}] 다중 이펙트
        self.dmg_popups    = []   # [{target, amount, timer, life}] 데미지 팝업
        self.total_dmg     = 0    # 현재 스킬 누적 피해
        self.total_side    = None # "ally"/"enemy" 시전자 진영 (Total 위치용)
        self.total_show    = False
        self.roll = None   # {actor,skill,primary,targets,timer,final_power,display}
        self._lb_ratio = 0.0   # 레터박스 펼침 비율 (실행 페이즈 동안 1 유지)
        self.anim_actor_offset = {}  # {combatant: (dx, dy)} 모션 중 위치 보정

        # 첫 룰렛 렉 방지: 모든 스킬 리소스 미리 로드
        self.preload_skill_assets()

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
                mp_y        = bar_y + bar_h + int(H * 0.012)
                tab_y       = mp_y + bar_h + int(H * 0.03)
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
                mp_y        = bar_y + bar_h + int(H * 0.012)
                tab_y       = mp_y + bar_h + int(H * 0.03)
                tab_h       = int(H * 0.06)
                if tab_y <= my <= tab_y + tab_h:
                    for ti in range(len(self.TAB_NAMES)):
                        tx = info_x + pad + ti * tab_w
                        if tx <= mx <= tx + tab_w:
                            self.inspect_tab = ti
                            self.inspect_scroll = 0
            return None

        if event.type == pygame.KEYDOWN:
            if self.state in (self.STATE_ANIM, self.STATE_ROLL):
                return None  # 모션/룰렛 중 입력 무시
            if event.key == pygame.K_ESCAPE:
                if self.state in (self.STATE_TARGET, self.STATE_SKILL):
                    pass  # 각 상태에서 개별 처리
                elif self.state == self.STATE_MENU:
                    # 계획 진행 중(2번째 이후)이면 전체 리셋, 첫 캐릭이면 나가기
                    if self.logic.planned:
                        self.logic.reset_plan()
                        self._sync_turn()
                    else:
                        pygame.mixer.music.stop()
                        return "back"
                elif self.state in (self.STATE_OVER, self.STATE_ENEMY):
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
                actor = self.logic.planning_actor()
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
                actor = self.logic.planning_actor()
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
            # 스프라이트 클릭(정보 열람)은 UI 영역이 아닐 때만 (UI가 위 레이어)
            if not on_ui:
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
                actor = self.logic.planning_actor()
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
            elif self.state == self.STATE_MENU and self.logic.planned:
                # 계획 진행 중 → 전체 리셋
                self.logic.reset_plan()
                self._sync_turn()

        elif event.type == pygame.MOUSEWHEEL:
            self.zoom = max(self.ZOOM_MIN, min(self.ZOOM_MAX, self.zoom + self.ZOOM_STEP * event.y))

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
            self.zoom = min(self.ZOOM_MAX, self.zoom + self.ZOOM_STEP)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
            self.zoom = max(self.ZOOM_MIN, self.zoom - self.ZOOM_STEP)

        return None
    def _sync_turn(self):
        """계획/실행 단계에 맞춰 상태 전환"""
        if self.logic.battle_over:
            self.state = self.STATE_OVER
            return
        if not self.logic.is_planning_done():
            # 계획 단계: 현재 계획 받을 아군에게 메뉴 표시
            actor = self.logic.planning_actor()
            if actor is None:
                return
            self.state = self.STATE_MENU
            self.menu_selected = 0
            self.current_actor = actor
        else:
            # 실행 단계: 현재 행동자의 예약 행동 실행
            self._exec_next()
    def _exec_next(self):
        """실행 단계: 현재 행동자의 예약 행동을 실행"""
        if self.logic.battle_over:
            self.state = self.STATE_OVER
            return
        actor = self.logic.current_actor()
        if actor is None:
            return
        self.current_actor = actor
        plan = self.logic.planned_action_of(actor)
        kind = plan.get("kind")

        if kind == "defend":
            self.logic.do_defend(actor)
            self.logic.advance()
            self._sync_turn()
            return
        if kind == "skip":
            self.logic.advance()
            self._sync_turn()
            return

        skill = plan.get("skill")
        primary = plan.get("primary")
        if skill is None:
            self.logic.advance()
            self._sync_turn()
            return

        targets = self.logic.resolve_targets(actor, skill, primary)
        # 적이 primary 미지정이면 대상 첫 번째를 primary로
        if primary is None and targets:
            primary = targets[0]
        # 위력 룰렛 연출 시작 (1초 후 모션)
        self._start_roll(actor, skill, primary, targets)
    def _target_list(self):
        """현재 pending_skill의 진영에 따른 대상 후보 리스트"""
        actor = self.logic.planning_actor() or self.logic.current_actor()
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
    MELEE_RUSH_SKILLS = {"난무", "쾌속 베기"}
    def _do_attack(self, target_idx):
        """계획 단계: 현재 아군의 스킬+대상을 계획에 저장"""
        actor = self.logic.planning_actor()
        if actor is None or self.pending_skill is None:
            return
        skill = self.pending_skill
        pool = self._target_list()
        primary = None
        if 0 <= target_idx < len(pool):
            primary = pool[target_idx]
        elif pool:
            primary = pool[0]
        self.logic.set_plan(actor, "skill", skill=skill, primary=primary)
        self.pending_skill = None
        self._after_plan_step()
    def _do_defend(self):
        actor = self.logic.planning_actor()
        if actor:
            self.logic.set_plan(actor, "defend")
            self._after_plan_step()
    def _after_plan_step(self):
        """계획 한 단계 끝난 뒤: 다음 아군 메뉴 or 실행 시작"""
        if self.logic.is_planning_done():
            # 전원 계획 완료 → 실행 시작
            self._sync_turn()
        else:
            # 다음 아군 계획
            self.state = self.STATE_MENU
            self.menu_selected = 0
            self.current_actor = self.logic.planning_actor()
    def update(self, dt):
        # 레터박스: 실행 페이즈 동안 펼침(1), 그 외 접힘(0) — 슬라이드 보간
        in_exec = self.logic.is_planning_done() and not self.logic.battle_over
        target_lb = 1.0 if in_exec else 0.0
        step = dt / self.LETTERBOX_SLIDE
        if self._lb_ratio < target_lb:
            self._lb_ratio = min(target_lb, self._lb_ratio + step)
        elif self._lb_ratio > target_lb:
            self._lb_ratio = max(target_lb, self._lb_ratio - step)

        # 쉐이크 감쇠
        if self.shake_timer > 0:
            self.shake_timer = max(0, self.shake_timer - dt)
        # 이펙트 타이머
        if self.effects:
            for ef in self.effects:
                ef["timer"] = max(0, ef["timer"] - dt)
            self.effects = [ef for ef in self.effects if ef["timer"] > 0]
        # 데미지 팝업 타이머
        if self.dmg_popups:
            for p in self.dmg_popups:
                p["timer"] = max(0, p["timer"] - dt)
            self.dmg_popups = [p for p in self.dmg_popups if p["timer"] > 0]

        # 적 턴 자동 진행
        if self.state == self.STATE_ENEMY:
            self.enemy_timer += dt
            if self.enemy_timer >= 600:
                pend = getattr(self, "_exec_pending", None)
                if pend:
                    actor, skill, primary = pend
                    self._start_total(actor)
                    _res = self.logic.use_skill(actor, skill, primary_target=primary)
                    self._play_skill_sound(skill)
                    self._register_damage(_res)
                    self._exec_pending = None
                self.logic.advance()
                self.enemy_timer = 0.0
                self._clear_total()
                self.roll = None
                self._sync_turn()

        # 스킬 모션 진행
        elif self.state == self.STATE_ANIM and self.anim:
            self.anim["elapsed"] = self.anim.get("elapsed", 0) + dt
            if self.anim["type"] == "command":
                self._update_command(dt)
            elif self.anim["type"] == "cast":
                self._update_cast(dt)
            else:
                self._update_melee_rush(dt)

        # 위력 룰렛 진행
        elif self.state == self.STATE_ROLL and self.roll:
            import random as _r
            self.roll["timer"] += dt
            t = self.roll["timer"]
            if t < self.ROLL_TIME:
                # 후반으로 갈수록 최종값에 가깝게 흔들림 폭 축소
                prog = t / self.ROLL_TIME
                fp = self.roll["final_power"]
                spread = max(1, int(fp * 0.6 * (1 - prog)))
                self.roll["display"] = max(0, fp + _r.randint(-spread, spread))
            else:
                # 최종 위력 확정 후 1초 대기 → 모션
                self.roll["display"] = self.roll["final_power"]
                if t >= self.ROLL_TIME + self.ROLL_HOLD:
                    self._begin_skill_motion()