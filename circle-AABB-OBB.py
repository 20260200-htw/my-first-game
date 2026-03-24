import pygame
import sys

# 1. 초기화 및 창 설정
pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("OBB & Rotation Visualization")

# 색상 정의
GRAY = (150, 150, 150)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BG_COLOR = (30, 30, 30)

# 2. 오브젝트 설정
player_rect = pygame.Rect(100, 100, 80, 80)
player_radius = player_rect.width // 2
player_speed = 5

static_rect = pygame.Rect(0, 0, 100, 100)
static_center = (screen_width // 2, screen_height // 2)
static_radius = static_rect.width // 2

# 회전 관련 변수
angle = 0
base_rotation_speed = 1

clock = pygame.time.Clock()

def get_obb_points(center, size, angle):
    """중심점, 크기, 각도를 받아 OBB의 네 꼭짓점 좌표를 반환"""
    cx, cy = center
    w, h = size
    # 사각형의 네 꼭짓점 상대 좌표
    points = [
        pygame.Vector2(-w//2, -h//2),
        pygame.Vector2(w//2, -h//2),
        pygame.Vector2(w//2, h//2),
        pygame.Vector2(-w//2, h//2)
    ]
    # 각 꼭짓점을 회전시킨 후 중심점을 더함
    rotated_points = [p.rotate(angle) + (cx, cy) for p in points]
    return rotated_points

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 3. 입력 처리
    keys = pygame.key.get_pressed()
    # 방향키 이동
    if keys[pygame.K_LEFT]:  player_rect.x -= player_speed
    if keys[pygame.K_RIGHT]: player_rect.x += player_speed
    if keys[pygame.K_UP]:    player_rect.y -= player_speed
    if keys[pygame.K_DOWN]:  player_rect.y += player_speed
    
    # Z 키로 회전 속도 조절
    rotation_speed = base_rotation_speed * 5 if keys[pygame.K_z] else base_rotation_speed
    angle += rotation_speed

    # 4. 원형 충돌 계산 (제곱 비교 방식)
    dx = player_rect.centerx - static_center[0]
    dy = player_rect.centery - static_center[1]
    distance_squared = dx**2 + dy**2
    radii_sum_squared = (player_radius + static_radius)**2
    circle_colliding = distance_squared <= radii_sum_squared

    # 5. 화면 그리기
    screen.fill(YELLOW if circle_colliding else BG_COLOR)

    # 고정 오브젝트 회전 표현을 위한 Surface 생성
    static_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
    static_surface.fill(GRAY)
    rotated_static = pygame.transform.rotate(static_surface, -angle) # 시계 방향 회전
    new_rect = rotated_static.get_rect(center=static_center)

    # 오브젝트 본체 그리기
    pygame.draw.rect(screen, GRAY, player_rect) # 플레이어
    screen.blit(rotated_static, new_rect.topleft) # 회전하는 사각형

    # AABB 표시 (빨간색 - 회전하지 않는 고정 영역)
    pygame.draw.rect(screen, RED, player_rect, 2)
    pygame.draw.rect(screen, RED, new_rect, 2) 

    # OBB 표시 (초록색 - 오브젝트와 함께 회전하는 영역)
    obb_points = get_obb_points(static_center, (100, 100), angle)
    pygame.draw.polygon(screen, GREEN, obb_points, 2)

    # 원형 Bounding Box 표시 (파란색)
    pygame.draw.circle(screen, BLUE, player_rect.center, player_radius, 2)
    pygame.draw.circle(screen, BLUE, static_center, static_radius, 2)

    pygame.display.flip()
    clock.tick(60)