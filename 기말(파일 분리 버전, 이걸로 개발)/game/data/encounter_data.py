# ══════════════════════════════════════════════════════════════════
#   구역(지역) × 회차별 배치 데이터
# ══════════════════════════════════════════════════════════════════
# 이 파일에서 "어느 구역을 몇 번째 방문했을 때" 각 노드에 무엇이 나올지 배치한다.
#
#   - battle      : 이 구간의 전투 노드에 출현 가능한 일반 몬스터 풀
#                   (characters_data.ENEMY_DEFS 의 이름을 나열)
#   - battle_size : (선택) 일반 전투 마릿수 범위 (최소, 최대). 기본 (1, 3)
#   - elite       : 엘리트 노드에 출현 가능한 엘리트 몬스터 풀
#   - elite_size  : (선택) 엘리트 전투 마릿수 범위. 기본 (1, 3)
#   - event       : 사건 노드에 순서대로 배치될 사건 (아래 EVENT_DEFS 키 또는 인라인 dict)
#   - reward      : 보상 노드에 순서대로 배치될 보상 정의
#   - mid_boss    : 중간 지점 중간보스 (None 이면 대화만 하고 통과)
#   - boss        : 구간 보스 (enemies / name / drop)
#
# ▶ 전투/엘리트 배치 규칙 — 랜덤 조합
#   전투 노드에 진입하면 풀에서 마릿수만큼 무작위로 뽑아(같은 몬스터 중복 허용)
#   그 자리에서 편성이 만들어진다. 매 전투마다 조합이 달라진다.
#   같은 이름을 풀에 여러 번 적으면 그 몬스터가 더 자주 나온다.
#     예) ["말단병사", "말단병사", "Eat_slime1"]  →  말단병사 출현 확률 2배
#
# ▶ 사건/보상 배치 규칙 — 번호 슬롯
#   같은 구간 안에서 그 종류의 노드를 N번째로 밟으면 목록의 N번째 항목이 나온다.
#   목록보다 노드가 많으면 처음부터 순환한다. (사건 4번째 = 목록 1번)
#
# ▶ 회차 폴백
#   REGION_PLAN[지역][회차] 에 해당 키가 없으면 그보다 낮은 회차에서 찾고,
#   그래도 없으면 DEFAULT_PLAN 을 쓴다.
#   → 2회차에 "boss" 만 적으면 나머지(battle/event/...)는 1회차 것을 그대로 쓴다.
#   → "mid_boss": None 을 명시하면 "중간보스 없음"으로 덮어쓴다.
#
# ▶ 지점(시작/중간/보스) 다이얼로그는 기존처럼 run_data.REGION_DIALOGUE 에서 관리.

import copy
import random


# ══════════════════════════════════════════════════════════════════
#   사건(이벤트) 라이브러리
# ══════════════════════════════════════════════════════════════════
# 각 사건:
#   "cuts"    : (선택) 선택지 전에 출력할 다이얼로그. story_dialogue 의 cuts 형식 그대로.
#               background / cutscene / characters / sound 등 전부 사용 가능.
#   "text"    : 선택지 화면에 표시될 상황 한 줄.
#   "choices" : [{"label": 버튼 문구, "outcome": (종류, 값)}]
#
# outcome 종류:
#   ("gold", 40)            골드 획득
#   ("heal", 30)            체력 30% 회복
#   ("ally", None)          동료 합류 (None=풀에서 랜덤, "금강" 처럼 이름 지정 가능)
#   ("skill", None)         스킬 획득 (None=랜덤, "강타" 처럼 SKILL_POOL 이름 지정 가능)
#   ("item", None)          아이템 획득 (None=랜덤, "낡은 검" 처럼 ITEMS 키 지정 가능)
#   ("battle", {...})       전투로 파생. spec:
#                             "enemies": ["말단병사", ...]   (필수)
#                             "drop":    승리 시 확정 아이템 키 (선택)
#                             "reward":  승리 후 3택1 종류 "skill"/"item" (선택)
#                             "gold":    승리 골드 (선택, 기본 전투 노드 골드)
#                           패배하면 일반 전투처럼 회차가 끝난다.
#   ("nothing", 0)          아무 일 없음

def _cut(speaker, text, affiliation="", sprite=None, x=0.5, y=1.0, scale=0.75, bg=""):
    cut = {"characters": [], "background": bg,
           "affiliation": affiliation, "speaker": speaker, "text": text}
    if sprite:
        cut["characters"] = [{"sprite": sprite, "x": x, "y": y, "scale": scale}]
    return cut


EVENT_DEFS = {
    "보물상자": {
        "cuts": [
            _cut("주인공", "수풀 사이에 낡은 보물상자가 놓여 있다."),
            _cut("주인공", "함정일지도 모르지만... 열어볼까?"),
        ],
        "text": "낡은 보물상자를 발견했다. 열어볼까?",
        "choices": [
            {"label": "연다",  "outcome": ("gold", 40)},
            {"label": "무시한다",     "outcome": ("nothing", 0)},
        ],
    },
    "휴식처": {
        "cuts": [
            _cut("주인공", "바람이 잔잔한 공터다. 잠시 쉬어 가기 좋아 보인다."),
        ],
        "text": "지친 몸을 쉴 수 있는 안전한 공터를 찾았다.",
        "choices": [
            {"label": "휴식한다", "outcome": ("heal", 100)},
            {"label": "그냥 지나간다",            "outcome": ("nothing", 0)},
        ],
    },
}


# ══════════════════════════════════════════════════════════════════
#   구역별 배치 (REGION_PLAN[지역][회차])
# ══════════════════════════════════════════════════════════════════
REGION_PLAN = {

    # ────────────────────────── 중앙 ──────────────────────────
    "중앙": {
        1: {
            "battle": ["slime", "goblin", "wild_boar"],
            "battle_size": (1, 2),
            "event": [
                "보물상자",                    # 1
                "휴식처",                      # 2
            ],
            "elite": ["dojuk"],
            "elite_size": (1, 1),       # 엘리트는 2~3마리
            # 중앙 구역 1회차 — 보상 노드
            "reward": [
                {"kind": "item"},                              # 1: 아이템 3택1 (랜덤)
                {"kind": "skill"},                             # 2: 스킬 3택1 (랜덤)
                {"kind": "item",                               # 3: 후보 직접 지정
                 "choices": ["생명의 부적", "재생의 반지", "신속의 장화"]},
            ],
            # 중간 지점 중간보스 (None = 대화만)
            "mid_boss": {"enemies": ["noob"]},
            # 구간 보스
            "boss": {"enemies": ["small_sky"]},
        },
    },

    # ────────────────────────── 동부 ──────────────────────────
    "동부": {
        1: {
            "battle": ["wood", "monkey"],
            "battle_size": (1, 3), 
            "event": [
                "보물상자",                    # 1
                "휴식처",                      # 2
            ],
            "elite": ["fox"],
            "elite_size": (1, 1),       # 항상 3마리 (고정 마릿수 예시)
            "reward": [
                {"kind": "item"},              # 1
                {"kind": "skill"},             # 2
            ],
            "mid_boss": {"enemies": ["dosa"]},
            "boss": {"enemies": ["kirin"]},
        },
    },

    # ────────────────────────── 서부 ──────────────────────────
    "서부": {
        1: {
            "battle": ["spin","ghost","ground_slime"],
            "battle_size": (2, 3), 
            "event": [
                "보물상자",                    # 1
                "휴식처",                      # 2
            ],
            "elite": ["small_shell"],
            "elite_size": (1, 1),
            "reward": [
                {"kind": "item"},              # 1
                {"kind": "skill"},             # 2
            ],
            "mid_boss": {"enemies": ["shell"]},
            "boss": {"enemies": ["jack"]},
        },
    },

    # ────────────────────────── 남부 ──────────────────────────
    "남부": {
        1: {
            "battle": ["leg_fish","sad_jelly", "fake_fish_man"],
            "battle_size": (1, 2), 
            "event": [
                "보물상자",                    # 1
                "휴식처",                      # 2
            ],
            "elite": ["long_fish"],
            "elite_size": (1, 1),       
            "reward": [
                {"kind": "skill"},             # 1
                {"kind": "item"},              # 2
            ],
            "mid_boss": {"enemies": ["octo"]},
            "boss": {"enemies": ["shark"]},
        },
    },

    # ────────────────────────── 북부 ──────────────────────────
    "북부": {
        1: {
            "battle": ["bear","ice_golem","wolf"],
            "battle_size": (1, 1), 
            "event": [
                "보물상자",                    # 1
                "휴식처",                      # 2
            ],
            "elite": ["snow_slime"],
            "elite_size": (1, 1),
            "reward": [
                {"kind": "item"},              # 1
                {"kind": "skill"},             # 2
            ],
            "mid_boss": {"enemies": ["ice_knight"]},
            "boss": {"enemies": ["north_wyvern"]},
        },
    },
}


# ══════════════════════════════════════════════════════════════════
#   마왕성 (6구간) 배치
# ══════════════════════════════════════════════════════════════════
MAW_REGION = "마왕성"

MAW_PLAN = {
    "battle": [""],
    "battle_size": (2, 3),
    "event": [
        "휴식처",                                  # 1
        "수상한 제단",                             # 2
    ],
    "elite": [""],
    "elite_size": (1, 2),
    "reward": [
        {"kind": "item"},                          # 1
        {"kind": "skill"},                         # 2
    ],
    "mid_boss": None,
    # 보스층 4갈래: 노드 열(col) 순서대로 0~3
    "bosses": [
        {"enemies": [""]},
        {"enemies": [""]},
        {"enemies": [""]},
        {"enemies": [""]},
    ],
    # 최종 마왕
    "final": {"enemies": [""]},
}


# ══════════════════════════════════════════════════════════════════
#   안전망 (지역/회차에 정의가 전혀 없을 때)
# ══════════════════════════════════════════════════════════════════
DEFAULT_PLAN = {
    "battle":      ["말단병사"],
    "battle_size": (1, 3),      # 전역 기본 마릿수
    "elite":       ["말단병사"],
    "elite_size":  (1, 3),
    "event":    ["보물상자"],
    "reward":   [{"kind": "item"}],
    "mid_boss": None,
    "boss":     {"enemies": ["벨라"], "name": "구역의 지배자", "drop": None},
}


# ══════════════════════════════════════════════════════════════════
#   조회 함수 (게임 로직이 사용)
# ══════════════════════════════════════════════════════════════════
def _plan_value(region, visit, key):
    """지역×회차에서 key 값을 찾는다. 낮은 회차 → DEFAULT 순으로 폴백."""
    if region == MAW_REGION:
        if key in MAW_PLAN:
            return MAW_PLAN[key]
        return DEFAULT_PLAN.get(key)
    reg = REGION_PLAN.get(region, {})
    for v in sorted((k for k in reg if k <= visit), reverse=True):
        if key in reg[v]:
            return reg[v][key]
    return DEFAULT_PLAN.get(key)


def _seq_pick(lst, seq):
    """목록에서 seq(0부터) 번째 항목. 목록을 넘으면 순환."""
    if not lst:
        return None
    return lst[seq % len(lst)]


def _rand_size(rng):
    """(최소, 최대) 범위에서 마릿수 결정. 잘못된 값은 보정, 상한 5."""
    try:
        lo, hi = int(rng[0]), int(rng[1])
    except (TypeError, ValueError, IndexError):
        lo, hi = 1, 3
    lo = max(1, lo)
    hi = min(5, max(lo, hi))
    return random.randint(lo, hi)


def _compose(pool, size_rng):
    """출현 풀에서 마릿수만큼 랜덤 조합 (같은 몬스터 중복 허용)."""
    pool = [n for n in pool if isinstance(n, str)]
    if not pool:
        pool = list(DEFAULT_PLAN["battle"])
    return random.choices(pool, k=_rand_size(size_rng))


def battle_group(region, visit):
    """전투 노드 진입 시: 그 구간의 출현 풀에서 랜덤 조합으로 편성 생성."""
    pool = _plan_value(region, visit, "battle") or DEFAULT_PLAN["battle"]
    return _compose(pool, _plan_value(region, visit, "battle_size"))


def elite_group(region, visit):
    """엘리트 노드 진입 시: 엘리트 출현 풀에서 랜덤 조합으로 편성 생성."""
    pool = _plan_value(region, visit, "elite") or DEFAULT_PLAN["elite"]
    return _compose(pool, _plan_value(region, visit, "elite_size"))


def event_def(region, visit, seq):
    """사건 노드 seq번째의 사건 정의 (사본). 문자열이면 EVENT_DEFS 에서 찾는다."""
    entries = _plan_value(region, visit, "event") or DEFAULT_PLAN["event"]
    entry = _seq_pick(entries, seq)
    if isinstance(entry, str):
        entry = EVENT_DEFS.get(entry)
    if not entry:
        entry = EVENT_DEFS["보물상자"]
    return copy.deepcopy(entry)


def reward_def(region, visit, seq):
    """보상 노드 seq번째의 보상 정의: {"kind": "item"/"skill", "choices": [...](선택)}."""
    entries = _plan_value(region, visit, "reward") or DEFAULT_PLAN["reward"]
    entry = _seq_pick(entries, seq) or {"kind": "item"}
    return copy.deepcopy(entry)


def mid_boss(region, visit):
    """중간 지점 중간보스 정의. 없으면 None."""
    return copy.deepcopy(_plan_value(region, visit, "mid_boss"))


def boss(region, visit):
    """구간 보스 정의 {"enemies", "name", "drop"}."""
    return copy.deepcopy(_plan_value(region, visit, "boss") or DEFAULT_PLAN["boss"])


def maw_boss(col):
    """마왕성 보스층 col번째 갈래의 사천왕."""
    bosses = MAW_PLAN["bosses"]
    return copy.deepcopy(bosses[col % len(bosses)])


def maw_final():
    """최종 마왕."""
    return copy.deepcopy(MAW_PLAN["final"])


# ══════════════════════════════════════════════════════════════════
#   배치 검증 (직접 실행: python -m data.encounter_data)
# ══════════════════════════════════════════════════════════════════
def validate():
    """적 이름 / 아이템 키 / 스킬 이름이 실제 데이터에 있는지 검사."""
    from data.characters_data import ENEMY_DEFS
    from data import run_data
    skill_names = {s["name"] for s in run_data.SKILL_POOL + run_data.STARTER_SKILLS}
    problems = []

    def chk_enemies(names, where):
        for n in names:
            if n not in ENEMY_DEFS:
                problems.append(f"{where}: 적 '{n}' 이(가) ENEMY_DEFS 에 없음")

    def chk_item(key, where):
        if key is not None and key not in run_data.ITEMS:
            problems.append(f"{where}: 아이템 '{key}' 이(가) ITEMS 에 없음")

    def chk_event(ev, where):
        if isinstance(ev, str):
            if ev not in EVENT_DEFS:
                problems.append(f"{where}: 사건 '{ev}' 이(가) EVENT_DEFS 에 없음")
                return
            ev = EVENT_DEFS[ev]
        for ch in ev.get("choices", []):
            kind, val = ch["outcome"]
            if kind == "battle":
                chk_enemies(val.get("enemies", []), where + "/전투")
                chk_item(val.get("drop"), where + "/드랍")
            elif kind == "item" and val is not None:
                chk_item(val, where)
            elif kind == "skill" and val is not None and val not in skill_names:
                problems.append(f"{where}: 스킬 '{val}' 이(가) 스킬 풀에 없음")

    def chk_pool(pool, where):
        if pool is None:
            return
        if not isinstance(pool, (list, tuple)):
            problems.append(f"{where}: 몬스터 이름을 나열한 풀(리스트)이어야 함")
            return
        for n in pool:
            if not isinstance(n, str):
                problems.append(f"{where}: {n!r} — 풀에는 몬스터 이름(문자열)만. 그룹 중첩 금지")
            elif n not in ENEMY_DEFS:
                problems.append(f"{where}: 적 '{n}' 이(가) ENEMY_DEFS 에 없음")

    def chk_size(rng, where):
        if rng is None:
            return
        ok = (isinstance(rng, (list, tuple)) and len(rng) == 2
              and all(isinstance(x, int) for x in rng)
              and 1 <= rng[0] <= rng[1] <= 5)
        if not ok:
            problems.append(f"{where}: 마릿수는 (최소, 최대) — 1~5 사이 정수, 최소≤최대")

    def chk_plan(plan, where):
        chk_pool(plan.get("battle"), where + "/battle")
        chk_size(plan.get("battle_size"), where + "/battle_size")
        chk_pool(plan.get("elite"), where + "/elite")
        chk_size(plan.get("elite_size"), where + "/elite_size")
        for ev in plan.get("event", []):
            chk_event(ev, where + "/event")
        for rd in plan.get("reward", []):
            if rd.get("kind") == "item":
                for k in rd.get("choices", []) or []:
                    chk_item(k, where + "/reward")
            elif rd.get("kind") == "skill":
                for n in rd.get("choices", []) or []:
                    if n not in skill_names:
                        problems.append(f"{where}/reward: 스킬 '{n}' 없음")
        mb = plan.get("mid_boss")
        if mb:
            chk_enemies(mb.get("enemies", []), where + "/mid_boss")
        b = plan.get("boss")
        if b:
            chk_enemies(b.get("enemies", []), where + "/boss")
            chk_item(b.get("drop"), where + "/boss")

    for region, visits in REGION_PLAN.items():
        for visit, plan in visits.items():
            chk_plan(plan, f"{region} {visit}회차")
    chk_plan(MAW_PLAN, "마왕성")
    for b in MAW_PLAN.get("bosses", []):
        chk_enemies(b.get("enemies", []), "마왕성/bosses")
    chk_enemies(MAW_PLAN["final"]["enemies"], "마왕성/final")

    return problems


if __name__ == "__main__":
    probs = validate()
    if probs:
        print("배치 데이터 문제 발견:")
        for p in probs:
            print(" -", p)
    else:
        print("배치 데이터 검증 통과: 문제 없음")
