-- ============================================================
-- Инициализация БД StudyRoomBooking (PostgreSQL, Тема 4).
-- Выполняется в SQL Shell (psql) ПОСЛЕ применения миграций Django
-- (python manage.py migrate) — сценарий добавляет справочные данные.
-- ============================================================

-- 1. Создание базы (если ещё не создана):
-- CREATE DATABASE studyroom_db WITH ENCODING 'UTF8' TEMPLATE template0;
-- \c studyroom_db

-- 2. (Необязательно) Отдельная роль приложения:
-- CREATE ROLE studyroom_app WITH LOGIN PASSWORD 'app_password';
-- GRANT CONNECT ON DATABASE studyroom_db TO studyroom_app;
-- GRANT USAGE ON SCHEMA public TO studyroom_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO studyroom_app;

-- 3. Комментарии к таблицам:
COMMENT ON TABLE rooms_room IS 'Аудитории: номер, корпус, этаж, вместимость, тип, статус';
COMMENT ON TABLE rooms_equipment IS 'Каталог оборудования';
COMMENT ON TABLE rooms_roomequipment IS 'Связь аудитория-оборудование (M:N) с количеством';
COMMENT ON TABLE bookings_booking IS 'Бронирования аудиторий с проверкой конфликтов';
COMMENT ON TABLE accounts_user IS 'Пользователи с ролями (user/admin)';
COMMENT ON TABLE accounts_passwordresettoken IS 'Одноразовые токены восстановления пароля (SHA-256)';

-- 4. Справочное оборудование (дублирует rooms/fixtures/init_data.json):
INSERT INTO rooms_equipment (name, description) VALUES
    ('Проектор', 'Мультимедийный проектор'),
    ('Компьютер', 'Рабочая станция'),
    ('Интерактивная доска', ''),
    ('Микрофон', ''),
    ('Wi-Fi', ''),
    ('Лабораторное оборудование', '')
ON CONFLICT (name) DO NOTHING;

-- 5. Пример аудитории:
INSERT INTO rooms_room (number, name, building, floor, capacity, room_type, status, description)
VALUES ('101', 'Лекционный зал', '1', 1, 60, 'lecture', 'active', 'Лекционный зал с проектором')
ON CONFLICT (number) DO NOTHING;

INSERT INTO rooms_roomequipment (room_id, equipment_id, quantity)
SELECT r.id, e.id, 1 FROM rooms_room r, rooms_equipment e
WHERE r.number = '101' AND e.name = 'Проектор'
  AND NOT EXISTS (SELECT 1 FROM rooms_roomequipment re
                  WHERE re.room_id = r.id AND re.equipment_id = e.id);

-- 6. Проверка:
-- SELECT count(*) FROM rooms_room;
-- SELECT number, name, capacity FROM rooms_room ORDER BY number;
-- SELECT b.id, r.number, b.date, b.time_start, b.time_end, b.status
--   FROM bookings_booking b JOIN rooms_room r ON r.id = b.room_id ORDER BY b.date;
