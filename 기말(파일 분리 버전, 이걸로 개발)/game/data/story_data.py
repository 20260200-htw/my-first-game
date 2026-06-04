# 메인 스토리 구조: 막(act) > 장(chapter) > 스테이지(stage)
# 실제 데이터는 data/story/ 하위 파일들로 분리되어 있으며, 여기서 합쳐 STORY 를 구성한다.
#   story_data_0       → 0막
#   story_data_1_1     → 1막 1장
#   story_data_1_2     → 1막 2장
#   story_data_1_3     → 1막 3장
#   story_data_1_4     → 1막 4장
#   story_data_1_5     → 1막 5장
#   story_data_1_final → 1막 최종장

from data.story.story_data_0       import ACT_0
from data.story.story_data_1_1     import CHAPTER as CH_1_1
from data.story.story_data_1_2     import CHAPTER as CH_1_2
from data.story.story_data_1_3     import CHAPTER as CH_1_3
from data.story.story_data_1_4     import CHAPTER as CH_1_4
from data.story.story_data_1_5     import CHAPTER as CH_1_5
from data.story.story_data_1_final import CHAPTER as CH_1_FINAL

STORY = {
    "0막": ACT_0,
    "1막": {
        "title": "1막 판타지아",
        "image": "",
        "chapters": {
            "1장":   CH_1_1,
            "2장":   CH_1_2,
            "3장":   CH_1_3,
            "4장":   CH_1_4,
            "5장":   CH_1_5,
            "최종장": CH_1_FINAL,
        },
    },
}
