# 메인 스토리 구조: 막(act) > 장(chapter) > 스테이지(stage)
# 각 항목의 "image" 는 선택 화면에서 쓰는 직사각형 이미지 경로 (없으면 회색 박스+제목으로 대체).
# 스테이지에는 추후 전투/다이얼로그 정보를 키로 추가 예정.

def _make_stages(chapter_no, count):
    """N-1 ~ N-count 스테이지 딕셔너리 생성"""
    stages = {}
    for i in range(1, count + 1):
        key = f"{chapter_no}-{i}"
        stages[key] = {
            "title": key,
            "image": "",      # 스테이지 이미지 경로 (미정)
        }
    return stages


STORY = {
    "0막": {
        "title": "0막",
        "image": "",
        "chapters": {
            "0장": {
                "title": "0막 0장",
                "image": "",
                "stages": {
                    "0-1": {
                        "title": "0-1",
                        "image": "",
                        # 다이얼로그: 컷(cut) 리스트
                        "dialogue": [
                            {
                                "characters": [],
                                "background": "assets/space_dialog.png",
                                "affiliation": "???",
                                "speaker": "주인공",
                                "text": "여긴... 어디지?",
                            },
                            {
                                "characters": [
                                    {"sprite": "assets/broadcaster.png", "x": 0.50, "y": 1, "scale": 0.50},
                                ],
                                "affiliation": "???",
                                "speaker": "???",
                                "sound": "assets/broadcaster.mp3",
                                "text": "..안녕하세요?",
                            },
                            {
                                "characters": [
                                    {"sprite": "assets/broadcaster.png", "x": 0.50, "y": 1, "scale": 0.50},
                                ],
                                "affiliation": "???",
                                "speaker": "주인공",
                                "text": ".....",
                            },
                            {
                                "characters": [
                                    {"sprite": "assets/broadcaster.png", "x": 0.50, "y": 1, "scale": 0.50},
                                ],
                                "affiliation": "???",
                                "speaker": "???",
                                "sound": "assets/broadcaster.mp3",
                                "text": "...아! 자기 소개를 안 했네요. 죄송합니다.",
                            },
                            {
                                "characters": [
                                    {"sprite": "assets/broadcaster.png", "x": 0.50, "y": 1, "scale": 0.50},
                                ],
                                "affiliation": "???",
                                "speaker": "???",
                                "sound": "assets/broadcaster.mp3",
                                "text": "제 이름은 ■■■... 아, 안 들리시려나...요?",
                            },
                            {
                                "characters": [
                                    {"sprite": "assets/broadcaster.png", "x": 0.50, "y": 1, "scale": 0.50},
                                ],
                                "affiliation": "???",
                                "speaker": "주인공",
                                "text": "이게 무슨...",
                            },
                            {
                                "characters": [
                                    {"sprite": "assets/broadcaster.png", "x": 0.50, "y": 1, "scale": 0.50},
                                ],
                                "affiliation": "중계자",
                                "speaker": "???",
                                "sound": "assets/broadcaster.mp3",
                                "text": "저는 중계자라고 해요. 당신을 이곳으로 이끌었답니다.",
                            },
                            {
                                "characters": [
                                    {"sprite": "assets/broadcaster.png", "x": 0.50, "y": 1, "scale": 0.50},
                                ],
                                "affiliation": "???",
                                "speaker": "주인공",
                                "text": "잠시만요. 잠시만... 지금 이게 무슨 상황이죠?",
                            },
                            {
                                "characters": [
                                    {"sprite": "assets/broadcaster.png", "x": 0.50, "y": 1, "scale": 0.50},
                                ],
                                "affiliation": "중계자",
                                "speaker": "???",
                                "sound": "assets/broadcaster.mp3",
                                "text": "...당신은 죽었어요. 당신이 살던 세계에서.",
                            },
                            {
                                "characters": [
                                    {"sprite": "assets/broadcaster.png", "x": 0.50, "y": 1, "scale": 0.50},
                                ],
                                "affiliation": "???",
                                "speaker": "주인공",
                                "text": "!",
                            },
                            {
                                "characters": [
                                    {"sprite": "assets/broadcaster.png", "x": 0.50, "y": 1, "scale": 0.50},
                                ],
                                "affiliation": "중계자",
                                "speaker": "???",
                                "sound": "assets/broadcaster.mp3",
                                "text": "당신이 삶의 끝에 닿기 직전, 제가 당신을 이곳으로 이끌었답니다.",
                            },
                            {
                                "characters": [
                                    {"sprite": "assets/broadcaster.png", "x": 0.50, "y": 1, "scale": 0.50},
                                ],
                                "affiliation": "???",
                                "speaker": "주인공",
                                "text": "(꿈인가...)",
                            },
                            {
                                "characters": [
                                    {"sprite": "assets/broadcaster.png", "x": 0.50, "y": 1, "scale": 0.50},
                                ],
                                "affiliation": "중계자",
                                "speaker": "???",
                                "sound": "assets/broadcaster.mp3",
                                "text": "꿈이 아니예요.",
                            },
                            {
                                "characters": [
                                    {"sprite": "assets/broadcaster.png", "x": 0.50, "y": 1, "scale": 0.50},
                                ],
                                "affiliation": "???",
                                "speaker": "주인공",
                                "text": "아 내 꿈이니까 내 생각이 꿈에 반영되겠지...",
                            },
                            {
                                "characters": [
                                    {"sprite": "assets/broadcaster.png", "x": 0.50, "y": 1, "scale": 0.50},
                                ],
                                "affiliation": "중계자",
                                "speaker": "???",
                                "sound": "assets/broadcaster.mp3",
                                "text": "정말로... 지금 이 상황이 꿈처럼 느껴지시나요?",
                            },
                            {
                                "characters": [
                                    {"sprite": "assets/broadcaster.png", "x": 0.50, "y": 1, "scale": 0.50},
                                ],
                                "affiliation": "중계자",
                                "speaker": "???",
                                "sound": "assets/broadcaster.mp3",
                                "text": "...믿지 못하시는 것도 충분히 이해해요.",
                            },
                            {
                                "characters": [
                                    {"sprite": "assets/broadcaster.png", "x": 0.50, "y": 1, "scale": 0.50},
                                ],
                                "affiliation": "중계자",
                                "speaker": "???",
                                "sound": "assets/broadcaster.mp3",
                                "text": "하지만 당신이 보고 듣고 느끼고 있는 이 공간, 이 상황은 꿈이 아닙니다.",
                            },
                            {
                                "characters": [
                                    {"sprite": "assets/broadcaster.png", "x": 0.50, "y": 1, "scale": 0.50},
                                ],
                                "affiliation": "???",
                                "speaker": "주인공",
                                "text": "(꿈이 많이 요란하네... 요즘 스트레스가 심했나.)",
                            },
                            {
                                "characters": [
                                    {"sprite": "assets/broadcaster.png", "x": 0.50, "y": 1, "scale": 0.50},
                                ],
                                "affiliation": "중계자",
                                "speaker": "???",
                                "sound": "assets/broadcaster.mp3",
                                "text": "꿈이 아니라니까요? ...상기시켜 드리고 싶지는 않았지만 보여드릴 수 밖에 없겠네요.",
                            },
                            {
                                "characters": [
                                    {"sprite": "assets/broadcaster.png", "x": 0.50, "y": 1, "scale": 0.50},
                                ],
                                "affiliation": "중계자",
                                "speaker": "???",
                                "sound": "assets/broadcaster.mp3",
                                "text": "이것이 당신이 저에게 닿기 전, 마지막 순간의 모습입니다.",
                            },
                        ],
                    },
                },
            },
        },
    },
    "1막": {
        "title": "1막 판타지아",
        "image": "",          # 막 직사각형 이미지 (미정)
        "chapters": {
            "1장": {
                "title": "1막 1장",
                "image": "",
                "stages": _make_stages(1, 10),
            },
            "2장": {
                "title": "1막 2장",
                "image": "",
                "stages": _make_stages(2, 10),
            },
        },
    },
}