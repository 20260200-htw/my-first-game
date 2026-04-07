# 6주차 실습 기록

## 사용한 에셋
- 이미지:
- RUN.png (https://xzany.itch.io/free-knight-2d-pixel-art)
- IDLE.png (https://xzany.itch.io/free-knight-2d-pixel-art)
- DEFEND.png (https://xzany.itch.io/free-knight-2d-pixel-art)
- BOSS_ATTACK 1.png (https://xzany.itch.io/samurai-2d-pixel-art)

- 사운드:
- boss_attack.wav (https://freesound.org/people/beerbelly38/sounds/362350/)
- boss_hit.ogg (https://freesound.org/people/micahlg/sounds/413185/)
- parry.wav (https://freesound.org/people/CTCollab/sounds/223629/)
- player_hit.ogg (https://freesound.org/people/micahlg/sounds/413174/)
- game_bgm.mp3 (https://pixabay.com/ko/music/%eb%b9%84%ed%8a%b8-trung-thu-s%c3%b4i-%c4%91%e1%bb%99ng-hi%e1%bb%87n-%c4%91%e1%ba%a1i-nh%e1%ba%a1c-n%e1%bb%81n-trung-thu-223228/)

## 사용한 AI 프롬프트 (요약)
1. 기존의 플레이어블 오브젝트를 스프라이트 시트로 바꿔줘. / 기존 사각형 오브젝트를 스프라이트 시트 애니메이션으로 변경
2. 보스 오브젝트를 추가해줘. / 기존에는 탄막만이 날아왔는데, 보스를 추가하여 보스 처치 시 승리 추가
3. 보스 오브젝트가 화면을 랜덤하게 움직이도록 해줘. / 보스가 고정되지 않고 일정 시간마다 방향 랜덤 변경
4. 탄막이 생성될 때 플레이어의 현재 위치를 방향으로 하게 해줘. / 플레이어 주위로 탄막이 지나가도록 함
5. 보스 체력바를 만들어줘. 그리고 플레이어의 체력바도 같은 형식이 되게 해줘. / 체력바 통일
6. 패링에 쿨타임을 추가하고, 플레이어블 오브젝트의 위에 표시되게 해줘. / 패링 쿨타임 추가

## AI 답변에서 도움이 된 것

1. 새로운 기능 추가 대부분 (보스 추가, 패링 조정, 탄막 조정 등)
2. 스프라이트 시트 코드를 기존 코드에 추가하는 것

## AI 답변을 수정하거나 버린 것

1. 기존 레벨 형식을 단계(페이즈) 형식으로 변경
2. AI가 제시한 값을 일부 변경함 (보스의 이동 속도나 방향 전환 간격)

## 적용 결과
- 잘 된 것: 대부분의 새로운 기능 추가
- 어려웠던 것: 패링 시스템 개선
- 다음에 시도할 것: 게임 시작 화면(로비) 추가 및 게임 클리어 시 엔딩 화면 추가