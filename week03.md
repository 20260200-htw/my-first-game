# Pygame 학습 대화 전문
**My First Pygame 프로젝트 진행 기록**

생성 파일: hello_pygame.py

---

## Q1. Pygame 코드 설명 요청

**질문:** 아래 Pygame 코드를 처음 프로그래밍하는 사람에게 설명해줘. 각 줄이 뭘 하는지, 왜 필요한지 알려줘.

**답변:**

### 준비 단계

```python
import pygame
import sys
```
- `pygame` : 게임 창을 만들고 도형을 그리는 등 모든 기능을 담은 도구 모음
- `sys` : 프로그램을 종료할 때 필요한 파이썬 기본 도구

```python
pygame.init()
```
Pygame을 시작(초기화)하는 코드. 모든 기능을 사용하기 전에 반드시 먼저 실행해야 함.

```python
screen = pygame.display.set_mode((800, 600))
```
게임 창을 만드는 코드. `(800, 600)`은 창의 크기(가로 800px, 세로 600px).

```python
pygame.display.set_caption("My First Pygame")
```
창 상단에 제목을 붙이는 코드.

```python
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
```
색깔을 정의하는 코드. Pygame에서 색깔은 `(빨강, 초록, 파랑)` 숫자 조합으로 표현(0~255).

```python
clock = pygame.time.Clock()
```
시간을 재는 시계를 만드는 코드. 게임 속도를 일정하게 유지하는 데 사용.

```python
running = True
```
게임이 계속 실행될지 결정하는 스위치. `True`이면 계속 돌고, `False`가 되면 멈춤.

### 게임 루프 (핵심 반복 구간)

```python
while running:
```
`running`이 True인 동안 아래 코드를 무한 반복.

```python
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
```
사용자의 행동(이벤트)을 감지. X 버튼을 누르면 `running = False`로 바꿔 반복문을 멈춤. **이 코드가 없으면 X 버튼을 눌러도 창이 안 닫힘.**

```python
    screen.fill(WHITE)
```
화면 전체를 흰색으로 칠하는 코드. 이전 그림을 지우고 새로 그리기 위해 필요.

```python
    pygame.draw.circle(screen, BLUE, (400, 300), 50)
```
파란 원을 그리는 코드. `(400, 300)`은 원의 중심 위치, `50`은 반지름.

```python
    pygame.display.flip()
```
완성된 그림을 실제 화면에 표시하는 코드. 화면이 깜빡이지 않도록 한 번에 표시.

```python
    clock.tick(60)
```
게임 속도를 초당 60번으로 제한. 1초에 60번 화면을 그린다는 의미(60fps).

### 종료 단계

```python
pygame.quit()
sys.exit()
```
프로그램을 깔끔하게 종료. `pygame.quit()`은 자원 반납, `sys.exit()`은 프로그램 완전 종료.

### 전체 흐름 요약
```
시작 → 창 만들기 → [이벤트 확인 → 화면 지우기 → 그림 그리기 → 화면 표시] 반복 → 종료
```

---

## Q2. 방향키로 도형 이동 기능 추가

**질문:** 그려진 도형이 키보드 방향키 입력을 받아 입력된 방향키 방향으로 5픽셀씩 움직이게 해줘.

**답변:** 핵심 변경 포인트 3가지

**1. 위치를 변수로 분리**
```python
circle_x = 400
circle_y = 300
```
좌표가 고정되어 있으면 움직일 수 없으므로 변수로 변경.

**2. 키 입력 감지 방식**
```python
keys = pygame.key.get_pressed()
```
`get_pressed()`는 키를 **누르고 있는 동안 매 프레임마다** 감지해 부드럽게 움직임.

**3. 도형 좌표를 변수로 교체**
```python
# 변경 전
pygame.draw.circle(screen, BLUE, (400, 300), RADIUS, 1)

# 변경 후
pygame.draw.circle(screen, BLUE, (circle_x, circle_y), RADIUS, 1)
```

**전체 추가 코드:**
```python
# [추가] 원의 초기 위치를 변수로 저장
circle_x = 400
circle_y = 300

# [추가] 현재 눌린 키를 가져옴
keys = pygame.key.get_pressed()

# [추가] 방향키에 따라 위치를 5픽셀씩 변경
if keys[pygame.K_LEFT]:
    circle_x -= 5
if keys[pygame.K_RIGHT]:
    circle_x += 5
if keys[pygame.K_UP]:
    circle_y -= 5
if keys[pygame.K_DOWN]:
    circle_y += 5
```

---

## Q3. FPS 좌측 상단 출력

**질문:** fps가 좌측 상단에 출력되게 해줘.

**답변:**

```python
# [추가] FPS 표시용 폰트 생성 (기본 폰트, 크기 24)
font = pygame.font.Font(None, 24)

# [추가] 현재 FPS를 정수로 가져와 문자열로 변환
fps = int(clock.get_fps())
fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))

# [추가] FPS 텍스트를 좌측 상단 (10, 10) 위치에 그리기
screen.blit(fps_text, (10, 10))
```

- `font.render()` : 문자열을 화면에 그릴 수 있는 이미지로 변환
- `screen.blit()` : 이미지를 화면의 특정 위치에 붙이는 함수

---

## Q4. pygame.key.get_pressed() 설명 / y -= 5가 왜 위쪽 이동인지 질문

**질문 1:** pygame.key.get_pressed() 가 뭔지 설명해줘

**답변:**

"지금 이 순간 어떤 키가 눌려 있나요?"라고 키보드 전체 상태를 한 번에 물어보는 함수.

| | `event` 방식 | `get_pressed()` 방식 |
|---|---|---|
| 감지 시점 | 키를 **누른 순간** 1번만 | 키를 **누르는 동안** 매 프레임마다 |
| 움직임 | 한 칸만 이동 | 누르는 동안 계속 이동 |
| 적합한 용도 | 점프, 메뉴 선택 | 캐릭터 이동 |

---

**질문 2:** y -= 5 는 왜 위쪽으로 이동하는 거야?

**답변:**

컴퓨터 화면의 좌표계가 수학 시간에 배운 것과 반대 방향이기 때문.

```
  수학 좌표계          컴퓨터 화면 좌표계

       y+                (0,0)──────→ x+
       ↑                   │
       │                   │
───────┼──────→ x+         ↓
       │                  y+
```

컴퓨터 화면은 **좌측 상단이 (0, 0)**이고, 아래로 내려갈수록 y값이 커짐.

```python
if keys[pygame.K_UP]:
    circle_y -= 5  # y가 작아짐 = 화면 위쪽으로 이동

if keys[pygame.K_DOWN]:
    circle_y += 5  # y가 커짐 = 화면 아래쪽으로 이동
```

---

## Q5. 도형이 화면 밖으로 나가지 못하게 경계 처리

**질문:** 도형이 화면(창) 밖으로 나가지 못하게 만들어줘.

**답변:**

```python
# [추가] 원의 반지름 변수로 분리
RADIUS = 10

# [추가] 원이 화면 밖으로 나가지 못하도록 좌표 제한
circle_x = max(RADIUS, min(circle_x, 400 - RADIUS))
circle_y = max(RADIUS, min(circle_y, 400 - RADIUS))
```

**벽 충돌 원리:**
```
     x=0   x=10        x=390  x=400
      벽  │←——————————————→│  벽
          ↑                ↑
       최솟값            최댓값
      (RADIUS)       (400-RADIUS)
```

`min()`으로 오른쪽 벽, `max()`로 왼쪽 벽을 제한. 반지름만큼 범위를 좁혀 테두리가 벽에 딱 붙게 함.

---

## Q6. 주석 제거

**질문:** 해당 코드에서 주석만 제거해줘.

**답변:** `#`로 시작하는 모든 주석 줄을 제거하고 코드만 남김.

---

## Q7. 방향키 입력 시 도형 색상 변경 (AI 주석 형식)

**질문:** 방향키를 누를 때마다 도형의 색이 변하도록 만들어줘. 관련 코드에는 주석을 달아주고 앞에 "AI로 작성된 주석입니다."를 붙여줘.

**답변:**

```python
import random # AI로 작성된 주석입니다. 랜덤 색상 생성을 위한 모듈 추가

# AI로 작성된 주석입니다. 원의 초기 색상을 BLUE로 설정
circle_color = BLUE

# AI로 작성된 주석입니다. 방향키 입력 감지 후 이동 + 색상 변경
key_pressed = False
if keys[pygame.K_LEFT]:
    circle_x -= 10
    key_pressed = True
if keys[pygame.K_RIGHT]:
    circle_x += 10
    key_pressed = True
if keys[pygame.K_UP]:
    circle_y -= 10
    key_pressed = True
if keys[pygame.K_DOWN]:
    circle_y += 10
    key_pressed = True

# AI로 작성된 주석입니다. 방향키가 눌렸을 때 RGB 각각 0~255 랜덤 색상 적용
if key_pressed:
    circle_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
```

---

## Q8. 방향키를 누를 때마다 색상 1회만 변경

**질문:** 방향키를 누르고 있으면 계속 색이 변하는 식이잖아 지금은? 방향키를 누를 때마다 1번씩 색이 변하도록 바꿔줘.

**답변:**

`get_pressed()` 방식은 누르는 동안 매 프레임 감지라 `KEYDOWN` 이벤트 방식으로 변경.

```python
# AI로 작성된 주석입니다. 키를 누른 순간 1회만 감지하는 KEYDOWN 이벤트
if event.type == pygame.KEYDOWN:
    if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
        # AI로 작성된 주석입니다. 방향키 입력 시 색상을 랜덤으로 1회 변경
        circle_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
```

| 기능 | 방식 | 이유 |
|---|---|---|
| 색상 변경 | `KEYDOWN` 이벤트 | 누른 순간 1회만 |
| 도형 이동 | `get_pressed()` | 누르는 동안 계속 |

---

## Q9. 원 대신 삼각형으로 변경 (AI 주석 형식)

**질문:** 도형을 삼각형으로 바꾸고 싶어. 관련 코드 위에는 주석을 달아주고 원이 아닌 삼각형이 만들어지게 해줘.

**답변:**

`pygame.draw.circle()` → `pygame.draw.polygon()` 으로 교체.

```python
# AI로 작성된 주석입니다. 삼각형의 세 꼭짓점 좌표 계산 (중심 기준 위쪽/좌하/우하)
triangle_points = [
    (circle_x, circle_y - SIZE),       # 위쪽 꼭짓점
    (circle_x - SIZE, circle_y + SIZE), # 좌측 하단 꼭짓점
    (circle_x + SIZE, circle_y + SIZE)  # 우측 하단 꼭짓점
]
# AI로 작성된 주석입니다. pygame.draw.polygon 으로 삼각형 그리기, 마지막 숫자(1) = 테두리 두께
pygame.draw.polygon(screen, BLUE, triangle_points, 1)
```

**삼각형 꼭짓점 구조:**
```
        (x, y - SIZE)         ← 위 꼭짓점
             △
            / \
           /   \
          /     \
(x-SIZE, y+SIZE)─(x+SIZE, y+SIZE)
   ← 좌하 꼭짓점      우하 꼭짓점 →
```

---

## Q10. 경계 처리 코드에 원리 설명 주석 달기

**질문:** 도형이 창 밖으로 나가지 못하는 관련 코드에 주석으로 코드에 대한 설명을 작성해줘. 왜 충돌하는지 어떤 원리인지 등.

**답변:**

```python
# 원의 중심 좌표(circle_x, circle_y)가 이동 가능한 범위를 제한하는 코드
# 원은 중심이 아닌 테두리가 벽에 닿아야 하므로, 반지름(RADIUS) 만큼 안쪽으로 범위를 좁힘
#
# X축 범위 : RADIUS(10) ~ 400 - RADIUS(390)
# Y축 범위 : RADIUS(10) ~ 400 - RADIUS(390)
#
# [왼쪽 벽 충돌 원리]
# 원이 왼쪽으로 이동 → circle_x 가 RADIUS(10) 보다 작아지려 할 때
# max(RADIUS, circle_x) 가 RADIUS 를 반환 → circle_x 가 10 아래로 못 내려감
# 결과 : 원의 왼쪽 테두리가 벽(x=0)에 딱 붙어서 멈춤
#
# [오른쪽 벽 충돌 원리]
# 원이 오른쪽으로 이동 → circle_x 가 400 - RADIUS(390) 보다 커지려 할 때
# min(circle_x, 390) 이 390 을 반환 → circle_x 가 390 위로 못 올라감
# 결과 : 원의 오른쪽 테두리가 벽(x=400)에 딱 붙어서 멈춤
#
# Y축도 동일한 원리로 위쪽/아래쪽 벽 충돌을 처리함
circle_x = max(RADIUS, min(circle_x, 400 - RADIUS))
circle_y = max(RADIUS, min(circle_y, 400 - RADIUS))
```

---

## Q11. 경계 처리 개념 질문

**질문:** 테두리 밖에 못 나가는 것이 경계 처리 맞지?

**답변:**

맞아요! 그 개념을 **경계 처리** 또는 영어로 **Boundary Checking** 이라고 불러요.

| 방식 | 설명 | 예시 |
|---|---|---|
| **막기** (현재 코드) | 벽에 닿으면 그 자리에서 멈춤 | `circle_x = max(RADIUS, min(...))` |
| **워프** | 한쪽 벽을 나가면 반대편에서 등장 | 팩맨 |
| **튕기기** | 벽에 닿으면 반대 방향으로 반사 | 벽돌깨기 |

---

## Q12. FPS 한국어 표기 변경

**질문:** fps가 한국어 "초당 프레임"으로 표기되게 바꾸고 싶어.

**답변:**

```python
# 변경 전 - 기본 내장 폰트 (한글 지원 안 됨)
font = pygame.font.Font(None, 24)

# 변경 후 - 한글을 지원하는 시스템 폰트 사용
font = pygame.font.SysFont("malgun gothic", 24)

# 변경 전
fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))

# 변경 후
fps_text = font.render(f"초당 프레임: {fps}", True, (255, 255, 255))
```

> 💡 `"malgun gothic"`은 Windows 기본 한글 폰트. Mac은 `"apple sd gothic neo"`, Linux는 `"nanum gothic"` 사용.

---

## Git 오류 해결 모음

### Git 오류 1: destination path already exists

**오류 메시지:**
```
fatal: destination path 'my-first-game' already exists and is not an empty directory.
```

**번역:** `'my-first-game'` 경로가 이미 존재하고, 비어 있지 않은 폴더입니다.

**해결 방법:**

```bash
# 1. 폴더 삭제 후 재클론 (Windows CMD)
rmdir /s /q my-first-game
git clone <주소>

# 2. 다른 이름으로 클론
git clone <주소> my-first-game-2

# 3. 이미 클론된 경우 폴더 안에서 pull
cd my-first-game
git pull
```

---

### Git 오류 2: rm 명령어 인식 안 됨 (Windows 환경)

**오류 메시지:**
```
'rm' is not recognized as an internal or external command
```

**해결 방법:**

| Mac/Linux | Windows CMD | Windows PowerShell |
|---|---|---|
| `rm -rf 폴더명` | `rmdir /s /q 폴더명` | `Remove-Item -Recurse -Force 폴더명` |

> `/s`는 하위 폴더까지 전부, `/q`는 확인 없이 바로 삭제.

---

### Git 오류 3: 사용자 정보 미등록 (no email was given)

**오류 메시지:**
```
fatal: no email was given and auto-detection is disabled
```

**해결 방법:**

```bash
git config --global user.email "이메일@example.com"
git config --global user.name "이름"
```

**등록 확인:**
```bash
git config --global user.email
git config --global user.name
```

> `--global`은 이 컴퓨터의 모든 Git 프로젝트에 동일한 정보를 사용한다는 의미. 한 번만 설정하면 됨.
