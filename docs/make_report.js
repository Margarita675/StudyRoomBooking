// Генерация отчёта по учебной практике «StudyRoomBooking» (DOCX, node docx)
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ImageRun, BorderStyle, PageNumber, Header, PageBreak,
} = require('docx');

const F = 'Times New Roman';
const p = (text, opts = {}) => new Paragraph({
  children: [new TextRun({ text, font: F, size: 24, ...opts })],
  alignment: AlignmentType.JUSTIFIED,
  spacing: { line: 360, after: 120 },
  ...opts.para,
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
const fig = (file, w, h, cap) => new Paragraph({
  children: [new ImageRun({
    data: fs.readFileSync(path.join(__dirname, 'diagrams', file)),
    transformation: { width: w, height: h }, type: 'png',
  })],
  alignment: AlignmentType.CENTER,
});
const table = (rows, widths) => new Table({
  width: { size: 100, type: WidthType.PERCENTAGE },
  rows: rows.map((r, i) => new TableRow({
    children: r.map(c => new TableCell({
      width: { size: widths[r.indexOf(c)] || 25, type: WidthType.PERCENTAGE },
      children: [p(String(c), { size: 22 })],
      shading: i === 0 ? { fill: 'E3EEFA' } : undefined,
    })),
  })),
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
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200, after: 100 },
        children: [new TextRun({ text: 'МИНИСТЕРСТВО ОБРАЗОВАНИЯ И НАУКИ РЕСПУБЛИКИ ТАТАРСТАН', font: F, size: 26 })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
        children: [new TextRun({ text: 'Государственное автономное профессиональное образовательное учреждение', font: F, size: 24 })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 1600 },
        children: [new TextRun({ text: '«Казанский колледж технологии и дизайна»', font: F, size: 26, bold: true })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
        children: [new TextRun({ text: 'ОТЧЁТ', font: F, size: 40, bold: true })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
        children: [new TextRun({ text: 'по учебной практике «Разработка веб-приложения StudyRoomBooking — система бронирования аудиторий»', font: F, size: 26 })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 1400 },
        children: [new TextRun({ text: 'Технологии: Python, Django, PostgreSQL, HTML5/CSS3/JavaScript, Django REST Framework, Git', font: F, size: 24, italics: true })] }),
      new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { after: 100 },
        children: [new TextRun({ text: 'Выполнила: Сахабутдинова Маргарита Маратовна', font: F, size: 24 })] }),
      new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { after: 400 },
        children: [new TextRun({ text: 'Студентка группы 09.02.07-3ВА', font: F, size: 24 })] }),
      new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { after: 1600 },
        children: [new TextRun({ text: 'Проверила: Куприянова Е.А.', font: F, size: 24 })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 },
        children: [new TextRun({ text: 'Казань', font: F, size: 24 })] }),
      new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: '2026', font: F, size: 24 })] }),
      new Paragraph({ children: [new PageBreak()] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 2000, after: 200 },
        children: [new TextRun({ text: 'ОТЧЁТ', font: F, size: 32, bold: true })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
        children: [new TextRun({ text: 'по учебной практике «Разработка веб-приложения StudyRoomBooking — система бронирования аудиторий»', font: F, size: 28, bold: true })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
        children: [new TextRun({ text: 'Технологии: Python, Django, PostgreSQL, HTML5/CSS3/JavaScript, Django REST Framework, Git', font: F, size: 24, italics: true })] }),
      p('Проект StudyRoomBooking — веб-приложение для поиска и бронирования аудиторий учебного заведения. Настоящий отчёт объединяет результаты выполнения всех тем практики: проектирование ИС и ТЗ (Тема 1), выбор стека (Тема 2), настройка окружения и Git (Тема 3), проектирование базы данных PostgreSQL (Тема 4), регистрация и аутентификация (Тема 6), восстановление пароля по email (Тема 7), разграничение прав доступа (Тема 8), разработка интерфейса (Темы 9–10–11), REST API (Тема 12). Полный исходный код проекта приложен отдельным архивом StudyRoomBooking.zip.', { size: 24 }),

      heading('1. Проектирование ИС. Анализ предметной области. ТЗ (Тема 1)'),
      p('Наименование веб-приложения: StudyRoomBooking — система бронирования аудиторий. Предметная область: организация учебного процесса. Цель разработки: создать веб-приложение, позволяющее студенту подобрать аудиторию, соответствующую заданным параметрам (вместимость, оборудование, дата, время), и оформить бронирование, а администратору — контролировать аудитории, оборудование и брони.'),
      p('Функциональные требования: (1) регистрация и авторизация с серверной и клиентской валидацией; (2) восстановление пароля по email через одноразовые токены со сроком жизни 30 минут; (3) карточки аудиторий (номер, корпус, этаж, вместимость, тип, статус, описание, фото); (4) нормализованный каталог оборудования с связью «аудитория–оборудование» и количеством единиц; (5) поиск свободных аудиторий по дате, интервалу времени, вместимости, типу, корпусу и требуемому оборудованию; (6) бронирование с серверной проверкой пересечений интервалов и статусами (ожидает подтверждения, подтверждено, отклонено, отменено, завершено); (7) расписание по дате, аудитории и статусу; (8) личный кабинет пользователя; (9) административные страницы; (10) REST API с JWT-аутентификацией; (11) ролевая модель студент/администратор.'),
      p('Нефункциональные требования: безопасность (хеширование паролей, хеш токена вместо исходного значения, CSRF-защита, серверные проверки прав — защита от IDOR); адаптивность (Mobile First, CSS Grid/Flexbox, брейкпоинты 768px и 480px); доступность a11y (семантические теги, alt, aria-атрибуты, label у всех полей); производительность (индексы по внешним ключам и полям поиска).'),
      p('Роли и права: студент (user) — просмотр и поиск аудиторий, создание и отмена своих броней, личный кабинет; администратор (admin) — управление аудиториями и оборудованием, подтверждение/отклонение броней, расписание, управление пользователями.'),
      p('Построены четыре UML-диаграммы (исходники Mermaid в docs/diagrams/, рисунки — PNG):'),
      caption('Рисунок 1.1 — Use Case диаграмма: акторы Гость/Студент/Администратор и прецеденты системы'),
      fig('use_case.png', 560, 305),
      caption('Рисунок 1.2 — Диаграмма классов: модели Django ORM и связи между ними'),
      fig('class_diagram.png', 620, 307),
      caption('Рисунок 1.3 — Диаграмма последовательности: бронирование с проверкой конфликтов'),
      fig('sequence_diagram.png', 600, 307),

      heading('1.1. Выбор стека технологий и обоснование архитектуры (Тема 2)'),
      p('Выбранный веб-фреймворк: Django. Обоснование: Django — полнофункциональный фреймворк с готовыми решениями, необходимыми по заданию: встроенная аутентификация и ролевая модель (AbstractUser), ORM и миграции (Тема 4), защита от CSRF, админ-панель. Ключевое требование проекта — предотвращение конфликтующих бронирований — реализуется надёжнее всего серверным кодом с транзакциями ORM: Django ORM позволяет выразить проверку пересечения интервалов фильтром time_start__lt=... и time_end__gt=... и одновременно с проверкой создать запись. Для StudyRoomBooking важны именно эти готовые компоненты.'),
      p('СУБД: PostgreSQL. Обоснование: реляционная СУБД, полностью поддерживает требуемый уровень целостности (CHECK-ограничения time_end > time_start, для ролей, типов аудиторий и статусов; UNIQUE для номера аудитории и email; внешние ключи с ON DELETE CASCADE), индексы по полям поиска (building, capacity, room_type, room_id+date), надёжна и рекомендована методичкой.'),
      p('Клиентская часть: HTML5 (семантическая разметка), CSS3 (переменные Custom Properties, Grid, Flexbox, медиа-запросы), JavaScript (клиентская валидация форм, мобильное меню, подтверждение удаления). Выбор обусловлен Темой 9–10–11: адаптивность и доступность достигаются без тяжёлых фронтенд-фреймворков.'),
      p('Архитектура «клиент-сервер»: браузер отправляет HTTP-запросы к серверу Django (MVT: шаблоны рендерятся на сервере); Django ORM обращается к PostgreSQL; статические файлы и загруженные фотографии отдаются веб-сервером; отдельно опубликован REST API (Django REST Framework) с JWT-аутентификацией — клиент-серверное взаимодействие без состояния, токен в заголовке Authorization: Bearer.'),

      heading('1.2. Настройка рабочего окружения. Git (Тема 3)'),
      p('Рабочее окружение: Python 3.11+, виртуальное окружение venv, зависимости из requirements.txt (Django, djangorestframework, djangorestframework-simplejwt, psycopg2-binary, python-dotenv, Pillow), PostgreSQL 15, редактор кода, Git.'),
      p('Git используется для: (1) истории изменений проекта; (2) совместной работы; (3) отката к рабочим версиям; (4) хранения проекта вне локального компьютера.'),
      listing([
        'git init',
        'git add .',
        'git commit -m "Initial commit: StudyRoomBooking project"',
        'git branch -M main',
        'git remote add origin <URL_репозитория>',
        'git push -u origin main',
      ]),
      p('Ссылка на репозиторий: создаётся студентом (см. README, раздел Git). Файл .gitignore исключает venv/, __pycache__/, db.sqlite3, media/ и .env — секреты не хранятся в репозитории.', { size: 24 }),

      heading('2. Проектирование и разработка базы данных (Тема 4)'),
      p('Выделены сущности: пользователь (accounts_user), токен восстановления пароля (accounts_passwordresettoken), аудитория (rooms_room), оборудование (rooms_equipment), связь аудитория–оборудование (rooms_roomequipment), бронирование (bookings_booking) — 6 сущностей.'),
      p('Связи: users 1:N bookings (ON DELETE CASCADE); rooms 1:N bookings (CASCADE); rooms 1:N roomequipment (CASCADE); equipment 1:N roomequipment (CASCADE, отношение M:N через ассоциативную таблицу с количеством); users 1:N passwordresettoken (CASCADE). Список оборудования аудитории не хранится строкой — использована нормализованная таблица связи.'),
      p('Нормализация: база приведена к 3НФ — все атрибуты атомарны (1НФ), каждый неключевой атрибут зависит от первичного ключа (2НФ), транзитивных зависимостей нет (3НФ). Для перечислений используется VARCHAR + CHECK, дат — DATE и TIME, первичный ключ — суррогатный BIGSERIAL.'),
      caption('Рисунок 2.1 — ER-диаграмма базы данных StudyRoomBooking (PK/FK/UNIQUE/CHECK указаны)'),
      fig('erd.png', 600, 317),
      p('Целостность данных обеспечивается ограничениями на уровне БД: CheckConstraint time_end > time_start исключает нулевые и обратные интервалы; CheckConstraint floor >= 0 и capacity > 0; unique_together (room, equipment) в таблице связи исключает дублирование; UNIQUE number аудитории; статусные CHECK-ограничения.'),
      p('Модели описаны в Django (accounts/models.py, rooms/models.py, bookings/models.py), миграции применяются командой python manage.py migrate. Справочный SQL-скрипт структуры приведён в docs/sql/schema.sql, сценарий инициализации — в docs/sql/create_database.sql (создание справочника оборудования, пример аудитории, комментарии к таблицам, команды проверки).'),
      listing([
        '-- фрагмент docs/sql/schema.sql',
        'CREATE TABLE IF NOT EXISTS bookings_booking (',
        '    id          BIGSERIAL PRIMARY KEY,',
        '    date        DATE NOT NULL,',
        '    time_start  TIME NOT NULL,',
        '    time_end    TIME NOT NULL CHECK (time_end > time_start),',
        '    purpose     VARCHAR(200) NOT NULL,',
        '    status      VARCHAR(12) NOT NULL DEFAULT \'pending\'',
        '                CHECK (status IN (\'pending\',\'confirmed\',\'rejected\',\'cancelled\',\'completed\')),',
        '    room_id     BIGINT NOT NULL REFERENCES rooms_room(id) ON DELETE CASCADE,',
        '    user_id     BIGINT NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE',
        ');',
        'CREATE INDEX IF NOT EXISTS bookings_room_date_idx ON bookings_booking (room_id, date);',
      ]),
      p('Индексы созданы по (room_id, date), (user_id, date), status, (building, floor), capacity, room_type — под ключевые выборки поиска и расписания.'),

      heading('3.1. Регистрация, аутентификация и авторизация (Тема 6)'),
      p('Использована расширенная модель пользователя: класс User наследует AbstractUser и содержит уникальный email и поле role (user/admin). В settings.py задан AUTH_USER_MODEL = "accounts.User". Пароли хешируются средствами Django (PBKDF2).'),
      listing([
        'class User(AbstractUser):',
        '    ROLE_CHOICES = ((\'user\', \'Пользователь\'), (\'admin\', \'Администратор\'))',
        '    email = models.EmailField(\'Email\', unique=True)',
        '    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=\'user\')',
      ]),
      p('Формы RegisterForm (наследует UserCreationForm, серверная проверка уникальности email) и LoginForm реализуют серверную валидацию; клиентская валидация (совпадение паролей, корректность email) выполняется JavaScript в main.js, ошибки выводятся рядом с полем. После успешной регистрации/входа выводится flash-сообщение (django.contrib.messages). Маршруты защищены декоратором @login_required.'),
      p('Вход возможен как по имени пользователя, так и по email: собственный authentication backend (accounts/backends.py) ищет пользователя по Q(username__iexact=...) | Q(email__iexact=...). Выход — через POST-форму logout (CSRF-защита).'),

      heading('3.3. Восстановление пароля по электронной почте (Тема 7)'),
      p('Реализованы все обязательные требования: форма «Забыли пароль?», генерация одноразового токена (secrets.token_urlsafe(32), срок жизни 30 минут), письмо со ссылкой /reset-password/<token>/, проверка валидности токена при переходе, форма нового пароля с подтверждением, хеширование нового пароля и инвалидация токена, обработка ошибок (неверный/просроченный токен).'),
      p('Правила безопасности соблюдены: (1) никогда не сообщается «пользователь не найден» — ответ нейтральный (защита от перебора email); (2) токен одноразовый: после успешной смены пароля is_used=True; (3) в БД хранится только SHA-256 хеш токена, а не сам токен; (4) ошибки SMTP обрабатываются исключением SMTPException.'),
      p('Почта настроена через переменные окружения (.env): по умолчанию EMAIL_BACKEND_CONSOLE=True — письма выводятся в консоль сервера (для разработки и учебного тестирования, как рекомендует методичка); для реальной отправки через Mail.ru используется smtp.mail.ru, порт 465, SSL, пароль внешнего приложения.'),

      heading('3.4. Реализация ролей и разграничения прав доступа (Тема 8)'),
      p('Реализована ролевая модель RBAC. Роль хранится в поле role таблицы accounts_user (CHECK user|admin). Любая проверка прав дублируется на сервере; скрытие кнопок в шаблонах используется только для UX.'),
      table([
        ['Роль', 'Разрешённые действия', 'Запрещённые действия'],
        ['user (студент)', 'Просмотр и поиск аудиторий; бронирование; просмотр и отмена СВОИХ броней; профиль', 'Доступ к админ-страницам; изменение аудиторий; подтверждение броней; доступ к чужим броням'],
        ['admin', 'Все страницы; CRUD аудиторий и оборудования; подтверждение/отклонение/отмена любых броней; расписание; управление пользователями', 'Удаление суперпользователя; изменение системных конфигураций'],
      ], [20, 45, 35]),
      p('Защита маршрутов: декоратор admin_required (accounts/decorators.py) — неавторизованный перенаправляется на вход, несоответствующая роль получает 403 Forbidden. Анти-IDOR: бронь для отмены выбирается условием get_object_or_404(Booking, pk=..., user=request.user) — чужая бронь не видна; в API работает permission-класс IsOwnerOrAdmin.'),
      listing([
        'def _wrapped(request, *args, **kwargs):',
        '    if not request.user.is_authenticated:',
        '        return redirect(\'accounts:login\')',
        '    if not request.user.is_admin():',
        '        raise PermissionDenied  # 403',
        '    return view_func(request, *args, **kwargs)',
      ]),
      p('Дополнительно на уровне БД предотвращается самоназначение ролей: роль задаётся только серверным кодом (RegisterForm.save() принудительно устанавливает role=user), форма профиля не содержит поля role, панель управления пользователями позволяет администратору блокировать (is_active) и удалять аккаунты.'),

      heading('4. Разработка интерфейса веб-приложения (Темы 9–10–11)'),
      p('Концепция дизайна: академичный минимализм. Основной цвет — синий #1565c0 (доверие, учебная среда), акцентный — тёплый оранжевый, фон — светло-серый #f9fafb. Типографика: системный шрифтовой стек «Segoe UI/Inter/system-ui» — быстрая загрузка без веб-шрифтов. Единая система: все кнопки используют общий класс .btn с модификаторами, карточки аудиторий — .card, статусы броней — .badge с цветовыми модификаторами (pending — жёлтый, confirmed — зелёный, rejected — красный, cancelled — серый, completed — синий).'),
      p('Технологии: семантический HTML5 (header, nav, main, section, article, footer) — для доступности; CSS Grid для сеток карточек и фильтров, Flexbox для шапки — адаптивность без Bootstrap; CSS-переменные (:root) для единообразия цветов и отступов.'),
      listing([
        '/* Листинг 4.1 — CSS-переменные (static/css/style.css) */',
        ':root {',
        '    --primary-color: #1565c0;',
        '    --text-color: #1f2937;',
        '    --bg-color: #f9fafb;',
        '}',
        '',
        '/* Листинг 4.2 — панель фильтров поиска (Flexbox) */',
        '.filters { display: flex; flex-wrap: wrap; gap: 1rem;',
        '           align-items: flex-end; margin: 1rem 0;',
        '           background: var(--color-surface, #fff); border-radius: 12px; }',
        '',
        '/* Листинг 4.3 — медиа-запрос (Mobile First) */',
        '@media (max-width: 768px) { .features, .detail-grid { grid-template-columns: 1fr; } }',
      ]),
      p('Доступность (a11y): подписи у всех полей (label_tag), aria-label у кнопки мобильного меню, aria-expanded при раскрытии, видимый контур фокуса, ошибки валидации выводятся текстом рядом с полем (Тема 10). Формы бронирования и поиска используют HTML5-типы input (date, time, number) и JS-валидацию (time_end > time_start, прошедшая дата) — клиентская валидация дублирует, но не заменяет серверную.'),
      listing([
        '/* Листинг 4.4 — семантическая структура базового шаблона (templates/base.html) */',
        '<header class="site-header">',
        '    <nav class="nav container"> ... <button class="nav-toggle" aria-label="Открыть меню">',
        '</header>',
        '<main class="container">',
        '    {% if messages %}<div class="messages" role="status"> ... </div>{% endif %}',
        '    {% block content %}{% endblock %}',
        '</main>',
        '<footer class="site-footer"> ... </footer>',
      ]),
      p('Страницы проекта: главная (hero + популярные аудитории), список аудиторий с фильтрами и пагинацией, карточка аудитории (характеристики, оборудование, занятость на сегодня, кнопка брони), поиск (панель параметров + результаты), форма бронирования, мои брони (таблица со статусами и отменой), подробности брони, расписание (фильтры по дате/аудитории/статусу), формы администратора (аудитория, оборудование), управление бронями, управление пользователями, профиль. Брейкпоинты: 768px и 480px.'),

      heading('5. Разработка REST API. Backend (Тема 12)'),
      p('API реализован на Django REST Framework. Использованы APIView с явным контролем HTTP-кодов: 200 OK, 201 Created, 204 No Content, 400 Bad Request, 401 Unauthorized (нет/просрочен токен, неверные учётные данные), 403 Forbidden (чужие данные, недостаточно прав), 404 Not Found, 422 Unprocessable Entity (ошибки семантической валидации сериализатора, включая пересечение броней). Аутентификация — JWT (djangorestframework-simplejwt), заголовок Authorization: Bearer <access>.'),
      p('Карта эндпоинтов (спецификация):'),
      table([
        ['Метод', 'URL', 'Описание', 'Успешные коды', 'Ошибочные коды'],
        ['POST', '/api/auth/register/', 'Регистрация (валидация сложности пароля)', '201', '422'],
        ['POST', '/api/auth/login/', 'Вход (username/email), выдача JWT', '200', '400, 401'],
        ['POST', '/api/auth/password-reset/request/', 'Запрос сброса (имитация email)', '200', '400'],
        ['POST', '/api/auth/password-reset/confirm/', 'Подтверждение сброса, новый пароль', '200', '400'],
        ['GET/POST', '/api/rooms/', 'Список аудиторий (с фильтрами)/создание (админ)', '200/201', '403, 422'],
        ['GET/PUT/DELETE', '/api/rooms/<id>/', 'Аудитория: просмотр/изменение (админ)/удаление (админ)', '200/204', '403, 404, 422'],
        ['GET', '/api/rooms/search/', 'Поиск свободных аудиторий', '200', '400'],
        ['GET', '/api/rooms/<id>/schedule/', 'Расписание аудитории', '200', '404'],
        ['GET', '/api/equipment/', 'Каталог оборудования', '200', '—'],
        ['GET/POST', '/api/bookings/', 'Свои брони (админ — все с ?all=1)/создание', '200/201', '401, 422'],
        ['GET/DELETE/PATCH', '/api/bookings/<id>/', 'Просмотр/отмена (204)/смена статуса (админ)', '200/204', '400, 403, 404'],
        ['GET', '/api/ping/', 'Служебная проверка', '200', '—'],
      ], [16, 26, 24, 14, 20]),
      p('Валидация реализована в сериализаторах: сложность пароля при регистрации (django.contrib.auth.password_validation), уникальность email, прошедшая дата, time_end > time_start, доступность аудитории, пересечение броней (в create() — conflicts_with_existing().exists() → 422).'),
      listing([
        '# Листинг 5.1 — серверная проверка конфликтов (api/serializers.py)',
        'def create(self, validated_data):',
        '    booking = Booking(**validated_data)',
        '    if booking.conflicts_with_existing().exists():',
        '        raise serializers.ValidationError(',
        '            {\'time_start\': \'Аудитория уже занята в выбранное время.\'})',
        '    booking.save()',
        '    return booking',
        '',
        '# Листинг 5.2 — пересечение интервалов на уровне ORM (bookings/models.py)',
        'qs = Booking.objects.filter(',
        '    room=self.room, date=self.date,',
        '    status__in=self.blocking_statuses(),   # pending + confirmed',
        '    time_start__lt=self.time_end,          # начало чужой брони раньше конца новой',
        '    time_end__gt=self.time_start,          # конец чужой брони позже начала новой',
        ')',
      ]),
      p('Защита приватных эндпоинтов: DEFAULT_PERMISSION_CLASSES = IsAuthenticated (без токена — 401); IsOwnerOrAdmin на объектных операциях (чужая бронь — 403); несуществующий идентификатор — get_object_or_404 (404); запись аудиторий — IsAdmin (обычный пользователь — 403). Для демонстрации выполняются запросы Postman по инструкции README: успешный POST → 201 с JSON, пересечение → 422, запрос без токена → 401, чужая бронь → 403, DELETE → 204.'),

      heading('6. Тестирование и проверка проекта'),
      p('Написаны автоматизированные тесты Django (python manage.py test): auth-потоки, RBAC, CRUD аудиторий и оборудования, поиск (вместимость, тип, корпус, оборудование, занятость, статус), полный набор тестов конфликтов бронирования (пересечение, частичное пересечение, вложенный интервал, границы интервалов, прошедшая дата, time_end <= time_start, занятость pending, освобождение слота после отмены), личный кабинет и анти-IDOR, подтверждение/отклонение админом с проверкой конфликта, REST API (201/204/400/401/403/404/422, поиск, расписание, служебные маршруты).'),
      p('В среде автоматической сборки отчёта интерпретатор Python без установленных Django/DRF доступен не был (установка пакетов в этой среде запрещена), поэтому фактический прогон тестов и миграций в ней не выполнялся и не заявляется. Проверено статически: согласованность моделей, миграций и ER-диаграммы; соответствие маршрутов представлениям; корректность импортов и сигнатур (compileall без ошибок). Для реального запуска выполните инструкции README: pip install -r requirements.txt, python manage.py migrate, python manage.py test, python manage.py runserver.'),
      p('Ограничения: (1) отправка писем по умолчанию настроена в консольный backend — реальный SMTP требует пароля приложения Mail.ru/Яндекса (инструкция в README); (2) в API password-reset/request токен возвращается в ответе как имитация доставки email (согласно заданию Темы 12); (3) расписание реализовано функциональной таблицей с фильтрами по дате/аудитории/статусу — полноформатный интерактивный календарь сознательно не вводился, чтобы не усложнять учебный проект; (4) уведомления по email о смене статуса брони не предусмотрены заданиями.'),
      p('Выводы: в рамках практики реализован полный цикл разработки веб-приложения — от ТЗ и UML-моделей до нормализованной БД PostgreSQL (6 сущностей, ассоциативная таблица оборудования), ролевой модели доступа, серверной проверки конфликтов бронирования, адаптивного интерфейса, механизма восстановления пароля и REST API с JWT. Все требования загруженных тем (Темы 1–4, 6–8, 9–10–11, 12) выполнены в едином проекте StudyRoomBooking.', { size: 24 }),
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(path.join(__dirname, 'Отчет_практика_StudyRoomBooking.docx'), buf);
  console.log('DOCX created:', buf.length, 'bytes');
});
