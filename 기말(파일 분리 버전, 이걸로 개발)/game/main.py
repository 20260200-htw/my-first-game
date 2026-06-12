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
    PlaceholderScreen, QuitDialog, GameStartScreen, ResetConfirmDialog
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
    """구간 종료 후: 다음 구간 지역 선택 또는 마왕성 진입.
    반환: (current, map_sc, region_sc)
    """
    if RUN.segment >= run_data.FINAL_SEGMENT:
        # 마왕성 종료 = 클리어(전투에서 result 처리됨). 안전망.
        return ("map", MapScreen(screen, W, H, fonts), None)
    if RUN.segment >= run_data.FINAL_SEGMENT - 1:
        # 5구간 종료 → 마왕성 진입
        RUN.last_region = RUN.region
        RUN.enter_maw()
        return ("map", MapScreen(screen, W, H, fonts), None)
    # 다음 구간 지역 선택
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

    while True:
        dt = clock.tick(FRAMERATES[settings["fps_index"]])

        # 화면에 맞는 배경음악 자동 전환 (매핑에 없는 화면은 현재 BGM 유지)
        utils.update_bgm(current)

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
                    settings_sc = SettingsScreen(screen, W, H, fonts)
                    current = "settings"
                elif a == "gallery":
                    gallery_sc = GalleryScreen(screen, W, H, fonts)
                    current = "gallery"
                elif a == "start":
                    # 로그라이크 회차 시작 → 1구간은 중앙 고정
                    RUN.start_new_run()
                    RUN.enter_region(run_data.FIRST_REGION)
                    map_sc = MapScreen(screen, W, H, fonts)
                    current = "map"
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
                    battle_sc = BattleScreen(screen, W, H, fonts,
                                             enemies=preset["enemies"],
                                             allies=preset["allies"],
                                             enemy_formation=preset["enemy_formation"],
                                             ally_formation=preset["ally_formation"],
                                             gap=preset.get("gap", 0.12))
                    current = "battle"

            elif current == "gamestart":
                r = gamestart_sc.handle_event(event)
                if r == "back":
                    current = "title"
                elif r == "story":
                    story_sc = ActSelectScreen(screen, W, H, fonts)
                    current = "story"

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
                elif r == "glossary":
                    gloss_stack.clear()
                    top_items = [(k, v) for k, v in GLOSSARY.items()]
                    push_gloss(CompendiumMenuScreen(screen, W, H, fonts, "용어", top_items))
                    current = "glossary"
                elif r == "compendium":
                    comp_stack.clear()
                    top_items = [(k, v) for k, v in COMPENDIUM.items()]
                    push_comp(CompendiumMenuScreen(screen, W, H, fonts, "도감", top_items))
                    current = "compendium"

            elif current == "battle":
                r = battle_sc.handle_event(event)
                if r == "back":
                    # ── 로그라이크 전투 종료 ──────────────────────
                    if RUN.active:
                        rl.sync_player_hp_from_battle(battle_sc)
                        won = rl.battle_won(battle_sc)
                        if not won:
                            # 패배 → 결과(실패)
                            rl_event_battle = None
                            result_sc = RunResultScreen(screen, W, H, fonts, success=False)
                            current = "run_result"
                        elif rl_event_battle is not None:
                            # ── 사건에서 파생된 전투: 승리 처리 ──
                            spec = rl_event_battle
                            rl_event_battle = None
                            RUN.gain_exp(run_data.EXP_REWARD.get(run_data.NODE_BATTLE, 0))
                            RUN.add_gold(spec.get("gold", run_data.GOLD_REWARD.get(run_data.NODE_BATTLE, 0)))
                            drop  = spec.get("drop")
                            rkind = spec.get("reward")      # "skill" / "item" / None
                            if drop or rkind:
                                reward_sc = RewardScreen(screen, W, H, fonts,
                                                         kind=(rkind or "item"),
                                                         special_item=drop,
                                                         fixed=(None if rkind else False))
                                current = "reward"
                            else:
                                current, map_sc, region_sc = _finish_node(screen, W, H, fonts)
                        else:
                            node = RUN.current_node()
                            # 경험치/골드 정산
                            RUN.gain_exp(run_data.EXP_REWARD.get(node, 0))
                            RUN.add_gold(run_data.GOLD_REWARD.get(node, 0))
                            if node == run_data.NODE_MAW:
                                RUN.advance_node()
                                result_sc = RunResultScreen(screen, W, H, fonts, success=True)
                                current = "run_result"
                            elif node == run_data.NODE_BOSS:
                                RUN.full_heal()
                                reward_sc = RewardScreen(screen, W, H, fonts,
                                                         kind="skill", special_item=rl_boss_drop)
                                rl_boss_drop = None
                                current = "reward"
                            elif node == run_data.NODE_ELITE:
                                reward_sc = RewardScreen(screen, W, H, fonts, kind="item")
                                current = "reward"
                            else:
                                reward_sc = RewardScreen(screen, W, H, fonts, kind="skill")
                                current = "reward"
                    elif story_ctx is not None:
                        # 스토리 전투 종료: 승리 시 클리어, 아니면 스테이지 선택으로
                        won = (battle_sc.logic.winner == "ally")
                        _ctx = story_ctx
                        story_ctx = None
                        if won:
                            _t = STORY[_ctx["act"]]["chapters"][_ctx["chap"]]["stages"][_ctx["stage"]]["title"]
                            save_data.on_stage_clear(_ctx["act"], _ctx["chap"], _ctx["stage"], STORY)
                            placeholder = PlaceholderScreen(screen, W, H, fonts, f"{_t} 클리어!")
                            current = "placeholder"
                        else:
                            story_sc = StageSelectScreen(screen, W, H, fonts, _ctx["act"], _ctx["chap"])
                            current = "story"
                    else:
                        current = "title"

            elif current == "loading":
                pass  # 로딩 중 입력 무시 (전환은 update 에서)

            elif current == "dialogue":
                r = dialogue_sc.handle_event(event)
                if r == "done":
                    stage_data = STORY[story_ctx["act"]]["chapters"][story_ctx["chap"]]["stages"][story_ctx["stage"]]
                    if stage_data.get("battle"):
                        b = stage_data["battle"]
                        battle_sc = BattleScreen(screen, W, H, fonts,
                                                 enemies=b["enemies"], allies=b["allies"],
                                                 enemy_formation=b.get("enemy_formation", "솔로"),
                                                 ally_formation=b.get("ally_formation", "솔로"),
                                                 gap=b.get("gap", 0.3))
                        current = "battle"
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
                    current = "title"
                elif isinstance(r, tuple) and r[0] == "region":
                    RUN.enter_region(r[1])
                    map_sc = MapScreen(screen, W, H, fonts)
                    current = "map"

            elif current == "map" and map_sc:
                r = map_sc.handle_event(event)
                if r == "back":
                    current = "title"
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
                        # 중간 지점: 다이얼로그 → (중간보스 있으면 전투, 없으면 노드 완료)
                        cuts = RUN.current_dialogue()
                        rl_dialogue_sc = DialogueScreen(screen, W, H, fonts, cuts or [])
                        mb = RUN.current_mid_boss()
                        if mb:
                            rl_after_dialogue = ("battle", mb["enemies"])
                        else:
                            rl_after_dialogue = "node"
                        current = "rl_dialogue"
                    elif node in (run_data.NODE_BATTLE, run_data.NODE_ELITE):
                        # 구역×회차 출현 풀에서 랜덤 조합으로 적 편성을 만든다
                        if node == run_data.NODE_ELITE:
                            enemies = encounter_data.elite_group(RUN.region, RUN.cur_visit)
                        else:
                            enemies = encounter_data.battle_group(RUN.region, RUN.cur_visit)
                        battle_sc = rl.make_battle(screen, W, H, fonts, enemies)
                        current = "battle"
                    elif node == run_data.NODE_BOSS:
                        # 보스 지점: 다이얼로그 → 전투
                        # (마왕성은 갈래(열)별 사천왕, 그 외에는 구역×회차 보스)
                        if RUN.region == "마왕성":
                            boss = encounter_data.maw_boss(RUN.cur_col)
                        else:
                            boss = encounter_data.boss(RUN.region, RUN.cur_visit)
                        rl_boss_drop = boss.get("drop")
                        cuts = RUN.current_dialogue()
                        rl_dialogue_sc = DialogueScreen(screen, W, H, fonts, cuts or [])
                        rl_after_dialogue = ("boss", boss["enemies"])
                        current = "rl_dialogue"
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
                        shop_sc = ShopScreen(screen, W, H, fonts)
                        current = "shop"

            elif current == "reward" and reward_sc:
                r = reward_sc.handle_event(event)
                if r == "done":
                    current, map_sc, region_sc = _finish_node(screen, W, H, fonts)

            elif current == "shop" and shop_sc:
                r = shop_sc.handle_event(event)
                if r == "done":
                    current, map_sc, region_sc = _finish_node(screen, W, H, fonts)

            elif current == "event" and event_sc:
                r = event_sc.handle_event(event)
                if r == "done":
                    current, map_sc, region_sc = _finish_node(screen, W, H, fonts)
                elif isinstance(r, tuple) and r[0] == "battle":
                    # 사건에서 파생된 전투 (승리 후 처리는 battle 핸들러의 rl_event_battle 분기)
                    rl_event_battle = r[1]
                    battle_sc = rl.make_battle(screen, W, H, fonts, list(rl_event_battle["enemies"]))
                    current = "battle"

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
                        battle_sc = rl.make_battle(screen, W, H, fonts, list(act[1]))
                        current = "battle"
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

        if current == "title":          title.update(dt)
        elif current == "battle_select": battle_select_sc.update(dt)
        elif current == "gamestart":    gamestart_sc.update(dt)
        elif current == "settings":     settings_sc.update(dt)
        elif current == "gallery":      gallery_sc.update(dt)
        elif current == "compendium" and comp_stack:
                                        comp_top().update(dt)
        elif current == "glossary" and gloss_stack:
                                        gloss_top().update(dt)
        elif current == "battle":       battle_sc.update(dt)
        elif current == "region_select" and region_sc:  region_sc.update(dt)
        elif current == "map" and map_sc:               map_sc.update(dt)
        elif current == "reward" and reward_sc:         reward_sc.update(dt)
        elif current == "shop" and shop_sc:             shop_sc.update(dt)
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
                    battle_sc = BattleScreen(screen, W, H, fonts,
                                             enemies=b["enemies"], allies=b["allies"],
                                             enemy_formation=b.get("enemy_formation", "솔로"),
                                             ally_formation=b.get("ally_formation", "솔로"),
                                             gap=b.get("gap", 0.3))
                    current = "battle"
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

        if current == "title":          title.draw()
        elif current == "battle_select": battle_select_sc.draw()
        elif current == "gamestart":    gamestart_sc.draw()
        elif current == "settings":     settings_sc.draw()
        elif current == "gallery":      gallery_sc.draw()
        elif current == "compendium" and comp_stack:
                                        comp_top().draw()
        elif current == "glossary" and gloss_stack:
                                        gloss_top().draw()
        elif current == "battle":       battle_sc.draw()
        elif current == "region_select" and region_sc:  region_sc.draw()
        elif current == "map" and map_sc:               map_sc.draw()
        elif current == "reward" and reward_sc:         reward_sc.draw()
        elif current == "shop" and shop_sc:             shop_sc.draw()
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

        pygame.display.flip()


if __name__ == "__main__":
    main()