import pygame
import sys

# 1. 초기화 및 창 설정
pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("SAT 기반 OBB 충돌 감지")

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

static_rect_size = (100, 100)
static_center = (screen_width // 2, screen_height // 2)
static_radius = static_rect_size[0] // 2

# 회전 관련 변수
angle = 0
base_rotation_speed = 1

clock = pygame.time.Clock()

# --- SAT 충돌 라이브러리 함수 ---

def get_obb_points(center, size, angle):
    cx, cy = center
    w, h = size
    points = [
        pygame.Vector2(-w//2, -h//2),
        pygame.Vector2(w//2, -h//2),
        pygame.Vector2(w//2, h//2),
        pygame.Vector2(-w//2, h//2)
    ]
    return [p.rotate(angle) + (cx, cy) for p in points]

def get_axes(points):
    """다각형의 변에 수직인 법선 벡터(분리축 후보)들을 추출"""
    axes = []
    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)]
        edge = p2 - p1
        # 변에 수직인 벡터(법선) 계산
        normal = pygame.Vector2(-edge.y, edge.x)
        if normal.length() > 0:
            axes.append(normal.normalize())
    return axes

def project_polygon(points, axis):
    """축 위로 다각형의 모든 점을 투영시켜 최소/최대 범위를 반환"""
    dots = [p.dot(axis) for p in points]
    return min(dots), max(dots)

def check_obb_collision(poly1, poly2):
    """SAT 알고리즘을 사용해 두 다각형의 충돌 여부 판단"""
    axes = get_axes(poly1) + get_axes(poly2)
    for axis in axes:
        min1, max1 = project_polygon(poly1, axis)
        min2, max2 = project_polygon(poly2, axis)
        # 투영된 범위 사이에 틈(Gap)이 있다면 충돌하지 않음
        if max1 < min2 or max2 < min1:
            return False
    return True # 모든 축에서 겹친다면 충돌

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 3. 입력 처리
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  player_rect.x -= player_speed
    if keys[pygame.K_RIGHT]: player_rect.x += player_speed
    if keys[pygame.K_UP]:    player_rect.y -= player_speed
    if keys[pygame.K_DOWN]:  player_rect.y += player_speed
    
    rotation_speed = base_rotation_speed * 5 if keys[pygame.K_z] else base_rotation_speed
    angle += rotation_speed

    # 4. 충돌 데이터 준비
    # 플레이어와 고정 오브젝트의 실시간 꼭짓점(OBB) 좌표 추출
    player_points = get_obb_points(player_rect.center, (player_rect.width, player_rect.height), 0)
    static_points = get_obb_points(static_center, static_rect_size, angle)

    # SAT 충돌 감지 수행
    obb_colliding = check_obb_collision(player_points, static_points)

    # 5. 화면 그리기
    # OBB 충돌 시 배경 빨간색, 원형 충돌 시 노란색 (중첩 시 빨간색 우선)
    dx = player_rect.centerx - static_center[0]
    dy = player_rect.centery - static_center[1]
    circle_colliding = (dx**2 + dy**2) <= (player_radius + static_radius)**2

    bg_color = RED if obb_colliding else (YELLOW if circle_colliding else BG_COLOR)
    screen.fill(bg_color)

    # 본체 그리기 (회전 구현)
    static_surface = pygame.Surface(static_rect_size, pygame.SRCALPHA)
    static_surface.fill(GRAY)
    rotated_static = pygame.transform.rotate(static_surface, -angle)
    new_rect = rotated_static.get_rect(center=static_center)
    
    pygame.draw.rect(screen, GRAY, player_rect)
    screen.blit(rotated_static, new_rect.topleft)

    # 시각화 (AABB-빨강, OBB-초록, 원-파랑)
    pygame.draw.rect(screen, RED, player_rect, 2)
    pygame.draw.rect(screen, RED, new_rect, 2)
    pygame.draw.polygon(screen, GREEN, static_points, 2)
    pygame.draw.polygon(screen, GREEN, player_points, 2)
    pygame.draw.circle(screen, BLUE, player_rect.center, player_radius, 2)
    pygame.draw.circle(screen, BLUE, static_center, static_radius, 2)

    pygame.display.flip()
    clock.tick(60)