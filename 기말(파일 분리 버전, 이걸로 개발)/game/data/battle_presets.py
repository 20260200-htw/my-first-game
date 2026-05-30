# ══════════════════════════════════════════════════════════════════
#   전투 프리셋
# ══════════════════════════════════════════════════════════════════

# 아군 배치 유형 (dx, dy) - 1번(주인공)이 기준점
# dx: 앞뒤 (음수=앞, 양수=뒤), dy: 상하 (음수=위, 양수=아래)
ALLY_FORMATIONS = {
    "솔로":   [(0, 0)],
    "듀오":   [(0, 1), (0, -1)],
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
}

# 테스트용 캐릭터
_ENEMIES = ["벨라", "말단병사", "말단병사", "말단병사", "말단병사"]
_Marie = ["보스 마리", "마리 따까리1", "마리 따까리1", "마리 따까리2", "마리 따까리2"]
_KL_WWE = ["벨라"]
_ALLIES_1 = ["주인공"]
_ALLIES_2 = ["주인공", "금강"]
_ALLIES_3 = ["주인공", "금강", "아우렐리우스"]
_ALLIES_4 = ["주인공", "금강", "아우렐리우스", "마리"]

BATTLE_PRESETS = {
    "솔로_vs_솔캐리_전방": {
        "title": "[솔로 vs 솔캐리 전방]",
        "enemies": _ENEMIES,
        "allies":  _ALLIES_1,
        "enemy_formation": "솔캐리_전방",
        "ally_formation":  "솔로",
        "gap": 0.3,
    },
    "솔로_vs_솔캐리_후방": {
        "title": "[솔로 vs 솔캐리 후방]",
        "enemies": _ENEMIES,
        "allies":  _ALLIES_1,
        "enemy_formation": "솔캐리_후방",
        "ally_formation":  "솔로",
        "gap": 0.3,
    },
    "솔로_vs_더블캐리": {
        "title": "[솔로 vs 더블캐리]",
        "enemies": _ENEMIES,
        "allies":  _ALLIES_1,
        "enemy_formation": "더블캐리",
        "ally_formation":  "솔로",
        "gap": 0.3,
    },
    "듀오_vs_솔캐리_전방": {
        "title": "[듀오 vs 솔캐리 전방]",
        "enemies": _ENEMIES,
        "allies":  _ALLIES_2,
        "enemy_formation": "솔캐리_전방",
        "ally_formation":  "듀오",
        "gap": 0.3,
    },
    "듀오_vs_솔캐리_후방": {
        "title": "[듀오 vs 솔캐리 후방]",
        "enemies": _ENEMIES,
        "allies":  _ALLIES_2,
        "enemy_formation": "솔캐리_후방",
        "ally_formation":  "듀오",
        "gap": 0.3,
    },
    "듀오_vs_더블캐리": {
        "title": "[듀오 vs 더블캐리]",
        "enemies": _ENEMIES,
        "allies":  _ALLIES_2,
        "enemy_formation": "더블캐리",
        "ally_formation":  "듀오",
        "gap": 0.3,
    },
    " 스쿼드_vs_솔캐리_전방": {
        "title": "[스쿼드 vs 솔캐리 전방]",
        "enemies": _ENEMIES,
        "allies":  _ALLIES_4,
        "enemy_formation": "솔캐리_전방",
        "ally_formation":  "스쿼드",
        "gap": 0.3,
    },
    "트리오_vs_솔캐리_후방": {
        "title": "[트리오 vs 솔캐리 후방]",
        "enemies": _ENEMIES,
        "allies":  _ALLIES_3,
        "enemy_formation": "솔캐리_후방",
        "ally_formation":  "트리오",
        "gap": 0.3,
    },
    
    "스쿼드_vs_솔로": {
        "title": "[스쿼드 vs 솔로]",
        "enemies": _KL_WWE,
        "allies":  _ALLIES_4,
        "enemy_formation": "솔로",
        "ally_formation":  "스쿼드",
        "gap": 0.3,
    },

    "트리오_vs_마리": {
        "title": "[트리오 vs 마리]",
        "enemies": _Marie,
        "allies":  _ALLIES_3,
        "enemy_formation": "보스_마리",
        "ally_formation":  "트리오",
        "gap": 0.3,
    },
}