# StudyRoomBooking — система бронирования аудиторий

Учебный проект (Python + Django + PostgreSQL + DRF + HTML5/CSS3/JS).
Система позволяет найти свободную аудиторию по дате, времени, вместимости
и оборудованию, оформить бронирование с серверной проверкой конфликтов,
посмотреть расписание и управлять аудиториями (роль «администратор»).

## Возможности
- Регистрация, вход (по логину **или** email), выход, профиль;
- восстановление пароля по email (одноразовый токен, хранится SHA-256 хеш);
- роли: студент / администратор (RBAC), защита от IDOR;
- аудитории: номер, корпус, этаж, вместимость, тип (лекционная, компьютерная,
  лабораторная, конференц-зал, учебная, универсальная), статус, фото, описание;
- оборудование: каталог + связь M:N с аудиториями (модель RoomEquipment, количество);
- поиск свободных аудиторий: дата, время, вместимость, тип, корпус, оборудование;
- бронирование: цели, статусы (ожидает/подтверждено/отклонено/отменено/завершено),
  серверная проверка пересечений интервалов (частичное, вложенное, границы);
- расписание по дате/аудитории/статусу, занятость на странице аудитории;
- личный кабинет: свои брони, отмена по правилам;
- админ-часть: CRUD аудиторий и оборудования, подтверждение/отклонение броней,
  управление пользователями;
- REST API (DRF + JWT): /api/... (см. ниже);
- служебные маршруты: GET /health/, GET /api/ping/.

## Структура проекта
```
StudyRoomBooking/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── config/          # настройки, urls, wsgi/asgi
├── accounts/        # пользователи, роли, восстановление пароля
├── rooms/           # аудитории и оборудование
├── bookings/        # бронирования, расписание, личный кабинет
├── api/             # REST API (DRF + JWT)
├── templates/       # базовые шаблоны
├── static/          # CSS, JS
├── media/           # фотографии аудиторий (не в Git)
└── docs/            # ТЗ, SQL, диаграммы, отчёты, инструкция
```

## Установка (Windows, по шагам)
1. Python 3.11+ — при установке отметьте **Add Python to PATH**.
2. PostgreSQL 15+ — запомните пароль пользователя postgres (порт 5432).
3. Git (git-scm.com).
4. Распакуйте проект, например в `C:\Projects\StudyRoomBooking`. Откройте cmd
   в этой папке:
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
5. Скопируйте `.env.example` в `.env` и заполните: `SECRET_KEY` (любая длинная
   строка), `DB_NAME=studyroom_db`, `DB_USER=postgres`, `DB_PASSWORD=ваш пароль`.
6. Создайте базу (SQL Shell (psql), пароль postgres):
```
CREATE DATABASE studyroom_db WITH ENCODING 'UTF8' TEMPLATE template0;
```
7. Примените миграции и создайте администратора:
```
python manage.py migrate
python manage.py loaddata rooms/fixtures/init_data.json
python manage.py createsuperuser
```
8. Запустите сервер:
```
python manage.py runserver
```
Сайт: http://127.0.0.1:8000/  Проверка: http://127.0.0.1:8000/health/
и http://127.0.0.1:8000/api/ping/ (JSON `{"status": "ok", ...}`).

## Основные страницы
| Адрес | Назначение |
|---|---|
| `/` | главная |
| `/register/`, `/login/` | регистрация, вход |
| `/rooms/` | список аудиторий (фильтры) |
| `/rooms/search/` | поиск свободных аудиторий |
| `/rooms/<id>/` | карточка аудитории, занятость, бронирование |
| `/rooms/equipment/` | каталог оборудования (админ) |
| `/bookings/my/` | мои брони (личный кабинет) |
| `/bookings/schedule/` | расписание |
| `/bookings/admin/` | подтверждение/отклонение броней (админ) |
| `/profile/` | профиль |
| `/admin-dashboard/` | управление пользователями (админ) |

## REST API (JWT Bearer)
| Метод | Адрес | Назначение | Доступ |
|---|---|---|---|
| POST | `/api/auth/register/` | регистрация (201, ошибка 422) | аноним |
| POST | `/api/auth/login/` | логин → access/refresh (200/401) | аноним |
| POST | `/api/auth/password-reset/request/` | запрос токена | аноним |
| POST | `/api/auth/password-reset/confirm/` | новый пароль по токену | аноним |
| GET/POST | `/api/rooms/` | список/создание (создание — админ) | публично/админ |
| GET/PUT/DELETE | `/api/rooms/<id>/` | карточка/изменение/удаление (204) | админ для записи |
| GET | `/api/rooms/search/` | поиск свободных (date, time_start, time_end, capacity, room_type, building, equipment) | публично |
| GET | `/api/rooms/<id>/schedule/` | расписание аудитории | публично |
| GET | `/api/equipment/` | каталог оборудования | публично |
| GET/POST | `/api/bookings/` | свои брони / создание (201/422) | авторизован |
| GET/DELETE/PATCH | `/api/bookings/<id>/` | просмотр/отмена (204)/смена статуса (админ) | владелец/админ |
| GET | `/api/ping/` | проверка работоспособности | аноним |

Пример запроса с токеном:
```
Authorization: Bearer <access>
GET http://127.0.0.1:8000/api/bookings/
```
Ошибки валидации возвращаются с кодом **422** (Тема 12).

## Тесты
```
python manage.py test
```
Покрываются: регистрация/логин, RBAC, восстановление пароля, CRUD аудиторий,
конфликты бронирования (пересечение, вложенный интервал, границы, прошедшие
даты, time_end <= time_start), личный кабинет, права, API-коды.

## Git
`.env`, `venv/`, `media/`, `db.sqlite3` не попадают в репозиторий (.gitignore).
```
git init && git add . && git commit -m "Initial commit: StudyRoomBooking"
git remote add origin https://github.com/<логин>/StudyRoomBooking.git
git push -u origin main
```

## Почта
По умолчанию письма выводятся в консоль (EMAIL_BACKEND_CONSOLE=True). Для реальной
отправки: EMAIL_BACKEND_CONSOLE=False и пароль приложения Mail.ru/Yandex в .env.
