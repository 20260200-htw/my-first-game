import pygame
import sys

# 1. 초기화 및 창 설정
pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Collision Comparison: Circle vs AABB vs OBB")

# 색상 정의
GRAY = (150, 150, 150)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BG_COLOR = (30, 30, 30)
WHITE = (255, 255, 255)

# 폰트 설정
font = pygame.font.SysFont("arial", 24, bold=True)

# 2. 오브젝트 설정
player_rect = pygame.Rect(100, 100, 80, 80)
player_radius = player_rect.width // 2
player_speed = 5

static_rect_size = (100, 100)
static_center = (screen_width // 2, screen_height // 2)
static_radius = static_rect_size[0] // 2

angle = 0
base_rotation_speed = 1

clock = pygame.time.Clock()

# --- SAT 충돌 함수 (OBB용) ---
def get_obb_points(center, size, angle):
    cx, cy = center
    w, h = size
    points = [pygame.Vector2(-w//2, -h//2), pygame.Vector2(w//2, -h//2),
              pygame.Vector2(w//2, h//2), pygame.Vector2(-w//2, h//2)]
    return [p.rotate(angle) + (cx, cy) for p in points]

def get_axes(points):
    axes = []
    for i in range(len(points)):
        edge = points[(i + 1) % len(points)] - points[i]
        axes.append(pygame.Vector2(-edge.y, edge.x).normalize())
    return axes

def project_polygon(points, axis):
    dots = [p.dot(axis) for p in points]
    return min(dots), max(dots)

def check_obb_collision(poly1, poly2):
    axes = get_axes(poly1) + get_axes(poly2)
    for axis in axes:
        min1, max1 = project_polygon(poly1, axis)
        min2, max2 = project_polygon(poly2, axis)
        if max1 < min2 or max2 < min1: return False
    return True

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 3. 입력 및 회전 업데이트
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  player_rect.x -= player_speed
    if keys[pygame.K_RIGHT]: player_rect.x += player_speed
    if keys[pygame.K_UP]:    player_rect.y -= player_speed
    if keys[pygame.K_DOWN]:  player_rect.y += player_speed
    
    rotation_speed = base_rotation_speed * 5 if keys[pygame.K_z] else base_rotation_speed
    angle += rotation_speed

    # 4. 각 충돌 방식 계산
    # [1] 원형 충돌
    dx = player_rect.centerx - static_center[0]
    dy = player_rect.centery - static_center[1]
    circle_hit = (dx**2 + dy**2) <= (player_radius + static_radius)**2

    # [2] OBB 충돌 (SAT)
    player_points = get_obb_points(player_rect.center, (player_rect.width, player_rect.height), 0)
    static_points = get_obb_points(static_center, static_rect_size, angle)
    obb_hit = check_obb_collision(player_points, static_points)

    # [3] AABB 충돌 (회전된 표면의 Rect 기반)
    static_surface = pygame.Surface(static_rect_size, pygame.SRCALPHA)
    rotated_static = pygame.transform.rotate(static_surface, -angle)
    new_rect = rotated_static.get_rect(center=static_center) # 이것이 회전체를 감싸는 AABB
    aabb_hit = player_rect.colliderect(new_rect)

    # 5. 화면 그리기
    screen.fill(BG_COLOR)

    # 오브젝트 본체
    static_surface.fill(GRAY)
    rotated_static = pygame.transform.rotate(static_surface, -angle)
    pygame.draw.rect(screen, GRAY, player_rect)
    screen.blit(rotated_static, new_rect.topleft)

    # --- 디버그 드로잉 ---
    # AABB (빨강)
    pygame.draw.rect(screen, RED, player_rect, 2)
    pygame.draw.rect(screen, RED, new_rect, 2)
    # OBB (초록)
    pygame.draw.polygon(screen, GREEN, player_points, 2)
    pygame.draw.polygon(screen, GREEN, static_points, 2)
    # Circle (파랑)
    pygame.draw.circle(screen, BLUE, player_rect.center, player_radius, 2)
    pygame.draw.circle(screen, BLUE, static_center, static_radius, 2)

    # --- UI 텍스트 표시 (왼쪽 상단) ---
    texts = [
        ("Circle: HIT", BLUE if circle_hit else GRAY),
        ("AABB: HIT", RED if aabb_hit else GRAY),
        ("OBB: HIT", GREEN if obb_hit else GRAY)
    ]

    for i, (msg, color) in enumerate(texts):
        label = font.render(msg, True, color)
        screen.blit(label, (20, 20 + (i * 35)))

    pygame.display.flip()
    clock.tick(60)