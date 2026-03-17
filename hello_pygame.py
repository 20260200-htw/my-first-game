import pygame
import sys
import random # AI로 작성된 주석입니다. 랜덤 색상 생성을 위한 모듈 추가
pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption("My First Pygame")
WHITE = (0, 0, 0)
BLUE = (255, 0, 0)
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)
RADIUS = 10
circle_x = 400
circle_y = 300
# AI로 작성된 주석입니다. 원의 초기 색상을 BLUE로 설정
circle_color = BLUE
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()

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

    circle_x = max(RADIUS, min(circle_x, 400 - RADIUS))
    circle_y = max(RADIUS, min(circle_y, 400 - RADIUS))
    screen.fill(WHITE)
    pygame.draw.circle(screen, circle_color, (circle_x, circle_y), RADIUS, 1)
    fps = int(clock.get_fps())
    fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
sys.exit()