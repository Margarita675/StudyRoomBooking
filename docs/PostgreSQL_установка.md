# Установка и настройка PostgreSQL для StudyRoomBooking (Windows)

## 1. Установка PostgreSQL
1. Скачайте установщик с https://www.postgresql.org/download/windows/ (версия 15 или новее).
2. При установке:
   - запомните пароль пользователя **postgres** (придумайте и запишите);
   - порт оставьте по умолчанию **5432**;
   - отметьте установку **pgAdmin** (графический клиент) — опционально;
   - после установки разрешите запуск службы PostgreSQL в качестве службы Windows (галочка предлагается установщиком).
3. Проверка: меню «Пуск» → PostgreSQL 15 → **SQL Shell (psql)**. Введите пароль postgres — появится приглашение `postgres=#`.

## 2. Создание базы данных
В SQL Shell (psql) выполните:
```sql
CREATE DATABASE studyroom_db WITH ENCODING 'UTF8' TEMPLATE template0;
```
Проверка: `\c studyroom_db` — подключение к новой базе.

Либо через pgAdmin: Servers → PostgreSQL → ПКМ Databases → Create → Database → имя `studyroom_db`, Encoding UTF8.

## 3. Настройка подключения в проекте
Скопируйте `.env.example` в `.env` и заполните:
```
DB_ENGINE=postgresql
DB_NAME=studyroom_db
DB_USER=postgres
DB_PASSWORD=ваш_пароль_postgres
DB_HOST=localhost
DB_PORT=5432
```
Django подключается через драйвер psycopg2 (установлен командой `pip install -r requirements.txt`).

## 4. Создание таблиц
```
venv\Scripts\activate
python manage.py migrate
python manage.py loaddata rooms.fixtures.init_data      # тестовые советы (опционально)
python manage.py createsuperuser      # администратор
```
`python manage.py migrate` применит миграции: Django (auth, admin, sessions…), затем
accounts 0001–0002, rooms 0001, bookings 0001.

## 5. Проверка базы данных
В psql:
```
\c studyroom_db
\dt                          -- список таблиц: accounts_user, rooms_room,
                             -- rooms_equipment, rooms_roomequipment,
                             -- bookings_booking, accounts_passwordresettoken + служебные
\d bookings_booking          -- внешние ключи и ограничения CHECK
SELECT count(*) FROM accounts_user;
```
Полный справочный DDL — `docs/sql/schema.sql`, сценарий инициализации — `docs/sql/create_database.sql`.

## 6. Если что-то не работает
| Ошибка | Причина и решение |
|---|---|
| `FATAL: password authentication failed` | Неверный пароль postgres в `.env` — исправьте DB_PASSWORD |
| `connection refused` | Служба PostgreSQL не запущена: Win+R → `services.msc` → запустить «postgresql-x64-15» |
| `relation "accounts_user" does not exist` | Миграции не применены: выполните `python manage.py migrate` |
| `database "studyroom_db" does not exist` | База не создана — см. раздел 2 |
