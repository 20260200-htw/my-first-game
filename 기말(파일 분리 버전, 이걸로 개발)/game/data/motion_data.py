# 전용 모션 정의
# 모션 번호(motion 값) → 스프라이트 시퀀스 + 베이스 연출
#
# frames: [(스프라이트경로, 유지시간초), ...]
#   - 모션 시작 시 첫 프레임부터 순서대로, 각자 유지시간만큼 표시
#   - 모든 프레임 끝나면 마지막 프레임 유지 (모션 종료 시 기본 스프라이트로 복귀)
# base:   기존 연출 방식 ("cast" / "behind" / "command" / "charge" / "smite").
#         움직임은 이걸 빌려 쓰고 스프라이트만 frames 로 교체.
#
#   ▶ 베이스 연출 종류
#     - stationary / behind : 근접 돌진(melee_rush)
#     - cast    : 시전자 줌인 → 대상으로 카메라 이동 → 다단 타격
#     - command : 시전자 확대 정지 후 일괄 발동 (지원기)
#     - charge  : 제자리에서 기를 모았다가(차징 오라) 일제 다단 타격. 카메라 시전자 고정
#     - smite   : 화면 암전 + 대상 위로 빛기둥 강하(강한 흔들림). 무거운 광역기
#
# 현호 전용 스프라이트: assets/ETs/ETs_battle_A.png ~ ETs_battle_Z.png
# 전투 기본 스프라이트(복귀용): assets/ETs/ETs_battle.png

_ETs = "assets/ETs/ETs_battle_{}.png"
_SS = "assets/SS/SS_battle_{}.png"

MOTION_DEFS = {
    # 여우불 — 3회 투사
    "ETs_skills_1": {
        "base": "cast",
        "frames": [
            (_ETs.format("F"), 1.0),
        ],
    },
    # 휘몰아치는 불꽃 — 전체 5회
    "ETs_skills_2": {
        "base": "cast",
        "frames": [
            (_ETs.format("D"), 0.3),
        ],
    },
    # 피해보세요! — 단일 강타 (근접)
    "ETs_skills_3": {
        "base": "stationary",
        "frames": [
            (_ETs.format("H"), 0.5),
            (_ETs.format("I"), 1.0),
        ],
    },
    # 잠깐 더울 거예요~ — 전체 1회
    "ETs_skills_4": {
        "base": "cast",
        "frames": [
            (_ETs.format("G"), 1.0),
        ],
    },
    # 여우가 춤을 추니... — 최강기, 전체 5회
    "ETs_skills_5": {
        "base": "charge",
        "frames": [
            (_ETs.format("E"), 0.4),
        ],
    },
    "SS_skills_1": {
        "base": "cast",
        "frames": [
            (_SS.format("A"), 1.0),
        ],
    },
    "SS_skills_2": {
        "base": "smite",
        "frames": [
            (_SS.format("B"), 1.0),
        ],
    },
    "SS_skills_3": {
        "base": "behind",
        "frames": [
            (_SS.format(""), 0.4),
            (_SS.format("C"), 1.0),
        ],
    },
    "SS_skills_4": {
        "base": "charge",
        "frames": [
            (_SS.format("B"), 1.0),
        ],
    },
}


def get_motion(motion_name):
    """모션 정의 반환. 없으면 None."""
    return MOTION_DEFS.get(motion_name)


def motion_base(motion_name):
    """모션의 베이스 연출 이름. 전용 모션이 아니면 motion_name 그대로."""
    m = MOTION_DEFS.get(motion_name)
    return m["base"] if m else motion_name