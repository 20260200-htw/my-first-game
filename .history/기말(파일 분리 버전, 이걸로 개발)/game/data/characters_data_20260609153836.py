# ── 수비 스킬 공용 정의 ───────────────────────────────────────────
# def_kind: "guard"(방어/자신 보호막) / "dodge"(회피/자신) / "assist"(원호/아군)
# 캐릭터 정의에 "defense_skills": ["방어","회피","원호"] 처럼 이름 리스트로 지정.
DEFENSE_SKILLS = {
    "방어": {"name": "방어", "power": 50, "type": "물리", "side": "자신", "count": "단일",
            "hits": 1, "tags": ["지원"], "motion": "command", "def_kind": "guard",
            "sprite": "", "desc": ["자신에게 보호막을 둘러 피해를 막는다."]},
    "회피": {"name": "회피", "power": 50, "type": "물리", "side": "자신", "count": "단일",
            "hits": 1, "tags": ["지원"], "motion": "command", "def_kind": "dodge",
            "sprite": "", "desc": ["회피 자세. 위력보다 약한 공격을 무효화한다."]},
    "원호": {"name": "원호", "power": 50, "type": "물리", "side": "아군", "count": "단일",
            "hits": 1, "tags": ["지원"], "motion": "command", "def_kind": "assist",
            "sprite": "", "desc": ["아군에게 보호막을 부여한다.",
                                    "그 보호막이 막은 피해만큼 자신이 대신 받는다."]},
}

ENEMY_DEFS = {
    "벨라": {
        "title":         "왕국 기사단장",
        "name":          "벨라",
        "type":          "boss",
        "level":         100,
        "phys_level":    100,
        "magic_level":   100,
        "hp_max":        10000,
        "mp_max":        10000,
        "sprite":        "assets/KL/KL_battle.png",
        "profile":       "assets/KL/KL_profile.png",
        "sprite_scale":  0.3,
        "click_w_ratio": 0.2,
        "background":    "assets/KL/KL_Test_BG.png",
        "floor":    "assets/KL/KL_G_F.png",
        "bgm":           "assets/KL/knight_leader_WWE.mp3",
        "overview": [
            "벨라 트릭스",
            "",
            "그녀는 중앙 왕국의 기사단장입니다.",
            "적의를 가지고 싸움을 건 것은 아닌 것으로 보입니다.",
            "",
            "그렇다고 해서 당신을 죽이지 않는다는 보장은 없으니",
            "최선을 다해서 그녀의 의도에 맞춰주는 것을 권장합니다.",
            "",
            "그녀와 싸우는 것은 이 세계에서 할 수 있는",
            "가장 멍청한 짓 중 하나일 것입니다.",
        ],
        "passives": [
            {
                "name": "'적당히 상대해 드리겠습니다.'",
                "desc": [
                    "벨라가 약화된 스킬을 사용합니다.",
                ]
            },
            {
                "name": "왕국 기사단장",
                "desc": [
                    "모든 피해로부터 받는 피해가 30% 감소합니다.",
                    "자신이 적에게 가하는 모든 피해가 50% 증가합니다.",
                ],
                "effects": [{"kind": "take_mult", "value": 0.7}, {"kind": "deal_mult", "value": 1.5}]
            },
            {
                "name": "기사단장의 명령",
                "desc": [
                    "이번 전투에서 왕국 기사단이 참전하지 않습니다.",
                    "또한 벨라가 '시험' 을 얻습니다. 자신이 사용하는 모든 스킬의 최종 위력이 50 감소합니다.",
                ],
                "effects": [{"kind": "power_add", "value": -50}]
            },
            {
                "name": "마력 발산 - 지옥불",
                "desc": [
                    "'마력 발산' 상태가 되면 모든 스킬의 최종 위력이 50 증가합니다.",
                    "매 턴이 시작될 때마다 (물리 레벨+마법 레벨)*1 만큼 모든 적에게 마법 피해를 입힙니다.",
                ],
                "effects": [{"kind": "power_add", "value": 50}]
            },
            {
                "name": "지옥불 결계",
                "desc": [
                    "매 턴이 시작될 때마다 보호막을 1000 만큼 얻습니다.",
                    "적에게 피해를 받으면 즉시 파괴되며, 다음 턴이 되기 전까지 보호막을 얻지 않습니다.",
                ]
            },
            {
                "name": "집중",
                "desc": [
                    "자신이 사용하는 스킬의 최종 위력이 50 이상이 되었을 때마다",
                    "해당 턴에 사용하는 스킬의 최종 위력이 10 증가하고 피해량이 20% 증가합니다.",
                ]
            },
            {
                "name": "초재생",
                "desc": [
                    "매 턴이 시작될 때마다 자신의 전체 마력의 1%를 소모합니다.",
                    "이때 소모한 마력*2 만큼 체력을 회복하고 해당 턴 동안 모든 스킬의 최종 위력이 5 증가합니다.",
                ]
            },
            {
                "name": "품위 유지",
                "desc": [
                    "한 턴에 500 이상의 피해를 받으면 다음 턴이 시작될 때 받았던 피해량의 50% 만큼 체력을 회복합니다.",
                ]
            },
            {
                "name": "압도",
                "desc": [
                    "자신이 사용하는 스킬의 최종 위력이 1000 이상이고 대상의 레벨이 자신보다 낮다면",
                    "해당 턴에 사용하는 스킬이 대상 최대 체력의 100% 만큼 추가 고정 피해를 입힙니다.",
                ]
            },
            {
                "name": "빠르고 정확하게",
                "desc": [
                    "매 턴이 시작될 때마다 자신의 속도가 20 이상이라면 해당 턴에 사용하는 스킬에 '필중' 효과가 적용됩니다.",
                ]
            },
            {
                "name": "전황 분석",
                "desc": [
                    "매 턴이 시작될 때마다 '전황 분석' 중첩을 1 얻습니다.",
                    "중첩 당 자신이 가하는 모든 피해가 5% 증가합니다.",
                ]
            },
            {
                "name": "가르침을 받은 몸",
                "desc": [
                    "???가 전투에 참전하면 '학습된 공포' 중첩을 1 얻습니다.",
                    "이후 매턴이 시작될 때마다 중첩을 1 얻으며, 중첩 당 모든 스킬의 최종 위력이 50 감소합니다.",
                ]
            },
        ],
        "buffs": {
            "시험": {
                "desc": [
                    "자신이 사용하는 모든 스킬의 최종 위력이 50 감소합니다.",
                ]
            },
        },
        "skills": [
            {
                "name":   "찌르기",
                "power":  50,
                "type":   "물리",
                "side": "적", "count": "단일",
                "hits":   1,
                "tags":   ["필중"],
                "sprite": "assets/KL/KL_skills_1.png",
                "motion": "stationary",
                "desc": [
                    "반드시 주인공을 대상으로 지정함",
                    "대상이 수비 스킬 '방어' 를 사용하였다면 피해량 -50%",
                ]
            },
            {
                "name":   "피하는 것이 좋을 겁니다",
                "power":  80,
                "type":   "물리",
                "side": "적", "count": "단일",
                "hits":   1,
                "tags":   ["필중"],
                "sprite": "assets/KL/KL_skills_2.png",
                "motion": "stationary",
                "desc": [
                    "반드시 주인공을 대상으로 지정함",
                    "대상이 수비 스킬 '방어' 를 사용하였다면 피해량 +500%",
                    "대상이 수비 스킬 '회피' 를 사용하였다면 최종 위력이 0으로 고정됨",
                ]
            },
            {
                "name":   "이번 건 피할 수 없을 겁니다",
                "power":  40,
                "type":   "물리",
                "side": "적", "count": "5인",
                "hits":   1,
                "tags":   ["난사"],
                "sprite": "assets/KL/KL_skills_3.png",
                "motion": "cast",
                "desc": [
                    "수비 스킬 '방어' 를 사용한 대상에게는 피해량 -90%",
                    "수비 스킬 '회피' 를 사용한 대상에게는 '필중' 효과가 함께 적용됨",
                ]
            },
            {
                "name":   "당신들도 예외는 아닙니다",
                "power":  130,
                "type":   "물리",
                "side": "적", "count": "단일",
                "hits":   1,
                "tags":   ["필중"],
                "sprite": "assets/KL/KL_skills_4.png",
                "motion": "stationary",
                "desc": [
                    "주인공을 제외한 적을 대상으로 지정함",
                    "대상이 '보호막' 을 가지고 있다면 피해를 입히기 전 보호막을 전부 파괴함",
                ]
            },
            {
                "name":   "꿰뚫는 불꽃",
                "power":  300,
                "type":   "마법",
                "side": "적", "count": "5인",
                "hits":   3,
                "tags":   [],
                "sprite": "assets/KL/KL_skills_5.png",
                "motion": "cast",
                "desc": [
                    "반드시 주인공을 대상으로 지정함",
                    "대상이 이 스킬로 피해를 받기 전 자신을 공격했다면 해당 스킬을 취소함",
                ]
            },
        ],
        "speed": 1,
    },
    "말단병사": {
        "title":         "",
        "name":          "말단병사",
        "type":          "normal",
        "level":         50,
        "phys_level":    53,
        "magic_level":   22,
        "hp_max":        1340,
        "sprite":        "assets/knight_maldan.png",
        "profile":       "assets/maldan_profile.png",
        "sprite_scale":  0.4,
        "click_w_ratio": 0.2,
        "background":    "assets/battle_bg_castle.png",
        "bgm":           "assets/battle_bgm_normal.mp3",
        "overview": [
            "왕국 기사단의 말단병사",
            "",
            "중앙 왕국 기사단의 가장 낮은 계급의 기사입니다.",
            "기사단장의 명령으로 이번 전투에는 참전하지 않습니다.",
        ],
        "speed": 0,
        "skills": [
            {"name": "찌르기", "power": 20, "type": "물리", "side": "적", "count": "단일", "hits": 1, "tags": [], "motion": "behind",
             "sprite": "", "desc": ["창으로 찌른다."]},
        ],
    },
    "Eat_slime1": {
        "title":         "",
        "name":          "포식 슬라임",
        "type":          "normal",
        "level_min":     12,
        "level_max":     17,
        "hp_min":        100,
        "hp_max_range":  132,
        "phys_min":      11,
        "phys_max":      13,
        "magic_min":     2,
        "magic_max":     3,
        "level":         12,
        "phys_level":    11,
        "magic_level":   2,
        "hp_max":        100,
        "sprite":        "assets/slime/slime_eat1.png",
        "profile":       "assets/slime/slime_eat1_profile.png",
        "sprite_scale":  0.5,
        "click_w_ratio": 0.2,
        "background":    "assets/battle_bg_forest.png",
        "speed_min": 2, "speed_max": 6,
        "skills": [
            {"name": "박치기", "power": 15, "type": "물리", "side": "적", "count": "단일", "hits": 1, "tags": [], "motion": "behind",
             "sprite": "", "desc": ["몸으로 부딪힌다."]},
        ],
    },
    "Eat_slime2": {
        "title":         "",
        "name":          "위장 슬라임",
        "type":          "normal",
        "level_min":     18,
        "level_max":     23,
        "hp_min":        140,
        "hp_max_range":  177,
        "phys_min":      17,
        "phys_max":      21,
        "magic_min":     2,
        "magic_max":     3,
        "level":         18,
        "phys_level":    17,
        "magic_level":   2,
        "hp_max":        140,
        "sprite":        "assets/slime/slime_eat2.png",
        "profile":       "assets/slime/slime_eat2_profile.png",
        "sprite_scale":  0.5,
        "click_w_ratio": 0.2,
        "speed_min": 2, "speed_max": 6,
        "skills": [
            {"name": "산성 침", "power": 20, "type": "마법", "side": "적", "count": "단일", "hits": 1, "tags": [], "motion": "cast",
             "sprite": "", "desc": ["산성 액체를 뱉는다."]},
        ],
    },
    "Eat_slime3": {
        "title":         "",
        "name":          "의태 슬라임",
        "type":          "normal",
        "level_min":     24,
        "level_max":     30,
        "hp_min":        330,
        "hp_max_range":  400,
        "phys_min":      26,
        "phys_max":      35,
        "magic_min":     21,
        "magic_max":     27,
        "level":         24,
        "phys_level":    26,
        "magic_level":   21,
        "hp_max":        330,
        "sprite":        "assets/slime/slime_eat3.png",
        "profile":       "assets/slime/slime_eat3_profile.png",
        "sprite_scale":  0.5,
        "click_w_ratio": 0.2,
        "speed_min": 1, "speed_max": 3,
        "skills": [
            {"name": "변형 강타", "power": 30, "type": "물리", "side": "적", "count": "단일", "hits": 1, "tags": [], "motion": "stationary",
             "sprite": "", "desc": ["변형한 팔로 내려친다."]},
        ],
    },
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
                    "'선원': 중첩 당 최종 위력이 1 증가합니다. 최대 10회 중첩 가능합니다.",
                ]
            },
        ],
        "speed_min": 21, "speed_max": 33,
        "skills": [
            {"name": "난무", "power": 5, "type": "물리", "side": "적", "count": "단일", "hits": 5, "tags": [],
             "sprite": "", "motion": "stationary", "split": 3,
             "effect_self": "assets/SSG/SSG_nanmu_self.png", "effect_target": "assets/SSG/SSG_nanmu_target.png",
             "sound": "assets/SSG/SSG_nanmu.mp3",
             "desc": ["무자비한 기세로 적을 벤다."]},
            {"name": "선장의 호령", "power": 35, "type": "마법", "side": "아군", "count": "5인", "hits": 1, "tags": ["지원"],
             "sprite": "", "motion": "command",
             "effect_self": "assets/SSG/SSG_command_self.png", "effect_target": "assets/SSG/SSG_command_target.png",
             "desc": ["아군 전체를 강화한다."]},
            {"name": "쾌속 베기", "power": 25, "type": "물리", "side": "적", "count": "단일", "hits": 3, "tags": [],
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
        "sprite_scale":  0.5,
        "click_w_ratio": 0.2,
        "overview": [
            "마리나 루나",
            "",
            "엘 로마올라스의 부선장입니다.",
            "마리 솔과는 절친한 사이로, 해적단의 주요 전투원입니다.",
            "",
            "단순 힘싸움으로는 그녀가 마리 솔보다 한 수 위입니다.",
            "말을 잘 듣는 성격은 아니지만요.",
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
            {"name": "난무! 내가 알려준 기술이지!", "power": 5, "type": "물리", "side": "적", "count": "단일", "hits": 5, "tags": [],
             "sprite": "", "motion": "stationary", "split": 3,
             "effect_self": "assets/SSG/SSG_nanmu_self.png", "effect_target": "assets/SSG/SSG_nanmu_target.png",
             "sound": "assets/SSG/SSG_nanmu.mp3",
             "desc": ["무자비한 기세로 적을 벤다."]},
            {"name": "쾌속 베기!", "power": 25, "type": "물리", "side": "적", "count": "단일", "hits": 3, "tags": [],
             "sprite": "", "motion": "behind",
             "desc": ["3회 연속 베기."]},
             {"name": "가끔은 한 방도 필요한 법이지~", "power": 100, "type": "물리", "side": "적", "count": "단일", "hits": 1, "tags": [],
             "sprite": "", "motion": "behind",
             "desc": ["강하게 적을 벤다."]},
             {"name": "파도를 쳐라, 나는 너를 치겠다!", "power": 30, "type": "마법", "side": "적", "count": "1인", "hits": 3, "tags": [],
             "sprite": "", "motion": "cast",
             "desc": ["파도 치듯 검을 빠르게 내려친다."]},
             {"name": "아 귀찮아~", "power": 0, "type": "물리", "side": "자신", "count": "1인", "hits": 0, "tags": [],
             "sprite": "", "motion": "command",
             "desc": ["마리나가 그 어떤 행동도 하지 않는다."]},
        ]
    },
    "마리 따까리1": {
        "name":          "칼 든 선원",
        "type":          "normal",
        "level":         41,
        "phys_level":    35,
        "magic_level":   21,
        "hp_max":        320,
        "mp_max":        290,
        "sprite":        "assets/south_normal/SSG_extra_1.png",
        "profile":       "assets/south_normal/SSG_extra_1_profile.png",
        "sprite_scale":  0.55,
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
        "speed_min": 1, "speed_max": 5,
        "skills": [
            {"name": "엉성한 난무", "power": 3, "type": "물리", "side": "적", "count": "단일", "hits": 3, "tags": [],
             "sprite": "", "motion": "stationary", "split": 2,
             "effect_self": "assets/SSG/SSG_nanmu_self.png", "effect_target": "assets/SSG/SSG_nanmu_target.png",
             "sound": "assets/SSG/SSG_nanmu.mp3", "desc": ["부선장에게 배운 선장에게 배운 기술이다."]},
        ],
    },
    "마리 따까리2": {
        "name":          "총 든 선원",
        "type":          "normal",
        "level":         42,
        "phys_level":    36,
        "magic_level":   20,
        "hp_max":        210,
        "mp_max":        300,
        "sprite":        "assets/south_normal/SSG_extra_2.png",
        "profile":       "assets/south_normal/SSG_extra_2_profile.png",
        "sprite_scale":  0.55,
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
        "speed_min": 9, "speed_max": 10,
        "skills": [
            {"name": "보조 사격", "power": 15, "type": "물리", "side": "적", "count": "단일", "hits": 1, "tags": [],
             "sprite": "", "motion": "cast",
             "effect_self": "assets/SSG/SSG_nanmu_self.png", "effect_target": "assets/gun_shot_target.png",
             "sound": "assets/gun_shot.mp3", "desc": ["총을 쏜다. 비겁하다."]},
        ]
    },
    "Eight_tails": {
        "name":          "팔미호",
        "type":          "boss",
        "level":         88,
        "phys_level":    84,
        "magic_level":   92,
        "hp_max":        8890,
        "mp_max":        3000,
        "sprite":        "assets/ETs/ETs_battle",
        "profile":       "assets/ETs/ETs_profile",
        "sprite_scale":  0.55,
        "click_w_ratio": 0.2,
        "overview": [
            "설명설명",
            "",
            "설명설명",
            "설명설명",
        ],
        "passives": [
            {
                "name": "미호",
                "desc": [
                    "가진 꼬리 1개당 가하는 피해량 +5% (가진 꼬리 개수: 8)",
                    "가진 꼬리 1개당 받는 피해량 -5% (가진 꼬리 개수: 8)",
                ],
                "effects": [{"kind": "take_mult", "value": 0.95}]
            },
            {
                "name": "여우불",
                "desc": [
                    "턴이 종료될 때 자신이 이번 턴에 스킬로 소모한 마력 만큼 '여우불' 중첩을 얻습니다.",
                    "턴이 종료될 때 자신이 이번 턴에 소모한 '여우불' 중첩 만큼 마력을 회복합니다.",
                    "여우불은 최대 (가진 꼬리의 개수 x 111) 까지 중첩되며, 최대 중첩을 달성한 다음 턴에 강력한 스킬을 사용합니다."
                ],
                "effects": [{"kind": "take_mult", "value": 0.95}]
            },
        ],
        "speed_min": 9, "speed_max": 10,
        "skills": [
            {"name": "보조 사격", "power": 15, "type": "물리", "side": "적", "count": "단일", "hits": 1, "tags": [],
             "sprite": "", "motion": "cast",
             "effect_self": "assets/SSG/SSG_nanmu_self.png", "effect_target": "assets/gun_shot_target.png",
             "sound": "assets/gun_shot.mp3", "desc": ["총을 쏜다. 비겁하다."]},
        ]
    },
    "template": {
        "title":         "",
        "name":          "템플릿",
        "type":          "normal",
        "level_min":     1,
        "level_max":     100,
        "hp_min":        10,
        "hp_max_range":  1000,
        "phys_min":      1,
        "phys_max":      100,
        "magic_min":     1,
        "magic_max":     100,
        "level":         1,
        "phys_level":    1,
        "magic_level":   1,
        "hp_max":        10,
        "sprite":        "assets/파일이름.png",
        "sprite_scale":  0.5,
        "click_w_ratio": 0.2,
    },
}

ALLY_DEFS = {
    "주인공": {
        "name":          "주인공",
        "defense_skills": ["방어", "회피", "원호"],
        "type":          "player",
        "level":         1,
        "phys_level":    1,
        "magic_level":   1,
        "hp_max":        100,
        "mp_max":        500,
        "sprite":        "assets/MC/main_character_B_battle.png",
        "profile":       "assets/MC/main_B_profile.png",
        "sprite_scale":  0.25,
        "click_w_ratio": 0.2,
        "speed":         5,
        "skills": [
            {"name": "휘두르기", "power": 30, "type": "물리", "side": "적", "count": "단일", "hits": 1, "tags": [], "motion": "behind",
             "sprite": "", "desc": ["기본적인 물리 공격."]},
            {"name": "마력탄", "power": 25, "type": "마법", "side": "적", "count": "단일", "hits": 1, "tags": [], "motion": "cast",
             "sprite": "", "desc": ["기본적인 마법 공격."]},
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
                    "이때 소모한 마력 만큼 아군 모두에게 회복 효과를 적용합니다.",
                ]
            },
            {
                "name": "마력 발산 - 대리인",
                "desc": [
                    "'마력 발산' 상태가 되면 회복 효과를 가진 모든 스킬의 최종 위력이 20 증가합니다.",
                    "자신 또는 아군에게 회복 효과를 적용할 때마다 적용된 회복량 만큼 보호막을 추가로 부여합니다.",
                ]
            },
            {
                "name": "성스러운 육체",
                "desc": [
                    "자신이 적에게 피해를 받으면 다음 턴이 시작될 때 받은 피해 만큼 보호막을 얻습니다.",
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
            {"name": "성스러운 빛", "power": 300, "type": "마법", "side": "아군", "count": "단일", "hits": 1, "tags": ["회복", "지원"], "motion": "command",
             "sprite": "", "desc": ["아군 하나를 회복한다."]},
            {"name": "심판의 일격", "power": 90, "type": "물리", "side": "적", "count": "단일", "hits": 1, "tags": [], "motion": "stationary",
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
            {"name": "금강", "power": 70, "type": "마법", "side": "자신", "count": "단일", "hits": 1, "tags": ["지원"], "motion": "command",
             "sprite": "", "desc": ["'금강' 상태가 된다."]},
            {"name": "철권", "power": 100, "type": "물리", "side": "적", "count": "단일", "hits": 1, "tags": [], "motion": "stationary",
             "sprite": "", "desc": ["강력한 물리 일격."]},
            {"name": "연환격", "power": 35, "type": "물리", "side": "적", "count": "단일", "hits": 3, "tags": [], "motion": "stationary",
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
                    "'선원': 중첩 당 최종 위력이 1 증가합니다. 최대 10회 중첩 가능합니다.",
                ]
            },
        ],
        "speed_min": 21, "speed_max": 33,
        "skills": [
            {"name": "난무", "power": 30, "type": "물리", "side": "적", "count": "단일", "hits": 4, "tags": [],
             "sprite": "", "motion": "stationary", "split": 3,
             "effect_self": "assets/SSG/SSG_nanmu_self.png", "effect_target": "assets/SSG/SSG_nanmu_target.png",
             "sound": "assets/SSG/SSG_nanmu.mp3",
             "desc": ["4회 연속 공격."]},
            {"name": "선장의 호령", "power": 35, "type": "마법", "side": "아군", "count": "5인", "hits": 1, "tags": ["지원"],
             "sprite": "", "motion": "command",
             "effect_self": "assets/SSG/SSG_command_self.png", "effect_target": "assets/SSG/SSG_command_target.png",
             "desc": ["아군 전체를 강화한다."]},
            {"name": "쾌속 베기", "power": 50, "type": "물리", "side": "적", "count": "단일", "hits": 3, "tags": [],
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
                "desc": [
                    "자신의 (현재 마력%÷2)%만큼 자신이 가하는 피해량이 증가합니다.",
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
            {"name": "화염포", "power": 120, "type": "마법", "side": "적", "count": "단일", "hits": 1, "tags": [], "motion": "cast",
             "sprite": "", "desc": ["강력한 마법 일격."]},
            {"name": "북부의 불길", "power": 60, "type": "마법", "side": "적", "count": "5인", "hits": 1, "tags": [], "motion": "cast",
             "sprite": "", "desc": ["적 전체에게 마법 피해."]},
            {"name": "관통사격", "power": 90, "type": "물리", "side": "적", "count": "단일", "hits": 1, "tags": [], "motion": "behind",
             "sprite": "", "desc": ["물리 관통 공격."]},
        ]
    },
}