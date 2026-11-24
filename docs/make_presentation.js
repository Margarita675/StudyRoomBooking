// Презентация к защите практики (Тема 17) — StudyRoomBooking
const PptxGenJS = require('pptxgenjs');
const pres = new PptxGenJS();
pres.layout = 'LAYOUT_16x9';
pres.author = 'Сахабутдинова М.М.';

const DARK = '1F3B73', LIGHT = 'E8F0FE', TXT = '222222';
function slideBase(s, title) {
  s.background = { color: 'FFFFFF' };
  s.addShape('rect', { x: 0, y: 0, w: 13.33, h: 0.9, fill: { color: DARK } });
  s.addText(title, { x: 0.5, y: 0.1, w: 12.3, h: 0.7, fontSize: 24, bold: true, color: 'FFFFFF', fontFace: 'Times New Roman' });
}
const t = (s, text, y, opts = {}) => s.addText(text, Object.assign({ x: 0.7, y, w: 11.9, h: 0.5, fontSize: 16, color: TXT, fontFace: 'Times New Roman' }, opts));
const bullet = (s, items, y) => s.addText(items.map(i => ({ text: i, options: { bullet: true, breakLine: true } })), { x: 0.9, y, w: 11.5, h: 4.5, fontSize: 16, color: TXT, fontFace: 'Times New Roman', lineSpacingMultiple: 1.3 });

let s = pres.addSlide(); slideBase(s, 'Разработка веб-приложения StudyRoomBooking');
t(s, 'ГБПОУ «Казанский колледж технологии и дизайна»', 1.3, { fontSize: 20, bold: true });
t(s, 'Учебная практика по модулю ПМ.05', 1.9, { fontSize: 18 });
t(s, 'Выполнила: Сахабутдинова Маргарита Маратовна, гр. 09.02.07-3ВА', 3.2, { fontSize: 18 });
t(s, 'Проверила: Куприянова Е.А.', 3.8, { fontSize: 18 });
t(s, 'Казань, 2026', 6.2, { fontSize: 18, align: 'center' });

s = pres.addSlide(); slideBase(s, 'Актуальность и цель');
bullet(s, [
  'Поиск свободной аудитории вручную занимает время и приводит к конфликтам брони',
  'Система автоматизирует подбор аудитории и бронирование',
  'Цель: закрепление знаний ПМ.05 при разработке полноценного веб-приложения',
  'Задачи: проектирование БД, сервер на Django, REST API, ИИ-агент, безопасность, тестирование',
], 1.3);

s = pres.addSlide(); slideBase(s, 'Стек технологий и архитектура');
bullet(s, [
  'Python 3.13 + Django 5.1 — серверная часть',
  'PostgreSQL 18 — база данных (6+ таблиц)',
  'Django REST Framework + JWT — API',
  'HTML5, CSS3, JavaScript — адаптивный интерфейс',
  'Ollama / OpenRouter — ИИ-агент (OpenAI-compatible)',
  'Архитектура «клиент-сервер»: браузер → Django → PostgreSQL / ИИ-провайдер',
], 1.3);

s = pres.addSlide(); slideBase(s, 'Проектирование: UML и база данных');
bullet(s, [
  'Use Case, Class, Sequence, ER-диаграммы (Mermaid → PNG)',
  'Сущности: User, Profile, PasswordResetToken, AiMessage, Room, Equipment (M:N), Booking',
  'Связи: 1:1 (User–Profile), 1:N (User–Booking), M:N (Room–Equipment)',
  'Ограничения: UNIQUE, CHECK (time_end > time_start), индексы, CASCADE',
  'Скриншот: pgAdmin — дерево таблиц studyroom_db',
], 1.3);

s = pres.addSlide(); slideBase(s, 'Роли и безопасность');
bullet(s, [
  'Роли: студент (поиск, бронирование, отмена) и администратор (аудитории, подтверждение брони, пользователи)',
  'RBAC + login_required + анти-IDOR (чужие записи недоступны)',
  'CSRF-токены (Django middleware), автоэкранирование XSS, ORM против SQL-инъекций',
  'Пароли: PBKDF2-SHA256; токены сброса: SHA-256 хеш, TTL 30 минут, одноразовые',
  'Секреты: .env, .gitignore; ключ ИИ-провайдера только в .env',
], 1.3);

s = pres.addSlide(); slideBase(s, 'Восстановление пароля');
bullet(s, [
  'Одноразовый токен со сроком жизни 30 минут, в БД — только SHA-256 хеш',
  'Одинаковый ответ для существующего и несуществующего email (защита от перебора)',
  'Письмо — через SMTP (пароль приложения) или консоль в учебном режиме',
  'Инвалидация после использования; повторное открытие ссылки не работает',
], 1.3);

s = pres.addSlide(); slideBase(s, 'Интеграция ИИ-агента');
bullet(s, [
  'Агент = системный промпт + контекст из БД + история диалога',
  'Ollama (локально, бесплатно) и OpenRouter (облако) — переключение 3 строками .env',
  'История хранится в PostgreSQL (таблица agent_aimessage)',
  'Доступ только авторизованным, rate limit 10 запросов / 5 минут (429)',
  'Ответ выводится через textContent (защита от XSS)',
], 1.3);

s = pres.addSlide(); slideBase(s, 'Поиск и бронирование — ключевой функционал');
bullet(s, [
  'Поиск: дата, время, вместимость, тип, корпус, оборудование',
  'Серверная проверка конфликтов: пересечение интервалов → ошибка 422',
  'Статусы брони: ожидает, подтверждена, отклонена, отменена',
  'Расписание аудиторий и личный кабинет',
], 1.3);

s = pres.addSlide(); slideBase(s, 'Разработка интерфейса');
bullet(s, [
  'Адаптивность: Grid/Flexbox, media-запросы 768/480px',
  'Доступность: alt, label, focus, aria',
  'Единый стиль: CSS-переменные, карточки, формы с сообщениями об ошибках',
  'Демонстрация: ПК и мобильная версия (DevTools, iPhone SE)',
], 1.3);

s = pres.addSlide(); slideBase(s, 'Тестирование');
bullet(s, [
  'Функциональное: позитивные, негативные, граничные сценарии',
  'Безопасность: 403 без прав, CSRF, XSS, SQL-инъекции',
  'API: Postman, коды 200/201/400/401/403/422/429',
  'Автотесты: python manage.py test — OK',
  'Чек-лист, 7 тест-кейсов, 2 баг-репорта (исправлены)',
], 1.3);

s = pres.addSlide(); slideBase(s, 'Итоги');
bullet(s, [
  'Все задачи практики выполнены: БД, сервер, API, ИИ-агент, безопасность, тесты',
  'Git-репозиторий: https://github.com/ЛОГИН/StudyRoomBooking',
  'Перспективы: уведомления по email, календарный интерфейс, роль «сотрудник колледжа»',
], 1.5);

s = pres.addSlide();
s.addText('Спасибо за внимание!', { x: 1, y: 2.5, w: 11.3, h: 1, fontSize: 40, bold: true, color: DARK, fontFace: 'Times New Roman', align: 'center' });
t(s, 'Готова ответить на ваши вопросы', 3.6, { fontSize: 20, align: 'center' });

pres.writeFile({ fileName: 'docs/Презентация_защита_StudyRoomBooking.pptx' })
  .then(f => console.log('PPTX created:', f));
