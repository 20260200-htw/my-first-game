# 탐험 데이터
# 5개 구역(중앙/동부/서부/남부/북부), 구역별 이벤트 확률과 내용.
# 이벤트 종류: "battle"(전투) / "text"(텍스트·다이얼로그)
# 현재는 전투도 결과 텍스트만 표시(실제 전투 진입은 추후 연결).

# 십자 지도 배치 (격자 좌표; col,row) — 화면에 십자로 그리기 위함
REGION_LAYOUT = {
    "북부": (1, 0),
    "서부": (0, 1),
    "중앙": (1, 1),
    "동부": (2, 1),
    "남부": (1, 2),
}

REGION_ORDER = ["중앙", "동부", "서부", "남부", "북부"]

# 구역별 설정
# events: [{ "kind": "battle"/"text", "weight": 확률가중치, ... }]
REGIONS = {
    "중앙": {
        "title": "중앙 구역",
        "desc": "왕국의 중심부. 비교적 안전하지만 마수가 출몰한다.",
        "events": [
            {"kind": "battle", "weight": 99,
             "enemy_pools": [
                 # 추후 적 프리셋으로 교체. 지금은 표시용 이름만.
                 "마수 무리",
             ]},
            {"kind": "text", "weight": 1,
             "dialogue": [
                 {"speaker": "주인공", "text": "낡은 상자를 발견했다."},
                 {"speaker": "주인공", "text": "안에는 약간의 골드가 들어 있었다."},
             ],
             "reward_gold": 50},
        ],
    },
    "동부": {
        "title": "동부 구역",
        "desc": "해안을 따라 이어진 동쪽 지역.",
        "events": [
            {"kind": "battle", "weight": 100, "enemy_pools": ["해안의 마수"]},
        ],
    },
    "서부": {
        "title": "서부 구역",
        "desc": "험준한 산악으로 이루어진 서쪽 지역.",
        "events": [
            {"kind": "battle", "weight": 100, "enemy_pools": ["산악의 마수"]},
        ],
    },
    "남부": {
        "title": "남부 구역",
        "desc": "끝없는 사막이 펼쳐진 남쪽 지역.",
        "events": [
            {"kind": "battle", "weight": 100, "enemy_pools": ["사막의 마수"]},
        ],
    },
    "북부": {
        "title": "북부 구역",
        "desc": "혹한의 설원이 이어진 북쪽 지역.",
        "events": [
            {"kind": "battle", "weight": 100, "enemy_pools": ["설원의 마수"]},
        ],
    },
}


def roll_event(region_key):
    """구역의 이벤트를 가중치에 따라 하나 뽑는다."""
    import random
    region = REGIONS.get(region_key)
    if not region or not region.get("events"):
        return None
    events = region["events"]
    total = sum(e.get("weight", 1) for e in events)
    r = random.uniform(0, total)
    acc = 0
    for e in events:
        acc += e.get("weight", 1)
        if r <= acc:
            return e
    return events[-1]
