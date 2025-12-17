import numpy as np
import matplotlib.pyplot as plt

# ===================== КОНСТАНТЫ KERBIN =====================
g0 = 9.81                         # м/с^2
R_kerbin = 600_000                # м
mu_kerbin = 3.5316e12             # м^3/с^2

# Атмосфера Kerbin (экспоненциальная модель)
rho0 = 1.225                      # кг/м^3
H = 5000                          # м

# Аэродинамика
Cx = 0.4

# ===================== ПАРАМЕТРЫ СТУПЕНЕЙ =====================
# m0, m_dry, thrust, Isp_sl, Isp_vac, burn_time, diameter
stages = [
    [278.975, 115.4, 5740, 257, 316, 60, 8.5],   # 1 ступень
    [115.4,   60.3,  1340, 314, 314, 130, 4.5],  # 2 ступень
    [36.3,    25.0,   860, 320, 320, 40,  4.5]   # 3 ступень
]

# Приведение к СИ
for s in stages:
    s[0] *= 1000        # т → кг
    s[1] *= 1000
    s[2] *= 1000        # кН → Н

# ===================== ФИЗИЧЕСКИЕ ФУНКЦИИ =====================
def gravity(h):
    """ g(h) = μ / (R + h)^2 """
    return mu_kerbin / (R_kerbin + h) ** 2


def density(h):
    """ ρ(h) = ρ0 * exp(-h / H) """
    return rho0 * np.exp(-h / H)


def isp_stage(h, stage_idx):
    """ Интерполяция Isp для 1 ступени """
    s = stages[stage_idx]
    if stage_idx == 0:
        return s[3] + (s[4] - s[3]) * (1 - np.exp(-h / H))
    else:
        return s[4]


# ===================== МОДЕЛИРОВАНИЕ =====================
dt = 0.1
total_time = sum(s[5] for s in stages)
time = np.arange(0, total_time + dt, dt)

# Массивы
m = np.zeros_like(time)
v = np.zeros_like(time)
a = np.zeros_like(time)
h = np.zeros_like(time)

# Начальные условия
m[0] = stages[0][0]
v[0] = 0
h[0] = 0

# Основной цикл
for i in range(len(time) - 1):
    t = time[i]

    # Определяем текущую ступень
    if t < stages[0][5]:
        stage_idx = 0
        t_stage = t
        m0, mdry, T, _, _, tburn, d = stages[0]
    elif t < stages[0][5] + stages[1][5]:
        stage_idx = 1
        t_stage = t - stages[0][5]
        m0, mdry, T, _, _, tburn, d = stages[1]
    else:
        stage_idx = 2
        t_stage = t - stages[0][5] - stages[1][5]
        m0, mdry, T, _, _, tburn, d = stages[2]

    # Расход массы
    Isp = isp_stage(h[i], stage_idx)
    mdot = T / (Isp * g0)

    m[i] = max(mdry, m0 - mdot * t_stage)

    # Силы
    g = gravity(h[i])
    rho = density(h[i])
    S = np.pi * (d / 2) ** 2

    F_thrust = T if t_stage <= tburn else 0
    F_gravity = m[i] * g
    F_drag = 0.5 * Cx * rho * S * v[i] ** 2 if v[i] > 0 else 0

    # Второй закон Ньютона
    a[i] = (F_thrust - F_gravity - F_drag) / m[i]

    # Интегрирование
    v[i + 1] = v[i] + a[i] * dt
    h[i + 1] = h[i] + v[i] * dt

# Последняя точка
m[-1] = m[-2]
a[-1] = a[-2]

# ===================== ГРАФИКИ =====================
plt.figure(figsize=(12, 9))

# Скорость
plt.subplot(3, 1, 1)
plt.plot(time, v, linewidth=2)
plt.ylabel("Скорость, м/с")
plt.title("Скорость от времени")
plt.grid(alpha=0.3)
plt.axvline(stages[0][5], linestyle='--')
plt.axvline(stages[0][5] + stages[1][5], linestyle='--')

# Ускорение
plt.subplot(3, 1, 2)
plt.plot(time, a, linewidth=2)
plt.ylabel("Ускорение, м/с²")
plt.title("Ускорение от времени")
plt.grid(alpha=0.3)
plt.axhline(0, alpha=0.3)
plt.axvline(stages[0][5], linestyle='--')
plt.axvline(stages[0][5] + stages[1][5], linestyle='--')

# Масса
plt.subplot(3, 1, 3)
plt.plot(time, m / 1000, linewidth=2)
plt.xlabel("Время, с")
plt.ylabel("Масса, т")
plt.title("Масса от времени")
plt.grid(alpha=0.3)
plt.axvline(stages[0][5], linestyle='--')
plt.axvline(stages[0][5] + stages[1][5], linestyle='--')

plt.tight_layout()
plt.show()

# ===================== ВЫВОД =====================
print("=" * 55)
print("РЕЗУЛЬТАТЫ МОДЕЛИРОВАНИЯ (Kerbin, KSP)")
print("=" * 55)
print(f"Максимальная скорость: {v.max():.0f} м/с")
print(f"Максимальное ускорение: {a.max():.2f} м/с²")
print(f"Максимальная высота: {h.max() / 1000:.1f} км")
print(f"Общее время работы двигателей: {total_time} с")
print("=" * 55)
