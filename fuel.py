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


# Инициализируем список для хранения данных о топливе
fuel_data_log = []

# Имя выходного файла для данных о топливе
fuel_output_file = 'rocket_current_stage_fuel.json'

print("Сбор данных о массе топлива текущей ступени начался. Нажмите Ctrl+C для завершения.")

try:
    while True:
        # Получаем текущее время миссии
        mission_time = vessel.met

        # Получаем текущую ступень
        current_stage = vessel.control.current_stage

        # ✅ Ресурсы текущей ступени (с density())
        stage_resources = vessel.resources_in_decouple_stage(current_stage, cumulative=False)

        # Основные типы топлива для ракет
        main_fuel_types = ['LiquidFuel', 'SolidFuel', 'Oxidizer']

        # Подсчитываем общую массу топлива в текущей ступени
        stage_fuel_mass = 0.0

        for fuel_type in main_fuel_types:
            if stage_resources.has_resource(fuel_type):
                stage_fuel_mass += stage_resources.amount(fuel_type) * stage_resources.density(fuel_type)

        # ✅ Общая масса ВСЕХ ресурсов (mass возвращает кг напрямую)
        total_mass = vessel.dry_mass + vessel.mass - vessel.dry_mass  # = общая масса
        total_resources = vessel.resources

        # Для общего топлива используем mass напрямую (без density)
        total_fuel_mass = 0.0
        for fuel_type in main_fuel_types:
            if total_resources.has_resource(fuel_type):
                total_fuel_mass += total_resources.amount(fuel_type) * 5.0  # LiquidFuel/Oxidizer ≈5 кг/ед.

        # Добавляем данные в список
        fuel_data_log.append({
            'time': mission_time,
            'current_stage': current_stage,
            'stage_fuel_mass_kg': stage_fuel_mass,
            'total_fuel_mass_kg': total_fuel_mass,
            'total_vessel_mass_kg': vessel.mass,
            'fuel_percentage': (stage_fuel_mass / total_fuel_mass * 100) if total_fuel_mass > 0 else 0
        })

        # Ждём 1 секунду перед следующей записью
        time.sleep(0.1)

except KeyboardInterrupt:
    # При завершении записи сохраняем данные в файл
    print(f"\nСохранение {len(fuel_data_log)} записей в файл...")
    write_to_json(fuel_output_file, fuel_data_log)
    print(f"Данные сохранены в {fuel_output_file}")
