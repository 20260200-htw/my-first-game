# 로그라이크 회차(런) 데이터
# 지역 / 노드 구성 / 적 풀 / 보스 / 아이템 / 스킬 풀 / 경험치 테이블
# 적은 기존 ENEMY_DEFS 를 재활용한다.

import random

# ══════════════════════════════════════════════════════════════════
#   구간(지역)
# ══════════════════════════════════════════════════════════════════
# 5개 지역. 1~5구간에서 직전 지역 제외하고 선택. 6구간은 마왕성 고정.
REGIONS = ["중앙", "동부", "서부", "남부", "북부"]

REGION_INFO = {
    "중앙": {"title": "중앙 평원", "desc": "왕국 중심부의 너른 평원."},
    "동부": {"title": "동부 해안", "desc": "거친 파도가 몰아치는 해안 지대."},
    "서부": {"title": "서부 산악", "desc": "험준한 봉우리가 이어진 산맥."},
    "남부": {"title": "남부 사막", "desc": "끝없는 모래바람의 사막."},
    "북부": {"title": "북부 설원", "desc": "혹한이 지배하는 설원."},
}

# 구간 번호(1~5) → 노드 개수
SEGMENT_NODE_COUNT = {1: 6, 2: 7, 3: 8, 4: 9, 5: 10}
FINAL_SEGMENT = 6  # 마왕성

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

# 일반 노드 비율 (보스 전 마지막은 상점 확정으로 별도 처리)
NODE_WEIGHTS = [
    (NODE_BATTLE, 50),
    (NODE_EVENT,  30),
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
#   지역별 적 풀 (기존 ENEMY_DEFS 이름 사용)
# ══════════════════════════════════════════════════════════════════
# 각 항목은 한 전투의 적 구성 (1웨이브). 추후 웨이브/적 추가 가능.
REGION_ENEMIES = {
    "중앙": {
        "battle": [["말단병사"], ["말단병사", "말단병사"], ["Eat_slime1"]],
        "elite":  [["벨라"], ["말단병사", "말단병사", "말단병사"]],
        "boss":   {"enemies": ["벨라"], "name": "평원의 지배자 벨라"},
    },
    "동부": {
        "battle": [["Eat_slime1"], ["Eat_slime1", "Eat_slime2"], ["말단병사"]],
        "elite":  [["Eat_slime1", "Eat_slime2", "Eat_slime3"]],
        "boss":   {"enemies": ["마리나"], "name": "해안의 검객 마리나"},
    },
    "서부": {
        "battle": [["말단병사"], ["Eat_slime2"], ["말단병사", "Eat_slime1"]],
        "elite":  [["말단병사", "말단병사", "말단병사"]],
        "boss":   {"enemies": ["마리 따까리1", "마리 따까리2"], "name": "산적단 두목"},
    },
    "남부": {
        "battle": [["Eat_slime3"], ["말단병사", "말단병사"], ["Eat_slime1", "Eat_slime2"]],
        "elite":  [["벨라"]],
        "boss":   {"enemies": ["벨라"], "name": "사막의 폭군"},
    },
    "북부": {
        "battle": [["Eat_slime1"], ["말단병사"], ["Eat_slime2", "Eat_slime3"]],
        "elite":  [["말단병사", "말단병사", "말단병사"]],
        "boss":   {"enemies": ["마리나"], "name": "설원의 추격자"},
    },
}

# 마왕성 4갈래 보스 + 최종 마왕
MAW_BOSSES = [
    {"enemies": ["벨라"],   "name": "마왕군 사천왕 · 벨라"},
    {"enemies": ["마리나"], "name": "마왕군 사천왕 · 마리나"},
    {"enemies": ["보스 마리"], "name": "마왕군 사천왕 · 마리"},
    {"enemies": ["마리 따까리1", "마리 따까리2"], "name": "마왕군 사천왕 · 쌍둥이"},
]
MAW_FINAL = {"enemies": ["보스 마리"], "name": "마왕"}


def pick_enemy_group(region, kind):
    """지역의 battle/elite 구성 중 하나를 랜덤 선택."""
    pools = REGION_ENEMIES.get(region, REGION_ENEMIES["중앙"])
    groups = pools.get(kind, pools["battle"])
    return list(random.choice(groups))


def region_boss(region):
    return REGION_ENEMIES.get(region, REGION_ENEMIES["중앙"])["boss"]


def enemy_formation_for(n):
    return {1: "솔로", 2: "듀오", 3: "트리오", 4: "스쿼드", 5: "풀파티"}.get(max(1, min(5, n)), "솔로")


# ══════════════════════════════════════════════════════════════════
#   경험치 / 레벨
# ══════════════════════════════════════════════════════════════════
# 노드 종류별 획득 경험치
EXP_REWARD = {
    NODE_BATTLE: 20,
    NODE_ELITE:  50,
    NODE_EVENT:  10,
    NODE_REWARD: 0,
    NODE_BOSS:   100,
    NODE_MAW:    300,
}

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
def _skill(name, power, stype, count="단일", hits=1, motion="behind", desc=None):
    return {
        "name": name, "power": power, "type": stype, "side": "적",
        "count": count, "hits": hits, "tags": [], "motion": motion,
        "sprite": "", "desc": desc or [f"{stype} 공격."],
    }

# 시작 시 보유 스킬 (물리1 + 마법1)
STARTER_SKILLS = [
    _skill("베기",   30, "물리", motion="behind", desc=["기본적인 물리 공격."]),
    _skill("마탄",   28, "마법", motion="cast",   desc=["기본적인 마법 공격."]),
]

# 보상으로 획득 가능한 스킬 풀
SKILL_POOL = [
    _skill("강타",     55, "물리", desc=["강한 일격을 가한다."]),
    _skill("연속 베기", 22, "물리", hits=3, desc=["3회 연속 공격한다."]),
    _skill("관통",     45, "물리", desc=["방어를 무시하는 일격."]),
    _skill("화염탄",   50, "마법", motion="cast", desc=["불꽃으로 적을 태운다."]),
    _skill("빙결",     40, "마법", motion="cast", desc=["냉기로 적을 얼린다."]),
    _skill("뇌격",     48, "마법", motion="cast", desc=["번개로 적을 친다."]),
    _skill("난무",     18, "물리", hits=4, desc=["4회 연속 난타."]),
    _skill("일섬",     70, "물리", desc=["혼신의 일격."]),
    _skill("폭렬 마법", 65, "마법", motion="cast", desc=["강력한 폭발 마법."]),
    _skill("연환 마탄", 20, "마법", hits=3, motion="cast", desc=["마탄을 3회 발사."]),
]

def roll_skill_choices(n=3, owned_names=None):
    """보상용 스킬 후보 n개 추첨 (중복 이름 제외 가능)."""
    owned_names = owned_names or []
    pool = [s for s in SKILL_POOL]
    random.shuffle(pool)
    return pool[:n]


# ══════════════════════════════════════════════════════════════════
#   아이템(유물) 10종 — 패시브 효과
# ══════════════════════════════════════════════════════════════════
# effect 는 전투/정산에서 해석할 키. 수치는 value.
ITEMS = {
    "낡은 검":      {"name": "낡은 검",      "effect": "atk_pct",     "value": 10, "desc": "가하는 피해 +10%"},
    "강철 갑옷":    {"name": "강철 갑옷",    "effect": "def_pct",     "value": 10, "desc": "받는 피해 -10%"},
    "생명의 부적":  {"name": "생명의 부적",  "effect": "hp_flat",     "value": 200, "desc": "최대 체력 +200"},
    "재생의 반지":  {"name": "재생의 반지",  "effect": "regen_pct",   "value": 5,  "desc": "턴 시작 시 체력 5% 회복"},
    "신속의 장화":  {"name": "신속의 장화",  "effect": "spd_flat",    "value": 5,  "desc": "속도 +5"},
    "광전사의 인장":{"name": "광전사의 인장","effect": "lowhp_atk",   "value": 30, "desc": "체력 50% 이하일 때 가하는 피해 +30%"},
    "현자의 돌":    {"name": "현자의 돌",    "effect": "exp_pct",     "value": 25, "desc": "획득 경험치 +25%"},
    "황금 주머니":  {"name": "황금 주머니",  "effect": "gold_pct",    "value": 30, "desc": "획득 골드 +30%"},
    "흡혈의 송곳니":{"name": "흡혈의 송곳니","effect": "lifesteal",   "value": 10, "desc": "가한 피해의 10%만큼 회복"},
    "불사의 깃털":  {"name": "불사의 깃털",  "effect": "revive",      "value": 1,  "desc": "전투당 1회, 치명상 시 체력 1로 생존"},
}

# 구간 보스별 특별 아이템 (보스 이름 → 아이템 키)
BOSS_DROP = {
    "평원의 지배자 벨라": "낡은 검",
    "해안의 검객 마리나": "신속의 장화",
    "산적단 두목":       "황금 주머니",
    "사막의 폭군":       "광전사의 인장",
    "설원의 추격자":     "강철 갑옷",
}

def roll_item_choices(n=3, owned_keys=None):
    """보상용 아이템 후보 n개 추첨 (이미 보유한 것 제외)."""
    owned_keys = owned_keys or []
    pool = [k for k in ITEMS.keys() if k not in owned_keys]
    random.shuffle(pool)
    return pool[:n]


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
