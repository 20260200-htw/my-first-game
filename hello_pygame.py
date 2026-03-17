import pygame
import sys
pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption("My First Pygame")
WHITE = (0, 0, 0)
BLUE = (255, 0, 0)
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)
SIZE = 10
circle_x = 400
circle_y = 300
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        circle_x -= 10
    if keys[pygame.K_RIGHT]:
        circle_x += 10
    if keys[pygame.K_UP]:
        circle_y -= 10
    if keys[pygame.K_DOWN]:
        circle_y += 10
    circle_x = max(SIZE, min(circle_x, 400 - SIZE))
    circle_y = max(SIZE, min(circle_y, 400 - SIZE))
    screen.fill(WHITE)

    # AI로 작성된 주석입니다. 삼각형의 세 꼭짓점 좌표 계산 (중심 기준 위쪽/좌하/우하)
    triangle_points = [
        (circle_x, circle_y - SIZE),
        (circle_x - SIZE, circle_y + SIZE),
        (circle_x + SIZE, circle_y + SIZE)
    ]
    # AI로 작성된 주석입니다. pygame.draw.polygon 으로 삼각형 그리기, 마지막 숫자(1) = 테두리 두께
    pygame.draw.polygon(screen, BLUE, triangle_points, 1)

    fps = int(clock.get_fps())
    fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
sys.exit()