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


# Инициализируем список для хранения данных скорости
speed_data_log = []

# Имя выходного файла для скорости
speed_output_file = 'rocket_speed_data.json'

print("Сбор данных о скорости начался. Нажмите Ctrl+C для завершения.")

try:
    while True:
        # Получаем текущую скалярную скорость ракеты (модуль вектора скорости)
        # Относительно поверхности планеты
        velocity = vessel.flight(vessel.orbit.body.reference_frame).speed

        # Получаем текущее время миссии
        mission_time = vessel.met

        # Добавляем данные в список (включая нулевые значения)
        speed_data_log.append({
            'time': mission_time,
            'speed': velocity
        })

        # Печатаем данные в консоль
        print(f"Time: {mission_time:.2f} s, Speed: {velocity:.2f} m/s")

        # Ждём 1 секунду перед следующей записью
        time.sleep(0.1)

except KeyboardInterrupt:
    # При завершении записи сохраняем данные в файл
    print(f"\nСохранение {len(speed_data_log)} записей в файл...")
    write_to_json(speed_output_file, speed_data_log)
    print(f"Данные сохранены в {speed_output_file}")