# ── 수비 스킬 공용 정의 ───────────────────────────────────────────
# def_kind: "guard"(방어/자신 보호막) / "dodge"(회피/자신) / "assist"(원호/아군)
# 캐릭터 정의에 "defense_skills": ["방어","회피","원호"] 처럼 이름 리스트로 지정.
DEFENSE_SKILLS = {
    "방어": {"name": "방어", "power": 50, "type": "물리", "side": "자신", "count": "1인",
            "hits": 1, "tags": ["지원"], "motion": "command", "def_kind": "guard",
            "sprite": "", "desc": ["자신에게 보호막을 둘러 피해를 막는다."]},
    "회피": {"name": "회피", "power": 50, "type": "물리", "side": "자신", "count": "1인",
            "hits": 1, "tags": ["지원"], "motion": "command", "def_kind": "dodge",
            "sprite": "", "desc": ["회피 자세. 위력보다 약한 공격을 무효화한다."]},
    "원호": {"name": "원호", "power": 50, "type": "물리", "side": "아군", "count": "1인",
            "hits": 1, "tags": ["지원"], "motion": "command", "def_kind": "assist",
            "sprite": "", "desc": ["아군에게 보호막을 부여한다.",
                                    "그 보호막이 막은 피해만큼 자신이 대신 받는다."]},
}

ENEMY_DEFS = {
    # ─────────────────────────────────────────────────────────────
    #  중앙 잡몹
    # ─────────────────────────────────────────────────────────────
    "slime": {
        "title":         "",
        "name":          "슬라임",
        "type":          "normal",
        "level_min":     3,
        "level_max":     6,
        "hp_min":        20,
        "hp_max_range":  30,
        "mp_max":        10,
        "phys_min":      1,
        "phys_max":      4,
        "magic_min":     1,
        "magic_max":     1,
        "sprite":        "assets/center_normal/slime.png",
        "profile":       "assets/center_normal/slime_profile.png",
        "bgm": "assets/center_normal/center.mp3",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.5,
        "background":    "assets/center_normal/center_normal_BG.png",
        "speed_min": 1, "speed_max": 1,
        "overview": [
            "슬라임",
            ""
            "가장 약하고 흔한 몬스터입니다.",
            "다양한 변종이 존재하지만, 이건 원종입니다.",
        ],
        "skills": [
            {"name": "박치기", "power": 3, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [], "motion": "stationary",
             "sprite": ""},
            {"name": "용해", "power": 2, "type": "마법", "side": "적", "count": "1인", "hits": 1,"cost": 10, "tags": [], "motion": "cast",
             "sprite": ""},
        ],
    },
    "goblin": {
        "title":         "",
        "name":          "고블린",
        "type":          "normal",
        "level_min":     4,
        "level_max":     7,
        "hp_min":        15,
        "hp_max_range":  40,
        "mp_max":        10,
        "phys_min":      2,
        "phys_max":      5,
        "magic_min":     1,
        "magic_max":     1,
        "sprite":        "assets/center_normal/goblin.png",
        "profile":       "assets/center_normal/goblin_profile.png",
        "bgm": "assets/center_normal/center.mp3",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.5,
        "background":    "assets/center_normal/center_normal_BG.png",
        "speed_min": 4, "speed_max": 7,
        "overview": [
            "고블린",
            "",
            "고블린입니다.",
            "",
        ],
        "skills": [
            {"name": "후려치기", "power": 1, "type": "물리", "side": "적", "count": "1인", "hits": 2, "tags": [], "motion": "stationary",
             "sprite": ""},
        ],
    },
    "wild_boar": {
        "title":         "",
        "name":          "와일드 보어",
        "type":          "normal",
        "level_min":     5,
        "level_max":     9,
        "hp_min":        50,
        "hp_max_range":  100,
        "mp_max":        10,
        "phys_min":      6,
        "phys_max":      11,
        "magic_min":     1,
        "magic_max":     1,
        "sprite":        "assets/center_normal/wild_boar.png",
        "profile":       "assets/center_normal/wild_boar_profile.png",
        "bgm": "assets/center_normal/center.mp3",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.5,
        "background":    "assets/center_normal/center_normal_BG.png",
        "speed_min": 1, "speed_max": 10,
        "overview": [
            "와일드 보어",
            "",
            "초원에 사는 돼지와 닮은 마물입니다.",
            "비교적 강한 신체 능력을 가지고 있어 주의가 필요합니다.",
        ],
        "passives": [
            {
                "name": "두꺼운 가죽",
                "desc": [
                    "모든 피해로부터 받는 피해가 2% 감소합니다.",
                ],
                "effects": [{"kind": "take_mult", "value": 0.98}]
            }
        ],
        "skills": [
            {"name": "돌진", "power": 5, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [], "motion": "behind",
             "sprite": ""},
        ],
    },
    # ─────────────────────────────────────────────────────────────
    #  중앙 엘리트
    # ─────────────────────────────────────────────────────────────
    "dojuk": {
        "title":         "",
        "name":          "도적",
        "type":          "normal",
        "level":         10,
        "phys_level":    13,
        "magic_level":   4,
        "hp_max":        200,
        "mp_max":        60,
        "sprite":        "assets/center_normal/dojuk.png",
        "profile":       "assets/center_normal/dojuk_profile.png",
        "bgm": "assets/center_normal/center.mp3",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.5,
        "background":    "assets/center_normal/center_normal_BG.png",
        "speed_min": 5, "speed_max": 7,
        "overview": [
            "도적",
            "",
            "당신을 습격한 도적입니다.",
            "그리 강하지는 않으나 기습에 능하니 그 속도를 따라잡을 필요가 있습니다.",
        ],
        "passives": [
            {
                "name": "약자 사냥",
                "desc": [
                    "매 턴이 시작될 때마다 자신보다 속도가 낮은 대상에게 가하는 피해 +5%",
                ],
            }
        ],
        "skills": [
            {"name": "찌르기", "power": 3, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [], "motion": "stationary",
             "sprite": ""},
            {"name": "기습", "power": 10, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [], "motion": "stationary",
             "sprite": "", "cond": [{"if": "self_speed_below_target", "power_set": 0}],
             "desc": ["대상보다 속도가 느리다면 최종 위력이 0이 됩니다."]},
        ],
    },
    # ─────────────────────────────────────────────────────────────
    #  중앙 중간보스
    # ─────────────────────────────────────────────────────────────
    "noob": {
        "title":         "",
        "name":          "누브",
        "type":          "boss",
        "level":         15,
        "phys_level":    11,
        "magic_level":   2,
        "hp_max":        230,
        "mp_max":        60,
        "sprite":        "assets/center_normal/noob.png",
        "profile":       "assets/center_normal/noob_profile.png",
        "bgm": "assets/SS/small_sky.mp3",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.5,
        "background":    "assets/SS/SS_BG.png",
        "speed_min": 2, "speed_max": 7,
        "overview": [
            "누브",
            "",
            "모험가 결투에 참여한 신입 모험가입니다.",
            "무재무능의 실력을 가지고 있습니다.",
        ],
        "skills": [
            {"name": "주먹질", "power": 2, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [], "motion": "stationary",
             "sprite": ""},
            {"name": "주먹질 3번", "power": 2, "type": "물리", "side": "적", "count": "1인", "hits": 3, "tags": [], "motion": "stationary",
             "sprite": ""},
        ],
    },
    # ─────────────────────────────────────────────────────────────
    #  중앙 최종보스
    # ─────────────────────────────────────────────────────────────
    "small_sky": {
        "title":         "",
        "name":          "소천",
        "defense_skills": ["회피"],
        "type":          "boss",
        "level":         20,
        "phys_level":    11,
        "magic_level":   17,
        "hp_max":        500,
        "mp_max":        300,
        "sprite":        "assets/SS/SS_battle.png",
        "profile":       "assets/SS/SS_profile.png",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.2,
        "background":    "assets/SS/SS_BG.png",
        "bgm":           "assets/SS/small_sky.mp3",
        "speed_min": 1, "speed_max": 1,
        "muhyeong_max": 10,   # '무형검' 최대 중첩 (도달 시 무형만참 발동). 무형만참 require_buff stacks 와 일치시킬 것
        "overview": [
            "소천",
            "",
            "모험가 결투에 참여한 신입 모험가입니다.",
            "동부의 이름난 문파의 문하생이기도 합니다.",
        ],
        "passives": [
            {
                "name": "무형검류",
                "desc": [
                    "자신보다 마법 레벨이 낮은 적에게 가하는 피해 +10%",
                    "대상이 자신보다 마법 레벨이 높다면 스킬의 필중 효과가 적용되지 않습니다."
                ],
            },
            {
                "name": "검으로 다지는 초석",
                "desc": [
                    "자신이 마법 스킬을 사용했다면 다음 턴에 '무형검' 중첩을 1 얻습니다.",
                    "'무형검' 중첩이 최대가 되면 강력한 스킬을 사용합니다.",
                ],
            }
        ],
        "skills": [
            {"name": "무형참", "power": 7, "type": "마법", "side": "적", "count": "1인", "hits": 1, "tags": ["필중"], "motion": "SS_skills_1",
             "sprite": "", "effect_self": "", "effect_target": "",
             "sound": "assets/SS/SS_slash.mp3",},
            {"name": "무형참 - 연", "power": 5, "type": "마법", "side": "적", "count": "1인", "hits": 3, "tags": ["필중"], "motion": "SS_skills_2", "split": 1,
             "sprite": "",  "effect_self": "", "effect_target": "",
             "sound": "assets/SS/SS_slash.mp3",},
            {"name": "받아치겠습니다.", "power": 10, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [], "motion": "SS_skills_3",
             "sprite": "", "cond": [{"if": "not_damaged_by_target", "power_set": 0}],
             "desc": ["이번 턴에 대상으로부터 피해를 받지 않았다면 최종 위력이 0이 됩니다."]},
            {"name": "무형참류 오의 - 무형만참", "power": 20, "type": "마법", "side": "적", "count": "1인", "hits": 5, "tags": ["필중"], "motion": "SS_skills_4", "split": 1,
             "sprite": "",  "effect_self": "", "effect_target": "",
             "sound": "assets/SS/SS_slash.mp3",
             "require_buff": {"name": "무형검", "stacks": 10, "consume": True},
             "cond": [{"if": "target_guard", "power_mult": 0.5}],
             "desc": ["'무형검' 중첩이 최대가 되었을 때 사용합니다.",
             "사용 시 모든 '무형검' 중첩을 소모합니다.",
             "수비 스킬 '방어' 를 사용한 대상에게는 피해량 -50%"]
            },
        ],
    },
    # ─────────────────────────────────────────────────────────────
    #  중앙 도전보스
    # ─────────────────────────────────────────────────────────────    #  (미작성)
    # ─────────────────────────────────────────────────────────────
    #  중앙 극한보스
    # ─────────────────────────────────────────────────────────────    #  (미작성)
    # ─────────────────────────────────────────────────────────────
    #  동부 잡몹
    # ─────────────────────────────────────────────────────────────
    "wood": {
        "title":         "",
        "name":          "목령",
        "type":          "normal",
        "level_min":     17,
        "level_max":     23,
        "hp_min":        40,
        "hp_max_range":  100,
        "mp_max":        100,
        "phys_min":      12,
        "phys_max":      15,
        "magic_min":     4,
        "magic_max":     6,
        "sprite":        "assets/east_normal/wood.png",
        "profile":       "assets/east_normal/wood_profile.png",
        "bgm": "assets/east_normal/east.mp3",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.5,
        "background":    "assets/east_normal/east_normal_BG.png",
        "speed_min": 0, "speed_max": 1,
        "overview": [
            "목령",
            ""
            "죽은 나무에 마력이 모여 생긴 마물입니다.",
            "행동이 굉장히 둔합니다.",
        ],
        "skills": [
            {"name": "뿌리치기", "power": 5, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [], "motion": "cast",
             "sprite": ""},
            {"name": "주시", "power": 3, "type": "마법", "side": "적", "count": "1인", "hits": 1,"cost": 10, "tags": [], "motion": "smite",
             "sprite": ""},
        ],
    },
    "monkey": {
        "title":         "",
        "name":          "원요",
        "type":          "normal",
        "level_min":     12,
        "level_max":     19,
        "hp_min":        50,
        "hp_max_range":  70,
        "mp_max":        50,
        "phys_min":      11,
        "phys_max":      14,
        "magic_min":     3,
        "magic_max":     7,
        "sprite":        "assets/east_normal/monkey.png",
        "profile":       "assets/east_normal/monkey.png",
        "bgm": "assets/east_normal/east.mp3",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.5,
        "background":    "assets/east_normal/east_normal_BG.png",
        "speed_min": 9, "speed_max": 10,
        "overview": [
            "원요",
            "",
            "원숭이와 닮은 마물입니다.",
            "보기와는 달리 꽤나 강하니 주의하세요.",
        ],
        "skills": [
            {"name": "원요권", "power": 13, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [], "motion": "stationary",
             "sprite": ""},
        ],
    },
    # ─────────────────────────────────────────────────────────────
    #  동부 엘리트
    # ─────────────────────────────────────────────────────────────
    "fox": {
        "title":         "",
        "name":          "꼬마 여우",
        "type":          "normal",
        "level_min":     20,
        "level_max":     20,
        "hp_min":        30,
        "hp_max_range":  30,
        "mp_max":        10,
        "phys_min":      10,
        "phys_max":      10,
        "magic_min":     10,
        "magic_max":     10,
        "sprite":        "assets/east_normal/fox.png",
        "profile":       "assets/east_normal/fox.png",
        "bgm": "assets/east_normal/east.mp3",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.5,
        "background":    "assets/east_normal/east_normal_BG.png",
        "speed_min": 10, "speed_max": 10,
        "overview": [
            "꼬마 여우",
            "",
            "요호라는 이름으로도 불리는 여우와 무서울 정도로 똑같이 생긴 마물입니다.",
            "아직은 마물에 그치지만, 후에 여러 강한 마족으로 진화할 수 있는 마물입니다.",
            "",
            "꼬마 여우는 자신을 해한 이를 영원히 기억한다는 말도 있습니다.",
        ],
        "passives": [
            {
                "name": "요호",
                "desc": [
                    "아직 진화하지 못한 상태입니다.",
                ],
            }
        ],
        "skills": [
            {"name": "물기", "power": 1, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [], "motion": "stationary",
             "sprite": ""},
        ],
    },
    # ─────────────────────────────────────────────────────────────
    #  동부 중간보스
    # ─────────────────────────────────────────────────────────────
    "dosa": {
        "title":         "",
        "name":          "도사",
        "type":          "boss",
        "level":         40,
        "phys_level":    1,
        "magic_level":   50,
        "hp_max":        300,
        "mp_max":        100,
        "sprite":        "assets/dosa/dosa_battle.png",
        "profile":       "assets/dosa/dosa_profile.png",
        "sprite_scale":  0.3,
        "click_w_ratio": 0.5,
        "background":    "assets/dosa/dosa_BG.png",
        "bgm": "assets/dosa/dosa.mp3",
        "speed_min": 11, "speed_max": 22,
        "overview": [
            "도사",
            "",
            "나에 대해 궁금할 것 같으니 내 친히 소개하겠네.",
            "내 이름은 도사. 길 도, 선비 사. 길을 닦는 위인이란 뜻이지.",
            "",
            "뭐, 믿든 안 믿든 상관 없다네.",
            "나 도사는 바람을 다루는 마법에 능통한 마법사.",
            "바람은 버티려는 상대를 쉬이 날려버릴 수 없다네.",
            "",
            "수비 스킬을 적절히 사용하는 것이 나를 상대하는 묘책이라는 말씀.",
        ],
        "passives": [
            {
                "name": "도사",
                "desc": [
                    "자신이 적에게 가하는 모든 피해가 999% 증가합니다.",
                ],
            },
            {
                "name": "거짓말쟁이",
                "desc": [
                    "그는 거짓말을 하고 있습니다.",
                ],
            }
        ],
        "skills": [
            {"name": "바람아 가거라!", "power": 5, "type": "물리", "side": "적", "count": "1인", "hits": 3, "tags": [], "motion": "cast",
             "sprite": "assets/dosa/dosa_skill_1.png","effect_self": "", "effect_target": "assets/dosa/dosa_wind1.png","effect_target_scale": 2.0,
             "sound": "assets/dosa/dosa_wind.mp3"},
            {"name": "하하, 정말 시원하단 말일세!", "power": 11, "type": "물리", "side": "적", "count": "1인", "hits": 3, "tags": [], "motion": "smite",
             "sprite": "assets/dosa/dosa_skill_2.png","effect_self": "", "effect_target": "assets/dosa/dosa_wind2.png", "effect_target_scale": 2.0,
             "sound": "assets/dosa/dosa_wind.mp3", "cond": [{"if": "target_guard", "power_set": 33}],
             "desc": ["대상이 수비 스킬 '방어' 를 사용하였다면 최종 위력이 0이 됩니다."]},
            {"name": "강한 돌풍은 쉬이 꺼지질 않지~", "power": 20, "type": "물리", "side": "적", "count": "1인", "hits": 3, "tags": [], "motion": "smite",
             "sprite": "assets/dosa/dosa_skill_3.png","effect_self": "", "effect_target": "assets/dosa/dosa_wind3.png", "effect_target_scale": 5.0,
             "sound": "assets/dosa/dosa_wind.mp3", "cond": [{"if": "target_guard", "damage_mult": 1.5}],
             "desc": ["대상이 수비 스킬 '방어' 를 사용하였다면 피해량이 50% 감소합니다."]},
            {"name": "풍류운산(風流雲散)! 하하 오마-주라네!", "power": 20, "type": "물리", "side": "적", "count": "5인", "hits": 5, "split": 3, "tags": [], "motion": "charge",
            "sprite": "assets/dosa/dosa_skill_4.png","effect_self": "", "effect_target": "assets/dosa/dosa_wind4.png", "effect_target_scale": 10.0,
             "sound": "assets/dosa/dosa_wind.mp3", "cond": [{"if": "target_guard", "power_add": 20}],
             "desc": ["대상이 수비 스킬 '방어' 를 사용하였다면 최종 위력이 20 감소합니다."]},
        ],
    },
    # ─────────────────────────────────────────────────────────────
    #  동부 최종보스
    # ─────────────────────────────────────────────────────────────
    "kirin": {
        "name": "기린",
        "type": "boss",
        "level": 70,
        "phys_level": 72,
        "magic_level": 74,
        "hp_max": 1550,
        "mp_max": 1000,
        "speed": 10,
        "sprite":  "assets/kirin/kirin_battle.png",     # 전투 기본 스프라이트
        "profile": "assets/kirin/kirin_profile.png", 
        "background":    "assets/kirin/kirin_battle_BG.png",
        "bgm":           "assets/kirin/kirin.mp3",   # 전투 프로필
        "sprite_scale": 0.50,
        "click_w_ratio": 0.25,
        "defense_skills": ["회피"],
        "overview": [
            "기린",
            "",
            "마족 중에서도 다수의 고위험도 마수가 속한 신수 중 하나.",
            "하지만 어째서인지 그 상태가 온전치 못해 보입니다.",
            "",
            "신수, 기린은 번개를 마법을 다루는 마족입니다.",
            "기린은 번개를 한 곳에 집중할 수도, 광범위하게 떨어뜨릴 수도 있습니다.",
        ],
        "passives": [
            {
                "name": "신수",
                "desc": [
                    "모든 피해로부터 받는 피해가 30% 감소합니다.",
                    "",
                ],
            },
            {
                "name": "약화",
                "desc": [
                    "어째서인지 상태가 안 좋아 보입니다.",
                    "기린의 물리 레벨과 마법 레벨이 30 감소합니다.",
                ],
            },
        ],
        "skills": [
            {
                "name": "낙뢰", "type": "마법", "side": "적", "count": "1인",
                "power": 15, "hits": 1,
                "motion": "smite", "sprite": "",
                "effect_self": "", "effect_target": "",   # ← 이펙트 이미지 경로 (비우면 전용 모션 스프라이트만)
                "desc": ["기린이 적에게 번개를 떨구어 공격합니다."],
            },
            {
                "name": "뇌격", "type": "물리", "side": "적", "count": "1인",
                "power": 10, "hits": 5,
                "motion": "smite", "sprite": "",
                "effect_self": "", "effect_target": "",   # ← 이펙트 이미지 경로 (비우면 전용 모션 스프라이트만)
                "desc": ["기린이 번개를 집중시켜 공격합니다."],
            },
            {
                "name": "격노의 천둥", "type": "물리", "side": "적", "count": "1인",
                "power": 100, "hits": 1,
                "motion": "", "sprite": "",
                "effect_self": "", "effect_target": "",   # ← 이펙트 이미지 경로 (비우면 전용 모션 스프라이트만)
                "damage_mult": 5.0,   # 이 스킬의 피해량 +500%
                "cond": [
                    {"if": "target_guard", "power_set": 1},   # 회피 시 위력 10
                ],
                "desc": [
                    "기린이 극한으로 압축한 번개를 내려칩니다."
                    "이 스킬의 피해량 +500%.",
                    "대상이 방어 시 위력이 1이 됩니다.",
                ],
            },
            {
                "name": "한 맺힌 우레", "type": "마법", "side": "적", "count": "5인",
                "power": 10, "hits": 5,
                "motion": "charge", "sprite": "",
                "effect_self": "", "effect_target": "",   # ← 이펙트 이미지 경로 (비우면 전용 모션 스프라이트만)
                "desc": [
                    "기린이 맺힌 한을 뿜어내 번개를 방출합니다.",
                ],
            },
        ]
    },
    # ─────────────────────────────────────────────────────────────
    #  동부 도전보스
    # ─────────────────────────────────────────────────────────────
    "현호": {
        "name": "현호",
        "type": "boss",
        "level": 88,
        "phys_level": 83,
        "magic_level": 92,
        "hp_max": 4000,
        "mp_max": 888,
        "speed": 10,
        "tails": 8,   # 미호 꼬리 수 (패시브/중첩 계산용)
        "sprite":  "assets/ETs/ETs_battle.png",     # 전투 기본 스프라이트
        "profile": "assets/ETs/ETs_profile.png", 
        "background":    "assets/ETs/ETs_battle_BG.png",
        "bgm":           "assets/ETs/eight_tails.mp3",   # 전투 프로필
        "sprite_scale": 0.30,
        "click_w_ratio": 0.22,
        "defense_skills": ["회피"],
        "overview": [
            "현호",
            "",
            "꼬마 여우의 상위 개체 중 하나인 '미호' 에 속하는 마족입니다.",
            "'미호' 는 꼬리의 수에 비례하여 그 격과 강함이 결정되는 마족입니다.",
            "",
            "지금 당신의 눈 앞에 있는 마족은 당신을 봐주고 있습니다.",
            "현호의 의도에 맞춰 전투에 임하는 것이 승리하는 방법일 것입니다.",
            "",
            "당신이 쓰러트린 꼬마 여우 중 하나가 진화한 것으로 보입니다.",
        ],
        "passives": [
            {
                "name": "미호",
                "desc": [
                    "꼬리 수만큼 가하는 피해가 증가하고 받는 피해가 감소합니다. (꼬리당 ±5%)",
                    "현호는 꼬리가 8개입니다. (가하는 피해 +40% / 받는 피해 -40%)"],
                    "effects": [{"kind": "deal_mult", "value": 1.4}],
                    "effects": [{"kind": "take_mult", "value": 0.6}],
            },
            {
                "name": "죽이진 않을 거예요",
                "desc": ["가하는 모든 피해가 90% 감소합니다."],
                "effects": [{"kind": "deal_mult", "value": 0.1}],
            },
            {
                "name": "여우불",
                "desc": [
                    "턴이 종료될 때, 이번 턴에 소모한 마력만큼 '여우불' 중첩을 얻습니다.",
                    "강력한 스킬을 사용해 '여우불' 중첩을 소모하면 소모한 중첩만큼 마력을 회복합니다.",
                    "최대 중첩은 꼬리 수 × 111 (888) 이며, 중첩이 최대일 때 강력한 스킬을 사용합니다.",
                ],
            },
        ],
        "skills": [
            {
                "name": "여우불", "type": "마법", "side": "적", "count": "1인",
                "power": 20, "hits": 3, "cost": 111,
                "motion": "ETs_skills_1", "sprite": "assets/ETs/ETs_skill_1.png",
                "effect_self": "", "effect_target": "assets/ETs/ETs_profile.png",
                 "effect_self_scale": 0.5, "effect_target_scale": 2.0,
                "desc": ["여우불을 3회 쏘아 보냅니다."],
            },
            {
                "name": "휘몰아치는 불꽃", "type": "마법", "side": "적", "count": "5인",
                "power": 5, "hits": 5, "cost": 222,
                "motion": "ETs_skills_2", "sprite": "assets/ETs/ETs_skill_2.png",
                "effect_self": "", "effect_target": "",   # ← 이펙트 이미지 경로 (비우면 전용 모션 스프라이트만)
                "desc": ["적 전체에게 휘몰아치는 불꽃을 5회 퍼붓습니다."],
            },
            {
                "name": "피해보세요!", "type": "물리", "side": "적", "count": "1인",
                "power": 200, "hits": 1, "cost": 111,
                "motion": "ETs_skills_3", "sprite": "assets/ETs/ETs_skill_3.png",
                "effect_self": "", "effect_target": "",   # ← 이펙트 이미지 경로 (비우면 전용 모션 스프라이트만)
                "damage_mult": 100.0,   # 이 스킬의 피해량 +10000%
                "cond": [
                    {"if": "target_dodge", "power_set": 0},   # 회피 시 위력 0
                ],
                # 대상 레벨이 더 낮고 이 스킬로 100 이상 피해 시 최대 체력 99% 고정 피해
                "desc": [
                    "이 스킬의 피해량 +10000%.",
                    "대상이 수비 스킬 '회피' 를 사용했다면 최종 위력이 0이 됩니다.",
                ],
            },
            {
                "name": "잠깐 더울 거예요~", "type": "마법", "side": "적", "count": "5인",
                "power": 1, "hits": 5, "cost": 333,
                "motion": "ETs_skills_4", "sprite": "assets/ETs/ETs_skill_4.png",
                "effect_self": "", "effect_target": "",   # ← 이펙트 이미지 경로 (비우면 전용 모션 스프라이트만)
                "cond": [
                    {"if": "target_not_guard", "power_add": 50},  # 방어 안 하면 +50
                ],
                "desc": ["대상이 수비 스킬 '방어' 를 사용하지 않았다면 최종 위력이 50 증가합니다."],
            },
            {
                "name": "여우가 춤을 추니, 그 모습이 마치 신선과 같더라", "type": "마법", "side": "적", "count": "5인",
                "power": 100, "hits": 5, "cost": 0,
                "motion": "ETs_skills_5", "sprite": "assets/ETs/ETs_skill_5.png",
                "effect_self": "", "effect_target": "",   # ← 이펙트 이미지 경로 (비우면 전용 모션 스프라이트만)
                "require_buff": {"name": "여우불", "stacks": 888, "consume": True},
                "cond": [
                    {"if": "target_guard", "power_set": 0},   # 수비(방어) 시 위력 0
                ],
                "true_damage_max_hp_pct": 15,   # 매 히트 최대 체력 5% 고정 피해
                "desc": [
                    "'여우불' 중첩이 최대(888)일 때 사용하며, 중첩을 모두 소모합니다.",
                    "대상이 수비 스킬 '방어' 를 사용하면 최종 위력이 0이 됩니다.",
                    "매 공격마다 대상 최대 체력의 15%만큼 추가 고정 피해를 입힙니다.",
                ],
            },
        ],
    },
    # ─────────────────────────────────────────────────────────────
    #  동부 극한보스
    # ─────────────────────────────────────────────────────────────
    "orochi": {
        "name": "오로치",
        "type": "boss",
        "level": 88,
        "phys_level": 0,
        "magic_level": 0,
        "hp_max": 8888,
        "mp_max": 888,
        "speed": 0,
        "heads": 8, #오로치 머리 수, 필드에 남아있는 또다른 머리 수가 감소함에 따라 1까지 감소
        "sprite":  "assets/orochi/orochi_battle.png",     # 전투 기본 스프라이트
        "profile": "assets/orochi/orochi_profile.png", 
        "background":    "assets/orochi/orochi_battle_BG.png",
        "bgm":           "assets/orochi/orochi.mp3",   # 전투 프로필
        "sprite_scale": 1.5,
        "click_w_ratio": 0.25,
        "defense_skills": ["방어"],
        "overview": [
            "야마타노오로치",
            "",
            "동부에 자리잡은 성물의 마력을 흡수한 마족입니다.",
            "본래도 고위험도를 가진 마족이나, 그 이상의 존재가 되어 버렸습니다.",
            "",
            "오로치는 각 머리들에 본신의 마력이 나뉘어 저장되어 있습니다.",
            "그 머리들을 하나씩 잘라 가며 오로치의 힘을 약화시켜야만 합니다.",
            "",
            "기회는 반드시 찾아올테니 급해져서는 안 됩니다.",
        ],
        "passives": [
            {
                "name": "오로치",
                "desc": [
                    "남아 있는 머리 수만큼 남은 모든 머리들의 물리 레벨과 마법 레벨이 증가합니다. (개당 11)",
                    "머리가 잘려 나갈 때마다 물리 레벨과 마법 레벨이 감소하고, 모든 머리가 잘리면 사망합니다."
                    "필드에 최대 2개의 또다른 머리가 존재할 수 있으며, 하나가 잘리면 남은 머리 중 하나가 그 자리를 대신합니다.",
                ],
            },
            {
                "name": "가운데 머리",
                "desc": ["오로치의 가운데 머리입니다.", "오로치의 모든 머리가 잘려 나가기 전까지 이 머리는 절대 잘리지 않습니다.",
                         "나머지 머리가 모두 잘리기 전까지 모든 피해로부터 받는 피해가 100% 감소하고 고정 피해를 받지 않습니다.",
                         "또한 나머지 머리가 모두 잘리기 전까지 이 머리의 속도는 0으로 고정됩니다."],
                "effects": [{"kind": "take_mult", "value": 0.0}],
            },
            {
                "name": "내게 네놈들의 하찮은 목숨을 바쳐라",
                "desc": [
                    "남아 있는 오로치의 머리 중 하나가 5턴마다 '포식' 스킬을 사용합니다.",
                    "'포식' 스킬을 사용한 머리는 '만족감' 중첩을 1 얻으며, 중첩 당 받는 피해가 50% 증가합니다.",
                    "만약 가운데 머리만 남아있다면, 주기마다 '포식' 대신 '아마노무라쿠모노츠루기' 스킬을 사용합니다.",
                ],
            },
            {
                "name": "맛있구나",
                "desc": [
                    "오로치가 '포식' 스킬로 대상을 처치하면, 모든 머리가 다시 재생되고 체력을 전부 회복합니다.",
                    "다음 턴부터 오로치가 머리 수에 상관 없이 속도가 80이 되며, '아마노무라쿠모노츠루기' 스킬을 매 턴마다 사용합니다.",
                ],
            },
        ],
        "skills": [
            {
                "name": "아마노무라쿠모노츠루기", "type": "마법", "side": "적", "count": "5인",
                "power": 888, "hits": 8,
                "motion": "", "sprite": "",
                "effect_self": "", "effect_target": "",   # ← 이펙트 이미지 경로 (비우면 전용 모션 스프라이트만)
                "desc": ["오로치가 자신의 몸에서 벼린 칼을 뽑아 휘두릅니다."],
            },
        ],
    },
    "orochi_head": {
        "name": "오로치의 또다른 머리",
        "type": "normal",
        "level": 88,
        "phys_level": 0,
        "magic_level": 0,
        "hp_max": 888,
        "mp_max": 888,
        "speed": 8,
        "sprite":  "assets/orochi/orochi_head_battle.png",     # 전투 기본 스프라이트
        "profile": "assets/orochi/orochi_head_profile.png", 
        "background":    "assets/orochi/orochi_battle_BG.png",
        "bgm":           "assets/orochi/orochi.mp3",   # 전투 프로필
        "sprite_scale": 0.75,
        "click_w_ratio": 0.25,
        "defense_skills": ["방어"],
        "overview": [
            "오로치의 또다른 머리",
            "",
            "야먀타노오로치의 또다른 머리입니다.",
            "오로치의 가운데 머리를 자르기 위해 또다른 머리들을 모두 잘라내야 합니다.",
        ],
        "passives": [
            {
                "name": "또다른 머리",
                "desc": ["오로치의 또다른 머리입니다.",
                         "'포식' 스킬을 사용하는 턴이 되면 스킬을 사용하는 머리를 제외한 모든 머리의 속도가 0이 됩니다."],
            },
        ],
        "skills": [
            {
                "name": "물기", "type": "물리", "side": "적", "count": "1인",
                "power": 10, "hits": 1,
                "motion": "behind", "sprite": "",
                "effect_self": "", "effect_target": "",   # ← 이펙트 이미지 경로 (비우면 전용 모션 스프라이트만)
                "desc": ["대상을 물어 뜯습니다."],
            },
            {
                "name": "포식", "type": "물리", "side": "적", "count": "1인",
                "power": 100, "hits": 1,
                "motion": "behind", "sprite": "",
                "effect_self": "", "effect_target": "",   # ← 이펙트 이미지 경로 (비우면 전용 모션 스프라이트만)
                "desc": ["오로치의 또다른 머리 중 하나가 대상을 물어 뜯습니다.",
                         "이 스킬의 대상이 처치되면 오로치의 '맛있구나' 패시브가 발동합니다."],
            },
        ],
    },
    # ─────────────────────────────────────────────────────────────
    #  서부 잡몹
    # ─────────────────────────────────────────────────────────────
    "ground_slime": {
        "title":         "",
        "name":          "땅 슬라임",
        "type":          "normal",
        "level_min":     22,
        "level_max":     24,
        "hp_min":        70,
        "hp_max_range":  150,
        "mp_max":        100,
        "phys_min":      22,
        "phys_max":      25,
        "magic_min":     1,
        "magic_max":     3,
        "sprite":        "assets/west_normal/ground_slime.png",
        "profile":       "assets/west_normal/ground_slime_profile.png",
        "bgm": "assets/west_normal/west.mp3",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.5,
        "background":    "assets/west_normal/west_normal_BG.png",
        "speed_min": 1, "speed_max": 1,
        "overview": [
            "땅 슬라임",
            ""
            "흙을 많이 먹어 몸이 단단해진 슬라임입니다.",
            "그래도 슬라임은... 슬라임이죠?",
        ],
        "skills": [
            {"name": "단단한 박치기", "power": 10, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [], "motion": "stationary",
             "sprite": ""},
        ],
    },
    "ghost": {
        "title":         "",
        "name":          "유령",
        "type":          "normal",
        "level_min":     21,
        "level_max":     21,
        "hp_min":        10,
        "hp_max_range":  10,
        "mp_max":        10,
        "phys_min":      10,
        "phys_max":      10,
        "magic_min":     10,
        "magic_max":     10,
        "sprite":        "assets/west_normal/ghost.png",
        "profile":       "assets/west_normal/ghost.png",
        "bgm": "assets/west_normal/west.mp3",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.5,
        "background":    "assets/west_normal/west_normal_BG.png",
        "speed_min": 30, "speed_max": 30,
        "overview": [
            "유령",
            "",
            "유령처럼 보이는 마물입니다.",
            "근데 진짜 유령은 아니고 마력의 집합체니 안심하고 처치하셔도 됩니다.",
        ],
        "skills": [
            {"name": "지평좌표계고정할퀴기", "power": 3, "type": "물리", "side": "적", "count": "1인", "hits": 2, "tags": [], "motion": "stationary",
             "sprite": ""},
        ],
    },
    "spin": {
        "title":         "",
        "name":          "회전초",
        "type":          "normal",
        "level_min":     24,
        "level_max":     27,
        "hp_min":        50,
        "hp_max_range":  70,
        "mp_max":        10,
        "phys_min":      21,
        "phys_max":      23,
        "magic_min":     3,
        "magic_max":     8,
        "sprite":        "assets/west_normal/spin.png",
        "profile":       "assets/west_normal/spin.png",
        "bgm": "assets/west_normal/west.mp3",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.5,
        "background":    "assets/west_normal/west_normal_BG.png",
        "speed_min": 1, "speed_max": 20,
        "overview": [
            "회전초",
            "",
            "서부의 넓은 땅을 구르며 다니던 회전초에 마력이 쌓여 탄생한 마물입니다.",
            "과거에는 그 수가 많지 않았으나, 현재는 대부분의 회전초가 마물이 되었습니다.",
            "",
            "따라서 서부에서는 회전초를 본다면 마물이 아니더라도 헤집어 놓는 것을 권장하고 있습니다..",
        ],
        "skills": [
            {"name": "구르기", "power": 3, "type": "물리", "side": "적", "count": "1인", "hits": 3, "tags": [], "motion": "behind",
             "sprite": ""},
        ],
    },
    # ─────────────────────────────────────────────────────────────
    #  서부 엘리트
    # ─────────────────────────────────────────────────────────────
    "small_shell": {
        "title":         "",
        "name":          "작은 시체 조개",
        "type":          "boss",
        "level":         40,
        "phys_level":    32,
        "magic_level":   9,
        "hp_max":        100,
        "mp_max":        100,
        "sprite":        "assets/west_normal/shell.png",
        "profile":       "assets/west_normal/shell_profile.png",
        "bgm": "assets/west_normal/west.mp3",
        "sprite_scale":  0.3,
        "click_w_ratio": 0.5,
        "background":    "assets/west_normal/west_normal_BG.png",
        "speed_min": 1, "speed_max": 1,
        "overview": [
            "시체 조개",
            "",
            "육지 조개라는 모순적인 마물의 유체입니다.",
            "사람을 잡아먹으니 토벌하는 것을 권장합니다.",
        ],
        "passives": [
            {
                "name": "깨진 조개",
                "desc": [
                    "모든 피해로부터 받는 피해가 50% 증가합니다.",
                ],
                "effects": [{"kind": "take_mult", "value": 0.5}]
            },
        ],
        "skills": [
            {"name": "조개치기", "power": 10, "type": "마법", "side": "적", "count": "1인", "hits": 3, "tags": [], "motion": "behind",
             "sprite": ""},
        ],
    },

    # ─────────────────────────────────────────────────────────────
    #  서부 중간보스
    # ─────────────────────────────────────────────────────────────
    "shell": {
        "title":         "",
        "name":          "시체 조개",
        "type":          "boss",
        "level":         54,
        "phys_level":    47,
        "magic_level":   12,
        "hp_max":        600,
        "mp_max":        100,
        "sprite":        "assets/west_normal/shell.png",
        "profile":       "assets/west_normal/shell_profile.png",
        "bgm": "assets/west_normal/west.mp3",
        "sprite_scale":  0.8,
        "click_w_ratio": 0.5,
        "background":    "assets/west_normal/west_normal_BG.png",
        "speed_min": 1, "speed_max": 1,
        "overview": [
            "시체 조개",
            "",
            "육지 조개라는 모순적인 마물입니다.",
            "사람을 잡아먹으니 토벌하는 것을 권장합니다.",
        ],
        "passives": [
            {
                "name": "깨진 조개",
                "desc": [
                    "모든 피해로부터 받는 피해가 50% 증가합니다.",
                ],
                "effects": [{"kind": "take_mult", "value": 0.5}]
            },
        ],
        "skills": [
            {"name": "조개치기", "power": 10, "type": "마법", "side": "적", "count": "1인", "hits": 3, "tags": [], "motion": "behind",
             "sprite": ""},
        ],
    },

    # ─────────────────────────────────────────────────────────────
    #  서부 최종보스
    # ─────────────────────────────────────────────────────────────
    "jack": {
        "title":         "",
        "name":          "잭 오 랜턴",
        "type":          "boss",
        "level":         60,
        "phys_level":    30,
        "magic_level":   64,
        "hp_max":        1031,
        "mp_max":        1031,
        "sprite":        "assets/jack/jack_battle.png",
        "profile":       "assets/jack/jack_profile.png",
        "bgm": "assets/jack/jack.mp3",
        "sprite_scale":  0.3,
        "click_w_ratio": 0.5,
        "background":    "assets/jack/jack_BG.png",
        "speed_min": 10, "speed_max": 10,
        "overview": [
            "잭 오 랜턴",
            "",
            "1년에 딱 하루 모습을 드러내는 마족입니다.",
            "잭 오 랜턴이 나타나는 날에는 수 많은 마물들이 그것을 따라 행진합니다.",
            "",
            "그는 방심한 상대에게 막강한 피해를 입히는 변칙성을 가지고 있습니다. 주의하세요.",
        ],
        "passives": [
            {
                "name": "잭 오",
                "desc": [
                    "모든 피해로부터 받는 피해가 20% 감소합니다.",
                ],
                "effects": [{"kind": "take_mult", "value": 0.8}]
            },
        ],
        "skills": [
            {"name": "음산한 기운", "power": 1, "type": "마법", "side": "적", "count": "3인", "hits": 3, "tags": [], "motion": "charge",
             "sprite": ""},
            {"name": "침묵하는 자에게 후회를", "power": 10, "type": "마법", "side": "적", "count": "1인", "hits": 3, "tags": [], "motion": "charge",
             "sprite": "", "effect_self": "", "effect_target": "",
             "sound": "", "desc": ["대상이 수비 스킬 '방어' 를 사용했다면 최종 위력이 100이 됩니다."],
             "cond": [
                    {"if": "target_guard", "power_set": 100},   # 수비(방어) 시 위력 10
                ]},
            {"name": "도피하는 자에게 질타를", "power": 10, "type": "마법", "side": "적", "count": "1인", "hits": 3, "tags": [], "motion": "charge",
             "sprite": "", "desc": ["대상이 수비 스킬 '회피' 를 사용했다면 최종 위력이 100이 됩니다."],
             "cond": [
                    {"if": "target_dodge", "power_set": 100},   # 수비(방어) 시 위력 10
                ]},
        ],
    },

    # ─────────────────────────────────────────────────────────────
    #  서부 도전보스
    # ─────────────────────────────────────────────────────────────    #  (미작성)
    # ─────────────────────────────────────────────────────────────
    #  서부 극한보스
    # ─────────────────────────────────────────────────────────────    #  (미작성)
    # ─────────────────────────────────────────────────────────────
    #  남부 잡몹
    # ─────────────────────────────────────────────────────────────
    "pirate1": {
        "name":          "칼 든 선원",
        "type":          "normal",
        "level":         41,
        "phys_level":    35,
        "magic_level":   21,
        "hp_max":        320,
        "mp_max":        290,
        "sprite":        "assets/south_normal/SSG_extra_1.png",
        "profile":       "assets/south_normal/SSG_extra_1_profile.png",
        "bgm": "assets/south_normal/south.mp3",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.2,
        "overview": [
            "엘 로마올라스 선원",
            "",
            "해적선 엘 로마올라스의 선원입니다.",
            "남부의 해적, 마리 솔의 선원들 중 하나입니다.",
        ],
        "passives": [
            {
                "name": "엘 로마올라스의 선원",
                "desc": [
                    "모든 피해로부터 받는 피해가 5% 감소합니다.",
                ],
                "effects": [{"kind": "take_mult", "value": 0.95}]
            },
        ],
        "speed_min": 7, "speed_max": 11,
        "skills": [
            {"name": "엉성한 난무", "power": 3, "type": "물리", "side": "적", "count": "1인", "hits": 3, "tags": [],
             "sprite": "", "motion": "stationary", "split": 2,
             "effect_self": "assets/SSG/SSG_nanmu_self.png", "effect_target": "assets/SSG/SSG_nanmu_target.png",
             "sound": "assets/SSG/SSG_nanmu.mp3", "desc": ["부선장에게 배운 선장에게 배운 기술입니다."]},
        ],
    },
    "pirate2": {
        "name":          "총 든 선원",
        "type":          "normal",
        "level":         42,
        "phys_level":    36,
        "magic_level":   20,
        "hp_max":        210,
        "mp_max":        300,
        "sprite":        "assets/south_normal/SSG_extra_2.png",
        "profile":       "assets/south_normal/SSG_extra_2_profile.png",
        "bgm": "assets/south_normal/south.mp3",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.2,
        "overview": [
            "엘 로마올라스 선원",
            "",
            "해적선 엘 로마올라스의 선원입니다.",
            "남부의 신호, 마리 솔의 부하들 중 하나입니다.",
        ],
        "passives": [
            {
                "name": "엘 로마올라스의 선원",
                "desc": [
                    "모든 피해로부터 받는 피해가 5% 감소합니다.",
                ],
                "effects": [{"kind": "take_mult", "value": 0.95}]
            },
        ],
        "speed_min": 15, "speed_max": 15,
        "skills": [
            {"name": "보조 사격", "power": 15, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [],
             "sprite": "", "motion": "cast",
             "effect_self": "assets/SSG/SSG_nanmu_self.png", "effect_target": "assets/gun_shot_target.png",
             "sound": "assets/gun_shot.mp3", "desc": ["총을 쏩니다. 비겁합니다."]},
        ]
    },
    "leg_fish": {
        "title":         "",
        "name":          "족어",
        "type":          "normal",
        "level_min":     46,
        "level_max":     51,
        "hp_min":        310,
        "hp_max_range":  500,
        "mp_max":        100,
        "phys_min":      39,
        "phys_max":      47,
        "magic_min":     11,
        "magic_max":     14,
        "sprite":        "assets/south_normal/leg_fish.png",
        "profile":       "assets/south_normal/leg_fish_profile.png",
        "bgm": "assets/south_normal/south.mp3",
        "sprite_scale":  0.3,
        "click_w_ratio": 0.5,
        "background":    "assets/south_normal/south_normal_BG.png",
        "speed_min": 3, "speed_max": 5,
        "overview": [
            "족어",
            "",
            "남부의 대표적인 해양 마물입니다.",
            "바다를 넘어 육지까지 영역을 넓힌 포식성 마물입니다.",
            "",
            "종을 가리지 않고 먹을 수 있는 것이라면 모두 먹어치우는 식성을 가졌습니다.",
            "주로 바다에서 활동하긴 하지만 약한 어린 인족을 잡아먹기 위해 육지에 올라오는 일도 잦기 때문에",
            "남부의 여러 해적들과 세력들은 족어가 출몰하는 곳이라면 서로 힘을 합쳐 모두 토벌하는 것이 관습이 되었습니다.",
        ],
        "skills": [
            {"name": "뜯어먹기", "power": 15, "type": "물리", "side": "적", "count": "1인", "hits": 2, "tags": [], "motion": "stationary",
             "sprite": ""},
        ],
    },
    "sad_jelly": {
        "title":         "",
        "name":          "비통하는 해파리",
        "type":          "normal",
        "level_min":     43,
        "level_max":     48,
        "hp_min":        210,
        "hp_max_range":  320,
        "mp_max":        100,
        "phys_min":      11,
        "phys_max":      13,
        "magic_min":     32,
        "magic_max":     46,
        "sprite":        "assets/south_normal/sad_jelly.png",
        "profile":       "assets/south_normal/sad_jelly_profile.png",
        "bgm": "assets/south_normal/south.mp3",
        "sprite_scale":  0.3,
        "click_w_ratio": 0.5,
        "background":    "assets/south_normal/south_normal_BG.png",
        "speed_min": 1, "speed_max": 1,
        "overview": [
            "비통하는 해파리",
            "",
            "남부에 최근 자주 출몰하는 마물입니다.",
            "바다에 빠져 죽은 사람이 길동무를 구하러 마물이 되었다는 괴담이 있습니다.",
            "",
            "머리 부분에 마력이 공명하여 끔찍한 소리를 냅니다.",
            "마치 바다에 빠져 도움을 요청하는 인족의 비명 소리 같은 것 말이죠.",
            "아직까지 생태가 명확히 밝혀지지 않아 아직도 많은 괴담이 존재하는 마물입니다.",
        ],
        "skills": [
            {"name": "비통", "power": 30, "type": "마법", "side": "적", "count": "1인", "hits": 1, "tags": [], "motion": "charge",
             "sprite": ""},
            {"name": "원망", "power": 0, "type": "마법", "side": "적", "count": "1인", "hits": 1, "tags": [], "motion": "smite",
             "sprite": "", "desc": [
                    "너희가 나를 ■■에 ■■ ■■했잖아",
                ]},
        ],
    },
    "fake_fish_man": {
        "title":         "",
        "name":          "가짜 어인",
        "type":          "normal",
        "level_min":     48,
        "level_max":     51,
        "hp_min":        440,
        "hp_max_range":  560,
        "mp_max":        100,
        "phys_min":      43,
        "phys_max":      47,
        "magic_min":     23,
        "magic_max":     33,
        "sprite":        "assets/south_normal/fake_fish_man.png",
        "profile":       "assets/south_normal/fake_fish_man_profile.png",
        "bgm": "assets/south_normal/south.mp3",
        "sprite_scale":  0.3,
        "click_w_ratio": 0.5,
        "background":    "assets/south_normal/south_normal_BG.png",
        "speed_min": 0, "speed_max": 1,
        "overview": [
            "가짜 어인",
            "",
            "마족 중 하나인 '어인' 을 따라하는 마물입니다.",
            "'어인' 은 바다 아래에 자신들의 공동체를 만들어 살아가고 있습니다.",
            "",
            "이 마물이 '어인' 을 따라하는 이유는 아직 아무도 밝혀내지 못 했습니다.",
            "따라한다면 인족으로 분류된 '인어' 를 따라하는 것이 더 좋을 것이라는 말과 함께 말이죠.",
            "",
            "이들은 '어인' 을 대신하여 자신들이 새로운 마족 공동체가 되기를 바라고 있는 것 아닐까요?",
        ],
        "skills": [
            {"name": "발악", "power": 21, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [], "motion": "stationary",
             "sprite": ""},
            {"name": "...언어?", "power": 0, "type": "마법", "side": "자신", "count": "1인", "hits": 1, "tags": ["지원"], "motion": "command",
             "sprite": "", "desc": [
                    "■■ ■리■ ■■ 둬... ■■는 ■족■ ■께 살■■■ ■어■... ■발.. ■■ 나■ ■■■마...",
                ]},
        ],
    },
    # ─────────────────────────────────────────────────────────────
    #  남부 엘리트
    # ─────────────────────────────────────────────────────────────
    "long_fish": {
        "title":         "",
        "name":          "긴긴물고기",
        "type":          "normal",
        "level":         50,
        "phys_level":    51,
        "magic_level":   1,
        "hp_max":        880,
        "mp_max":        10,
        "sprite":        "assets/south_normal/long_fish.png",
        "profile":       "assets/south_normal/long_fish_profile.png",
        "bgm": "assets/south_normal/south.mp3",
        "sprite_scale":  0.5,
        "click_w_ratio": 0.5,
        "background":    "assets/south_normal/south_normal_BG.png",
        "speed_min": 1, "speed_max": 50,
        "overview": [
            "긴긴물고기",
            "",
            "긴 몸과 강한 추진력을 가진 마물입니다.",
            "몸을 움직이는데 많은 에너지를 소모하기 때문에 다소 변칙적인 움직임을 보입니다.",
            "",
            "하지만 자신의 몸을 쉽게 주체하지 못 하는 것 같으니 공격을 피하기 쉬울 것입니다.",
        ],
        "skills": [
            {"name": "포식자의 돌진", "power": 30, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [], "motion": "behind",
             "sprite": "", "cond": [
                    {"if": "target_dodge", "power_set": 0},   # 회피 시 위력 0
                ], "desc": [
                    "대상이 수비 스킬 '회피' 를 사용했다면 최종 위력이 0이 됩니다.",
                ]},
            {"name": "똬리틀기", "power": 3, "type": "물리", "side": "적", "count": "1인", "hits": 5, "tags": [], "motion": "charge",
             "sprite": ""},
        ],
    },
    # ─────────────────────────────────────────────────────────────
    #  남부 중간보스
    # ─────────────────────────────────────────────────────────────
    "octo": {
        "name":          "학자 문어",
        "type":          "boss",
        "level":         60,
        "phys_level":    60,
        "magic_level":   65,
        "hp_max":        880,
        "mp_max":        1000,
        "sprite":        "assets/south_normal/octo.png",
        "profile":       "assets/south_normal/octo_profile.png",
        "background":    "assets/south_normal/octo_BG.png",
        "bgm":    "assets/south_normal/octo.mp3",
        "sprite_scale":  0.5,
        "click_w_ratio": 0.2,
        "overview": [
            "학자 문어",
            "",
            "남부의 바다에 자리 잡은 문어와 닮은 마족입니다.",
            "지능이 마족 중에서도 굉장히 높으며, 인족에게 큰 관심을 갖고 있습니다.",
            "",
            "이 마족의 영역에는 두개골이 파헤쳐진 인족의 유골이 가득하다는 소문이 있습니다.",
        ],
        "passives": [
            {
                "name": "단단한 외피",
                "desc": [
                    "모든 피해로부터 받는 피해가 10% 감소합니다.",
                ],
                "effects": [{"kind": "take_mult", "value": 0.90}]
            },
        ],
        "speed_min": 1, "speed_max": 1,
        "skills": [
            {"name": "인족의 외피에는 이정도면 충분하겠군", "power": 20, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [],
             "sprite": "", "motion": "smite",
             "effect_self": "", "effect_target": "",
             "sound": ""},
            {"name": "뇌의 외부 작용 저항력은 어떻지?", "power": 5, "type": "마법", "side": "적", "count": "1인", "hits": 5, "tags": [],
             "sprite": "", "motion": "cast",
             "effect_self": "", "effect_target": "",
             "sound": ""},
            {"name": "예상보다 인족의 외피는 단단하군", "power": 50, "type": "물리", "side": "적", "count": "1인", "hits": 5, "tags": [],
             "sprite": "", "motion": "smite",
             "effect_self": "", "effect_target": "",
             "sound": "", "desc": ["학자 문어가 적을 연속으로 내려칩니다.", "대상이 수비 스킬 '방어' 를 사용했다면 최종 위력이 10이 됩니다."],
             "cond": [
                    {"if": "target_guard", "power_set": 10},   # 수비(방어) 시 위력 10
                ]},
            {"name": "이만 탐구를 끝내야겠어.", "power": 100, "type": "마법", "side": "적", "count": "5인", "hits": 10, "tags": [],
             "sprite": "", "motion": "charge",
             "effect_self": "", "effect_target": "",
             "sound": "", "desc": ["학자 문어가 정신을 집중하여 초진동을 일으켜 뇌손상을 유발합니다.", "대상이 수비 스킬 '방어' 를 사용했다면 최종 위력이 1이 됩니다."],
             "cond": [
                    {"if": "target_guard", "power_set": 1},   # 수비(방어) 시 위력 1
                ]},
        ],
    },
    # ─────────────────────────────────────────────────────────────
    #  남부 최종보스
    # ─────────────────────────────────────────────────────────────
    "shark": {
        "name":          "상어 어인",
        "type":          "boss",
        "level":         70,
        "phys_level":    75,
        "magic_level":   13,
        "hp_max":        1330,
        "mp_max":        100,
        "sprite":        "assets/south_normal/shark.png",
        "profile":       "assets/south_normal/shark_profile.png",
        "background":    "assets/south_normal/shark_BG.png",
        "bgm":    "assets/south_normal/shark.mp3",
        "sprite_scale":  0.5,
        "click_w_ratio": 0.2,
        "overview": [
            "상어 어인",
            "",
            "남부의 깊은 심해에 자리를 잡은 마족입니다.",
            "'어인' 은 인간에게 꽤나 우호적인 종족이지만, 이 어인은 인간의 맛을 본 것 같습니다.",
            "",
            "바다의 대표적인 포식자의 특징을 가진 어인인만큼 그 위력은 무시하지 못 할 것 같습니다.",
        ],
        "passives": [
            {
                "name": "상어 피부",
                "desc": [
                    "모든 피해로부터 받는 피해가 10% 감소합니다.",
                    "자신이 가하는 모든 피해가 10% 증가합니다.",
                ],
                "effects": [{"kind": "take_mult", "value": 0.9}],
                "effects": [{"kind": "deal_mult", "value": 1.1}]
            },
        ],
        "speed_min": 15, "speed_max": 20,
        "skills": [
            {"name": "잡아뜯고 씹어먹기", "power": 10, "type": "물리", "side": "적", "count": "1인", "hits": 2, "tags": [],
             "sprite": "", "motion": "stationary",
             "effect_self": "", "effect_target": "",
             "sound": ""},
            {"name": "포식자의 공포", "power": 5, "type": "마법", "side": "적", "count": "1인", "hits": 5, "tags": [],
             "sprite": "", "motion": "charge",
             "effect_self": "", "effect_target": "",
             "sound": ""},
            {"name": "인간 사냥", "power": 50, "type": "물리", "side": "적", "count": "1인", "hits": 3, "tags": [],
             "sprite": "", "motion": "behind",
             "effect_self": "", "effect_target": "",
             "sound": "", "desc": ["상어 어인이 맹렬히 돌진합니다.", "대상이 수비 스킬 '방어' 를 사용했다면 최종 위력이 20이 됩니다."],
             "cond": [
                    {"if": "target_guard", "power_set": 20},   # 수비(방어) 시 위력 10
                ]},
        ],
    },

    # ─────────────────────────────────────────────────────────────
    #  더미 데이터
    # ─────────────────────────────────────────────────────────────

    "보스 마리": {
        "name":          "마리",
        "defense_skills": ["방어", "회피", "원호"],
        "type":          "boss",
        "level":         87,
        "phys_level":    83,
        "magic_level":   88,
        "hp_max":        2780,
        "mp_max":        5000,
        "sprite":        "assets/SSG/SSG_battle.png",
        "profile":       "assets/SSG/SSG_profile.png",
        "floor":    "assets/SSG/SSG_battle_F.png",
        "background":    "assets/SSG/SSG_battle_BG.png",
        "bgm":           "assets/SSG/SSG_battle_bgm.mp3",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.2,
        "overview": [
            "마리 솔",
            "",
            "그녀는 남부의 신호입니다.",
            "해적이지만 악인보다는 선인에 가까운 자입니다.",
            "",
            "남부는 수 많은 섬으로 이루어진 구역이기 때문에",
            "그녀는 남부 섬들 간의 교류와 마물의 토벌을 책임지고 있습니다.",
            "",
            "해적이긴 하지만요.",
        ],
        "passives": [
            {
                "name": "엘 로마올라스의 선장",
                "desc": [
                    "모든 피해로부터 받는 피해가 20% 감소합니다.",
                    "전투 지역이 엘 로마올라스라면 매 턴이 시작될 때마다 모든 아군이 전체 마력의 20%를 회복합니다.",
                ],
                "effects": [{"kind": "take_mult", "value": 0.8}]
            },
            {
                "name": "쾌검",
                "desc": [
                    "공격 횟수가 3 이상인 모든 스킬의 피해량이 30% 증가합니다.",
                    "만약 이전 턴에 회피에 성공했다면 공격 횟수가 3 이상인 모든 스킬의 최종 위력이 10 증가합니다.",
                ]
            },
            {
                "name": "마력 발산 - 선장",
                "threshold": 0.5,   # 최대 마력의 50% 소모 시 마력 발산 발동 (캐릭터별 조정 가능)
                "desc": [
                    "'마력 발산' 상태가 되면 모든 지원 스킬의 최종 위력이 25 증가합니다.",
                    "또한 공격 횟수가 3 이상인 모든 스킬의 공격 횟수가 1 증가하며, 피해량이 10% 증가합니다.",
                    "'엘 로마올라스의 선장' 이 활성화되어 있다면",
                    "매 턴이 시작될 때마다 모든 아군에게 최대 체력의 10%의 보호막을 부여합니다.",
                ]
            },
            {
                "name": "사기 증진",
                "desc": [
                    "자신 또는 아군에게 지원 스킬을 사용하면 이번 턴 동안 모든 아군의 최종 위력이 10 증가합니다.",
                ]
            },
            {
                "name": "승선",
                "desc": [
                    "자신의 체력이 최대 체력의 70% 이하로 내려갔다면 다음 턴이 시작될 때 보호막을 2000 얻습니다.",
                ]
            },
            {
                "name": "남부의 신호",
                "desc": [
                    "아군에게 지원 스킬을 사용하면 해당 아군에게 '선원' 중첩을 1 부여합니다.",
                    "'선원': 중첩당 최종 위력이 1 증가합니다. 최대 10회 중첩 가능합니다.",
                ]
            },
        ],
        "speed_min": 21, "speed_max": 33,
        "skills": [
            {"name": "난무", "power": 5, "type": "물리", "side": "적", "count": "1인", "hits": 5, "tags": [],
             "sprite": "", "motion": "stationary", "split": 3,
             "effect_self": "assets/SSG/SSG_nanmu_self.png", "effect_target": "assets/SSG/SSG_nanmu_target.png",
             "sound": "assets/SSG/SSG_nanmu.mp3",
             "desc": ["무자비한 기세로 적을 벤다."]},
            {"name": "선장의 호령", "power": 35, "type": "마법", "side": "아군", "count": "5인", "hits": 1, "tags": ["지원"],
             "sprite": "", "motion": "command",
             "effect_self": "assets/SSG/SSG_command_self.png", "effect_target": "assets/SSG/SSG_command_target.png",
             "desc": ["아군 전체를 강화한다."]},
            {"name": "쾌속 베기", "power": 25, "type": "물리", "side": "적", "count": "1인", "hits": 3, "tags": [],
             "sprite": "", "motion": "behind",
             "desc": ["3회 연속 베기."]},
             {"name": "파도 치는 검격", "power": 30, "type": "마법", "side": "적", "count": "2인", "hits": 3, "tags": [],
             "sprite": "", "motion": "cast",
             "desc": ["3회 연속 베기."]},
             {"name": "대양의 마법", "power": 10, "type": "마법", "side": "적", "count": "5인", "hits": 5, "tags": [],
             "sprite": "", "motion": "cast", "split": 5,
             "desc": ["파도를 부르는 마법이다."]},
        ],
    },
    # ─────────────────────────────────────────────────────────────
    #  남부 도전보스
    # ─────────────────────────────────────────────────────────────
    "마리나": {
        "name":          "마리나",
        "defense_skills": ["회피", "원호"],
        "type":          "normal",
        "level":         82,
        "phys_level":    87,
        "magic_level":   81,
        "hp_max":        3460,
        "mp_max":        3700,
        "sprite":        "assets/SSG2/SSG2_battle.png",
        "profile":       "assets/SSG2/SSG2_profile.png",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.2,
        "overview": [
            "마리나 루나",
            "",
            "엘 로마올라스의 부선장입니다.",
            "선장과는 절친한 사이로, 해적단의 주요 전투원입니다.",
            "",
            "단순 힘싸움으로는 그녀가 선장보다 한 수 위입니다.",
            "강함에 비해 무게를 잡는 성격은 아닌 것 같습니다.",
        ],
        "passives": [
            {
                "name": "엘 로마올라스의 부선장",
                "desc": [
                    "자신이 적에게 가하는 모든 피해가 30% 증가합니다.",
                ],
                "effects": [{"kind": "deal_mult", "value": 1.3}]
            },
            {
                "name": "쾌검",
                "desc": [
                    "공격 횟수가 3 이상인 모든 스킬의 피해량이 30% 증가합니다.",
                    "만약 이전 턴에 회피에 성공했다면 공격 횟수가 3 이상인 모든 스킬의 최종 위력이 10 증가합니다.",
                ]
            },
            {
                "name": "마력 발산 - 부선장",
                "threshold": 0.5,   # 최대 마력의 50% 소모 시 마력 발산 발동 (캐릭터별 조정 가능)
                "desc": [
                    "'마력 발산' 상태가 되면 공격 횟수가 3 이상인 모든 스킬의 공격 횟수가 2 증가합니다.",
                    "또한 자신의 최대 체력이 50% 이하라면 공격 횟수가 3 이상인 모든 스킬의 공격 대상이 1 증가합니다.",
                ]
            },
            {
                "name": "바다의 처형자",
                "desc": [
                    "자신이 공격하는 대상이 대상 최대 체력의 30% 이하라면 해당 적에게 가하는 피해량이 30% 증가합니다.",
                ]
            },
            {
                "name": "나는 검이 두 자루야~",
                "desc": [
                    "공격 횟수가 3 이상인 모든 스킬의 공격 대상이 1 증가합니다.",
                ]
            },
        ],
        "speed_min": 20, "speed_max": 20,
        "skills": [
            {"name": "난무!", "power": 5, "type": "물리", "side": "적", "count": "1인", "hits": 5, "tags": [],
             "sprite": "", "motion": "stationary", "split": 3,
             "effect_self": "assets/SSG/SSG_nanmu_self.png", "effect_target": "assets/SSG/SSG_wave_slash.png",
             "sound": "assets/SSG/SSG_nanmu.mp3",
             "desc": ["적을 마구 벱니다."]},
            {"name": "쾌속 베기!", "power": 25, "type": "물리", "side": "적", "count": "1인", "hits": 3, "tags": [],
             "sprite": "", "motion": "behind",
             "desc": ["빠르게 달려들어 적을 3번 벱니다."]},
             {"name": "가끔은 한 방도 필요한 법이지~", "power": 100, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [],
             "sprite": "", "motion": "smite",
             "desc": ["강한 한 방을 날립니다."]},
             {"name": "파도를 쳐라, 나는 너를 치겠다!", "power": 30, "type": "마법", "side": "적", "count": "1인", "hits": 3, "tags": [],
             "sprite": "", "motion": "cast",
             "desc": ["파도 치듯 검을 빠르게 내려친다."]},
             {"name": "아 귀찮아~", "power": 0, "type": "물리", "side": "자신", "count": "1인", "hits": 0, "tags": [],
             "sprite": "", "motion": "command",
             "desc": ["마리나가 그 어떤 행동도 하지 않는다."]},
        ]
    },
    # ─────────────────────────────────────────────────────────────
    #  남부 극한보스
    # ─────────────────────────────────────────────────────────────    #  (미작성)
    # ─────────────────────────────────────────────────────────────
    #  북부 잡몹
    # ─────────────────────────────────────────────────────────────
    "wolf": {
        "title":         "",
        "name":          "북부 거대 늑대",
        "type":          "normal",
        "level_min":     64,
        "level_max":     71,
        "hp_min":        750,
        "hp_max_range":  880,
        "mp_max":        10,
        "phys_min":      65,
        "phys_max":      73,
        "magic_min":     5,
        "magic_max":     7,
        "sprite":        "assets/north_normal/wolf.png",
        "profile":       "assets/north_normal/wolf_profile.png",
        "bgm": "assets/north_normal/north.mp3",
        "sprite_scale":  0.3,
        "click_w_ratio": 0.5,
        "background":    "assets/north_normal/north_normal_BG.png",
        "speed_min": 9, "speed_max": 16,
        "overview": [
            "북부 거대 늑대",
            "",
            "딱히 설명할 것이 없는 늑대와 닮은 마물입니다.",
            "공격의 위력이 약하니 공격을 회피하는 것이 좋은 상대법입니다.",
        ],
        "skills": [
            {"name": "물고물고물고물기", "power": 11, "type": "물리", "side": "적", "count": "1인", "hits": 5, "tags": [], "motion": "stationary",
             "sprite": ""},
        ],
    },
    "bear": {
        "title":         "",
        "name":          "괴물 곰",
        "type":          "normal",
        "level_min":     72,
        "level_max":     78,
        "hp_min":        900,
        "hp_max_range":  1000,
        "mp_max":        30,
        "phys_min":      71,
        "phys_max":      79,
        "magic_min":     10,
        "magic_max":     13,
        "sprite":        "assets/north_normal/bear.png",
        "profile":       "assets/north_normal/bear_profile.png",
        "bgm": "assets/north_normal/north.mp3",
        "sprite_scale":  0.4,
        "click_w_ratio": 0.5,
        "background":    "assets/north_normal/north_normal_BG.png",
        "speed_min": 0, "speed_max": 1,
        "overview": [
            "괴물 곰",
            "",
            "북부의 생태계를 파괴한 마물입니다.",
            "강한 힘을 가졌지만 힘에 부쳐 행동하지 못 할 때가 있으니 그때를 노리는 것이 좋습니다.",
        ],
        "skills": [
            {"name": "우어엉", "power": 30, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [], "motion": "stationary",
             "sprite": "","desc": ["대상이 수비 스킬 '방어' 를 사용했다면 최종 위력이 15가 됩니다."],
             "cond": [
                    {"if": "target_guard", "power_set": 15},   # 수비(방어) 시 위력 10
                ]},
        ],
    },
    "ice_golem": {
        "title":         "",
        "name":          "빙석",
        "type":          "normal",
        "level_min":     50,
        "level_max":     50,
        "hp_min":        500,
        "hp_max_range":  500,
        "mp_max":        100,
        "phys_min":      15,
        "phys_max":      15,
        "magic_min":     30,
        "magic_max":     40,
        "sprite":        "assets/north_normal/ice_golem.png",
        "profile":       "assets/north_normal/ice_golem_profile.png",
        "bgm": "assets/north_normal/north.mp3",
        "sprite_scale":  0.4,
        "click_w_ratio": 0.5,
        "background":    "assets/north_normal/north_normal_BG.png",
        "speed_min": 0, "speed_max": 0,
        "overview": [
            "빙석",
            "",
            "북부에 어째서인지 존재하는 정지형 마물입니다.",
            "그 어떤 행동도 하지 않으나, 일단 처치해두는 것이 좋을 것 같네요.",
        ],
        "skills": [
            {"name": "...", "power": 0, "type": "마법", "side": "자신", "count": "1인", "hits": 1, "tags": ["지원"], "motion": "command",
             "sprite": ""},
        ],
    },
    # ─────────────────────────────────────────────────────────────
    #  북부 엘리트
    # ─────────────────────────────────────────────────────────────
    "snow_slime": {
        "title":         "",
        "name":          "눈 슬라임",
        "type":          "normal",
        "level_min":     60,
        "level_max":     60,
        "hp_min":        800,
        "hp_max_range":  800,
        "mp_max":        100,
        "phys_min":      55,
        "phys_max":      55,
        "magic_min":     50,
        "magic_max":     50,
        "sprite":        "assets/north_normal/snow_golem.png",
        "profile":       "assets/north_normal/snow_golem_profile.png",
        "bgm": "assets/north_normal/north.mp3",
        "sprite_scale":  0.7,
        "click_w_ratio": 0.5,
        "background":    "assets/north_normal/north_normal_BG.png",
        "speed_min": 1, "speed_max": 1,
        "overview": [
            "눈 슬라임",
            "",
            "발견된 슬라임의 변종 중 가장 피해 규모가 큰 슬라임입니다.",
            "자체는 그다지 강한 것 같지 않으나, 넓은 공격 범위를 가져 처리해주는 것이 좋을 것입니다.",
        ],
        "skills": [
            {"name": "눈사태", "power": 3, "type": "마법", "side": "적", "count": "5안", "hits": 5, "tags": [""], "motion": "charge",
             "sprite": ""},
        ],
    },
    # ─────────────────────────────────────────────────────────────
    #  북부 중간보스
    # ─────────────────────────────────────────────────────────────
    "ice_knight": {
        "name":          "얼어붙은 기사",
        "type":          "normal",
        "level":         70,
        "phys_level":    70,
        "magic_level":   30,
        "hp_max":        1500,
        "mp_max":        540,
        "sprite":        "assets/north_normal/ice_knight.png",
        "profile":       "assets/north_normal/ice_knight_profile.png",
        "background":    "assets/north_normal/ice_knight_BG.png",
        "bgm":    "assets/north_normal/north_normal_BG.mp3",
        "sprite_scale":  0.5,
        "click_w_ratio": 0.2,
        "overview": [
            "얼어붙은 기사",
            "",
            "북부의 혹한에 얼어붙은 기사입니다.",
            "그 강함을 보아 그는 중앙 왕국의 기사단이었던 것 같습니다.",
            "",
            "마력이 얼어붙어 죽지도 못 하고 있는 그는, 지금 피아식별을 하지 못 하고 있습니다.",
        ],
        "passives": [
            {
                "name": "얼어붙은 기사의 갑옷",
                "desc": [
                    "모든 피해로부터 받는 피해가 20% 감소합니다.",
                ],
                "effects": [{"kind": "take_mult", "value": 0.8}]
            },
        ],
        "speed_min": 0, "speed_max": 1,
        "skills": [
            {"name": "베기", "power": 30, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [],
             "sprite": "", "motion": "smite",
             "effect_self": "", "effect_target": "",
             "sound": ""},
            {"name": "마물이로구나...", "power": 15, "type": "물리", "side": "적", "count": "1인", "hits": 3, "tags": [],
             "sprite": "", "motion": "smite",
             "effect_self": "", "effect_target": "",
             "sound": ""},
            {"name": "너는 뭐지? 그리고... 나는?", "power": 0, "type": "물리", "side": "자신", "count": "1인", "hits": 1, "tags": ["지원"],
             "sprite": "", "motion": "command",
             "effect_self": "", "effect_target": "",
             "sound": ""},
            {"name": "■■■■님... 지금 가겠습니다...", "power": 100, "type": "물리", "side": "적", "count": "5인", "hits": 10, "tags": [],
             "sprite": "", "motion": "charge",
             "effect_self": "", "effect_target": "",
             "sound": "", "desc": ["기사가 이성을 잃고 눈앞에 보이는 모든 것을 베어 나갑니다.", "대상이 수비 스킬 '방어' 를 사용했다면 최종 위력이 10이 됩니다."],
             "cond": [
                    {"if": "target_guard", "power_set": 10},   # 수비(방어) 시 위력 1
                ]},
        ],
    },
    # ─────────────────────────────────────────────────────────────
    #  북부 최종보스
    # ─────────────────────────────────────────────────────────────
    "north_wyvern": {
        "name":          "북부 와이번",
        "type":          "normal",
        "level":         70,
        "phys_level":    70,
        "magic_level":   70,
        "hp_max":        2000,
        "mp_max":        500,
        "sprite":        "assets/north_normal/north_wyvern.png",
        "profile":       "assets/north_normal/inorth_wyvern_profile.png",
        "background":    "assets/north_normal/north_wyvern_BG.png",
        "bgm":    "assets/north_normal/north_wyvern.mp3",
        "sprite_scale":  0.5,
        "click_w_ratio": 0.2,
        "overview": [
            "북부 와이번",
            "",
            "용과 닮았지만 용이 아닌, 마물에 그친 종족입니다.",
            "지성을 가지고 있지는 않지만 강함은 용에 근접한 고위험도의 마물입니다.",
            "",
            "그다지 당신에게 관심을 가지고 있는 것 같지 않습니다.",
        ],
        "passives": [
            {
                "name": "용과 닮은 외피",
                "desc": [
                    "모든 피해로부터 받는 피해가 30% 감소합니다.",
                ],
                "effects": [{"kind": "take_mult", "value": 0.7}]
            },
        ],
        "speed_min": 10, "speed_max": 20,
        "skills": [
            {"name": "달려들기", "power": 30, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [],
             "sprite": "", "motion": "stationary",
             "effect_self": "", "effect_target": "",
             "sound": ""},
            {"name": "영하 브레스", "power": 5, "type": "물리", "side": "적", "count": "1인", "hits": 10, "tags": [],
             "sprite": "", "motion": "cast",
             "effect_self": "", "effect_target": "",
             "sound": ""},
            {"name": "승천", "power": 200, "type": "물리", "side": "적", "count": "5인", "hits": 3, "tags": [],
             "sprite": "", "motion": "charge",
             "effect_self": "", "effect_target": "",
             "sound": "", "desc": ["와이번이 용의 모습을 따라합니다.", "대상이 수비 스킬 '방어' 를 사용했다면 최종 위력이 20이 됩니다."],
             "cond": [
                    {"if": "target_guard", "power_set": 10},   # 수비(방어) 시 위력 1
                ]},
        ],
    },
    # ─────────────────────────────────────────────────────────────
    #  북부 도전보스
    # ─────────────────────────────────────────────────────────────    #  (미작성)
    # ─────────────────────────────────────────────────────────────
    #  북부 극한보스
    # ─────────────────────────────────────────────────────────────
    "snowdin_wild_boar_king": {
        "title":         "",
        "name":          "설산 멧돼지 왕",
        "type":          "boss",
        "level":         88,
        "phys_level":    88,
        "magic_level":   88,
        "hp_max":        26789,
        "mp_max":        5000,
        "sprite":        "assets/north_normal/snowdin_wild_boar_king.png",
        "profile":       "assets/north_normal/snowdin_wild_boar_king.png",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.5,
        "background":    "assets/battle_bg_forest.png",
        "speed_min": 1, "speed_max": 10,
        "overview": [
            "빙설 속에 살면서 얼어붙은 동족들이 깨어나기를 기다리고 있는 「왕」.",
            "아주 먼 옛날, 황야의 사냥꾼들 사이에서는 발길이 끊긴 얼어붙은 대지가 생기를 되찾고, 불청객이 얼음 동굴의 안녕을 방해할 때, 설산 멧돼지 족속을 위대",
            "하게 이끌 「왕」이 잠에서 깨어나 쌓인 눈을 털어내고 예의를 모르는 손님에게 대가를 치르게 할 거라는 전설이 전해 내려온다",
        ],
        "skills": [
            {"name": "돌진", "power": 999, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [], "motion": "behind",
             "sprite": ""},
        ],
    },
    # ─────────────────────────────────────────────────────────────
    #  마왕
    # ─────────────────────────────────────────────────────────────    #  (미작성)



    # ─────────────────────────────────────────────────────────────
    #  아군
    # ─────────────────────────────────────────────────────────────
}
ALLY_DEFS = {
    "주인공": {
        "name":          "주인공",
        "defense_skills": ["방어", "회피", "원호"],
        "type":          "player",
        "level":         29,
        "phys_level":    30,
        "magic_level":   1,
        "hp_max":        500,
        "mp_max":        500,
        "sprite":        "assets/MC/main_character_B_battle.png",
        "profile":       "assets/MC/main_B_profile.png",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.2,
        "speed":         5,
        "skills": [
            {"name": "난타", "power": 30, "type": "물리", "side": "적", "count": "1인", "hits": 3, "tags": [], "motion": "stationary","split": 1,
             "sprite": "", "desc": ["물리 난타"]},
        ],
    },
    "아우렐리우스": {
        "name":          "아우렐리우스",
        "defense_skills": ["방어", "원호"],
        "type":          "ally",
        "level":         81,
        "phys_level":    85,
        "magic_level":   82,
        "hp_max":        3920,
        "mp_max":        3000,
        "sprite":        "assets/SHM/SHM_battle.png",
        "profile":       "assets/SHM/SHM_profile.png",
        "sprite_scale":  0.3,
        "click_w_ratio": 0.2,
        "overview": [
            "플라비우스 아우렐리우스",
            "",
            "그는 서부의 신호입니다.",
            "타인을 돕고 치유하는 것에 주로 시간을 씁니다.",
            "",
            "그가 회복 마법을 주로 사용한다고 얕잡아 보아서는 안 됩니다.",
            "'신호' 의 칭호를 가졌다는 것은, 이 세계에서 손에 꼽는 강자라는 의미입니다.",
            "",
            "그가 따르고 있는 신은 존재하지 않고, 그도 그것을 알고 있습니다.",
            "그럼에도 그가 신을 따르는 이유는 타인을 돕는 행위에 의미를 부여하기 위함입니다.",
        ],
        "passives": [
            {
                "name": "신이 없는 세계의 사제",
                "desc": [
                    "모든 피해로부터 받는 피해가 10% 감소합니다.",
                    "자신과 아군에게 가하는 회복 효과가 50% 증가합니다.",
                ],
                "effects": [{"kind": "take_mult", "value": 0.9}]
            },
            {
                "name": "황금 빛으로 빛나는",
                "desc": [
                    "매 턴이 시작될 때마다 자신의 전체 마력의 5%를 소모합니다.",
                    "이때 소모한 마력만큼 아군 모두에게 회복 효과를 적용합니다.",
                ]
            },
            {
                "name": "마력 발산 - 대리인",
                "threshold": 0.5,   # 최대 마력의 50% 소모 시 마력 발산 발동 (캐릭터별 조정 가능)
                "desc": [
                    "'마력 발산' 상태가 되면 회복 효과를 가진 모든 스킬의 최종 위력이 20 증가합니다.",
                    "자신 또는 아군에게 회복 효과를 적용할 때마다 적용된 회복량만큼 보호막을 추가로 부여합니다.",
                ]
            },
            {
                "name": "성스러운 육체",
                "desc": [
                    "자신이 적에게 피해를 받으면 다음 턴이 시작될 때 받은 피해만큼 보호막을 얻습니다.",
                    "이 효과로 얻는 보호막은 보호막을 전부 소모하기 전까지 사라지지 않으며, 무한히 중첩됩니다.",
                ]
            },
            {
                "name": "서부의 신호",
                "desc": [
                    "자신에게 회복 효과가 적용되면 다음 턴에 물리 스킬의 최종 위력이 10 증가합니다.",
                    "이 효과는 누구의 회복 효과든 발동이 가능하며, 중첩되지 않고 다음 턴이 되면 사라집니다.",
                ]
            },
        ],
        "speed_min": 8, "speed_max": 12,
        "skills": [
            {"name": "성스러운 빛", "power": 300, "type": "마법", "side": "아군", "count": "1인", "hits": 1, "cost": 2000, "tags": ["회복", "지원"], "motion": "command",
             "sprite": "", "desc": ["아군 하나를 회복한다."]},
            {"name": "심판의 일격", "power": 90, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [], "motion": "stationary",
             "sprite": "", "desc": ["적에게 물리 피해를 입힌다."]},
            {"name": "축복", "power": 40, "type": "마법", "side": "아군", "count": "5인", "hits": 1, "tags": ["회복", "지원"], "motion": "command",
             "sprite": "", "desc": ["아군 전체를 회복한다."]},
        ]
    },
    "금강": {
        "name":          "금강",
        "defense_skills": ["방어", "회피", "원호"],
        "type":          "ally",
        "level":         79,
        "phys_level":    87,
        "magic_level":   63,
        "hp_max":        3130,
        "mp_max":        1000,
        "sprite":        "assets/SFG/SFG_battle.png",
        "profile":       "assets/SFG/SFG_profile.png",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.2,
        "overview": [
            "금강",
            "",
            "그녀는 동부의 신호입니다.",
            "금강석과 비슷한 성질로 신체를 강화하는 마법만을 고수합니다.",
            "",
            "그녀는 2년 전, 19살이라는 어린 나이에 '신호' 의 칭호를 받았습니다.",
            "그렇기에 다른 '신호' 들에 비해 확실히 어리숙한 면이 돋보이는 자입니다.",
            "",
            "만만해 보이지만, 그녀 또한 이 세계에서 손에 꼽는 강자라는 것을 잊어서는 안 됩니다.",
        ],
        "passives": [
            {
                "name": "금강석",
                "desc": [
                    "모든 피해로부터 받는 피해가 10% 감소합니다.",
                    "자신이 적에게 가하는 모든 피해가 10% 증가합니다.",
                ],
                "effects": [{"kind": "take_mult", "value": 0.9}, {"kind": "deal_mult", "value": 1.1}]
            },
            {
                "name": "집착에 가까운 단련",
                "desc": [
                    "'금강' 외의 다른 마법 스킬을 사용할 수 없습니다.",
                ]
            },
            {
                "name": "마력 발산 - 금강석",
                "threshold": 0.5,   # 최대 마력의 50% 소모 시 마력 발산 발동 (캐릭터별 조정 가능)
                "desc": [
                    "'마력 발산' 상태가 되면 항상 '금강' 상태로 취급됩니다.",
                    "'금강석' 으로 얻는 피해 감소 효과가 60%로 증가하고, 모든 물리 스킬의 최종 위력이 15 증가합니다.",
                ]
            },
            {
                "name": "금강석과도 같은 육체",
                "desc": [
                    "매 턴이 시작될 때마다 최대 체력의 10% 만큼 보호막을 얻습니다.",
                    "대신 '금강' 상태가 되면 매 턴이 시작될 때마다 최대 체력의 30% 만큼 보호막을 얻습니다.",
                ]
            },
            {
                "name": "동부의 신호",
                "desc": [
                    "마법 스킬로 피해를 입으면 공격자에게 (물리 레벨)*2 만큼 물리 피해를 입힙니다.",
                ]
            },
        ],
        "speed_min": 13, "speed_max": 17,
        "skills": [
            {"name": "금강", "power": 70, "type": "마법", "side": "자신", "count": "1인", "hits": 1, "tags": ["지원"], "motion": "command",
             "sprite": "", "desc": ["'금강' 상태가 된다."]},
            {"name": "철권", "power": 100, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [], "motion": "stationary",
             "sprite": "", "desc": ["강력한 물리 일격."]},
            {"name": "연환격", "power": 35, "type": "물리", "side": "적", "count": "1인", "hits": 3, "tags": [], "motion": "stationary",
             "sprite": "", "desc": ["3회 연속 공격."]},
        ]
    },
    "마리": {
        "name":          "마리",
        "defense_skills": ["회피"],
        "type":          "ally",
        "level":         87,
        "phys_level":    83,
        "magic_level":   88,
        "hp_max":        2780,
        "mp_max":        5000,
        "sprite":        "assets/SSG/SSG_battle.png",
        "profile":       "assets/SSG/SSG_profile.png",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.2,
        "overview": [
            "마리 솔",
            "",
            "그녀는 남부의 신호입니다.",
            "해적이지만 악인보다는 선인에 가까운 자입니다.",
            "",
            "남부는 수 많은 섬으로 이루어진 구역이기 때문에",
            "그녀는 남부 섬들 간의 교류와 마물의 토벌을 책임지고 있습니다.",
            "",
            "해적이긴 하지만요.",
        ],
        "passives": [
            {
                "name": "엘 로마올라스의 선장",
                "desc": [
                    "모든 피해로부터 받는 피해가 20% 감소합니다.",
                    "전투 지역이 엘 로마올라스라면 매 턴이 시작될 때마다 모든 아군이 전체 마력의 20%를 회복합니다.",
                ],
                "effects": [{"kind": "take_mult", "value": 0.8}]
            },
            {
                "name": "쾌검",
                "desc": [
                    "공격 횟수가 3 이상인 모든 스킬의 피해량이 30% 증가합니다.",
                    "만약 이전 턴에 회피에 성공했다면 공격 횟수가 3 이상인 모든 스킬의 최종 위력이 10 증가합니다.",
                ]
            },
            {
                "name": "마력 발산 - 선장",
                "threshold": 0.5,   # 최대 마력의 50% 소모 시 마력 발산 발동 (캐릭터별 조정 가능)
                "desc": [
                    "'마력 발산' 상태가 되면 모든 지원 스킬의 최종 위력이 25 증가합니다.",
                    "또한 공격 횟수가 3 이상인 모든 스킬의 공격 횟수가 1 증가하며, 피해량이 10% 증가합니다.",
                    "'엘 로마올라스의 선장' 이 활성화되어 있다면",
                    "매 턴이 시작될 때마다 모든 아군에게 최대 체력의 10%의 보호막을 부여합니다.",
                ]
            },
            {
                "name": "사기 증진",
                "desc": [
                    "자신 또는 아군에게 지원 스킬을 사용하면 이번 턴 동안 모든 아군의 최종 위력이 10 증가합니다.",
                ]
            },
            {
                "name": "승선",
                "desc": [
                    "자신의 체력이 최대 체력의 70% 이하로 내려갔다면 다음 턴이 시작될 때 보호막을 2000 얻습니다.",
                ]
            },
            {
                "name": "남부의 신호",
                "desc": [
                    "아군에게 지원 스킬을 사용하면 해당 아군에게 '선원' 중첩을 1 부여합니다.",
                    "'선원': 중첩당 최종 위력이 1 증가합니다. 최대 10회 중첩 가능합니다.",
                ]
            },
        ],
        "speed_min": 21, "speed_max": 33,
        "skills": [
            {"name": "난무", "power": 30, "type": "물리", "side": "적", "count": "1인", "hits": 4, "tags": [],
             "sprite": "", "motion": "stationary", "split": 3,
             "effect_self": "assets/SSG/SSG_nanmu_self.png", "effect_target": "assets/SSG/SSG_nanmu_target.png",
             "sound": "assets/SSG/SSG_nanmu.mp3",
             "desc": ["4회 연속 공격."]},
            {"name": "선장의 호령", "power": 35, "type": "마법", "side": "아군", "count": "5인", "hits": 1, "tags": ["지원"],
             "sprite": "", "motion": "command",
             "effect_self": "assets/SSG/SSG_command_self.png", "effect_target": "assets/SSG/SSG_command_target.png",
             "desc": ["아군 전체를 강화한다."]},
            {"name": "쾌속 베기", "power": 50, "type": "물리", "side": "적", "count": "1인", "hits": 3, "tags": [],
             "sprite": "", "motion": "behind",
             "desc": ["3회 연속 베기."]},
        ]
    },
    "막심 오그네프": {
        "name":          "막심 오그네프",
        "defense_skills": ["방어"],
        "type":          "ally",
        "level":         90,
        "phys_level":    89,
        "magic_level":   91,
        "hp_max":        4160,
        "mp_max":        1000,
        "sprite":        "assets/SSM/super_snow_man.png",
        "profile":       "assets/SSM/maxim_profile.png",
        "sprite_scale":  0.5,
        "click_w_ratio": 0.2,
        "overview": [
            "막심 오그네프",
            "",
            "그는 북부의 신호입니다.",
            "북부는 마물의 출현이 잦기 때문에 항상 긴장 상태를 유지합니다.",
        ],
        "passives": [
            {
                "name": "북부 전선의 지휘관",
                "desc": [
                    "자신이 적에게 가하는 모든 피해가 30% 증가합니다.",
                    "대상이 마물 혹은 마족이라면 추가 10% 증가합니다.",
                ],
                "effects": [{"kind": "deal_mult", "value": 1.3}, {"kind": "deal_mult", "value": 1.1, "vs": ["마물", "마족"]}]
            },
            {
                "name": "총공세",
                "desc": [
                    "매 턴이 시작될 때마다 현재 마력의 10%를 소모합니다.",
                    "소모한 마력만큼 자신이 사용하는 모든 마법 스킬이 추가 고정 피해를 입힙니다.",
                ]
            },
            {
                "name": "마력 발산 - 지휘관",
                "threshold": 0.5,   # 최대 마력의 50% 소모 시 마력 발산 발동 (캐릭터별 조정 가능)
                "desc": [
                    "자신의 (현재 마력%÷2)% 만큼 자신이 가하는 피해량이 증가합니다.",
                    "",
                    "자신을 제외한 모든 아군에게 다음 효과를 부여합니다.",
                    "모든 공격 스킬의 최종 위력이 10 증가합니다.",
                    "모든 수비 스킬의 최종 위력이 10 증가합니다.",
                    "속도의 최솟값과 최댓값이 1 증가합니다.",
                ]
            },
            {
                "name": "고양감",
                "desc": [
                    "진행된 턴 수에 따라 다음 효과를 얻습니다.",
                    "1~5턴: 매 턴이 시작될 때마다 자신의 최대 마력의 5%를 회복합니다.",
                    "6~19턴: 자신이 적에게 가하는 모든 피해가 30% 증가합니다.",
                    "20턴~: 모든 스킬의 최종 위력이 10 증가하고 이전까지의 효과를 모두 얻습니다.",
                ]
            },
            {
                "name": "회로 작열",
                "desc": [
                    "자신의 턴이 시작될 때, 현재 마력이 최대 마력의 30% 이하라면 최대 체력의 10% 만큼 피해를 받습니다.",
                ]
            },
            {
                "name": "북부의 신호",
                "desc": [
                    "모든 행동 제어에 면역이 됩니다.",
                    "또한 속도의 값이 변하지 않으며, 1로 고정됩니다.",
                ]
            },
        ],
        "speed": 1,
        "skills": [
            {"name": "화염포", "power": 120, "type": "마법", "side": "적", "count": "1인", "hits": 1, "tags": [], "motion": "cast",
             "sprite": "", "desc": ["강력한 마법 일격."]},
            {"name": "북부의 불길", "power": 60, "type": "마법", "side": "적", "count": "5인", "hits": 1, "tags": [], "motion": "cast",
             "sprite": "", "desc": ["적 전체에게 마법 피해."]},
            {"name": "관통사격", "power": 90, "type": "물리", "side": "적", "count": "1인", "hits": 1, "tags": [], "motion": "behind",
             "sprite": "", "desc": ["물리 관통 공격."]},
        ]
    },
}

# ══════════════════════════════════════════════════════════════════
#   스킬 필드 기본값 보강
#   (새로 추가한 스킬에 일부 필드가 빠져도 KeyError 가 나지 않도록,
#    모든 적/아군 스킬에 표준 필드를 채워 넣는다.)
# ══════════════════════════════════════════════════════════════════
def _normalize_skill_fields(defs):
    defaults = {
        "tags": [],
        "effect_self": "",
        "effect_target": "",
        "sound": "",
        "sprite": "",
        "motion": "behind",
        "count": "1인",
        "hits": 1,
        "side": "적",
        "desc": [],
    }
    for d in defs.values():
        for sk in d.get("skills", []):
            for k, v in defaults.items():
                if k not in sk:
                    sk[k] = list(v) if isinstance(v, list) else v

_normalize_skill_fields(ENEMY_DEFS)
_normalize_skill_fields(ALLY_DEFS)