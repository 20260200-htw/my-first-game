from ursina import *
app = Ursina(borderless=False)
box = Entity(model='cube', color=color.orange, position=Vec3(-2, 0, 0))
ball = Entity(model='sphere', color=color.azure, position=Vec3( 0, 0, 0))
ground = Entity(model='plane', color=color.green, scale=10,
    position=Vec3(0, -1, 0))
camera.position = (0, 3, -10)
camera.look_at(Vec3(0, 0, 0))
def update():
    box.rotation_y += 50 * time.dt
    ball.rotation_x += 30 * time.dt
app.run()
