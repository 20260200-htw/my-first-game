# 로그라이크 흐름 헬퍼
# 노드 진입 시 전투 생성, 주인공 스킬/아이템 반영, 전투 결과 정산 등.

import copy
import save_data
from run_state import RUN
from data import run_data
from data.characters_data import ALLY_DEFS, ENEMY_DEFS
from screens.battle_screens import BattleScreen


def _player_def_for_battle():
    """주인공 전투 정의 = 기본 정의에 런의 장착 스킬을 주입한 사본."""
    d = copy.deepcopy(ALLY_DEFS["주인공"])
    # 장착 스킬로 교체 (없으면 기본 스킬 유지)
    if RUN.skills_equipped:
        d["skills"] = copy.deepcopy(RUN.skills_equipped)
    # 아이템: 최대 HP 반영 (combatant 가 hp_bonus 로 처리하므로 여기선 hp_max 직접 보정)
    d["hp_max"] = RUN.hp_max
    return d


def _ally_def_for_battle(name):
    """합류 동료 전투 정의."""
    if name == "주인공":
        return _player_def_for_battle()
    if name in ALLY_DEFS:
        return copy.deepcopy(ALLY_DEFS[name])
    # 혹시 모를 fallback
    return copy.deepcopy(ALLY_DEFS["주인공"])


def make_battle(screen, W, H, fonts, enemies, temp_allies=None):
    """현재 런 파티로 전투 화면 생성.
    enemies: 적 이름 리스트 (1웨이브)
    temp_allies: 이 전투 한정 동료
    """
    ally_names = RUN.battle_party(temp_allies)
    n = len(ally_names)
    ef = run_data.enemy_formation_for(len(enemies))

    # BattleScreen 은 ALLY_DEFS/ENEMY_DEFS 이름으로 생성하므로,
    # 주인공 스킬 주입을 위해 임시로 ALLY_DEFS["주인공"] 을 교체했다가 복구한다.
    orig_player = ALLY_DEFS["주인공"]
    ALLY_DEFS["주인공"] = _player_def_for_battle()
    try:
        bs = BattleScreen(screen, W, H, fonts,
                          enemies=list(enemies),
                          allies=ally_names,
                          enemy_formation=ef,
                          ally_formation=run_data.enemy_formation_for(n),
                          gap=0.3)
    finally:
        ALLY_DEFS["주인공"] = orig_player

    # 주인공 현재 HP 를 런 상태로 동기화 (전투 시작 시점)
    for c in bs.allies:
        if getattr(c, "ctype", None) == "player":
            c.hp = min(c.hp_max, RUN.hp_cur if RUN.hp_cur > 0 else c.hp_max)
            break
    return bs


def sync_player_hp_from_battle(bs):
    """전투 종료 후 주인공 HP 를 런 상태로 가져온다."""
    for c in bs.allies:
        if getattr(c, "ctype", None) == "player":
            RUN.hp_cur = max(0, c.hp)
            break


def battle_won(bs):
    return getattr(bs.logic, "winner", None) == "ally"
