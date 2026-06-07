import pygame
import os
from utils import *
from combatant import Combatant
from data.characters_data import ENEMY_DEFS, ALLY_DEFS
from data.recruit_data import RECRUIT_POOL
from battle_logic import BattleLogic


def _ally_def(name):
    """아군 정의를 ALLY_DEFS(스토리/주인공) 또는 RECRUIT_POOL(모집)에서 찾는다."""
    if name in ALLY_DEFS:
        return ALLY_DEFS[name]
    return RECRUIT_POOL[name]


# 출전 인원수 → 아군 배치 이름
_ALLY_FORM_BY_COUNT = {1: "솔로", 2: "듀오", 3: "트리오", 4: "스쿼드", 5: "풀파티"}


def ally_formation_for(n):
    return _ALLY_FORM_BY_COUNT.get(max(1, min(5, n)), "솔로")


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
    ZOOM_MAX       = 2
    ZOOM_STEP      = 0.1
    STATE_MENU   = "menu"
    STATE_SKILL  = "skill"
    STATE_DEFENSE = "defense"   # 수비 스킬 선택
    STATE_TARGET = "target"
    STATE_ENEMY  = "enemy"
    STATE_ANIM   = "anim"
    STATE_ROLL   = "roll"
    STATE_OVER   = "over"
    STATE_EXEC_INTRO = "exec_intro"  # 실행 직전: 레터박스만 올라오고 대기(로딩)
    STATE_TURN_END   = "turn_end"    # 턴 종료: 페이드아웃 → n턴 종료 → 페이드인

    # 연출 타이밍(ms)
    EXEC_INTRO_HOLD  = 350   # 레터박스 올라온 뒤 대기 시간
    TURN_END_FADE    = 250   # 페이드 인/아웃 각각 시간
    TURN_END_HOLD    = 500   # "n턴 종료" 표시 유지 시간
    TAB_NAMES = ["개요", "스킬", "패시브"]
    def __init__(self, screen, W, H, fonts, enemies=None, allies=None,
                 enemy_formation="솔캐리_전방", ally_formation="트리오", gap=0.12,
                 waves=None):
        self.screen  = screen
        self.W, self.H = W, H
        self.fonts   = fonts

        self.enemy_max_w = int(W * 0.55)
        self.enemy_max_h = int(H * 0.55)
        self.ally_max_w  = int(W * 0.5)
        self.ally_max_h  = int(H * 0.5)

        # ── 웨이브 구성 ────────────────────────────────────────────
        # waves 가 주어지면 그것을, 아니면 단일 enemies 를 1웨이브로 변환
        if waves:
            self.waves = waves
        else:
            self.waves = [{"enemies": enemies or [], "enemy_formation": enemy_formation}]
        self.wave_idx = 0

        # ── 아군 (전 웨이브 공통, 인원수로 배치 자동 결정) ──────────
        allies = allies or ["주인공"]
        self.allies = [Combatant(_ally_def(k), W, H, self.ally_max_w, self.ally_max_h) for k in allies]
        self.ally_formation = ally_formation_for(len(self.allies))
        self.gap            = gap

        # ── 첫 웨이브 적 생성 ──────────────────────────────────────
        self._spawn_wave(0)

        self.ui_y    = int(H * (1.0 - self.UI_H_RATIO))

        self.state           = self.STATE_MENU
        self.menu_selected   = 0
        self.target_selected = 0
        self.skill_selected  = 0
        self.defense_selected = 0
        self.pending_is_defense = False
        self.UI_ITEMS        = ["스킬", "수비", "아이템"]
        self.pending_skill   = None
        self.current_actor   = None
        self._exec_pending   = None

        # 전투 로직
        self.logic = BattleLogic(self.enemies, self.allies)
        self.logic.on_enemy_wiped = self._on_enemy_wiped   # 웨이브 전환 콜백
        self.logic.start_turn()
        self.enemy_timer = 0.0
        self._sync_turn()

        self.inspect_enemy   = None

    def _on_enemy_wiped(self):
        """현재 웨이브 적 전멸 시 호출. 다음 웨이브가 있으면 전환하고 True."""
        if self.wave_idx + 1 < len(self.waves):
            self.wave_idx += 1
            self._spawn_wave(self.wave_idx)
            # 로직의 적 목록 교체 + 새 턴 시작
            self.logic.enemies = self.enemies
            self.logic.start_turn()
            self._sync_turn()
            return True
        return False

    def _spawn_wave(self, idx):
        """idx 웨이브의 적을 생성하고 배경/바닥/BGM 을 로드(첫 웨이브에서만)."""
        W, H = self.W, self.H
        wave = self.waves[idx]
        enemies = wave["enemies"]
        self.enemy_formation = wave.get("enemy_formation", "솔로")
        self.enemies = [Combatant(ENEMY_DEFS[k], W, H, self.enemy_max_w, self.enemy_max_h)
                        for k in enemies]

        # 배경/바닥/BGM 은 첫 웨이브 진입 시 1회만 세팅 (웨이브마다 바꾸려면 wave에 키 추가)
        if idx == 0:
            WLD_W = int(W * 2.5)
            self.background = None
            for nm in enemies:
                bg_path = ENEMY_DEFS[nm].get("background")
                if bg_path and os.path.exists(bg_path):
                    try:
                        bg_img = pygame.image.load(bg_path).convert()
                        ow, oh = bg_img.get_size()
                        sc = WLD_W / ow
                        self.background = pygame.transform.smoothscale(bg_img, (WLD_W, int(oh*sc)))
                        break
                    except Exception as e:
                        print(f"배경 로드 실패: {bg_path} - {e}")
            self.floor = None
            for nm in enemies:
                fp = ENEMY_DEFS[nm].get("floor")
                if fp and os.path.exists(fp):
                    try:
                        fimg = pygame.image.load(fp).convert_alpha()
                        ow, oh = fimg.get_size()
                        sc = WLD_W / ow
                        self.floor = pygame.transform.smoothscale(fimg, (WLD_W, int(oh*sc)))
                        break
                    except Exception as e:
                        print(f"바닥 로드 실패: {fp} - {e}")
            for nm in enemies:
                bgm = ENEMY_DEFS[nm].get("bgm")
                if bgm and os.path.exists(bgm):
                    try:
                        pygame.mixer.music.load(bgm)
                        pygame.mixer.music.set_volume(settings["bgm_vol"] / 100.0)
                        pygame.mixer.music.play(-1)
                        break
                    except Exception as e:
                        print(f"BGM 로드 실패: {bgm} - {e}")
        # 캐시 무효화 (다음 draw에서 재생성)
        self._cache_zoom = None
        self._preload_done = False
        self._enemy_cache = []
        self.inspect_ally    = None
        self.inspect_tab     = 0
        self.inspect_sprite  = None
        self.inspect_scroll  = 0
        self._inspect_dragging = False
        self._drag_last_y = 0
        self._underline_rects = []

        # ── 카메라 ────────────────────────────────────────────────
        self.cam_x    = 0.0
        self.cam_y    = 0.0
        self.zoom     = self.ZOOM_MIN   # 전투 시작 시 최대 축소 상태
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
        self._buff_icon_cache = {}  # 버프 아이콘 캐시
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
        self._exec_intro_timer = 0.0   # 실행 인트로 대기 타이머
        self._turn_end_timer   = 0.0   # 턴 종료 연출 타이머
        self._turn_end_phase   = None  # "out" / "hold" / "in"
        self._turn_end_label   = ""    # 표시할 "n턴 종료" 문구
        self._was_executing    = False # 실행 페이즈 진행 중이었는지(턴 종료 감지용)
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
    def _inspect_content_geom(self):
        """열람창 content 영역의 (content_y, content_h) 반환"""
        W, H = self.W, self.H
        pad   = int(W * 0.02)
        bar_y = pad + int(H * 0.22)
        bar_h = int(H * 0.03)
        mp_y  = bar_y + bar_h + int(H * 0.012)
        tab_y = mp_y + bar_h + int(H * 0.03)
        tab_h = int(H * 0.06)
        content_y = tab_y + tab_h
        content_h = H - pad * 2 - content_y
        return content_y, content_h

    def _inspect_max_scroll(self):
        """현재 열람 탭 내용의 최대 스크롤량"""
        H = self.H
        c = self._inspect_target()
        if c is None:
            return 0
        content_y, content_h = self._inspect_content_geom()
        if self.inspect_tab == 2 and c.passives:
            gap_name  = int(H * 0.035)
            gap_desc  = int(H * 0.03)
            gap_block = int(H * 0.015)
            total = int(H * 0.02)
            for passive in c.passives:
                total += gap_name + len(passive["desc"]) * gap_desc + gap_block * 2
            return max(0, total - content_h)
        if self.inspect_tab == 1 and (c.skills or getattr(c, "defense_skills", [])):
            icon_size = int(H * 0.08)
            gap_line  = int(H * 0.03)
            gap_block = int(H * 0.015)
            total = int(H * 0.02)
            for skill in c.skills:
                block_h = max(icon_size, int(icon_size * 0.2) + int(H * 0.033) + int(H * 0.035) + len(skill["desc"]) * gap_line)
                total += block_h + gap_block * 2
            defense = getattr(c, "defense_skills", [])
            if defense:
                total += int(H * 0.05)
                for skill in defense:
                    desc = skill.get("desc", [])
                    block_h = max(icon_size, int(icon_size * 0.2) + int(H * 0.033) + int(H * 0.035) + len(desc) * gap_line)
                    total += block_h + gap_block * 2
            return max(0, total - content_h)
        if self.inspect_tab == 0 and c.overview:
            line_h = int(H * 0.04)
            total  = int(H * 0.025)
            for line in c.overview:
                total += line_h // 2 if line == "" else line_h
            return max(0, total - content_h)
        return 0

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
            elif (event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5)) or event.type == pygame.MOUSEWHEEL:
                if event.type == pygame.MOUSEWHEEL:
                    scroll_dir = -1 if event.y > 0 else 1
                else:
                    scroll_dir = -1 if event.button == 4 else 1
                max_scroll = self._inspect_max_scroll()
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
                else:
                    # content 영역 안에서 좌클릭 홀드 → 드래그 스크롤 시작
                    content_y = tab_y + tab_h
                    content_bottom = H - pad
                    if (content_y <= my <= content_bottom
                            and info_x <= mx <= info_x + info_w):
                        self._inspect_dragging = True
                        self._drag_last_y = my
            elif event.type == pygame.MOUSEMOTION and getattr(self, "_inspect_dragging", False):
                # 드래그 중: 마우스가 위로 가면 내용도 위로(스크롤 증가)
                _, my = event.pos
                dy = self._drag_last_y - my
                self._drag_last_y = my
                max_scroll = self._inspect_max_scroll()
                self.inspect_scroll = max(0, min(max_scroll, self.inspect_scroll + dy))
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._inspect_dragging = False
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
                        actor = self.logic.planning_actor()
                        if actor and getattr(actor, "defense_skills", []):
                            self.state = self.STATE_DEFENSE
                            self.defense_selected = 0
            elif self.state == self.STATE_DEFENSE:
                actor = self.logic.planning_actor()
                dfs = getattr(actor, "defense_skills", []) if actor else []
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.defense_selected = (self.defense_selected - 1) % max(1, len(dfs))
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.defense_selected = (self.defense_selected + 1) % max(1, len(dfs))
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if dfs:
                        self._select_defense(dfs[self.defense_selected])
                elif event.key == pygame.K_ESCAPE:
                    self.state = self.STATE_MENU
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
                    self.state = self.STATE_DEFENSE if self.pending_is_defense else self.STATE_SKILL
                    self.pending_skill = None
                    self.pending_is_defense = False

        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            # 카메라 드래그
            if self.dragging:
                dx = (mx - self.drag_start_mouse[0]) / self.zoom
                dy = (my - self.drag_start_mouse[1]) / self.zoom
                self.cam_x = self.drag_start_cam[0] - dx
                self.cam_y = self.drag_start_cam[1] - dy
                self._clamp_cam()
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
            elif self.state == self.STATE_DEFENSE:
                actor = self.logic.planning_actor()
                dfs = getattr(actor, "defense_skills", []) if actor else []
                tr = self._target_rect()
                if tr.collidepoint(mx, my) and dfs:
                    slot_h = tr.height // max(5, len(dfs))
                    for i in range(len(dfs)):
                        slot_rect = pygame.Rect(tr.left, tr.top + i * slot_h, tr.width, slot_h)
                        if slot_rect.collidepoint(mx, my):
                            self.defense_selected = i
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
            on_ui = ui.collidepoint(mx, my) or (self.state in (self.STATE_TARGET, self.STATE_SKILL, self.STATE_DEFENSE) and tr.collidepoint(mx, my))
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
                            actor = self.logic.planning_actor()
                            if actor and getattr(actor, "defense_skills", []):
                                self.state = self.STATE_DEFENSE
                                self.defense_selected = 0
            elif self.state == self.STATE_DEFENSE and tr.collidepoint(mx, my):
                actor = self.logic.planning_actor()
                dfs = getattr(actor, "defense_skills", []) if actor else []
                if dfs:
                    slot_h = tr.height // max(5, len(dfs))
                    for i in range(len(dfs)):
                        slot_rect = pygame.Rect(tr.left, tr.top + i * slot_h, tr.width, slot_h)
                        if slot_rect.collidepoint(mx, my):
                            self.defense_selected = i
                            self._select_defense(dfs[i])
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
                self.state = self.STATE_DEFENSE if self.pending_is_defense else self.STATE_SKILL
                self.pending_skill = None
                self.pending_is_defense = False
            elif self.state == self.STATE_SKILL:
                self.state = self.STATE_MENU
            elif self.state == self.STATE_DEFENSE:
                self.state = self.STATE_MENU
            elif self.state == self.STATE_MENU and self.logic.planned:
                # 계획 진행 중 → 전체 리셋
                self.logic.reset_plan()
                self._sync_turn()

        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self._zoom_at_mouse(self.ZOOM_STEP * event.y)
            elif event.y < 0:
                # 축소: 화면 중심 기준 + 배경 밖 안 보이게 clamp
                self.zoom = max(self.ZOOM_MIN, self.zoom + self.ZOOM_STEP * event.y)
                self._clamp_cam()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
            self._zoom_at_mouse(self.ZOOM_STEP)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
            self.zoom = max(self.ZOOM_MIN, self.zoom - self.ZOOM_STEP)
            self._clamp_cam()

        return None

    def _clamp_cam(self):
        """카메라가 배경 밖을 너무 보여주지 않도록 제한.
        확대될수록(zoom>1) 화면에 보이는 월드가 좁아지므로 더 많이 움직여도 된다."""
        z = max(0.0001, self.zoom)
        scale = 1.0 / z   # 화면이 덮는 월드 비율
        extra_w = (self.W * 0.5) * max(0.0, 1.0 - scale)
        extra_h = (self.H * 0.5) * max(0.0, 1.0 - scale)
        mx   = self.W * self.CAM_MOVE_RATIO + extra_w
        mup  = self.H * 0.25 + extra_h
        mdown = self.H * 0.05 + extra_h
        self.cam_x = max(-mx, min(mx, self.cam_x))
        self.cam_y = max(-mup, min(mdown, self.cam_y))

    def _zoom_at_mouse(self, delta):
        """마우스 커서 위치를 중심으로 확대 (커서 아래 월드 좌표 고정)."""
        W, H = self.W, self.H
        mx, my = pygame.mouse.get_pos()
        old_zoom = self.zoom
        new_zoom = max(self.ZOOM_MIN, min(self.ZOOM_MAX, old_zoom + delta))
        if new_zoom == old_zoom:
            return
        # 커서 아래 월드 좌표가 줌 전후 동일하도록 카메라 보정
        self.cam_x += (mx - W / 2) * (1.0 / old_zoom - 1.0 / new_zoom)
        self.cam_y += (my - H / 2) * (1.0 / old_zoom - 1.0 / new_zoom)
        self.zoom = new_zoom
        self._clamp_cam()
    def _sync_turn(self):
        """계획/실행 단계에 맞춰 상태 전환"""
        if self.logic.battle_over:
            self.state = self.STATE_OVER
            return
        if not self.logic.is_planning_done():
            # 실행 중이었다가 계획 단계로 돌아왔다면 = 한 턴이 끝난 것
            if getattr(self, "_was_executing", False):
                self._was_executing = False
                self._begin_turn_end(self.logic.turn_count - 1)
                return
            # 계획 단계: 현재 계획 받을 아군에게 메뉴 표시
            actor = self.logic.planning_actor()
            if actor is None:
                return
            self.state = self.STATE_MENU
            self.menu_selected = 0
            self.current_actor = actor
        else:
            self._was_executing = True
            # 실행 단계: 현재 행동자의 예약 행동 실행
            self._exec_next()

    def _begin_turn_end(self, turn_no):
        """턴 종료 연출 시작: 페이드아웃 → 'n턴 종료' → 페이드인"""
        self.state = self.STATE_TURN_END
        self._turn_end_phase = "out"
        self._turn_end_timer = 0.0
        self._turn_end_label = f"{turn_no}턴 종료"
        self.zoom = self.ZOOM_MIN   # 턴 종료 시 최대 축소
        self._lb_ratio = 0.0        # 레터박스 즉시 제거 (올라오지 않게)
        self.roll = None
        self.anim = None
        self._clear_total()
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
        if kind == "defense":
            # 수비 스킬: 일반 스킬처럼 룰렛 + 지원 모션
            skill = plan.get("skill")
            primary = plan.get("primary")
            if skill is None:
                self.logic.advance(); self._sync_turn(); return
            targets = [primary] if primary is not None else [actor]
            self._start_roll(actor, skill, primary, targets)
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
        if self.pending_is_defense and skill.get("def_kind") == "assist":
            return self._defense_target_list()
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
        if self.pending_is_defense:
            self.logic.set_plan(actor, "defense", skill=skill, primary=primary)
        else:
            self.logic.set_plan(actor, "skill", skill=skill, primary=primary)
        self.pending_skill = None
        self.pending_is_defense = False
        self._after_plan_step()
    def _select_defense(self, skill):
        """수비 스킬 선택. 원호는 대상(아군) 지정, 그 외는 자신 대상 즉시 계획."""
        actor = self.logic.planning_actor()
        if actor is None:
            return
        self.pending_skill = skill
        self.pending_is_defense = True
        if skill.get("def_kind") == "assist":
            # 자신 제외 아군 중 대상 선택
            pool = self._defense_target_list()
            if not pool:
                # 지정 가능한 아군 없음 → 사용 불가, 목록으로 복귀
                self.pending_skill = None
                self.pending_is_defense = False
                return
            self.state = self.STATE_TARGET
            self.target_selected = 0
        else:
            # 방어/회피: 자신 대상
            self.logic.set_plan(actor, "defense", skill=skill, primary=actor)
            self.pending_skill = None
            self.pending_is_defense = False
            self._after_plan_step()

    def _defense_target_list(self):
        """원호 대상 후보: 자신 제외 살아있는 아군"""
        actor = self.logic.planning_actor() or self.logic.current_actor()
        if actor is None:
            return []
        return [c for c in self.logic.allies_of(actor) if c.hp > 0 and c is not actor]

    def _do_defend(self):
        actor = self.logic.planning_actor()
        if actor:
            self.logic.set_plan(actor, "defend")
            self._after_plan_step()
    def _after_plan_step(self):
        """계획 한 단계 끝난 뒤: 다음 아군 메뉴 or 실행 시작"""
        if self.logic.is_planning_done():
            # 전원 계획 완료 → 실행 인트로(레터박스만 올라오고 대기)
            self.state = self.STATE_EXEC_INTRO
            self._exec_intro_timer = 0.0
            self.zoom = self.ZOOM_MIN   # 실행 시작은 최대 축소
        else:
            # 다음 아군 계획
            self.state = self.STATE_MENU
            self.menu_selected = 0
            self.current_actor = self.logic.planning_actor()
    def update(self, dt):
        # 레터박스: 실행 페이즈/인트로 동안만 펼침(1). 턴종료에서는 접는다.
        if self.state == self.STATE_TURN_END:
            # 턴 종료 연출 동안 레터박스는 즉시 사라진 상태로 유지
            self._lb_ratio = 0.0
            target_lb = 0.0
        else:
            in_exec = (self.logic.is_planning_done() and not self.logic.battle_over) \
                      or self.state == self.STATE_EXEC_INTRO
            target_lb = 1.0 if in_exec else 0.0
            step = dt / self.LETTERBOX_SLIDE
            if self._lb_ratio < target_lb:
                self._lb_ratio = min(target_lb, self._lb_ratio + step)
            elif self._lb_ratio > target_lb:
                self._lb_ratio = max(target_lb, self._lb_ratio - step)

        # ── 실행 인트로: 레터박스 다 올라오고 대기 후 첫 행동 시작 ──
        if self.state == self.STATE_EXEC_INTRO:
            self._exec_intro_timer += dt
            # 레터박스가 충분히 올라오고 대기시간 경과하면 실행 시작
            if self._lb_ratio >= 1.0 and self._exec_intro_timer >= self.EXEC_INTRO_HOLD:
                self._was_executing = True
                self._exec_next()
            return

        # ── 턴 종료 연출: 페이드아웃 → n턴 종료 → 페이드인 ──
        if self.state == self.STATE_TURN_END:
            self._turn_end_timer += dt
            if self._turn_end_phase == "out":
                if self._turn_end_timer >= self.TURN_END_FADE:
                    self._turn_end_phase = "hold"
                    self._turn_end_timer = 0.0
            elif self._turn_end_phase == "hold":
                if self._turn_end_timer >= self.TURN_END_HOLD:
                    self._turn_end_phase = "in"
                    self._turn_end_timer = 0.0
            elif self._turn_end_phase == "in":
                if self._turn_end_timer >= self.TURN_END_FADE:
                    # 연출 종료 → 다음 턴 계획 화면으로
                    self._turn_end_phase = None
                    actor = self.logic.planning_actor()
                    if actor is not None:
                        self.state = self.STATE_MENU
                        self.menu_selected = 0
                        self.current_actor = actor
                    else:
                        self._sync_turn()
            return

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