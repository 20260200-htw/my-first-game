# ══════════════════════════════════════════════════════════════════
#   전투 프리셋
# ══════════════════════════════════════════════════════════════════

# 아군 배치 유형 (dx, dy) - 1번(주인공)이 기준점
# dx: 앞뒤 (음수=앞, 양수=뒤), dy: 상하 (음수=위, 양수=아래)
ALLY_FORMATIONS = {
    "솔로":   [(0, 0)],
    "듀오":   [(0, 2), (0, -2)],
    "트리오": [(0, 0), (2, 2), (2, -2)],
    "스쿼드": [(0, 1), (0,  -1), (2, 1), (2, -1)],
    "풀파티": [(0, 0), (1,  0), (1, -1), (2, -1), (2,  1)],
}

# 적 배치 유형 (dx, dy) - 1번이 기준점
ENEMY_FORMATIONS = {
    "솔로":         [(0, 0)],
    "듀오":         [(0, 0), (1,  0)],
    "트리오":       [(0, 0), (1, -1), (1,  1)],
    #   5
    # 2
    #   4
    # 1
    #   3
    "더블캐리":     [(0, 0.5), (0, -0.5), (2,  1), (3,  0), (2, -1)],
    # 5
    # 4
    #       1 (보스 뒤)
    # 3
    # 2
    "솔캐리_후방":  [(2, 0), (0, -2), (0, -1), (0,  1), (0,  2)],
    #    5
    #    4
    # 1     (보스 앞)
    #    3
    #    2
    "솔캐리_전방":  [(0, 0), (2, 2), (2, 1), (2,  -1), (2,  -2)],
    "보스_마리":  [(2, 0), (0, -2), (0, 2), (3,  -3), (3,  3)],
    "오로치":  [(4, 0), (0, 0), (2, -4), (2, 4), (-2,  -5), (-2,  5), (8,  -4), (8,  4)],
}

# 테스트용 캐릭터
_Hyeonho = ["현호"]
_ALLIES_1 = ["주인공"]
snowdin = ["snowdin_wild_boar_king"]
SS = ["small_sky"]
dosa = ["dosa"]
kirin = ["kirin"]
shark = ["shark"]
orochi = ["orochi", "orochi_head", "orochi_head", "orochi_head", "orochi_head", "orochi_head", "orochi_head", "orochi_head"]

BATTLE_PRESETS = {
    "설산 멧돼지 왕": {
        "title": "[설산 멧돼지 왕]",
        "enemies": snowdin,
        "allies":  _ALLIES_1,
        "enemy_formation": "솔캐리_전방",
        "ally_formation":  "솔로",
        "gap": 0.3,
    },
    "소천": {
        "title": "[소천]",
        "enemies": SS,
        "allies":  _ALLIES_1,
        "enemy_formation": "솔캐리_전방",
        "ally_formation":  "솔로",
        "gap": 0.3,
    },
    "도사": {
        "title": "[도사]",
        "enemies": dosa,
        "allies":  _ALLIES_1,
        "enemy_formation": "솔캐리_전방",
        "ally_formation":  "솔로",
        "gap": 0.3,
    },
    "기린": {
        "title": "[기린]",
        "enemies": kirin,
        "allies":  _ALLIES_1,
        "enemy_formation": "솔로",
        "ally_formation":  "솔로",
        "gap": 0.3,
    },
    "오로치": {
        "title": "[오로치]",
        "enemies": orochi,
        "allies":  _ALLIES_1,
        "enemy_formation": "오로치",
        "ally_formation":  "솔로",
        "gap": 0.3,
    },
    "솔로_vs_현호": {
        "title": "[솔로 vs 현호]",
        "enemies": _Hyeonho,
        "allies":  _ALLIES_1,
        "enemy_formation": "솔로",
        "ally_formation":  "솔로",
        "gap": 0.3,
    },
}