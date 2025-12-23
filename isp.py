import krpc
import time
import json

# Подключаемся к серверу kRPC
conn = krpc.connect()
vessel = conn.space_center.active_vessel


# Функция для записи данных в JSON-файл
def write_to_json(file_name, data):
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)


# Инициализируем список для хранения данных
isp_data_log = []

# Имя выходного файла
isp_output_file = 'rocket_specific_impulse.json'

print("Сбор данных об удельном импульсе начался. Нажмите Ctrl+C для завершения.")

try:
    while True:
        # Получаем текущее время миссии
        mission_time = vessel.met

        # Считаем активные двигатели и их удельный импульс
        active_engines = 0
        total_isp = 0

        for engine in vessel.parts.engines:
            if engine.active:
                active_engines += 1
                # specific_impulse - текущий удельный импульс с учетом атмосферного давления
                total_isp += engine.specific_impulse

        # Рассчитываем средний удельный импульс
        avg_isp = total_isp / active_engines if active_engines > 0 else 0

        # Получаем высоту и атмосферное давление для контекста
        altitude = vessel.flight().mean_altitude
        atm_pressure = vessel.flight().static_pressure / 1000  # в кПа

        # Добавляем данные в список
        isp_data_log.append({
            'time': mission_time,
            'active_engines': active_engines,
            'average_specific_impulse': avg_isp,
            'altitude_m': altitude,
            'atmospheric_pressure_kpa': atm_pressure
        })


        # Ждём 1 секунду перед следующей записью
        time.sleep(0.1)

except KeyboardInterrupt:
    # При завершении записи сохраняем данные в файл
    print(f"\nСохранение {len(isp_data_log)} записей в файл...")
    write_to_json(isp_output_file, isp_data_log)
    print(f"Данные сохранены в {isp_output_file}")