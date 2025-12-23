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

# Инициализируем список для хранения данных массы
mass_data_log = []

# Имя выходного файла для массы
mass_output_file = 'rocket_mass_data.json'

print("Сбор данных о массе начался. Нажмите Ctrl+C для завершения.")

try:
    while True:
        # Получаем текущую массу ракеты
        mass = vessel.mass

        # Получаем текущее время миссии
        mission_time = vessel.met

        # Добавляем данные в список
        mass_data_log.append({
            'time': mission_time,
            'mass': mass
        })

        # Печатаем данные в консоль (опционально)
        print(f"Time: {mission_time:.2f} s, Mass: {mass:.2f} kg")

        # Ждём 1 секунду перед следующей записью
        time.sleep(0.1)

except KeyboardInterrupt:
    # При завершении записи сохраняем данные в файл
    print("\nСохранение данных в файл...")
    write_to_json(mass_output_file, mass_data_log)
    print(f"Данные сохранены в {mass_output_file}")


