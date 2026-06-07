# 모집(가챠) 풀 데이터
# 등급: 1급(무지개) 2급(황금) 3급(은) 4급(구리) 5급(나무)
# 확률: 1급 1% / 2급 4% / 3급 10% / 4급 30% / 5급 55%
# 풀 인원: 1급 3 / 2급 5 / 3급 10 / 4급 10 / 5급 10

# 등급 메타
GRADE_INFO = {
    1: {"name": "1급", "color": (190, 120, 230), "rate": 0.01,  # 무지개(대표색)
        "dup_contact": 1000, "exchange_cost": 1000, "rainbow": True},
    2: {"name": "2급", "color": (235, 200,  70), "rate": 0.04,  # 황금
        "dup_contact": 500,  "exchange_cost": 500},
    3: {"name": "3급", "color": (200, 200, 210), "rate": 0.10,  # 은
        "dup_contact": 100,  "exchange_cost": 100},
    4: {"name": "4급", "color": (200, 130,  80), "rate": 0.30,  # 구리
        "dup_contact": 25,   "exchange_cost": None},  # 교환 불가
    5: {"name": "5급", "color": (150, 180, 130), "rate": 0.55,  # 나무
        "dup_contact": 10,   "exchange_cost": None},  # 교환 불가
}

GRADE_ORDER = [1, 2, 3, 4, 5]

# 풀 인원수
_POOL_COUNT = {1: 3, 2: 5, 3: 10, 4: 10, 5: 10}


# 등급별 임시 전투 스탯 템플릿 (방향 B 본격화 전까지 사용)
# 추후 캐릭터별 고유 데이터로 교체 예정
_GRADE_STATS = {
    1: {"hp": 3500, "mp": 2000, "spd": 22, "phys": 90, "mag": 90, "pow": 120},
    2: {"hp": 2800, "mp": 1600, "spd": 18, "phys": 75, "mag": 75, "pow": 90},
    3: {"hp": 2000, "mp": 1200, "spd": 15, "phys": 60, "mag": 60, "pow": 70},
    4: {"hp": 1400, "mp": 900,  "spd": 12, "phys": 45, "mag": 45, "pow": 55},
    5: {"hp": 900,  "mp": 600,  "spd": 10, "phys": 30, "mag": 30, "pow": 40},
}


def _grade_skills(grade):
    """등급별 임시 스킬셋 (캐릭터별 고유 데이터 전까지 공용)."""
    s = _GRADE_STATS[grade]
    p = s["pow"]
    return [
        {"name": "베기", "power": p, "type": "물리", "side": "적", "count": "단일",
         "hits": 1, "tags": [], "motion": "behind", "sprite": "",
         "desc": ["적에게 물리 피해를 입힌다."]},
        {"name": "마탄", "power": int(p * 0.9), "type": "마법", "side": "적", "count": "단일",
         "hits": 1, "tags": [], "motion": "cast", "sprite": "",
         "desc": ["적에게 마법 피해를 입힌다."]},
        {"name": "연격", "power": int(p * 0.4), "type": "물리", "side": "적", "count": "단일",
         "hits": 3, "tags": [], "motion": "behind", "sprite": "",
         "desc": ["적을 3회 연속 공격한다."]},
    ]


def _make_pool():
    """등급별 더미 동료 생성. 등급별 임시 전투 데이터 포함."""
    pool = {}
    for grade, cnt in _POOL_COUNT.items():
        gname = GRADE_INFO[grade]["name"]
        st = _GRADE_STATS[grade]
        # 등급별 고정 레벨 (1급이 가장 높음)
        lvl = {1: 80, 2: 65, 3: 50, 4: 35, 5: 20}[grade]
        for i in range(1, cnt + 1):
            key = f"{gname}-{i:02d}"   # 예: "1급-01"
            pool[key] = {
                "name":          key,
                "grade":         grade,
                "type":          "ally",
                "level":         lvl,
                "phys_level":    st["phys"],
                "magic_level":   st["mag"],
                "hp_max":        st["hp"],
                "mp_max":        st["mp"],
                "speed":         st["spd"],
                "sprite":        "",   # 추후 이미지 경로 지정
                "profile":       "",
                "sprite_scale":  0.25,
                "click_w_ratio": 0.2,
                "defense_skills": ["방어", "회피", "원호"],
                "passives":      [],
                "skills":        _grade_skills(grade),
                "overview": [key, "", f"{gname} 모집 동료입니다.", "(임시 데이터)"],
            }
    return pool


RECRUIT_POOL = _make_pool()


def grade_of(name):
    return RECRUIT_POOL.get(name, {}).get("grade", 5)


def names_by_grade(grade):
    return [k for k, v in RECRUIT_POOL.items() if v["grade"] == grade]