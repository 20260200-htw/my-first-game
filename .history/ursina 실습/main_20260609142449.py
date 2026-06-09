from ursina import *
app = Ursina(borderless=False) # 창 이동 가능하게
box = Entity(
    model = 'cube', # 'sphere', 'plane' 으로 바꿔보기
    color = color.azure, # color.red, color.azure 등
    position = Vec3(0, 0, 0), # 위치 바꿔보기
    scale = Vec3(1, 1, 1), # Vec3(2,1,1) 등
)

def update():
    box.rotation_y += 50 * time.dt # 초당 50° 회전
app.run()
