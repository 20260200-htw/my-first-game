import pygame

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Sound Basics")
clock = pygame.time.Clock()

# ── ① 효과음 로드 ──────────────────────────────
shoot_sound = pygame.mixer.Sound("./assets/sounds/shoot.wav")

# ── ② 배경음악 로드 ────────────────────────────
pygame.mixer.music.load("./assets/sounds/bgm.wav")

# ── ③ 볼륨 조절 ────────────────────────────────
shoot_sound.set_volume(1)        # 0.0 ~ 1.0
pygame.mixer.music.set_volume(0.25)

# ── ④ 배경음악 재생 ────────────────────────────
pygame.mixer.music.play(2)  # -1: 무한 반복 / #play()인수에서 ()에 들어가는 수는 추가 반복의 의미, 2면 3번 재생

running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            # ── ⑤ 스페이스바로 효과음 재생 ────
            if event.key == pygame.K_SPACE:
                shoot_sound.play()

    screen.fill((30, 30, 40))
    pygame.display.flip()

pygame.quit()
