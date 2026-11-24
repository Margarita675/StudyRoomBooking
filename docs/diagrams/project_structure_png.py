"""Схема структуры проекта StudyRoomBooking (Тема 5, рисунок 1)."""
from PIL import Image, ImageDraw, ImageFont

def font(size, bold=False):
    for cand in (['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'] if bold else [],
                 ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']):
        try: return ImageFont.truetype(cand[0], size)
        except Exception: continue
    return ImageFont.load_default()

F, FB = font(15), font(16, True)
BLUE, DARK, LIGHT, GREY = (47, 111, 79), (31, 41, 55), (231, 246, 238), (107, 114, 128)
tree = [
    ('StudyRoomBooking/', True, 0),
    ('manage.py, requirements.txt, README.md, .env.example, .gitignore', False, 1),
    ('config/          настройки (settings.py), корневые маршруты (urls.py), wsgi/asgi', True, 0),
    ('accounts/          пользователи: регистрация, вход, профиль, роли (RBAC), сброс пароля', True, 0),
    ('rooms/             аудитории и оборудование (Room, Equipment, RoomEquipment)', True, 0),
    ('bookings/          бронирования, расписание, личный кабинет', True, 0),
    ('api/               REST API (DRF, JWT), служебные ping/health', True, 0),
    ('templates/         общие шаблоны: base.html, home.html', True, 0),
    ('static/css, static/js     стили (CSS-переменные, Grid/Flex) и клиентская валидация', True, 0),
    ('media/             фотографии аудиторий', True, 0),
    ('docs/              ТЗ, SQL-скрипты БД, UML-диаграммы, отчёты по темам практики', True, 0),
]
W, H = 900, 480
img = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(img)
y = 20
for text, is_dir, level in tree:
    indent = 14 + level * 22
    if is_dir:
        d.rectangle([indent, y, W - 20, y + 28], fill=LIGHT, outline=BLUE, width=1)
        d.text((indent + 10, y + 5), text, font=FB, fill=DARK)
    else:
        d.text((indent + 24, y + 5), text, font=F, fill=GREY)
    y += 36
d.text((20, H - 24), 'Рисунок 1. Структура проекта StudyRoomBooking (приложения выделены цветом)', font=F, fill=DARK)
img.save('project_structure.png')
print('ok')
