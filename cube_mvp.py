import taichi as ti
import math

ti.init(arch=ti.cpu)

# 8个顶点，12条边
NUM_VERTICES = 8
NUM_EDGES = 12

vertices    = ti.Vector.field(3, dtype=ti.f32, shape=NUM_VERTICES)
screen_coords = ti.Vector.field(2, dtype=ti.f32, shape=NUM_VERTICES)

# 12条边，每条边是两个顶点的索引
edges = ti.Vector.field(2, dtype=ti.i32, shape=NUM_EDGES)

def init_cube():
    # 单位正方体，中心在原点，边长2，顶点坐标在[-1,1]
    verts = [
        [-1, -1, -1],  # 0
        [ 1, -1, -1],  # 1
        [ 1,  1, -1],  # 2
        [-1,  1, -1],  # 3
        [-1, -1,  1],  # 4
        [ 1, -1,  1],  # 5
        [ 1,  1,  1],  # 6
        [-1,  1,  1],  # 7
    ]
    for i, v in enumerate(verts):
        vertices[i] = v

    # 12条边：底面4 + 顶面4 + 侧面4
    edg = [
        [0, 1], [1, 2], [2, 3], [3, 0],  # 底面
        [4, 5], [5, 6], [6, 7], [7, 4],  # 顶面
        [0, 4], [1, 5], [2, 6], [3, 7],  # 侧面
    ]
    for i, e in enumerate(edg):
        edges[i] = e

@ti.func
def get_model_matrix_y(angle: ti.f32):
    """绕Y轴旋转"""
    rad = angle * math.pi / 180.0
    c = ti.cos(rad)
    s = ti.sin(rad)
    return ti.Matrix([
        [ c,  0.0, s,  0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-s,  0.0, c,  0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])

@ti.func
def get_model_matrix_x(angle: ti.f32):
    """绕X轴旋转"""
    rad = angle * math.pi / 180.0
    c = ti.cos(rad)
    s = ti.sin(rad)
    return ti.Matrix([
        [1.0, 0.0, 0.0, 0.0],
        [0.0,  c,  -s,  0.0],
        [0.0,  s,   c,  0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])

@ti.func
def get_view_matrix(eye_pos: ti.template()):
    return ti.Matrix([
        [1.0, 0.0, 0.0, -eye_pos[0]],
        [0.0, 1.0, 0.0, -eye_pos[1]],
        [0.0, 0.0, 1.0, -eye_pos[2]],
        [0.0, 0.0, 0.0,          1.0]
    ])

@ti.func
def get_projection_matrix(eye_fov: ti.f32, aspect_ratio: ti.f32, zNear: ti.f32, zFar: ti.f32):
    n = -zNear
    f = -zFar
    fov_rad = eye_fov * math.pi / 180.0
    t = ti.tan(fov_rad / 2.0) * ti.abs(n)
    b = -t
    r = aspect_ratio * t
    l = -r

    M_p2o = ti.Matrix([
        [n,   0.0, 0.0,    0.0],
        [0.0, n,   0.0,    0.0],
        [0.0, 0.0, n + f, -n * f],
        [0.0, 0.0, 1.0,    0.0]
    ])
    M_ortho_trans = ti.Matrix([
        [1.0, 0.0, 0.0, -(r + l) / 2.0],
        [0.0, 1.0, 0.0, -(t + b) / 2.0],
        [0.0, 0.0, 1.0, -(n + f) / 2.0],
        [0.0, 0.0, 0.0,  1.0]
    ])
    M_ortho_scale = ti.Matrix([
        [2.0 / (r - l), 0.0,           0.0,           0.0],
        [0.0,           2.0 / (t - b), 0.0,           0.0],
        [0.0,           0.0,           2.0 / (n - f), 0.0],
        [0.0,           0.0,           0.0,           1.0]
    ])
    return M_ortho_scale @ M_ortho_trans @ M_p2o

@ti.kernel
def compute_transform(angle_y: ti.f32, angle_x: ti.f32):
    eye_pos = ti.Vector([0.0, 0.0, 5.0])
    model = get_model_matrix_y(angle_y) @ get_model_matrix_x(angle_x)
    view  = get_view_matrix(eye_pos)
    proj  = get_projection_matrix(45.0, 1.0, 0.1, 50.0)
    mvp   = proj @ view @ model

    for i in range(NUM_VERTICES):
        v  = vertices[i]
        v4 = ti.Vector([v[0], v[1], v[2], 1.0])
        v_clip = mvp @ v4
        v_ndc  = v_clip / v_clip[3]
        screen_coords[i][0] = (v_ndc[0] + 1.0) / 2.0
        screen_coords[i][1] = (v_ndc[1] + 1.0) / 2.0

def main():
    init_cube()

    gui     = ti.GUI("3D Cube Rotate (Taichi)", res=(700, 700))
    angle_y = 30.0
    angle_x = 20.0

    print("操作说明：")
    print("  A / D  —— 绕 Y 轴旋转")
    print("  W / S  —— 绕 X 轴旋转")
    print("  Esc    —— 退出")

    while gui.running:
        if gui.get_event(ti.GUI.PRESS):
            if gui.event.key == 'a':
                angle_y += 10.0
            elif gui.event.key == 'd':
                angle_y -= 10.0
            elif gui.event.key == 'w':
                angle_x += 10.0
            elif gui.event.key == 's':
                angle_x -= 10.0
            elif gui.event.key == ti.GUI.ESCAPE:
                gui.running = False

        compute_transform(angle_y, angle_x)

        for i in range(NUM_EDGES):
            idx_a = edges[i][0]
            idx_b = edges[i][1]
            pa = screen_coords[idx_a]
            pb = screen_coords[idx_b]
            gui.line(pa, pb, radius=2, color=0x00CFFF)

        gui.show()

if __name__ == '__main__':
    main()
