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

# Инициализируем список для хранения данных высоты
height_data_log = []

# Имя выходного файла для высоты
height_output_file = 'rocket_height_data.json'

print("Сбор данных о высоте начался. Нажмите Ctrl+C для завершения.")

try:
    while True:
        # Получаем текущую высоту ракеты над уровнем моря
        height = vessel.flight().mean_altitude

        # Получаем текущее время миссии
        mission_time = vessel.met

        # Добавляем данные в список
        height_data_log.append({
            'time': mission_time,
            'height': height
        })

        # Печатаем данные в консоль (опционально)
        print(f"Time: {mission_time:.2f} s, height: {height:.2f} m")

        # Ждём 1 секунду перед следующей записью
        time.sleep(0.1)

except KeyboardInterrupt:
    # При завершении записи сохраняем данные в файл
    print("\nСохранение данных в файл...")
    write_to_json(height_output_file, height_data_log)
    print(f"Данные сохранены в {height_output_file}")