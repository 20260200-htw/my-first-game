import pygame
import sys

# 1. 초기화 및 창 설정
pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Optimized Circle Collision (No sqrt)")

# 색상 정의
GRAY = (150, 150, 150)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BG_COLOR = (30, 30, 30)

# 2. 오브젝트 설정
player_rect = pygame.Rect(100, 100, 80, 80)
player_radius = player_rect.width // 2
player_speed = 5

static_rect = pygame.Rect(0, 0, 100, 100)
static_rect.center = (screen_width // 2, screen_height // 2)
static_radius = static_rect.width // 2

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 3. 방향키 입력 이동
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  player_rect.x -= player_speed
    if keys[pygame.K_RIGHT]: player_rect.x += player_speed
    if keys[pygame.K_UP]:    player_rect.y -= player_speed
    if keys[pygame.K_DOWN]:  player_rect.y += player_speed

    # 4. 원형 충돌 계산 (제곱 비교 방식 - math.sqrt 미사용)
    dx = player_rect.centerx - static_rect.centerx
    dy = player_rect.centery - static_rect.centery
    
    # 거리의 제곱: dx^2 + dy^2
    distance_squared = dx**2 + dy**2
    
    # 반지름 합의 제곱: (r1 + r2)^2
    radii_sum_squared = (player_radius + static_radius)**2
    
    # 루트를 씌우지 않고 제곱 상태 그대로 비교
    circle_colliding = distance_squared <= radii_sum_squared

    # 5. 화면 그리기
    screen.fill(YELLOW if circle_colliding else BG_COLOR)

    # 본체 및 테두리 그리기
    pygame.draw.rect(screen, GRAY, player_rect)
    pygame.draw.rect(screen, GRAY, static_rect)
    pygame.draw.rect(screen, RED, player_rect, 2)
    pygame.draw.rect(screen, RED, static_rect, 2)
    pygame.draw.circle(screen, BLUE, player_rect.center, player_radius, 2)
    pygame.draw.circle(screen, BLUE, static_rect.center, static_radius, 2)

    pygame.display.flip()
    clock.tick(60)