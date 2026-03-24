import pygame
import sys

# 1. 초기화 및 창 설정 (800x600)
pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("AABB 시각화 예제")

# 색상 정의
GRAY = (150, 150, 150)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BG_COLOR = (30, 30, 30)

# 2. 오브젝트 설정
# 이동하는 사각형 (초기 위치: 100, 100)
player_rect = pygame.Rect(100, 100, 80, 80)
player_speed = 5

# 중앙 고정 사각형
static_rect = pygame.Rect(0, 0, 100, 100)
static_rect.center = (screen_width // 2, screen_height // 2)

clock = pygame.time.Clock()

while True:
    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 3. 방향키 입력으로 이동 처리
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_rect.x += player_speed
    if keys[pygame.K_UP]:
        player_rect.y -= player_speed
    if keys[pygame.K_DOWN]:
        player_rect.y += player_speed

    # 화면 그리기
    screen.fill(BG_COLOR)

    # 4. 오브젝트 및 AABB 표시
    # 회색 사각형 그리기
    pygame.draw.rect(screen, GRAY, player_rect)
    pygame.draw.rect(screen, GRAY, static_rect)

    # AABB 시각화 (빨간색 테두리)
    # 두 사각형이 충돌하는지 체크하여 선 굵기를 조절할 수도 있습니다.
    is_colliding = player_rect.colliderect(static_rect)
    line_width = 4 if is_colliding else 2

    pygame.draw.rect(screen, RED, player_rect, line_width)
    pygame.draw.rect(screen, RED, static_rect, line_width)

    # 업데이트
    pygame.display.flip()
    clock.tick(60)