import base64, io
import pygame

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  스프라이트 시트 Base64 데이터
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SHEET_B64 = "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"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCREEN_W, SCREEN_H = 480, 320
FRAME_W, FRAME_H   = 96, 84
COLS               = 8
FRAME_DELAY        = 150   # ms
DISPLAY_SCALE      = 4     # 화면 확대 배율

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Sprite Animation Demo")
clock = pygame.time.Clock()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  시트 로드 → 프레임 리스트
#  인덱스 0 ~ 7 (총 8개)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sheet_bytes = base64.b64decode(SHEET_B64)
player_sheet = pygame.image.load(io.BytesIO(sheet_bytes)).convert_alpha()

player_frames = []
for i in range(8):
    row, col = divmod(i, COLS)
    rect = pygame.Rect(col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H)
    player_frames.append(player_sheet.subsurface(rect))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  walk_frames: 선택한 프레임 순서
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
walk_frames = [player_frames[i] for i in [0, 1, 2, 3, 4, 5, 6, 7]]

frame_index = 0
frame_timer = 0
x = SCREEN_W // 2 - (FRAME_W * DISPLAY_SCALE) // 2
y = SCREEN_H // 2 - (FRAME_H * DISPLAY_SCALE) // 2

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  게임 루프
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
running = True
while running:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    frame_timer += dt
    if frame_timer >= FRAME_DELAY:
        frame_index = (frame_index + 1) % len(walk_frames)
        frame_timer = 0

    screen.fill((30, 30, 40))
    frame_img = pygame.transform.scale(
        walk_frames[frame_index],
        (FRAME_W * DISPLAY_SCALE, FRAME_H * DISPLAY_SCALE)
    )
    screen.blit(frame_img, (x, y))
    pygame.display.flip()

pygame.quit()
