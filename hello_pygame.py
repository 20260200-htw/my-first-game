import pygame
import sys
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
    circle_x = max(RADIUS, min(circle_x, 400 - RADIUS))
    circle_y = max(RADIUS, min(circle_y, 400 - RADIUS))
    screen.fill(WHITE)
    pygame.draw.circle(screen, BLUE, (circle_x, circle_y), RADIUS, 1)
    fps = int(clock.get_fps())
    fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
sys.exit()