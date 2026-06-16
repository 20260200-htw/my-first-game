# 로그라이크 회차(런) 데이터
# 지역 / 노드 구성 / 적 풀 / 보스 / 아이템 / 스킬 풀 / 경험치 테이블
# 적은 기존 ENEMY_DEFS 를 재활용한다.

import random

# ══════════════════════════════════════════════════════════════════
#   구간(지역)
# ══════════════════════════════════════════════════════════════════
# 일반 모드: 5개 지역을 모두 1번씩 방문하는 고정 경로 (순서만 플레이어 선택).
#   1구간=중앙(고정) → 2구간=동서남북 중 택1 → 3구간=남은 것 중 택1
#   → 4구간=남은 것 중 택1 → 5구간=마지막 남은 지역(자동) → 그 지역 보스 클리어 시 회차 종료.
# 같은 회차 안에서 지역 재방문 없음. 마왕성은 일반 모드에 없음(보스 모드로 분리).
REGIONS = ["중앙", "동부", "서부", "남부", "북부"]
MIDDLE_REGIONS = ["동부", "서부", "남부", "북부"]   # 중앙 제외, 순서 선택 대상

REGION_INFO = {
    "중앙": {
        "title": "중앙 구역",
        "desc": "왕국이 위치한 비교적 안전한 구역",
        "image": "assets/regions/center.png"
    },
    "동부": {
        "title": "동부 구역",
        "desc": "산과 숲으로 이루어진 구역",
        "image": "assets/regions/east.png"
    },
    "서부": {
        "title": "서부 구역",
        "desc": "넓은 평야로 이루어진 구역",
        "image": "assets/regions/west.png"
    },
    "남부": {
        "title": "남부 구역",
        "desc": "섬으로 이루어진 고위험 구역",
        "image": "assets/regions/south.png"
    },
    "북부": {
        "title": "북부 구역",
        "desc": "모든 것이 얼어붙은 고위험 구역",
        "image": "assets/regions/north.png"
    },
}

# 구역별 맵 배경 이미지. assets/backgrounds/ 안의 파일명.
# 파일이 없으면 흰 배경으로 자동 폴백되므로, 원하는 구역만 채워 넣으면 된다.
REGION_BACKGROUNDS = {
    "중앙": "center.png",
    "동부": "east.png",
    "서부": "west.png",
    "남부": "south.png",
    "북부": "north.png",
}

def region_background_path(region):
    """구역 배경 이미지의 전체 경로 (없으면 None)."""
    import os
    fn = REGION_BACKGROUNDS.get(region)
    if not fn:
        return None
    path = os.path.join("assets", "backgrounds", fn)
    return path if os.path.exists(path) else None

# 구역별 노드 선택(맵) 화면 OST. assets/bgm/ 안의 파일명.
# 파일이 없으면 공통 map.wav(SCREEN_BGM["map"])로 자동 폴백된다.
REGION_BGM = {
    "중앙": "map_center.mp3",
    "동부": "map_east.mp3",
    "서부": "map_west.mp3",
    "남부": "map_south.mp3",
    "북부": "map_north.mp3",
}

def region_bgm_path(region):
    """구역별 맵 OST의 전체 경로 (없으면 None → 공통 BGM 사용)."""
    import os
    fn = REGION_BGM.get(region)
    if not fn:
        return None
    path = os.path.join("assets", "bgm", fn)
    return path if os.path.exists(path) else None

# 스킬에 sound 가 지정되지 않았거나 파일이 없을 때 대신 재생할 공용 효과음.
# assets/sfx/ 안의 파일을 두면 적용된다 (없으면 무음 — 에러 없음).
DEFAULT_SKILL_SOUND = "assets/sfx/hit_default.wav"

# 모든 구간: 시작 + 3노드 + 중간 + 3노드 + 보스 (좌우 직진 레인)
SEGMENT_MID_NODES = 3      # 시작~중간, 중간~보스 사이 각 노드 수
FINAL_SEGMENT = 5          # 일반 모드 마지막 구간(5구간 보스 클리어 시 회차 종료)
FIRST_REGION = "중앙"      # 첫 구간 고정 지역

# ══════════════════════════════════════════════════════════════════
#   보스 모드 (일반 모드와 별개, 보스전만 진행)
#   tier: challenge(도전) → extreme(극한) → final(최종)
#   enemies 가 None 이면 '미구현(없음)' 슬롯.
# ══════════════════════════════════════════════════════════════════
CHALLENGE_BOSSES = {
    "중앙": None,
    "동부": {"enemies": ["현호"],   "name": "동부의 도전자 · 현호"},
    "서부": None,
    "남부": {"enemies": ["마리나"], "name": "남부의 도전자 · 마리나"},
    "북부": None,
}
EXTREME_BOSSES = {
    "중앙": None,
    "동부": {"enemies": ["orochi", "orochi_head", "orochi_head"], "name": "야마타노오로치"},
    "서부": None,
    "남부": None,
    "북부": None,
}
FINAL_BOSS = {"마왕": None}   # 최종보스(마왕) — 미구현

# 보스 모드 지역 표시 순서
BOSS_REGION_ORDER = ["중앙", "동부", "서부", "남부", "북부"]

# ══════════════════════════════════════════════════════════════════
#   노드 타입
# ══════════════════════════════════════════════════════════════════
NODE_BATTLE = "battle"
NODE_ELITE  = "elite"
NODE_EVENT  = "event"
NODE_REWARD = "reward"
NODE_SHOP   = "shop"
NODE_BOSS   = "boss"
NODE_MAW    = "maw"     # 최종 마왕
NODE_START  = "start"   # 시작 지점 (다이얼로그)
NODE_MID    = "mid"     # 중간 지점 (다이얼로그, 중간보스 가능)

# 일반 노드 비율 (보스 전 마지막은 상점 확정으로 별도 처리)
NODE_WEIGHTS = [
    (NODE_BATTLE, 70),
    (NODE_EVENT,  10),
    (NODE_ELITE,  10),
    (NODE_REWARD, 10),
]

def roll_node_type():
    total = sum(w for _, w in NODE_WEIGHTS)
    r = random.uniform(0, total)
    acc = 0
    for t, w in NODE_WEIGHTS:
        acc += w
        if r <= acc:
            return t
    return NODE_BATTLE


# ══════════════════════════════════════════════════════════════════
#   적/사건/보상 배치 → data/encounter_data.py 로 이동
# ══════════════════════════════════════════════════════════════════
# 구역×회차별 전투/엘리트/사건/보상/중간보스/보스 배치는 전부
# data/encounter_data.py 의 REGION_PLAN / MAW_PLAN 에서 관리한다.


def enemy_formation_for(n):
    return {1: "솔로", 2: "듀오", 3: "트리오", 4: "스쿼드", 5: "풀파티"}.get(max(1, min(5, n)), "솔로")


# ══════════════════════════════════════════════════════════════════
#   경험치 / 레벨
# ══════════════════════════════════════════════════════════════════
# 노드 종류별 획득 경험치 (현재 미사용 — 전투 승리는 LEVEL_REWARD 로 레벨을 직접 올림)
EXP_REWARD = {
    NODE_BATTLE: 20,
    NODE_ELITE:  50,
    NODE_EVENT:  10,
    NODE_REWARD: 0,
    NODE_BOSS:   100,
    NODE_MAW:    300,
}

# 전투 승리 시 직접 오르는 레벨 수 (경험치 대신)
LEVEL_REWARD = {
    NODE_BATTLE: 1,    # 일반 전투 +1
    NODE_ELITE:  3,    # 엘리트 전투 +2
    NODE_BOSS:   5,    # 보스 전투 +5
    NODE_MAW:    5,    # 최종 마왕 (클리어 직전이라 사실상 무의미)
}

# 주인공 최대 레벨 (이 이상 오르지 않음)
LEVEL_CAP = 70

# 골드 보상
GOLD_REWARD = {
    NODE_BATTLE: 25,
    NODE_ELITE:  60,
    NODE_EVENT:  15,
    NODE_REWARD: 40,
    NODE_BOSS:   120,
    NODE_MAW:    0,
}

# 레벨업 필요 경험치: level N → N+1 에 필요한 양
def exp_to_next(level):
    return 50 + (level - 1) * 30

# 레벨업 시 획득 포인트
LEVELUP_BASIC_POINT = 1   # 물리/마법 각각? → 기초 포인트 (물리+마법 합쳐 분배)
LEVELUP_EXTRA_POINT = 3   # 부가 능력치 포인트


# ══════════════════════════════════════════════════════════════════
#   시작 스킬 + 스킬 풀 (보상으로 획득)
# ══════════════════════════════════════════════════════════════════
def _skill(name, power, stype, count="단일", hits=1, motion="behind",
           side="적", tags=None, desc=None):
    return {
        "name": name, "power": power, "type": stype, "side": side,
        "count": count, "hits": hits, "tags": list(tags or []), "motion": motion,
        "sprite": "", "desc": desc or [f"{stype} 공격."],
    }

# 시작 시 보유 스킬 (물리1 + 마법1)
STARTER_SKILLS = [
    _skill("때리기",   5, "물리", motion="stationary", desc=["기본적인 물리 공격."]),
    _skill("마탄",   5, "마법", motion="cast",   desc=["기본적인 마법 공격."]),
]

# 보상/상점으로 획득 가능한 스킬 풀
# 유형: 단일 강공 / 다단히트 / 광역(2~5인) / 필중 / 회복(아군)
SKILL_POOL = [
    # ── 단일 물리 ──
    _skill("강타",       55, "물리", desc=["강한 일격을 가한다."]),
    _skill("관통",       45, "물리", tags=["필중"], desc=["반드시 적중하는 일격."]),
    _skill("일섬",       72, "물리", desc=["혼신의 단일 일격."]),
    _skill("처형",       90, "물리", desc=["막대한 피해를 주는 강공."]),
    # ── 다단 물리 ──
    _skill("연속 베기",   22, "물리", hits=3, desc=["3회 연속 공격한다."]),
    _skill("난무",       16, "물리", hits=4, desc=["4회 연속 난타."]),
    _skill("폭풍 검무",   13, "물리", hits=5, desc=["5회 연속 휘몰아친다."]),
    # ── 광역 물리 ──
    _skill("회전 베기",   34, "물리", count="2인", desc=["적 2명을 동시에 벤다."]),
    _skill("대지 가르기", 30, "물리", count="5인", desc=["적 전체를 강타한다."]),
    # ── 단일 마법 ──
    _skill("화염탄",     50, "마법", motion="cast", desc=["불꽃으로 적을 태운다."]),
    _skill("빙결",       42, "마법", motion="cast", tags=["필중"], desc=["반드시 적중하는 냉기."]),
    _skill("뇌격",       48, "마법", motion="cast", desc=["번개로 적을 친다."]),
    _skill("폭렬 마법",   68, "마법", motion="cast", desc=["강력한 폭발 마법."]),
    _skill("운석 낙하",   95, "마법", motion="cast", desc=["거대한 운석을 떨군다."]),
    # ── 다단 마법 ──
    _skill("연환 마탄",   18, "마법", hits=3, motion="cast", desc=["마탄을 3회 발사."]),
    _skill("마력 폭주",   14, "마법", hits=5, motion="cast", desc=["마력탄을 5회 난사."]),
    # ── 광역 마법 ──
    _skill("화염 폭풍",   30, "마법", count="5인", motion="cast", desc=["적 전체를 불태운다."]),
    _skill("빙하 시대",   26, "마법", count="5인", motion="cast", tags=["필중"], desc=["적 전체를 얼린다."]),
    # ── 회복(자신) ──
    _skill("재생",       40, "마법", side="자신", count="단일", motion="cast",
           tags=["회복", "지원"], desc=["자신의 체력을 회복한다."]),
    _skill("대치유",     70, "마법", side="자신", count="단일", motion="cast",
           tags=["회복", "지원"], desc=["자신의 체력을 크게 회복한다."]),
]

def roll_skill_choices(n=3, owned_names=None):
    """보상용 스킬 후보 n개 추첨 (이미 보유한 이름 제외).
    스킬이 영구 보존되므로 중복 획득을 막는다. 남은 게 없으면 빈 목록."""
    owned_names = set(owned_names or [])
    pool = [s for s in SKILL_POOL if s["name"] not in owned_names]
    random.shuffle(pool)
    return pool[:n]


def skill_by_name(name):
    """스킬 풀(+시작 스킬)에서 이름으로 스킬 정의 사본을 찾는다. 없으면 None."""
    import copy
    for s in SKILL_POOL + STARTER_SKILLS:
        if s["name"] == name:
            return copy.deepcopy(s)
    return None


# ══════════════════════════════════════════════════════════════════
#   아이템(유물) 10종 — 패시브 효과
# ══════════════════════════════════════════════════════════════════
# effect 는 전투/정산에서 해석할 키. 수치는 value.
ITEMS = {
    "낡은 검":      {"name": "낡은 검",      "effect": "atk_pct",     "value": 10, "desc": "가하는 피해 +10%"},
    "강철 갑옷":    {"name": "강철 갑옷",    "effect": "def_pct",     "value": 10, "desc": "받는 피해 -10%"},
    "생명의 부적":  {"name": "생명의 부적",  "effect": "hp_flat",     "value": 200, "desc": "최대 체력 +200"},
    "신속의 장화":  {"name": "신속의 장화",  "effect": "spd_flat",    "value": 5,  "desc": "속도 +5"},
}

# 구간 보스의 확정 드랍은 encounter_data 의 boss 정의 안 "drop" 키로 지정한다.

# ══════════════════════════════════════════════════════════════════
#   아이템 시너지: 세트의 모든 아이템을 '장착'하면 추가 효과가 발동
#   items: 필요한 아이템 키 목록 (전부 장착 시 완성)
#   bonus_effects: 추가로 합산되는 효과 [{effect, value}, ...] (ITEMS 와 같은 effect 체계)
#   desc: 시너지 설명
# ══════════════════════════════════════════════════════════════════
SYNERGIES = {
}


def active_synergies(equipped_keys):
    """장착 아이템으로 완성된 시너지 이름 목록."""
    eq = set(equipped_keys)
    out = []
    for name, syn in SYNERGIES.items():
        if all(k in eq for k in syn["items"]):
            out.append(name)
    return out


def _synergy_bonus_effects(equipped_keys):
    """완성된 시너지들의 추가 효과를 effect→value 합계로."""
    totals = {}
    for name in active_synergies(equipped_keys):
        for be in SYNERGIES[name]["bonus_effects"]:
            totals[be["effect"]] = totals.get(be["effect"], 0) + be["value"]
    return totals


def item_effect_value(equipped_keys, effect):
    """장착 아이템 + 완성 시너지의 특정 effect 값 합계."""
    total = sum(ITEMS[k]["value"] for k in equipped_keys
                if k in ITEMS and ITEMS[k]["effect"] == effect)
    total += _synergy_bonus_effects(equipped_keys).get(effect, 0)
    return total


def roll_item_choices(n=3, owned_keys=None):
    """보상용 아이템 후보 n개 추첨 (이미 보유한 것 제외)."""
    owned_keys = owned_keys or []
    pool = [k for k in ITEMS.keys() if k not in owned_keys]
    random.shuffle(pool)
    return pool[:n]


def items_to_passives(item_keys):
    """보유 아이템들을 전투용 패시브(effects) 한 덩어리로 변환.
    combatant 의 _iter_effects 가 읽는 형식.
    전투에서 직접 반영되는 효과만 변환 (hp_flat/exp/gold 는 별도 처리)."""
    effects = []
    descs = []
    # 합산용
    atk_pct = 0
    def_pct = 0
    lowhp_atk = 0
    lifesteal = 0
    regen = 0
    revive = 0
    for k in item_keys:
        it = ITEMS.get(k)
        if not it:
            continue
        eff, val = it["effect"], it["value"]
        if eff == "atk_pct":
            atk_pct += val
        elif eff == "def_pct":
            def_pct += val
        elif eff == "lowhp_atk":
            lowhp_atk += val
        elif eff == "lifesteal":
            lifesteal += val
        elif eff == "regen_pct":
            regen += val
        elif eff == "revive":
            revive += val
    # 완성된 시너지의 추가 효과 합산
    syn = _synergy_bonus_effects(item_keys)
    atk_pct   += syn.get("atk_pct", 0)
    def_pct   += syn.get("def_pct", 0)
    lowhp_atk += syn.get("lowhp_atk", 0)
    lifesteal += syn.get("lifesteal", 0)
    regen     += syn.get("regen_pct", 0)
    revive    += syn.get("revive", 0)
    for sname in active_synergies(item_keys):
        descs.append(f"[시너지] {SYNERGIES[sname]['desc']}")
    if atk_pct:
        effects.append({"kind": "deal_mult", "value": 1 + atk_pct / 100.0})
        descs.append(f"가하는 피해 +{atk_pct}%")
    if def_pct:
        effects.append({"kind": "take_mult", "value": 1 - def_pct / 100.0})
        descs.append(f"받는 피해 -{def_pct}%")
    if lowhp_atk:
        # 자신 체력 50% 이하일 때 주는 피해 증가
        effects.append({"kind": "deal_mult", "value": 1 + lowhp_atk / 100.0,
                        "if_self_hp_ratio_below": 0.5})
        descs.append(f"체력 50%↓ 시 가하는 피해 +{lowhp_atk}%")
    meta = {"lifesteal": lifesteal, "regen": regen, "revive": revive}
    return effects, descs, meta


# ══════════════════════════════════════════════════════════════════
#   상점 가격
# ══════════════════════════════════════════════════════════════════
SHOP_PRICE = {
    "skill": 60,    # 스킬 1개
    "item":  80,    # 아이템 1개
    "heal":  40,    # 체력 30% 회복
}
SHOP_HEAL_PCT = 30


# ══════════════════════════════════════════════════════════════════
#   합류 동료 풀 (이벤트로 합류, 회차 한정)
# ══════════════════════════════════════════════════════════════════
# 기존 ALLY_DEFS 의 스토리 동료를 합류 동료로 재활용
JOINABLE_ALLIES = ["금강", "아우렐리우스", "마리", "막심 오그네프"]


# ══════════════════════════════════════════════════════════════════
#   구간 다이얼로그 (구역 × 지점 × 방문횟수)
# ══════════════════════════════════════════════════════════════════
# 지점: "start"(시작) / "mid"(중간) / "boss"(보스)
# 방문횟수: 1회차, 2회차... (현재 회차에서 그 구역을 몇 번째 방문하는지)
# 형식: story_dialogue 의 cuts 형식 (background/characters/speaker/text...)
# 내용은 임시. 나중에 교체.

def _cut(speaker, text, affiliation="", sprite=None, x=0.5, y=1.0, scale=0.75, bg=""):
    cut = {"characters": [], "background": bg,
           "affiliation": affiliation, "speaker": speaker, "text": text}
    if sprite:
        cut["characters"] = [{"sprite": sprite, "x": x, "y": y, "scale": scale}]
    return cut


def _placeholder_dialogue(region, spot, visit):
    """임시 다이얼로그 한 컷. 구역/지점/방문횟수를 명시."""
    spot_name = {"start": "시작 지점", "mid": "중간 지점", "boss": "보스 지점"}[spot]
    title = REGION_INFO.get(region, {}).get("title", region)
    return [
        _cut("주인공", f"({title} — {spot_name} / {visit}회차 방문)"),
        _cut("주인공", "(여기에 대사가 들어갈 예정입니다.)"),
    ]


# 구역별 커스텀 다이얼로그를 여기에 채운다.
# REGION_DIALOGUE[region][spot][visit] = cuts
# 없으면 _placeholder_dialogue 로 대체된다.
REGION_DIALOGUE = {
    # 예시 자리 (실제 내용은 추후):
    # "중앙": {
    #     "start": {1: [ _cut("주인공", "중앙 평원에 도착했다.") ]},
    #     "mid":   {1: [...]},
    #     "boss":  {1: [...]},
    # },
}

# 마왕성 다이얼로그
MAW_DIALOGUE = {
    "start": [_cut("주인공", "(마왕성 — 시작 지점)"), _cut("주인공", "(드디어 마왕성에 들어섰다.)")],
    "mid":   [_cut("주인공", "(마왕성 — 중간 지점)")],
    # 보스/마왕 직전 대사는 보스 노드에서
}


def dialogue_for(region, spot, visit):
    """구역/지점/방문횟수에 맞는 다이얼로그 cuts 반환."""
    if region == "마왕성":
        return MAW_DIALOGUE.get(spot, _placeholder_dialogue(region, spot, visit))
    reg = REGION_DIALOGUE.get(region, {})
    spot_map = reg.get(spot, {})
    # 해당 방문횟수 없으면 가장 가까운 낮은 회차, 그것도 없으면 임시
    if visit in spot_map:
        return spot_map[visit]
    avail = sorted(k for k in spot_map.keys() if k <= visit)
    if avail:
        return spot_map[avail[-1]]
    return _placeholder_dialogue(region, spot, visit)


# ══════════════════════════════════════════════════════════════════
#   중간 지점 중간보스 → encounter_data 의 "mid_boss" 키로 이동
# ══════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════
#   보스 모드 헬퍼
# ══════════════════════════════════════════════════════════════════
def challenge_boss(region):
    """도전보스 정의 (없으면 None=미구현)."""
    return CHALLENGE_BOSSES.get(region)

def extreme_boss(region):
    """극한보스 정의 (없으면 None=미구현)."""
    return EXTREME_BOSSES.get(region)

def boss_tier_defs(tier):
    """tier별 {지역: 보스def or None} 매핑."""
    if tier == "challenge":
        return CHALLENGE_BOSSES
    if tier == "extreme":
        return EXTREME_BOSSES
    if tier == "final":
        return FINAL_BOSS
    return {}

def implemented_bosses(tier):
    """해당 tier에서 실제 구현된(=None이 아닌) 지역 목록."""
    return [r for r, b in boss_tier_defs(tier).items() if b is not None]