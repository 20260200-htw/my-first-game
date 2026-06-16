import pygame
import sys
import os

# PyInstaller exe 실행 시 작업 디렉토리를 assets가 있는 곳으로 설정
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

import utils
from utils import *
from combatant import Combatant
from data.characters_data import ENEMY_DEFS, ALLY_DEFS
from data.archive_data import GLOSSARY, COMPENDIUM
from screens.menu_screens import (
    TitleScreen, SettingsScreen, GalleryScreen,
    CompendiumMenuScreen, CompendiumDetailScreen, GlossaryDetailScreen,
    PlaceholderScreen, QuitDialog, GameStartScreen, ResetConfirmDialog,
    PauseMenu, GiveUpConfirmDialog
)
from screens.battle_screens import BattleScreen
from screens.menu_screens import BattleSelectScreen
from screens.story_screens import ActSelectScreen, ActMenuScreen, ChapterSelectScreen, StageSelectScreen
from screens.growth_screen import GrowthScreen
from screens.story_dialogue import DialogueScreen
from screens.loading_screen import LoadingScreen
from data.story_data import STORY
import save_data

# ── 로그라이크 ────────────────────────────────────────────────────
from run_state import RUN
from data import run_data
from data import encounter_data
import roguelike_flow as rl
from screens.region_select_screen import RegionSelectScreen
from screens.map_screen import MapScreen
from screens.reward_screen import RewardScreen
from screens.shop_screen import ShopScreen
from screens.event_screen import EventScreen
from screens.run_result_screen import RunResultScreen
from screens.boss_mode_screen import BossSelectScreen, CreditsScreen
from screens.fade_transition import FadeTransition
from screens.skill_config_screen import SkillConfigScreen
from screens.item_view_screen import ItemViewScreen


def load_fonts(H):
    def _f(filename, size):
        path = os.path.join("assets", "fonts", filename)
        try:
            return pygame.font.Font(path, size)
        except Exception:
            return pygame.font.SysFont("malgungothic,nanumgothic,sans-serif", size)
    return {
        "title":      _f("Paperlogy-9Black.ttf",    int(H * 0.08)),
        "menu":       _f("Paperlogy-9Black.ttf",    int(H * 0.038)),
        "hint":       _f("Paperlogy-6SemiBold.ttf", int(H * 0.022)),
        "hint_bold":  _f("Paperlogy-7Bold.ttf",     int(H * 0.022)),
        "small_bold": _f("Paperlogy-6SemiBold.ttf", int(H * 0.016)),
        "small":      _f("Paperlogy-6SemiBold.ttf", int(H * 0.016)),
    }


def _finish_node(screen, W, H, fonts):
    """노드(전투 후 보상/이벤트/상점/보상노드) 완료 후 다음 화면 결정.
    분기맵: 보스/마왕을 깼으면 구간 종료, 아니면 맵으로 돌아가 다음 노드 선택.
    반환: (current, map_sc, region_sc)
    """
    RUN.advance_node()  # 보스/마왕이면 cleared_boss 갱신
    if RUN.is_segment_done():
        return _after_segment(screen, W, H, fonts)
    return ("map", MapScreen(screen, W, H, fonts), None)


def _after_segment(screen, W, H, fonts):
    """구간 종료 후: 다음 구간 지역 선택. 5구간(마지막) 보스 클리어 시 회차 완료.
    반환: (current, map_sc, region_sc)
    """
    if RUN.segment >= run_data.FINAL_SEGMENT:
        # 5구간(마지막 지역) 보스 클리어 = 일반 모드 완료 → 결과 화면 (전투 쪽에서 처리됨). 안전망.
        return ("map", MapScreen(screen, W, H, fonts), None)
    # 다음 구간 지역 선택 (아직 방문 안 한 지역 중)
    RUN.last_region = RUN.region
    return ("region_select", None, RegionSelectScreen(screen, W, H, fonts))


def main():
    pygame.init()
    pygame.display.set_caption("뻔하디 뻔한 JRPG")

    info = pygame.display.Info()
    utils.MON_W, utils.MON_H = info.current_w, info.current_h

    screen, W, H = apply_resolution()
    fonts  = load_fonts(H)
    clock  = pygame.time.Clock()

    save_data.load()   # 저장 파일 로드

    title        = TitleScreen(screen, W, H, fonts)
    current      = "title"
    overlay      = None
    quit_dlg     = None
    pause_menu   = None   # 게임 중 ESC 일시정지 메뉴
    pause_bg     = None   # 일시정지 진입 시 캡처한 정지 배경 (깜빡임 방지)
    giveup_dlg   = None   # 회차 포기 확인
    menu_return  = None   # 설정/아카이브를 게임 중 열었을 때 복귀할 화면 ("map"/"region_select")
    settings_back = None  # 설정 팝업을 닫은 뒤 복귀할 오버레이 ("pause") / None(타이틀)
    placeholder  = None
    story_sc     = None
    act_menu_sc  = None   # 막 내부 메뉴
    growth_sc    = None   # 성장 화면
    skill_sc     = None   # 스킬 배치 화면 (성장)
    item_sc      = None   # 아이템 화면 (성장)
    loading_sc   = None
    dialogue_sc  = None
    story_ctx    = None   # 진행 중 스테이지 정보 {act,chap,stage}
    after_load   = None   # 로딩 끝난 뒤 갈 단계: 'dialogue' / 'battle' / 'clear'
    settings_sc  = None
    gallery_sc   = None
    battle_sc        = None
    gamestart_sc     = None
    battle_select_sc = None
    boss_select_sc = None
    credits_sc = None
    fade_sc = None      # FadeTransition (게임시작→구역선택, 구역선택→맵 전환용)
    fade_bg_draw = None # fade 중 검은 베일 뒤에 그릴 화면(콜백)
    fade_display_key = None  # fade 중 _draw_current_screen 이 표시할 화면 키
    # ── 로그라이크 화면 핸들 ──────────────────────────────────────
    region_sc   = None
    map_sc      = None
    reward_sc   = None
    shop_sc     = None
    event_sc    = None
    result_sc   = None
    rl_growth_sc = None       # 정비(성장) 화면
    rl_skill_sc  = None       # 스킬 배치 화면
    rl_item_sc   = None       # 아이템 화면 (정비)
    rl_dialogue_sc = None     # 로그라이크 지점 다이얼로그
    rl_after_dialogue = None  # 다이얼로그 종료 후 동작: ("battle", enemies)/("boss", enemies)/("maw", enemies)/("event", 사건def)/"node"
    rl_after_battle = None    # 전투 후 처리: "reward_skill"/"reward_item"/"boss"/"maw"/None
    rl_boss_drop = None       # 보스 전리품 아이템 키
    rl_event_battle = None    # 사건에서 파생된 전투 spec ({"enemies","drop","reward","gold"})
    reset_dlg    = None   # 데이터 초기화 확인 다이얼로그

    comp_stack   = []
    gloss_stack  = []

    def push_comp(screen_obj):
        comp_stack.append(screen_obj)

    def pop_comp():
        if comp_stack:
            comp_stack.pop()

    def comp_top():
        return comp_stack[-1] if comp_stack else None

    def push_gloss(screen_obj):
        gloss_stack.append(screen_obj)

    def pop_gloss():
        if gloss_stack:
            gloss_stack.pop()

    def gloss_top():
        return gloss_stack[-1] if gloss_stack else None

    def _draw_current_screen():
        """fade 전환 중 '뒤 화면'을 그리기 위한 디스패처.
        current 가 'fade'인 동안은 fade_display_key 가 실제 표시할 화면을 가리킨다."""
        key = fade_display_key if current == "fade" else current
        if key == "battle" and battle_sc:
            battle_sc.draw()
        elif key == "map" and map_sc:
            map_sc.draw()
        elif key == "region_select" and region_sc:
            region_sc.draw()
        elif key == "reward" and reward_sc:
            reward_sc.draw()
        elif key == "event" and event_sc:
            event_sc.draw()
        elif key == "run_result" and result_sc:
            result_sc.draw()
        elif key == "boss_select" and boss_select_sc:
            boss_select_sc.draw()
        elif key == "rl_dialogue" and rl_dialogue_sc:
            rl_dialogue_sc.draw()
        elif key == "placeholder" and placeholder:
            placeholder.draw()
        elif key == "story" and story_sc:
            story_sc.draw()
        elif key == "dialogue" and dialogue_sc:
            dialogue_sc.draw()
        elif key == "loading" and loading_sc:
            loading_sc.draw()
        elif key == "title":
            title.draw()
        else:
            screen.fill((0, 0, 0))

    def start_battle_fade(build_battle_fn):
        """전투 진입 페이드: 현재 화면을 검게 덮음(1초) → build_battle_fn()으로
        battle_sc 생성 + current='battle' → 페이드아웃(1초, BATTLE START로 이어짐)."""
        nonlocal fade_sc, fade_bg_draw, fade_display_key, current
        fade_display_key = current   # 덮이기 전: 현재(맵 등) 화면을 표시
        def _cover():
            nonlocal current, fade_display_key
            build_battle_fn()
            current = "battle"
            fade_display_key = "battle"   # 덮인 후: 전투 화면을 표시
        fade_sc = FadeTransition(screen, W, H, on_covered=_cover, fade_in=1000, fade_out=1000)
        fade_bg_draw = _draw_current_screen
        current = "fade"

    def end_battle_fade(build_next_fn):
        """전투 종료 페이드: 전투 화면을 검게 덮음(1초) → build_next_fn()으로
        다음 화면(current/관련 _sc) 준비 → 페이드아웃(1초)."""
        nonlocal fade_sc, fade_bg_draw, fade_display_key, current
        fade_display_key = "battle"   # 덮이기 전: 전투(STAGE CLEAR 등) 화면을 표시
        def _cover():
            nonlocal fade_display_key
            build_next_fn()
            fade_display_key = current    # 덮인 후: build_next_fn 이 설정한 새 current 화면을 표시
        fade_sc = FadeTransition(screen, W, H, on_covered=_cover, fade_in=1000, fade_out=1000)
        fade_bg_draw = _draw_current_screen
        current = "fade"

    while True:
        dt = clock.tick(FRAMERATES[settings["fps_index"]])

        # 화면에 맞는 배경음악 자동 전환 (매핑에 없는 화면은 현재 BGM 유지)
        utils.update_bgm(current, region=RUN.region)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if overlay == "reset":
                r = reset_dlg.handle_event(event)
                if r == "done":
                    overlay = None
                    # 저장 초기화 후 타이틀로 (스토리 화면 상태도 리셋)
                    story_sc = None
                elif r == "cancel":
                    overlay = None
                # reset 오버레이 중에는 아래 이벤트 처리 건너뜀
                continue

            if overlay == "quit":
                r = quit_dlg.handle_event(event)
                if r == "yes":  pygame.quit(); sys.exit()
                elif r == "no": overlay = None
                continue

            if overlay == "pause":
                r = pause_menu.handle_event(event)
                if r == "settings":
                    settings_sc = SettingsScreen(screen, W, H, fonts)
                    settings_back = "pause"        # 닫으면 일시정지 메뉴로 복귀
                    overlay = "settings"
                elif r == "giveup":
                    giveup_dlg = GiveUpConfirmDialog(screen, W, H, fonts)
                    overlay = "giveup"
                elif r == "close":
                    overlay = None                 # 메뉴 닫고 게임 복귀
                continue

            if overlay == "settings":
                r = settings_sc.handle_event(event)
                if r == "back":
                    screen, W, H = apply_resolution()  # 해상도 변경 반영
                    fonts = load_fonts(H)
                    if settings_back == "pause":
                        # 게임 중: 화면 재생성 후 일시정지 메뉴로 복귀
                        if current == "map":
                            map_sc = MapScreen(screen, W, H, fonts)
                            map_sc.draw()
                        elif current == "region_select":
                            region_sc = RegionSelectScreen(screen, W, H, fonts)
                            region_sc.draw()
                        pause_bg = screen.copy()       # 해상도 바뀌었을 수 있으니 배경 재캡처
                        pause_menu = PauseMenu(screen, W, H, fonts)
                        overlay = "pause"
                    else:
                        title = TitleScreen(screen, W, H, fonts)
                        current = "title"
                        overlay = None
                    settings_back = None
                continue

            if overlay == "giveup":
                r = giveup_dlg.handle_event(event)
                if r == "yes":
                    RUN.end_run()                  # 회차 포기 → 휘발 상태 해제
                    overlay = None
                    title = TitleScreen(screen, W, H, fonts)
                    current = "title"
                elif r == "no":
                    overlay = "pause"              # 포기 취소 → 일시정지 메뉴로
                continue

            if overlay == "shop":
                r = shop_sc.handle_event(event)
                if r == "done":
                    overlay = None
                    # 상점 닫음 → 다음 노드로 진행
                    current, map_sc, region_sc = _finish_node(screen, W, H, fonts)
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

            if current == "glossary" and gloss_stack:
                top = gloss_top()
                r   = top.handle_event(event)

                if isinstance(top, GlossaryDetailScreen):
                    if r == "back":
                        pop_gloss()
                        if not gloss_stack:
                            current = "gallery"

                elif isinstance(top, CompendiumMenuScreen):
                    if r is None:
                        pass
                    elif r[0] == "back":
                        pop_gloss()
                        if not gloss_stack:
                            current = "gallery"
                    elif r[0] == "select":
                        val  = r[1]
                        name = top.items[top.selected][0]
                        if isinstance(val, dict) and "image" in val:
                            push_gloss(GlossaryDetailScreen(screen, W, H, fonts, val))
                        elif isinstance(val, dict):
                            items = [(k, v) for k, v in val.items()]
                            push_gloss(CompendiumMenuScreen(screen, W, H, fonts, name, items))
                        elif val is None:
                            pass
                continue

            if current == "title":
                a = title.handle_event(event)
                if a == "quit":
                    quit_dlg = QuitDialog(screen, W, H, fonts)
                    overlay  = "quit"
                elif a == "settings":
                    pause_bg = screen.copy()       # 정지 배경 캡처
                    settings_sc = SettingsScreen(screen, W, H, fonts)
                    settings_back = None       # 닫으면 타이틀로 복귀
                    overlay = "settings"
                elif a == "start":
                    # 1) 검은 화면이 덮임(1초) → 2) 뒤에서 구역선택(중앙만) 준비 → 3) 페이드아웃(1초)
                    region_sc = None
                    def _cover_to_region_select():
                        nonlocal region_sc, current
                        region_sc = RegionSelectScreen(screen, W, H, fonts, only_region=run_data.FIRST_REGION)
                        current = "region_select"
                    fade_sc = FadeTransition(screen, W, H, on_covered=_cover_to_region_select,
                                             fade_in=1000, fade_out=1000)
                    # 덮이기 전엔 타이틀, 덮인 후엔 구역선택이 보임 (region_sc 생성 시점에 자동 전환)
                    fade_bg_draw = lambda: (region_sc.draw() if region_sc is not None else title.draw())
                    current = "fade"
                elif a == "boss_mode":
                    boss_select_sc = BossSelectScreen(screen, W, H, fonts)
                    current = "boss_select"
                elif a == "reset":
                    reset_dlg = ResetConfirmDialog(screen, W, H, fonts)
                    overlay = "reset"
                elif a == "battle_test":
                    battle_select_sc = BattleSelectScreen(screen, W, H, fonts)
                    current = "battle_select"

            elif current == "battle_select":
                r = battle_select_sc.handle_event(event)
                if r == "back":
                    current = "title"
                elif isinstance(r, tuple) and r[0] == "start":
                    preset = r[1]
                    def _build(preset=preset):
                        nonlocal battle_sc
                        battle_sc = BattleScreen(screen, W, H, fonts,
                                                 enemies=preset["enemies"],
                                                 allies=preset["allies"],
                                                 enemy_formation=preset["enemy_formation"],
                                                 ally_formation=preset["ally_formation"],
                                                 gap=preset.get("gap", 0.12))
                    start_battle_fade(_build)

            elif current == "boss_select":
                r = boss_select_sc.handle_event(event)
                if r == "back":
                    current = "title"
                elif isinstance(r, tuple) and r[0] == "boss_start":
                    _, tier, region = r
                    bdef = (run_data.challenge_boss(region) if tier == "challenge"
                            else run_data.extreme_boss(region) if tier == "extreme"
                            else run_data.FINAL_BOSS.get(region))
                    if bdef is not None:
                        def _build(tier=tier, region=region, bdef=bdef):
                            nonlocal battle_sc
                            RUN.start_boss_battle(tier, region)
                            battle_sc = rl.make_battle(screen, W, H, fonts, list(bdef["enemies"]))
                            battle_sc.set_reward_preview(levels=0, gold=0, extra="보스 격파")
                        start_battle_fade(_build)

            elif current == "credits":
                r = credits_sc.handle_event(event)
                if r == "back":
                    title = TitleScreen(screen, W, H, fonts)
                    current = "title"

            elif current == "fade":
                pass  # 페이드 전환 중에는 입력 무시

            elif current == "gamestart":
                r = gamestart_sc.handle_event(event)
                if r == "back":
                    current = "title"
                elif r == "story":
                    story_sc = ActSelectScreen(screen, W, H, fonts)
                    current = "story"

            elif current == "battle":
                r = battle_sc.handle_event(event)
                if r == "back":
                    # ── 로그라이크 전투 종료 ──────────────────────
                    if RUN.active:
                        rl.sync_player_hp_from_battle(battle_sc)
                        won = rl.battle_won(battle_sc)
                        if RUN.boss_mode is not None:
                            # ── 보스 모드(도전/극한/최종): 보스전만 ──────────
                            bm = RUN.boss_mode
                            if won:
                                first = save_data.mark_boss_cleared(bm["tier"], bm["region"])
                                RUN.end_run()
                                if bm["tier"] == "final":
                                    def _next():
                                        nonlocal credits_sc, current
                                        credits_sc = CreditsScreen(screen, W, H, fonts)
                                        current = "credits"
                                else:
                                    def _next():
                                        nonlocal boss_select_sc, current
                                        boss_select_sc = BossSelectScreen(screen, W, H, fonts)
                                        current = "boss_select"
                            else:
                                RUN.end_run()
                                def _next():
                                    nonlocal boss_select_sc, current
                                    boss_select_sc = BossSelectScreen(screen, W, H, fonts)
                                    current = "boss_select"
                            end_battle_fade(_next)
                        elif not won:
                            # 패배 → 결과(실패)
                            rl_event_battle = None
                            def _next():
                                nonlocal result_sc, current
                                result_sc = RunResultScreen(screen, W, H, fonts, success=False)
                                current = "run_result"
                            end_battle_fade(_next)
                        elif rl_event_battle is not None:
                            # ── 사건에서 파생된 전투: 승리 처리 ──
                            spec = rl_event_battle
                            rl_event_battle = None
                            RUN.gain_levels(run_data.LEVEL_REWARD.get(run_data.NODE_BATTLE, 1))
                            RUN.add_gold(spec.get("gold", run_data.GOLD_REWARD.get(run_data.NODE_BATTLE, 0)))
                            drop  = spec.get("drop")
                            rkind = spec.get("reward")      # "skill" / "item" / None
                            if drop or rkind:
                                def _next(drop=drop, rkind=rkind):
                                    nonlocal reward_sc, current
                                    reward_sc = RewardScreen(screen, W, H, fonts,
                                                             kind=(rkind or "item"),
                                                             special_item=drop,
                                                             fixed=(None if rkind else False))
                                    current = "reward"
                            else:
                                def _next():
                                    nonlocal current, map_sc, region_sc
                                    current, map_sc, region_sc = _finish_node(screen, W, H, fonts)
                            end_battle_fade(_next)
                        else:
                            node = RUN.current_node()
                            # ── 전투 승리 보상: 레벨 + 골드만 (아이템/스킬은 상점·사건·보상 노드에서) ──
                            RUN.gain_levels(run_data.LEVEL_REWARD.get(node, 0))
                            RUN.add_gold(run_data.GOLD_REWARD.get(node, 0))
                            if node == run_data.NODE_MAW:
                                def _next():
                                    nonlocal result_sc, current
                                    RUN.advance_node()
                                    result_sc = RunResultScreen(screen, W, H, fonts, success=True)
                                    current = "run_result"
                                end_battle_fade(_next)
                            elif node == run_data.NODE_BOSS:
                                RUN.full_heal()
                                rl_boss_drop = None
                                RUN.advance_node()
                                if RUN.segment >= run_data.FINAL_SEGMENT and RUN.cleared_boss:
                                    # 5구간(마지막 지역) 보스 클리어 = 일반 모드 완료
                                    save_data.mark_normal_cleared()
                                    def _next():
                                        nonlocal result_sc, current
                                        result_sc = RunResultScreen(screen, W, H, fonts, success=True)
                                        current = "run_result"
                                else:
                                    def _next():
                                        nonlocal current, map_sc, region_sc
                                        current, map_sc, region_sc = _finish_node(screen, W, H, fonts)
                                end_battle_fade(_next)
                            else:
                                # 일반/엘리트 전투: 보상 화면 없이 다음 노드로
                                def _next():
                                    nonlocal current, map_sc, region_sc
                                    current, map_sc, region_sc = _finish_node(screen, W, H, fonts)
                                end_battle_fade(_next)
                    elif story_ctx is not None:
                        # 스토리 전투 종료: 승리 시 클리어, 아니면 스테이지 선택으로
                        won = (battle_sc.logic.winner == "ally")
                        _ctx = story_ctx
                        story_ctx = None
                        if won:
                            def _next(_ctx=_ctx):
                                nonlocal placeholder, current
                                _t = STORY[_ctx["act"]]["chapters"][_ctx["chap"]]["stages"][_ctx["stage"]]["title"]
                                save_data.on_stage_clear(_ctx["act"], _ctx["chap"], _ctx["stage"], STORY)
                                placeholder = PlaceholderScreen(screen, W, H, fonts, f"{_t} 클리어!")
                                current = "placeholder"
                        else:
                            def _next(_ctx=_ctx):
                                nonlocal story_sc, current
                                story_sc = StageSelectScreen(screen, W, H, fonts, _ctx["act"], _ctx["chap"])
                                current = "story"
                        end_battle_fade(_next)
                    else:
                        def _next():
                            nonlocal current
                            current = "title"
                        end_battle_fade(_next)

            elif current == "loading":
                pass  # 로딩 중 입력 무시 (전환은 update 에서)

            elif current == "dialogue":
                r = dialogue_sc.handle_event(event)
                if r == "done":
                    stage_data = STORY[story_ctx["act"]]["chapters"][story_ctx["chap"]]["stages"][story_ctx["stage"]]
                    if stage_data.get("battle"):
                        b = stage_data["battle"]
                        def _build(b=b):
                            nonlocal battle_sc
                            battle_sc = BattleScreen(screen, W, H, fonts,
                                                     enemies=b["enemies"], allies=b["allies"],
                                                     enemy_formation=b.get("enemy_formation", "솔로"),
                                                     ally_formation=b.get("ally_formation", "솔로"),
                                                     gap=b.get("gap", 0.3))
                        start_battle_fade(_build)
                    else:
                        _t = stage_data["title"]
                        save_data.on_stage_clear(story_ctx["act"], story_ctx["chap"], story_ctx["stage"], STORY)
                        _ctx = story_ctx; story_ctx = None
                        placeholder = PlaceholderScreen(screen, W, H, fonts, f"{_t} 클리어!")
                        current = "placeholder"

            elif current == "act_menu" and act_menu_sc:
                r = act_menu_sc.handle_event(event)
                if r == "back":
                    story_sc = ActSelectScreen(screen, W, H, fonts)  # 반드시 새로 생성
                    current = "story"
                elif r == "story":
                    story_sc = ChapterSelectScreen(screen, W, H, fonts, act_menu_sc.act_key)
                    current = "story"
                elif r == "explore":
                    placeholder = PlaceholderScreen(screen, W, H, fonts, "탐험")
                    current = "placeholder"
                elif r == "growth":
                    growth_sc = GrowthScreen(screen, W, H, fonts)
                    current = "growth"
                elif r in ("formation", "recruit"):
                    labels = {"formation": "편성", "recruit": "모집"}
                    placeholder = PlaceholderScreen(screen, W, H, fonts, labels[r])
                    current = "placeholder"

            elif current == "growth" and growth_sc:
                r = growth_sc.handle_event(event)
                if r == "back":
                    if act_menu_sc is None:
                        story_sc = ActSelectScreen(screen, W, H, fonts)
                        current = "story"
                    else:
                        current = "act_menu"
                elif r == "skill_config":
                    skill_sc = SkillConfigScreen(screen, W, H, fonts)
                    current = "skill_config"
                elif r == "item_view":
                    item_sc = ItemViewScreen(screen, W, H, fonts)
                    current = "item_view"

            elif current == "skill_config" and skill_sc:
                r = skill_sc.handle_event(event)
                if r == "back":
                    current = "growth"

            elif current == "item_view" and item_sc:
                r = item_sc.handle_event(event)
                if r == "back":
                    current = "growth"

            elif current == "story" and story_sc:
                r = story_sc.handle_event(event)
                if r == "back":
                    # 현재 화면 종류에 따라 상위로
                    if isinstance(story_sc, StageSelectScreen):
                        story_sc = ChapterSelectScreen(screen, W, H, fonts, story_sc.act_key)
                    elif isinstance(story_sc, ChapterSelectScreen):
                        story_sc = None
                        if act_menu_sc is None:
                            story_sc = ActSelectScreen(screen, W, H, fonts)
                            current = "story"
                        else:
                            current = "act_menu"
                    else:
                        story_sc = None
                        current = "gamestart"
                elif isinstance(r, tuple):
                    if r[0] == "act":
                        if r[1] == "0막":
                            # 0막: 메뉴 없이 바로 장 선택
                            story_sc = ChapterSelectScreen(screen, W, H, fonts, r[1])
                        else:
                            act_menu_sc = ActMenuScreen(screen, W, H, fonts, r[1])
                            current = "act_menu"
                    elif r[0] == "chapter":
                        story_sc = StageSelectScreen(screen, W, H, fonts, r[1], r[2])
                    elif r[0] == "stage":
                        # 스테이지 진입: 검은 로딩 → 다이얼로그/전투/클리어
                        story_ctx = {"act": r[1], "chap": r[2], "stage": r[3]}
                        stage_data = STORY[r[1]]["chapters"][r[2]]["stages"][r[3]]
                        after_load = "dialogue" if stage_data.get("dialogue") else (
                                     "battle" if stage_data.get("battle") else "clear")
                        loading_sc = LoadingScreen(screen, W, H, fonts, r[3])
                        current = "loading"

            elif current == "placeholder":
                r = placeholder.handle_event(event)
                if r == "back":
                    current = "title"

            # ── 로그라이크 분기 ───────────────────────────────────
            elif current == "region_select" and region_sc:
                r = region_sc.handle_event(event)
                if r == "back":
                    pause_bg = screen.copy()                      # 정지 배경 캡처
                    pause_menu = PauseMenu(screen, W, H, fonts)   # ESC → 일시정지 메뉴
                    overlay = "pause"
                elif isinstance(r, tuple) and r[0] == "region":
                    if not RUN.active:
                        # 첫 시작(중앙 선택) → 페이드인 → 회차 시작+맵 준비 → 페이드아웃
                        chosen = r[1]
                        map_sc = None
                        def _cover_to_map():
                            nonlocal map_sc, current
                            RUN.start_new_run()
                            RUN.enter_region(chosen)
                            map_sc = MapScreen(screen, W, H, fonts)
                            current = "map"
                        fade_sc = FadeTransition(screen, W, H, on_covered=_cover_to_map,
                                                 fade_in=1000, fade_out=1000)
                        # 덮이기 전엔 구역선택, 덮인 후엔 맵이 보임 (map_sc 생성 시점에 자동 전환)
                        fade_bg_draw = lambda: (map_sc.draw() if map_sc is not None else region_sc.draw())
                        current = "fade"
                    else:
                        # 진행 중인 회차에서 다음 구역 선택 (기존 동작 유지)
                        RUN.enter_region(r[1])
                        map_sc = MapScreen(screen, W, H, fonts)
                        current = "map"

            elif current == "map" and map_sc:
                r = map_sc.handle_event(event)
                if r == "back":
                    pause_bg = screen.copy()                      # 정지 배경 캡처
                    pause_menu = PauseMenu(screen, W, H, fonts)   # ESC → 일시정지 메뉴
                    overlay = "pause"
                elif r == "menu":
                    rl_growth_sc = GrowthScreen(screen, W, H, fonts)
                    current = "rl_growth"
                elif isinstance(r, tuple) and r[0] == "node":
                    node = r[2]
                    if node == run_data.NODE_START:
                        # 시작 지점: 다이얼로그 → 노드 완료
                        cuts = RUN.current_dialogue()
                        rl_dialogue_sc = DialogueScreen(screen, W, H, fonts, cuts or [])
                        rl_after_dialogue = "node"
                        current = "rl_dialogue"
                    elif node == run_data.NODE_MID:
                        # 중간 지점: 스토리 없이 (중간보스 있으면 전투, 없으면 노드 완료)
                        mb = RUN.current_mid_boss()
                        if mb:
                            def _build(mb=mb):
                                nonlocal battle_sc
                                battle_sc = rl.make_battle(screen, W, H, fonts, mb["enemies"])
                                battle_sc.set_reward_preview(
                                    levels=run_data.LEVEL_REWARD.get(run_data.NODE_BATTLE, 0),
                                    gold=run_data.GOLD_REWARD.get(run_data.NODE_MID, 0))
                            start_battle_fade(_build)
                        else:
                            current, map_sc, region_sc = _finish_node(screen, W, H, fonts)
                    elif node in (run_data.NODE_BATTLE, run_data.NODE_ELITE):
                        # 구역×회차 출현 풀에서 랜덤 조합으로 적 편성을 만든다
                        if node == run_data.NODE_ELITE:
                            enemies = encounter_data.elite_group(RUN.region, RUN.cur_visit)
                        else:
                            enemies = encounter_data.battle_group(RUN.region, RUN.cur_visit)
                        def _build(enemies=enemies, node=node):
                            nonlocal battle_sc
                            battle_sc = rl.make_battle(screen, W, H, fonts, enemies)
                            battle_sc.set_reward_preview(
                                levels=run_data.LEVEL_REWARD.get(node, 0),
                                gold=run_data.GOLD_REWARD.get(node, 0))
                        start_battle_fade(_build)
                    elif node == run_data.NODE_BOSS:
                        # 보스 지점: 스토리 없이 바로 전투
                        boss = encounter_data.boss(RUN.region, RUN.cur_visit)
                        rl_boss_drop = boss.get("drop")
                        def _build(boss=boss, node=node):
                            nonlocal battle_sc
                            battle_sc = rl.make_battle(screen, W, H, fonts, boss["enemies"])
                            battle_sc.set_reward_preview(
                                levels=run_data.LEVEL_REWARD.get(node, 0),
                                gold=run_data.GOLD_REWARD.get(node, 0),
                                extra="체력 전체 회복")
                        start_battle_fade(_build)
                    elif node == run_data.NODE_MAW:
                        cuts = RUN.current_dialogue()
                        rl_dialogue_sc = DialogueScreen(screen, W, H, fonts, cuts or [])
                        rl_after_dialogue = ("maw", encounter_data.maw_final()["enemies"])
                        current = "rl_dialogue"
                    elif node == run_data.NODE_EVENT:
                        # 구역×회차 배치표에서 N번째 사건을 가져온다 (cuts가 있으면 다이얼로그 먼저)
                        ev = encounter_data.event_def(RUN.region, RUN.cur_visit, RUN.next_seq("event"))
                        RUN.add_gold(run_data.GOLD_REWARD.get(run_data.NODE_EVENT, 0))
                        cuts = ev.get("cuts") if ev else None
                        if cuts:
                            rl_dialogue_sc = DialogueScreen(screen, W, H, fonts, cuts)
                            rl_after_dialogue = ("event", ev)
                            current = "rl_dialogue"
                        else:
                            event_sc = EventScreen(screen, W, H, fonts, ev)
                            current = "event"
                    elif node == run_data.NODE_REWARD:
                        # 구역×회차 배치표에서 N번째 보상을 가져온다
                        rdef = encounter_data.reward_def(RUN.region, RUN.cur_visit, RUN.next_seq("reward"))
                        RUN.add_gold(run_data.GOLD_REWARD.get(run_data.NODE_REWARD, 0))
                        reward_sc = RewardScreen(screen, W, H, fonts,
                                                 kind=rdef.get("kind", "item"),
                                                 fixed=rdef.get("choices"))
                        current = "reward"
                    elif node == run_data.NODE_SHOP:
                        # 상점: 화면 전환 없이 맵 위에 팝업 (닫으면 다음 노드로)
                        shop_sc = ShopScreen(screen, W, H, fonts, popup=True)
                        overlay = "shop"

            elif current == "reward" and reward_sc:
                r = reward_sc.handle_event(event)
                if r == "done":
                    current, map_sc, region_sc = _finish_node(screen, W, H, fonts)

            elif current == "event" and event_sc:
                r = event_sc.handle_event(event)
                if r == "done":
                    current, map_sc, region_sc = _finish_node(screen, W, H, fonts)
                elif isinstance(r, tuple) and r[0] == "battle":
                    # 사건에서 파생된 전투 (승리 후 처리는 battle 핸들러의 rl_event_battle 분기)
                    rl_event_battle = r[1]
                    def _build(spec=rl_event_battle):
                        nonlocal battle_sc
                        battle_sc = rl.make_battle(screen, W, H, fonts, list(spec["enemies"]))
                        battle_sc.set_reward_preview(
                            levels=run_data.LEVEL_REWARD.get(run_data.NODE_BATTLE, 1),
                            gold=spec.get("gold", run_data.GOLD_REWARD.get(run_data.NODE_BATTLE, 0)))
                    start_battle_fade(_build)

            elif current == "rl_growth" and rl_growth_sc:
                r = rl_growth_sc.handle_event(event)
                if r == "back":
                    current = "map"
                elif r == "skill_config":
                    rl_skill_sc = SkillConfigScreen(screen, W, H, fonts)
                    current = "rl_skill"
                elif r == "item_view":
                    rl_item_sc = ItemViewScreen(screen, W, H, fonts)
                    current = "rl_item"

            elif current == "rl_skill" and rl_skill_sc:
                r = rl_skill_sc.handle_event(event)
                if r == "back":
                    current = "rl_growth"

            elif current == "rl_item" and rl_item_sc:
                r = rl_item_sc.handle_event(event)
                if r == "back":
                    current = "rl_growth"

            elif current == "rl_dialogue" and rl_dialogue_sc:
                r = rl_dialogue_sc.handle_event(event)
                if r == "done":
                    act = rl_after_dialogue
                    rl_after_dialogue = None
                    if isinstance(act, tuple) and act[0] in ("battle", "boss", "maw"):
                        def _build(act=act):
                            nonlocal battle_sc
                            battle_sc = rl.make_battle(screen, W, H, fonts, list(act[1]))
                        start_battle_fade(_build)
                    elif isinstance(act, tuple) and act[0] == "event":
                        # 사건 도입 다이얼로그 종료 → 선택지 화면으로
                        event_sc = EventScreen(screen, W, H, fonts, act[1])
                        current = "event"
                    else:
                        # 대화만 (시작/중간 대화) → 노드 완료 처리
                        current, map_sc, region_sc = _finish_node(screen, W, H, fonts)

            elif current == "run_result" and result_sc:
                r = result_sc.handle_event(event)
                if r == "title":
                    title = TitleScreen(screen, W, H, fonts)
                    current = "title"

        _modal_overlay = overlay in ("pause", "settings", "giveup")
        if fade_sc is not None:
            if fade_sc.update(dt) == "done":
                fade_sc = None
                fade_bg_draw = None
                fade_display_key = None
        elif _modal_overlay:                 # 일시정지/설정/포기 중엔 뒤 화면 정지
            pass
        elif current == "title":          title.update(dt)
        elif current == "battle_select": battle_select_sc.update(dt)
        elif current == "boss_select" and boss_select_sc: boss_select_sc.update(dt)
        elif current == "credits" and credits_sc: credits_sc.update(dt)
        elif current == "gamestart":    gamestart_sc.update(dt)
        elif current == "compendium" and comp_stack:
                                        comp_top().update(dt)
        elif current == "glossary" and gloss_stack:
                                        gloss_top().update(dt)
        elif current == "battle":
            battle_sc.update(dt)
            # STAGE CLEAR 연출이 끝나면 자동으로 종료 이벤트를 발생 (기존 back 경로 재사용)
            if getattr(battle_sc, "_battle_done", False):
                battle_sc._battle_done = False
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        elif current == "region_select" and region_sc:  region_sc.update(dt)
        elif current == "map" and map_sc:               map_sc.update(dt)
        elif current == "reward" and reward_sc:         reward_sc.update(dt)
        elif current == "event" and event_sc:           event_sc.update(dt)
        elif current == "rl_growth" and rl_growth_sc:   rl_growth_sc.update(dt)
        elif current == "rl_skill" and rl_skill_sc:     rl_skill_sc.update(dt)
        elif current == "rl_item" and rl_item_sc:       rl_item_sc.update(dt)
        elif current == "rl_dialogue" and rl_dialogue_sc: rl_dialogue_sc.update(dt)
        elif current == "run_result" and result_sc:     result_sc.update(dt)
        elif current == "act_menu" and act_menu_sc:   act_menu_sc.update(dt)
        elif current == "growth" and growth_sc:           growth_sc.update(dt)
        elif current == "skill_config" and skill_sc:      skill_sc.update(dt)
        elif current == "item_view" and item_sc:          item_sc.update(dt)
        elif current == "story" and story_sc:             story_sc.update(dt)
        elif current == "loading":
            if loading_sc.update(dt) == "done":
                stage_data = STORY[story_ctx["act"]]["chapters"][story_ctx["chap"]]["stages"][story_ctx["stage"]]
                if after_load == "dialogue":
                    dialogue_sc = DialogueScreen(screen, W, H, fonts, stage_data["dialogue"])
                    current = "dialogue"
                elif after_load == "battle":
                    b = stage_data["battle"]
                    def _build(b=b):
                        nonlocal battle_sc
                        battle_sc = BattleScreen(screen, W, H, fonts,
                                                 enemies=b["enemies"], allies=b["allies"],
                                                 enemy_formation=b.get("enemy_formation", "솔로"),
                                                 ally_formation=b.get("ally_formation", "솔로"),
                                                 gap=b.get("gap", 0.3))
                    start_battle_fade(_build)
                else:
                    _t = stage_data["title"]
                    save_data.on_stage_clear(story_ctx["act"], story_ctx["chap"], story_ctx["stage"], STORY)
                    _ctx = story_ctx; story_ctx = None
                    placeholder = PlaceholderScreen(screen, W, H, fonts, f"{_t} 클리어!")
                    current = "placeholder"
        elif current == "dialogue":     dialogue_sc.update(dt)
        elif current == "placeholder":  placeholder.update(dt)
        if overlay == "reset":          reset_dlg.update(dt)
        elif overlay == "quit":         quit_dlg.update(dt)
        elif overlay == "pause":        pause_menu.update(dt)
        elif overlay == "settings":     settings_sc.update(dt)
        elif overlay == "giveup":       giveup_dlg.update(dt)
        elif overlay == "shop" and shop_sc: shop_sc.update(dt)

        _use_snapshot = (_modal_overlay and pause_bg is not None
                         and pause_bg.get_size() == screen.get_size())
        if fade_sc is not None:
            if fade_bg_draw is not None:
                fade_bg_draw()       # 베일 뒤 화면 (콜백으로 전환 전/후 화면을 그림)
            fade_sc.draw()           # 검은 베일
        elif _use_snapshot:                  # 정지된 배경 한 장만 사용 (어른거림/깜빡임 제거)
            screen.blit(pause_bg, (0, 0))
        elif current == "title":          title.draw()
        elif current == "battle_select": battle_select_sc.draw()
        elif current == "boss_select" and boss_select_sc: boss_select_sc.draw()
        elif current == "credits" and credits_sc: credits_sc.draw()
        elif current == "gamestart":    gamestart_sc.draw()
        elif current == "compendium" and comp_stack:
                                        comp_top().draw()
        elif current == "glossary" and gloss_stack:
                                        gloss_top().draw()
        elif current == "battle":       battle_sc.draw()
        elif current == "region_select" and region_sc:  region_sc.draw()
        elif current == "map" and map_sc:               map_sc.draw()
        elif current == "reward" and reward_sc:         reward_sc.draw()
        elif current == "event" and event_sc:           event_sc.draw()
        elif current == "rl_growth" and rl_growth_sc:   rl_growth_sc.draw()
        elif current == "rl_skill" and rl_skill_sc:     rl_skill_sc.draw()
        elif current == "rl_item" and rl_item_sc:       rl_item_sc.draw()
        elif current == "rl_dialogue" and rl_dialogue_sc: rl_dialogue_sc.draw()
        elif current == "run_result" and result_sc:     result_sc.draw()
        elif current == "act_menu" and act_menu_sc:   act_menu_sc.draw()
        elif current == "growth" and growth_sc:           growth_sc.draw()
        elif current == "skill_config" and skill_sc:      skill_sc.draw()
        elif current == "item_view" and item_sc:          item_sc.draw()
        elif current == "story" and story_sc:             story_sc.draw()
        elif current == "loading":      loading_sc.draw()
        elif current == "dialogue":     dialogue_sc.draw()
        elif current == "placeholder":  placeholder.draw()
        if overlay == "reset":          reset_dlg.draw()
        elif overlay == "quit":         quit_dlg.draw()
        elif overlay == "pause":        pause_menu.draw()
        elif overlay == "settings":     settings_sc.draw()
        elif overlay == "giveup":       giveup_dlg.draw()
        elif overlay == "shop" and shop_sc: shop_sc.draw()

        pygame.display.flip()


if __name__ == "__main__":
    main()