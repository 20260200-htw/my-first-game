from ursina import *
app = Ursina(borderless=False) # 창 이동 가능하게
box = Entity(model='cube', color=color.orange)
def update():
    box.rotation_y += 50 * time.dt # 초당 50° 회전
app.run()
