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


# Инициализируем список для хранения данных угла
angle_data_log = []

# Имя выходного файла для угла
angle_output_file = 'rocket_vertical_angle_data.json'

print("Сбор данных об угле между вертикалью и ракетой начался. Нажмите Ctrl+C для завершения.")

try:
    while True:
        # Получаем текущее время миссии
        mission_time = vessel.met

        # Получаем тангаж (pitch) ракеты
        # Pitch: 90° = вертикально вверх, 0° = горизонтально, -90° = вертикально вниз
        pitch = vessel.flight().pitch
        pitch_vertical = abs(90 - pitch)

        # Добавляем данные в список
        angle_data_log.append({
            'time': mission_time,
            'pitch_vertical': pitch_vertical
        })

        # Ждём 1 секунду перед следующей записью
        time.sleep(0.1)

except KeyboardInterrupt:
    # При завершении записи сохраняем данные в файл
    print("\nСохранение данных в файл...")
    write_to_json(angle_output_file, angle_data_log)
    print(f"Данные сохранены в {angle_output_file}")