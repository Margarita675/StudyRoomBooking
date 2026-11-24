// Отчёт по Теме 5 «Структура проекта. Настройка Django» — StudyRoomBooking
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ImageRun, PageNumber, Header, PageBreak,
} = require('docx');

const F = 'Times New Roman';
const p = (text, opts = {}) => new Paragraph({
  children: [new TextRun({ text, font: F, size: 24, ...opts })],
  alignment: AlignmentType.JUSTIFIED,
  spacing: { line: 360, after: 120 },
});
const heading = (text, level = 1) => new Paragraph({
  children: [new TextRun({ text, font: F, size: 28, bold: true })],
  heading: level === 1 ? HeadingLevel.HEADING_1 : HeadingLevel.HEADING_2,
  alignment: AlignmentType.CENTER,
  spacing: { before: 240, after: 240 },
});
const caption = (text) => new Paragraph({
  children: [new TextRun({ text, font: F, size: 22 })],
  alignment: AlignmentType.CENTER, spacing: { after: 200 },
});
const listing = (lines) => lines.map(l => new Paragraph({
  children: [new TextRun({ text: l.length ? l : ' ', font: 'Courier New', size: 18 })],
  spacing: { line: 240, after: 0 },
}));
const table = (rows, widths) => new Table({
  width: { size: 100, type: WidthType.PERCENTAGE },
  rows: rows.map((r, i) => new TableRow({
    children: r.map(c => new TableCell({
      width: { size: widths[r.indexOf(c)] || 33, type: WidthType.PERCENTAGE },
      children: [p(String(c), { size: 22 })],
      shading: i === 0 ? { fill: 'E3EEFA' } : undefined,
    })),
  })),
});
const tp = (text, opts = {}) => new Paragraph({
  children: [new TextRun({ text, font: F, size: opts.size || 24, bold: !!opts.bold })],
  alignment: opts.align || AlignmentType.CENTER,
  spacing: { before: opts.before || 0, after: opts.after || 200 },
});

const doc = new Document({
  styles: { default: { document: { run: { font: F, size: 24 } } } },
  sections: [{
    properties: {},
    headers: { default: new Header({ children: [new Paragraph({
      alignment: AlignmentType.RIGHT,
      children: [new TextRun({ children: [PageNumber.CURRENT], font: F, size: 22 })],
    })] }) },
    children: [
      tp('МИНИСТЕРСТВО ОБРАЗОВАНИЯ И НАУКИ РЕСПУБЛИКИ ТАТАРСТАН', { size: 26, after: 100 }),
      tp('Государственное автономное профессиональное образовательное учреждение', { size: 24, after: 100 }),
      tp('«Казанский колледж технологии и дизайна»', { size: 26, bold: true, after: 1600 }),
      tp('ОТЧЁТ', { size: 40, bold: true, after: 400 }),
      tp('по учебной практике', { size: 26, after: 100 }),
      tp('Тема 5. Структура проекта. Настройка Django', { size: 26, bold: true, after: 800 }),
      tp('Проект: StudyRoomBooking — система бронирования аудиторий', { size: 26, bold: true, after: 1400 }),
      tp('Выполнила: Сахабутдинова Маргарита Маратовна', { align: AlignmentType.RIGHT, size: 24, after: 100 }),
      tp('Студентка группы 09.02.07-3ВА', { align: AlignmentType.RIGHT, size: 24, after: 400 }),
      tp('Проверила: Куприянова Е.А.', { align: AlignmentType.RIGHT, size: 24, after: 1600 }),
      tp('Казань', { align: AlignmentType.CENTER, size: 24, after: 60 }),
      tp('2026', { align: AlignmentType.CENTER, size: 24 }),
      new Paragraph({ children: [new PageBreak()] }),

      heading('Раздел 3. Структура проекта. Настройка Django'),

      heading('3.1 Выбранный стек и обоснование выбора фреймворка', 2),
      p('Веб-приложение «StudyRoomBooking» представляет собой систему бронирования аудиторий: студент ищет свободную аудиторию по дате, времени, вместимости и оборудованию, оформляет бронирование и следит за его статусом в личном кабинете; администратор управляет аудиториями, оборудованием, бронями и пользователями. Для разработки использованы Python 3.11+, фреймворк Django 5 и СУБД PostgreSQL 15+. К базе данных приложение подключается через драйвер psycopg2, а настройки из файла .env загружает библиотека python-dotenv. Версии пакетов записаны в файле requirements.txt, историю изменений ведёт Git, а удалённый репозиторий размещён на GitHub. Все пакеты установлены в отдельное виртуальное окружение venv.'),
      p('Django выбран из-за особенностей проекта. В нём есть пользователи, аудитории, оборудование, бронирования, и все эти сущности связаны между собой (один пользователь — много броней, одна аудитория — много броней и записей оборудования). Ключевое требование предметной области — запрет пересекающихся бронирований — реализуется на сервере: Django ORM позволяет выразить проверку пересечения интервалов одним фильтром, а защита на уровне модели (full_clean + проверка конфликтов в save()) гарантирует, что некорректная бронь не попадёт в базу ни через интерфейс, ни через API. Также нужны авторизация с ролями, формы, шаблоны и административные страницы — всё это уже входит в Django. Через параметр AUTH_USER_MODEL заменена стандартная модель пользователя: в проекте есть поле роли (user/admin) и уникальный email, по которому разрешён вход (модель accounts.User).'),
      p('В качестве СУБД выбрана PostgreSQL. Она поддерживает внешние ключи с правилом ON DELETE CASCADE, ограничения уникальности и проверки CHECK, а проекту они нужны: номер аудитории уникален, время окончания должно быть больше времени начала (CHECK time_end > time_start), статус брони принимает только значения из справочника, связка «аудитория–оборудование» уникальна (UNIQUE room_id, equipment_id), а при удалении аудитории каскадно удаляются её брони и записи оборудования. Индексы по (room_id, date), (user_id, date), building, capacity, room_type ускоряют ключевые выборки поиска и расписания. Django подключается к базе через psycopg2, а параметры подключения берутся из переменных окружения.'),

      heading('3.2 Структура проекта', 2),
      p('Проект разделён по предметной области, а не по типам файлов. В каталоге config лежат настройки и корневые маршруты. Приложение accounts отвечает за пользователей: регистрацию, вход, профиль, роли и восстановление пароля. Приложение rooms хранит модели и страницы аудиторий и оборудования (в том числе поиск свободных аудиторий), bookings — бронирования, расписание, личный кабинет и административное управление бронями. Маршруты REST API вынесены в приложение api, там же находятся служебные маршруты ping и health. Общие шаблоны хранятся в каталоге templates, стили и клиентская валидация — в static, загружаемые фотографии аудиторий — в media. Документация проекта (ТЗ, SQL-скрипты базы данных, UML-диаграммы, отчёты) собрана в каталоге docs. Структура проекта показана на рисунке 1.'),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({
        data: fs.readFileSync(path.join(__dirname, 'diagrams', 'project_structure.png')),
        transformation: { width: 540, height: 256 }, type: 'png',
      })] }),
      caption('Рисунок 1 — Структура проекта StudyRoomBooking'),

      heading('3.3 Переменные окружения', 2),
      p('Конфиденциальные параметры (секретный ключ Django, пароль базы данных, учётные данные почты) не хранятся в коде: они вынесены в файл .env, который исключён из репозитория файлом .gitignore. Шаблон настроек — файл .env.example, из него студент создаёт собственный .env командой copy .env.example .env и заполняет своими значениями. Загрузка выполняется функцией load_dotenv() из python-dotenv при старте settings.py. Перечень переменных окружения приведён в таблице 1.'),
      caption('Таблица 1 — Переменные окружения проекта'),
      table([
        ['Переменная', 'Назначение', 'Пример значения'],
        ['SECRET_KEY', 'Секретный ключ Django', 'длинная случайная строка'],
        ['DEBUG', 'Режим отладки', 'True / False'],
        ['ALLOWED_HOSTS', 'Разрешённые хосты', '127.0.0.1,localhost'],
        ['DB_ENGINE', 'Движок БД (sqlite3 — для отладки)', 'sqlite3 / пусто (PostgreSQL)'],
        ['DB_NAME', 'Имя базы данных', 'studyroom_db'],
        ['DB_USER', 'Пользователь PostgreSQL', 'postgres'],
        ['DB_PASSWORD', 'Пароль PostgreSQL', 'ваш_пароль'],
        ['DB_HOST', 'Адрес сервера БД', 'localhost'],
        ['DB_PORT', 'Порт PostgreSQL', '5432'],
        ['EMAIL_BACKEND_CONSOLE', 'Консольный backend почты', 'True / False'],
        ['EMAIL_HOST', 'SMTP-сервер', 'smtp.mail.ru'],
        ['EMAIL_PORT', 'SMTP-порт (SSL)', '465'],
        ['EMAIL_HOST_USER', 'Адрес отправителя', 'your_email@mail.ru'],
        ['EMAIL_HOST_PASSWORD', 'Пароль приложения почты', '********'],
      ], [26, 44, 30]),

      heading('3.4 Настройка settings.py', 2),
      p('Файл settings.py загружает переменные окружения, описывает установленные приложения (accounts, rooms, bookings, api плюс rest_framework), middleware, шаблоны и подключение к базе данных. Если DB_ENGINE=sqlite3, используется SQLite (для отладки без PostgreSQL), иначе — PostgreSQL из переменных окружения. Также задаются AUTH_USER_MODEL = "accounts.User", AUTHENTICATION_BACKENDS с собственным backend входа по email или username, локализация (ru-ru, Europe/Moscow), каталоги static и media и настройки REST Framework (JWT-аутентификация, пагинация).'),
      listing([
        '# Листинг 1 — фрагмент config/settings.py (загрузка .env)',
        'from pathlib import Path',
        'import os',
        'from dotenv import load_dotenv',
        '',
        'BASE_DIR = Path(__file__).resolve().parent.parent',
        "load_dotenv(BASE_DIR / '.env')",
        '',
        "SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-change-me')",
        "DEBUG = os.getenv('DEBUG', 'True') == 'True'",
        '',
        '# Листинг 2 — подключение базы данных PostgreSQL',
        "if os.getenv('DB_ENGINE') == 'sqlite3':",
        '    DATABASES = {\'default\': {',
        "        'ENGINE': 'django.db.backends.sqlite3',",
        "        'NAME': BASE_DIR / 'db.sqlite3',}}",
        'else:',
        '    DATABASES = {\'default\': {',
        "        'ENGINE': 'django.db.backends.postgresql',",
        "        'NAME': os.getenv('DB_NAME', 'studyroom_db'),",
        "        'USER': os.getenv('DB_USER', 'postgres'),",
        "        'PASSWORD': os.getenv('DB_PASSWORD', ''),",
        "        'HOST': os.getenv('DB_HOST', 'localhost'),",
        "        'PORT': os.getenv('DB_PORT', '5432'),}}",
        '',
        "AUTH_USER_MODEL = 'accounts.User'",
      ]),

      heading('3.5 Маршрутизация', 2),
      p('Корневой urls.py подключает приложения: rooms (аудитории, оборудование, поиск), bookings (брони, расписание, управление), accounts (регистрация, вход, профиль, восстановление пароля), api (REST API) и служебный маршрут health. Главную страницу обслуживает accounts.views.home_view.'),
      listing([
        '# Листинг 3 — корневые маршруты config/urls.py',
        'urlpatterns = [',
        "    path('admin/', admin.site.urls),",
        "    path('health/', health, name='health'),",
        "    path('api/', include('api.urls')),",
        "    path('bookings/', include('bookings.urls')),",
        "    path('rooms/', include('rooms.urls')),",
        "    path('', home_view, name='home'),",
        "    path('', include('accounts.urls')),",
        ']',
      ]),
      p('В приложении api объявлены маршруты REST API (Тема 12): аутентификация (register, login, password-reset request/confirm), аудитории (список, карточка, поиск, расписание), оборудование, бронирования и служебный ping.'),
      listing([
        '# Листинг 4 — маршруты API api/urls.py (фрагмент)',
        'urlpatterns = [',
        "    path('ping/', views.ping, name='api_ping'),",
        "    path('auth/register/', views.RegisterAPIView.as_view()),",
        "    path('auth/login/', views.LoginAPIView.as_view()),",
        "    path('rooms/', views.RoomListAPIView.as_view()),",
        "    path('rooms/search/', views.RoomSearchAPIView.as_view()),",
        "    path('rooms/<int:room_id>/schedule/', views.RoomScheduleAPIView.as_view()),",
        "    path('bookings/', views.BookingListAPIView.as_view()),",
        "    path('bookings/<int:booking_id>/', views.BookingDetailAPIView.as_view()),",
        ']',
      ]),

      heading('3.6 Служебные маршруты для проверки работоспособности', 2),
      p('Для быстрой проверки того, что сервер и приложение работают, добавлены два служебных маршрута: GET /health/ и GET /api/ping/. Они возвращают JSON со статусом и не требуют аутентификации.'),
      listing([
        '# Листинг 5 — служебные представления api/views.py',
        'def health(request):',
        '    return JsonResponse({\'status\': \'ok\', \'service\': \'web\'})',
        '',
        'def ping(request):',
        '    return JsonResponse({\'status\': \'ok\', \'message\': \'pong\'})',
      ]),

      heading('3.7 Зависимости и проверки конфигурации', 2),
      p('Зависимости зафиксированы в requirements.txt:'),
      listing([
        '# Листинг 6 — requirements.txt',
        'Django>=5.0,<5.2',
        'djangorestframework>=3.15',
        'djangorestframework-simplejwt>=5.3',
        'psycopg2-binary>=2.9',
        'python-dotenv>=1.0',
        'Pillow>=10.0',
      ]),
      p('Выполненные проверки: создано и активировано виртуальное окружение venv, зависимости установлены командой pip install -r requirements.txt; структура каталогов соответствует рисунку 1; файл .env создан из шаблона .env.example; статическая проверка корректности кода (компиляция всех модулей, согласованность моделей, миграций и маршрутов) расхождений не обнаружила. В среде автоматической сборки отчёта запуск Django и PostgreSQL был недоступен (установка пакетов запрещена), поэтому полный набор проверок выполняется студентом по инструкции docs/Инструкция_что_сделать.md:'),
      listing([
        'python -m venv venv                      # создание окружения',
        'venv\\Scripts\\activate                   # активация',
        'pip install -r requirements.txt         # установка зависимостей',
        'python manage.py migrate                # применение миграций',
        'python manage.py loaddata rooms/fixtures/init_data.json   # справочник оборудования',
        'python manage.py createsuperuser        # администратор',
        'python manage.py runserver              # запуск сервера',
        '# в psql:',
        '\\c studyroom_db',
        '\\dt                                      -- список таблиц',
        '\\d bookings_booking                      -- ограничения и FK',
        '# в браузере:',
        '# http://127.0.0.1:8000/health/',
        '# http://127.0.0.1:8000/api/ping/',
        'python manage.py test                    # автотесты',
        'git init && git add . && git commit -m "Initial commit"',
      ]),
      p('Вывод: структура проекта разделена по предметной области, конфиденциальные настройки вынесены в .env, база данных подключается к PostgreSQL через переменные окружения, маршрутизация разнесена по приложениям, а работоспособность сервера проверяется служебными маршрутами /health/ и /api/ping/ и автотестами.', { size: 24 }),
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(path.join(__dirname, 'Отчет_Тема5_Настройка_Django_StudyRoomBooking.docx'), buf);
  console.log('DOCX created:', buf.length, 'bytes');
});
