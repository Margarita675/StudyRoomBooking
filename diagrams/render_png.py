"""
Генерация PNG-версий диаграмм StudyRoomBooking (Тема 1).
Рисунки строятся скриптом Python (Pillow) так, чтобы точно соответствовать
моделям проекта. Исходники Mermaid лежат рядом (.mmd).
Запуск: python render_png.py
"""
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = None
try:
    from matplotlib import font_manager
    FONT_PATH = font_manager.findfont('DejaVu Sans')
except Exception:
    pass

def font(size, bold=False):
    for cand in (['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'] if bold else [],
                 ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'],
                 [FONT_PATH] if FONT_PATH else []):
        try:
            return ImageFont.truetype(cand[0], size)
        except Exception:
            continue
    return ImageFont.load_default()

F_TITLE, F_BOX, F_SMALL = font(28, True), font(17), font(14)
BLUE, DARK, GREY, LIGHT, RED = (21, 101, 192), (31, 41, 55), (107, 114, 128), (227, 238, 250), (183, 28, 28)

def text_center(d, xy, text, f=F_BOX, fill=DARK):
    w = d.textlength(text, font=f)
    d.text((xy[0] - w / 2, xy[1]), text, font=f, fill=fill)

def box(d, x, y, w, h, title, fill=(255, 255, 255), outline=BLUE, r=8):
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill, outline=outline, width=2)
    text_center(d, (x + w / 2, y + 8), title, F_BOX, DARK)

def actor(d, x, y, label):
    d.ellipse([x - 11, y, x + 11, y + 22], outline=DARK, width=2)
    d.line([x, y + 22, x, y + 52], fill=DARK, width=2)
    d.line([x - 18, y + 34, x + 18, y + 34], fill=DARK, width=2)
    d.line([x, y + 52, x - 14, y + 72], fill=DARK, width=2)
    d.line([x, y + 52, x + 14, y + 72], fill=DARK, width=2)
    text_center(d, (x, y + 78), label, F_BOX, DARK)

def draw_use_case():
    img = Image.new('RGB', (1250, 680), 'white'); d = ImageDraw.Draw(img)
    d.rectangle([250, 30, 1000, 650], outline=GREY, width=2)
    text_center(d, (625, 36), 'Система StudyRoomBooking', F_TITLE, DARK)
    actor(d, 120, 80, 'Гость'); actor(d, 120, 290, 'Студент'); actor(d, 120, 510, 'Администратор')
    ucs = ['Регистрация', 'Вход в систему', 'Восстановление пароля',
           'Просмотр аудиторий', 'Поиск свободных аудиторий', 'Просмотр занятости',
           'Создание бронирования', 'Отмена своей брони', 'Личный кабинет',
           'Управление аудиториями', 'Управление оборудованием',
           'Подтверждение/отклонение броней', 'Расписание', 'Управление пользователями']
    ys = [70, 115, 160, 205, 250, 295, 340, 385, 430, 475, 520, 565, 610, 610]
    xs = [625] * 13 + [625]
    for x, y, t in zip(xs, ys, ucs):
        d.ellipse([x - 150, y - 18, x + 150, y + 18], fill=LIGHT, outline=BLUE, width=2)
        text_center(d, (x, y - 9), t, F_SMALL, DARK)
    for y in (70, 115, 160, 205):
        d.line([132, 100, 470, y], fill=DARK, width=1)
    for y in (250, 295, 340, 385, 430, 475):
        d.line([132, 310, 470, y], fill=DARK, width=1)
    for y in (475, 520, 565, 610):
        d.line([132, 530, 470, y], fill=DARK, width=1)
    img.save('use_case.png')

def entity_box(d, x, y, w, title, attrs, outline=BLUE):
    h = 34 + 22 * (len(attrs) + 1)
    d.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=(255, 255, 255), outline=outline, width=2)
    d.rectangle([x, y, x + w, y + 30], fill=LIGHT, outline=outline)
    text_center(d, (x + w / 2, y + 4), title, F_SMALL, DARK)
    ty = y + 34
    for a in attrs:
        d.text((x + 10, ty), a, font=F_SMALL, fill=DARK); ty += 22
    return x, y, w, h

def draw_class():
    img = Image.new('RGB', (1250, 620), 'white'); d = ImageDraw.Draw(img)
    text_center(d, (625, 10), 'Диаграмма классов StudyRoomBooking', F_TITLE, DARK)
    e = entity_box
    pos = {}
    pos['User'] = e(d, 60, 70, 250, 'User', ['+username: str', '+email: str', '+role: str', '+full_name: str', '+is_admin(): bool'])
    pos['PRT'] = e(d, 60, 260, 250, 'PasswordResetToken', ['+token_hash: str', '+expires_at', '+is_used: bool', '+is_valid(): bool'])
    pos['Room'] = e(d, 480, 70, 300, 'Room', ['+number: str', '+building: str', '+floor: int', '+capacity: int', '+room_type: str', '+status: str', '+is_available(): bool'])
    pos['Eq'] = e(d, 900, 70, 280, 'Equipment', ['+name: str', '+description: str'])
    pos['RE'] = e(d, 900, 250, 280, 'RoomEquipment', ['+quantity: int'])
    pos['B'] = e(d, 480, 330, 300, 'Booking', ['+date: date', '+time_start', '+time_end', '+purpose: str', '+status: str', '+conflicts_with_existing()'])
    def link(a, b, la, lb, label=''):
        (ax, ay, aw, ah), (bx, by, bw, bh) = pos[a], pos[b]
        x1, y1, x2, y2 = ax + aw / 2, ay + ah / 2, bx + bw / 2, by + bh / 2
        d.line([x1, y1, x2, y2], fill=DARK, width=2)
        d.line([x1 - 6, y1 - 6, x1 + 6, y1 + 6], fill=DARK, width=2)
        d.line([x1 - 6, y1 + 6, x1 + 6, y1 - 6], fill=DARK, width=2)
        d.polygon([(x2 - 8, y2 - 4), (x2 - 8, y2 + 4), (x2 + 8, y2)], fill=DARK)
        if label:
            text_center(d, ((x1 + x2) / 2, (y1 + y2) / 2 - 20), label, F_SMALL, GREY)
    link('User', 'PRT', '', '', '1 : *')
    link('User', 'B', '', '', '1 : *')
    link('Room', 'B', '', '', '1 : *')
    link('Room', 'RE', '', '', '')
    link('Eq', 'RE', '', '', '')
    img.save('class_diagram.png')

def draw_erd():
    img = Image.new('RGB', (1250, 660), 'white'); d = ImageDraw.Draw(img)
    text_center(d, (625, 10), 'ERD StudyRoomBooking (PostgreSQL)', F_TITLE, DARK)
    pos = {}
    pos['u'] = entity_box(d, 60, 70, 280, 'accounts_user', ['id PK', 'username UK', 'email UK', 'role CHECK', 'full_name'])
    pos['prt'] = entity_box(d, 60, 300, 280, 'accounts_passwordresettoken', ['id PK', 'token_hash UK', 'expires_at', 'is_used', 'user_id FK'])
    pos['r'] = entity_box(d, 500, 60, 280, 'rooms_room', ['id PK', 'number UK', 'building, floor', 'capacity CHECK', 'room_type CHECK', 'status CHECK'])
    pos['e'] = entity_box(d, 900, 60, 280, 'rooms_equipment', ['id PK', 'name UK', 'description'])
    pos['re'] = entity_box(d, 900, 250, 280, 'rooms_roomequipment', ['id PK', 'quantity CHECK', 'room_id FK', 'equipment_id FK'])
    pos['b'] = entity_box(d, 500, 370, 280, 'bookings_booking', ['id PK', 'date', 'time_start', 'time_end CHECK', 'purpose', 'status CHECK', 'room_id FK', 'user_id FK'])
    def line(a, b, label):
        (ax, ay, aw, ah), (bx, by, bw, bh) = pos[a], pos[b]
        d.line([ax + aw / 2, ay + ah / 2, bx + bw / 2, by + bh / 2], fill=DARK, width=2)
        text_center(d, ((ax + bx) / 2 + 20, (ay + by) / 2 - 24), label, F_SMALL, GREY)
    line('u', 'b', '1:N'); line('u', 'prt', '1:N'); line('r', 'b', '1:N')
    line('r', 're', '1:N'); line('e', 're', '1:N')
    img.save('erd.png')

def lifeline(d, x, top, bottom, label):
    d.rectangle([x - 80, top - 40, x + 80, top], fill=LIGHT, outline=DARK, width=2)
    text_center(d, (x, top - 34), label, F_SMALL, DARK)
    d.line([x, top, x, bottom], fill=GREY, width=2)

def draw_sequence():
    img = Image.new('RGB', (1250, 640), 'white'); d = ImageDraw.Draw(img)
    text_center(d, (625, 8), 'Бронирование аудитории: проверка конфликтов', F_TITLE, DARK)
    xs = [150, 420, 700, 950, 1150]
    labels = ['Студент', 'BookingForm', 'View (save)', 'PostgreSQL', 'Администратор']
    lifeline(d, xs[0], 60, 600, labels[0]); lifeline(d, xs[1], 60, 600, labels[1])
    lifeline(d, xs[2], 60, 600, labels[2]); lifeline(d, xs[3], 60, 600, labels[3])
    lifeline(d, xs[4], 60, 600, labels[4])
    def arrow(x1, x2, y, text, color=DARK, dash=False):
        d.line([x1, y, x2, y], fill=color, width=2)
        if dash:
            d.line([x1, y + 2, x2, y + 2], fill='white', width=1)
        d.polygon([(x2 - 9, y - 5), (x2 - 9, y + 5), (x2, y)], fill=color)
        text_center(d, ((x1 + x2) / 2, y - 20), text, F_SMALL, color)
    arrow(xs[0], xs[1], 110, 'POST /bookings/room/<id>/')
    arrow(xs[1], xs[2], 150, 'is_valid(), clean()')
    arrow(xs[2], xs[3], 190, 'SELECT пересечений', dash=False)
    d.rectangle([xs[3] - 130, 240, xs[3] + 130, 280], outline=RED, width=2)
    text_center(d, (xs[3], 250), 'start < other.end AND end > other.start', F_SMALL, RED)
    arrow(xs[3], xs[2], 320, 'конфликт?', dash=True, color=GREY)
    arrow(xs[2], xs[0], 360, 'Ошибка «Аудитория занята»', color=RED, dash=True)
    arrow(xs[2], xs[3], 400, 'INSERT booking (pending)', dash=True, color=BLUE)
    arrow(xs[3], xs[2], 440, 'id', dash=True, color=BLUE)
    arrow(xs[0], xs[0], 470, '', color='white')
    arrow(xs[4], xs[2], 480, 'action=confirm')
    arrow(xs[2], xs[3], 520, 'UPDATE status=confirmed', dash=True, color=BLUE)
    img.save('sequence_diagram.png')

if __name__ == '__main__':
    draw_use_case(); draw_class(); draw_erd(); draw_sequence()
    print('PNG-диаграммы перегенерированы.')
