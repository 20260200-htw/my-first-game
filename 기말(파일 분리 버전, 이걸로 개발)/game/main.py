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
import roguelike_flow as rl
from screens.region_select_screen import RegionSelectScreen
from screens.map_screen import MapScreen
from screens.reward_screen import RewardScreen
from screens.shop_screen import ShopScreen
from screens.event_screen import EventScreen
from screens.run_result_screen import RunResultScreen


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
    rl_after_battle = None    # 전투 후 처리: "reward_skill"/"reward_item"/"boss"/"maw"/None
    rl_boss_drop = None       # 보스 전리품 아이템 키
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
                    # 로그라이크 회차 시작 (주인공 1명으로 시작 → 지역 선택)
                    RUN.start_new_run()
                    region_sc = RegionSelectScreen(screen, W, H, fonts)
                    current = "region_select"
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
                            result_sc = RunResultScreen(screen, W, H, fonts, success=False)
                            current = "run_result"
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
                    if node in (run_data.NODE_BATTLE, run_data.NODE_ELITE):
                        kind = "elite" if node == run_data.NODE_ELITE else "battle"
                        enemies = run_data.pick_enemy_group(RUN.region, kind)
                        battle_sc = rl.make_battle(screen, W, H, fonts, enemies)
                        current = "battle"
                    elif node == run_data.NODE_BOSS:
                        boss = run_data.region_boss(RUN.region)
                        rl_boss_drop = run_data.BOSS_DROP.get(boss["name"])
                        battle_sc = rl.make_battle(screen, W, H, fonts, boss["enemies"])
                        current = "battle"
                    elif node == run_data.NODE_MAW:
                        battle_sc = rl.make_battle(screen, W, H, fonts, run_data.MAW_FINAL["enemies"])
                        current = "battle"
                    elif node == run_data.NODE_EVENT:
                        event_sc = EventScreen(screen, W, H, fonts)
                        RUN.add_gold(run_data.GOLD_REWARD.get(run_data.NODE_EVENT, 0))
                        current = "event"
                    elif node == run_data.NODE_REWARD:
                        RUN.add_gold(run_data.GOLD_REWARD.get(run_data.NODE_REWARD, 0))
                        reward_sc = RewardScreen(screen, W, H, fonts, kind="item")
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

            elif current == "rl_growth" and rl_growth_sc:
                r = rl_growth_sc.handle_event(event)
                if r == "back":
                    current = "map"

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
        elif current == "run_result" and result_sc:     result_sc.update(dt)
        elif current == "act_menu" and act_menu_sc:   act_menu_sc.update(dt)
        elif current == "growth" and growth_sc:           growth_sc.update(dt)
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
        elif current == "run_result" and result_sc:     result_sc.draw()
        elif current == "act_menu" and act_menu_sc:   act_menu_sc.draw()
        elif current == "growth" and growth_sc:           growth_sc.draw()
        elif current == "story" and story_sc:             story_sc.draw()
        elif current == "loading":      loading_sc.draw()
        elif current == "dialogue":     dialogue_sc.draw()
        elif current == "placeholder":  placeholder.draw()
        if overlay == "reset":          reset_dlg.draw()
        elif overlay == "quit":         quit_dlg.draw()

        pygame.display.flip()


if __name__ == "__main__":
    main()