import numpy as np # реализует математические функции
import matplotlib.pyplot as plt # отвечает за построение графиков
import json

# КОНСТАНТЫ из твоей модели
mu_k = 3.5316e12      # гравитационный параметр Kerbin, м³/с²
R_k = 600000          # радиус Kerbin, м [file:42]
g0 = 9.81             # ускорение свободного падения у поверхности, м/с²
rho0 = 1.225          # плотность на уровне моря, кг/м³
H = 5000              # масштаб высоты атмосферы Kerbin, м

ton = 1000
kN = 1000

# ХАРАКТЕРИСТИКИ СТУПЕНЕЙ РАКЕТЫ
stages = [
    {  # Первая ступень
        'm0': 278.975 * ton,           # стартовая масса всей ракеты, кг
        'mt': (278.975 - 166.0) * ton, # масса топлива, кг
        't_stage': 60,                 # время работы, с
        'thrust': 5740 * kN,           # тяга, Н
        'Isp_sl': 257,                 # удельный импульс у земли, с
        'Isp_vac': 316,                # удельный импульс в вакууме, с
        'S': 56.75,                    # площадь = π*(8.5/2)², м²
        'Cx': 0.8                   # коэффициент лобового сопротивления
    },
    {  # Вторая ступень
        'm0': 115.4 * ton,             # масса в момент включения, кг
        'mt': (115.4 - 60.3) * ton,    # масса топлива, кг
        't_stage': 130,                # время работы, с
        'thrust': 1340 * kN,           # тяга, Н
        'Isp_vac': 314,                # удельный импульс в вакууме, с
        'S': 15.90,                    # площадь = π*(4.5/2)², м²
        'Cx': 0.4
    },
    {  # Третья ступень
        'm0': 36.3 * ton,              # масса в момент включения, кг
        'mt': (36.3 - 25.0) * ton,     # масса топлива, кг
        't_stage': 40,                 # время работы, с
        'thrust': 860 * kN,            # тяга, Н
        'Isp_vac': 320,                # удельный импульс в вакууме, с
        'S': 15.90,                    # площадь = π*(4.5/2)², м²
        'Cx': 0.4
    }
]

# Чтение углов из KSP
with open("rocket_vertical_angle_data.json", encoding="UTF-8") as f:
    sl_pitchs = json.load(f)

pitchs = {}
for i in range(len(sl_pitchs)):
    pitchs[round(sl_pitchs[i]["time"])] = round(sl_pitchs[i]["pitch_vertical"])

# Чтение Isp из KSP
with open("rocket_specific_impulse.json", encoding="UTF-8") as f:
    sl_isp = json.load(f)

isps = {}
for i in range(len(sl_isp)):
    isps[round(sl_isp[i]["time"])] = round(sl_isp[i]["average_specific_impulse"])

def rho(h): # зависимость плотности воздуха от высоты ρ(h)=ρ0 exp(-h/H)
    if h <= 0:
        h = 0
    return rho0 * np.exp(-h / H)

# НАЧАЛЬНЫЕ УСЛОВИЯ
t_total = sum(stage['t_stage'] for stage in stages)  # общее время полёта
dt = 0.1
t = np.arange(0, 230, dt)  # 60+130+40=230с

# Массивы результатов
h = np.zeros_like(t)  # высота, м
vx = np.zeros_like(t)  # горизонтальная скорость, м/с
vy = np.zeros_like(t)  # вертикальная скорость, м/с
v = np.zeros_like(t)  # модуль скорости, м/с
m = np.zeros_like(t)  # масса, кг
ax = np.zeros_like(t)  # горизонтальное ускорение, м/с²
ay = np.zeros_like(t)  # вертикальное ускорение, м/с²
stage_idx = np.zeros_like(t, dtype=int)  # номер текущей ступени

# Начальные значения
h[0] = 0
vx[0] = 0
vy[0] = 0
m[0] = stages[0]['m0']
current_stage = 0
t_stage_start = 0

for i in range(1, len(t)):
    t_curr = t[i]
    # определяем текущую ступень
    while current_stage < len(stages) and t_curr >= t_stage_start + stages[current_stage]['t_stage']:
        t_stage_start += stages[current_stage]['t_stage']
        current_stage += 1

    if current_stage >= len(stages):
        current_stage = len(stages) - 1  # последняя ступень до конца

    stage = stages[current_stage]
    stage_idx[i] = current_stage

    t_in_stage = t_curr - t_stage_start

    # масса линейно уменьшается при сжигании топлива m(t)=m0-ṁt, ṁ=mt/t_stage
    if t_in_stage <= stage['t_stage']:
        m[i] = stage['m0'] - (stage['mt'] / stage['t_stage']) * t_in_stage
    else:
        # сухая масса после ступени
        m[i] = stage['m0'] - stage['mt']

    # g(h)=μk/(Rk+h)²
    g_h = mu_k / (R_k + h[i - 1]) ** 2
    rho_h = rho(h[i - 1]) # плотность воздуха ρ(h)=ρ0 exp(-h/H)
    v[i] = np.sqrt(vx[i - 1] ** 2 + vy[i - 1] ** 2) # модуль скорости

    # Isp: из JSON или по модели Isp(h) для 1-й ступени
    I_json = isps.get(round(t_curr), None)
    if current_stage == 0 and I_json is None:
        # Isp(h)=Isp_sl+(Isp_vac-Isp_sl)*(1-exp(-h/H))
        I = (stage['Isp_sl'] + (stage['Isp_vac'] - stage['Isp_sl']) * (1.0 - np.exp(-h[i-1]/H)))
    else:
        I = I_json if I_json is not None else stage.get('Isp_vac', 300)

    # тяга по модели: ṁ=T/(Isp g0), F_thrust=ṁ Isp g0
    T = stage['thrust']
    mdot = T / (I * g0)
    F_thrust = mdot * I * g0  # =T математически

    # выключаем тягу
    if t_in_stage > stage['t_stage']:
        F_thrust = 0.0

    # проекции силы тяги из JSON
    theta_t = np.deg2rad(pitchs.get(round(t_curr), 90))  # 90° по умолчанию
    F_thrust_x = F_thrust * np.sin(theta_t)
    F_thrust_y = F_thrust * np.cos(theta_t)

    F_gravity = m[i] * g_h # сила тяжести
    F_drag = 0.5 * stage['Cx'] * rho_h * stage['S'] * v[i] ** 2

    # проекции (противоположно скорости)
    if v[i] > 0:
        F_drag_x = -F_drag * (vx[i - 1] / v[i])
        F_drag_y = -F_drag * (vy[i - 1] / v[i])
    else:
        F_drag_x, F_drag_y = 0.0, 0.0

    # ускорения по итоговой системе
    ax[i] = (F_thrust_x + F_drag_x) / m[i]
    ay[i] = (F_thrust_y - F_gravity + F_drag_y) / m[i]

    # обновление скоростей и высоты
    vx[i] = vx[i - 1] + ax[i] * dt
    vy[i] = vy[i - 1] + ay[i] * dt
    h[i] = h[i - 1] + vy[i] * dt

# Чтение KSP данных
with open("rocket_mass_data.json", encoding="UTF-8") as f:
    sl_mass = json.load(f)
mass_ksp = [elem['mass'] for elem in sl_mass if elem["time"] <= 230]
mass_ksp_t = [elem['time'] for elem in sl_mass if elem["time"] <= 230]

with open("rocket_height_data.json", encoding="UTF-8") as f:
    sl_height = json.load(f)
height_ksp = [elem['height'] for elem in sl_height if elem["time"] <= 230]
height_ksp_t = [elem['time'] for elem in sl_height if elem["time"] <= 230]

with open("rocket_speed_data.json", encoding="UTF-8") as f:
    sl_speed = json.load(f)
speed_ksp = [elem['speed'] for elem in sl_speed if elem["time"] <= 230]
speed_ksp_t = [elem['time'] for elem in sl_speed if elem["time"] <= 230]

# ПОСТРОЕНИЕ ГРАФИКОВ
fig, axs = plt.subplots(3, 1, figsize=(12, 14))
fig.suptitle('Графики зависимости высоты, скорости и массы от времени', fontsize=16)

dt = 0.1  # шаг времени из твоего кода
t_215_idx = int(215 / dt) + 1

# Высота
axs[0].plot(t[:t_215_idx], h[:t_215_idx], label='Мат. модель', color='navy')
axs[0].plot([x for x in height_ksp_t if x <= 215],
            [y for x, y in zip(height_ksp_t, height_ksp) if x <= 215],
            label="KSP", color="red")
axs[0].set_xlabel('Время, с')
axs[0].set_ylabel('Высота, м')
axs[0].set_title('Высота полёта, м')
axs[0].grid(True, linestyle='--', alpha=0.7)
axs[0].legend()

# Скорость
axs[1].plot(t[:t_215_idx], v[:t_215_idx], label='Мат. модель', color='navy')
axs[1].plot([x for x in speed_ksp_t if x <= 215],
            [y for x, y in zip(speed_ksp_t, speed_ksp) if x <= 215],
            label="KSP", color="red", alpha=0.7)
axs[1].set_xlabel('Время, с')
axs[1].set_ylabel('Скорость, м/с')
axs[1].grid(True, linestyle='--', alpha=0.7)
axs[1].set_title('Скорость полёта, м/с')
axs[1].legend()

# Масса
axs[2].plot(t[:t_215_idx], m[:t_215_idx], label='Мат. модель', color='navy')
axs[2].plot([x for x in mass_ksp_t if x <= 215],
            [y for x, y in zip(mass_ksp_t, mass_ksp) if x <= 215],
            label="KSP", color="red")
axs[2].set_xlabel('Время, с')
axs[2].set_ylabel('Масса, кг')
axs[2].grid(True, linestyle='--', alpha=0.7)
axs[2].set_title('Масса ракеты, кг')
axs[2].legend()

for ax in axs:
    ax.set_xlim(0, 220)
    ax.set_xticks(np.arange(0, 221, 20))

plt.tight_layout(rect=[0, 0, 1, 0.90])

fig.suptitle('Графики зависимости высоты, скорости и массы от времени',
             fontsize=13, y=0.98)

plt.tight_layout()
plt.show()


