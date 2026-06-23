# Experiment2_Rotation_Transformation
# 202411081099 计算机科学与技术 席子琦
本项目通过 [Taichi](https://www.taichi-lang.org/) 框架，手动推导并实现了完整的 **Model-View-Projection（MVP）** 变换流程，将三维空间中的几何体投影到二维屏幕上并进行实时线框渲染。

---

## 实验内容

### 基础任务：三角形旋转

实现三维空间中一个三角形的 MVP 变换，按键控制其绕 Z 轴旋转。

**顶点坐标：**
| 顶点 | 坐标 |
|------|------|
| v₀ | (2.0, 0.0, -2.0) |
| v₁ | (0.0, 2.0, -2.0) |
| v₂ | (-2.0, 0.0, -2.0) |

![三角形旋转演示](https://github.com/user-attachments/assets/430bf1d9-ee9c-47ec-b681-ec2862658a06)


**操作方式：**
- `A` — 逆时针旋转（绕 Z 轴）
- `D` — 顺时针旋转（绕 Z 轴）
- `Esc` — 退出

---

### 选做任务：三维立方体旋转

将基础任务升级为真正的三维线框立方体，支持双轴旋转与自动旋转，展现完整的透视空间感。

**立方体规格：**
- 中心在原点 `(0, 0, 0)`
- 边长为 2（顶点坐标在 `[-1, 1]` 之间）
- 8 个顶点，12 条棱

![立方体旋转演示](https://github.com/user-attachments/assets/b1e2a146-cf8c-48b0-9e69-946044cb338f)


**操作方式：**
- `A` / `D` — 绕 Y 轴旋转
- `W` / `S` — 绕 X 轴旋转
- `Space` — 切换自动旋转
- `Esc` — 退出

---

## MVP 变换流程

```
世界坐标 → [Model] → 视图空间 → [View] → 裁剪空间 → [Projection] → NDC → 屏幕坐标
```

### 1. 模型变换矩阵（Model Matrix）

绕 Z 轴旋转角度 θ：

$$M_{model} = \begin{bmatrix} \cos\theta & -\sin\theta & 0 & 0 \\ \sin\theta & \cos\theta & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}$$

### 2. 视图变换矩阵（View Matrix）

将相机从 `eye_pos` 平移至原点：

$$M_{view} = \begin{bmatrix} 1 & 0 & 0 & -e_x \\ 0 & 1 & 0 & -e_y \\ 0 & 0 & 1 & -e_z \\ 0 & 0 & 0 & 1 \end{bmatrix}$$

### 3. 投影变换矩阵（Projection Matrix）

先将透视平截头体挤压为正交长方体（$M_{persp \to ortho}$），再进行正交投影（$M_{ortho}$）：

$$M_{proj} = M_{ortho} \cdot M_{persp \to ortho}$$

其中视锥体边界由视场角 fov 和近截面距离 $|n|$ 推导：

$$t = \tan\!\left(\frac{fov}{2}\right) \cdot |n|, \quad b=-t, \quad r = aspect \cdot t, \quad l=-r$$

### 4. 透视除法

经 MVP 变换后得齐次坐标 $(x, y, z, w)$，除以 $w$ 得标准设备坐标（NDC）：

$$\mathbf{v}_{NDC} = \frac{\mathbf{v}_{clip}}{w}$$

### 5. 屏幕映射

$$screen_x = \frac{NDC_x + 1}{2}, \quad screen_y = \frac{NDC_y + 1}{2}$$

---

## 环境依赖

```
Python  3.12+
taichi  >= 1.7.0
```

安装依赖：

```bash
conda activate leaf
pip install taichi -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 运行方式

```bash
# 基础任务：三角形
python sanjiaoxing.py

# 选做任务：立方体
python cube_mvp.py
```

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `sanjiaoxing.py` | 基础任务：三角形 MVP 变换 |
| `cube_mvp.py` | 选做任务：三维立方体线框渲染 |
