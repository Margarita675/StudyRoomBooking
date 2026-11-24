from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                     serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
            ],
            options={'verbose_name': 'Оборудование', 'verbose_name_plural': 'Оборудование',
                     'ordering': ('name',)},
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                     serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=20, unique=True,
                     verbose_name='Номер аудитории')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('building', models.CharField(default='1', max_length=50, verbose_name='Корпус')),
                ('floor', models.PositiveSmallIntegerField(default=1, verbose_name='Этаж')),
                ('capacity', models.PositiveSmallIntegerField(default=10,
                     verbose_name='Вместимость')),
                ('room_type', models.CharField(choices=[
                     ('lecture', 'Лекционная'), ('computer', 'Компьютерная'),
                     ('lab', 'Лабораторная'), ('conference', 'Конференц-зал'),
                     ('classroom', 'Учебная'), ('universal', 'Универсальная')],
                     default='classroom', max_length=15, verbose_name='Тип аудитории')),
                ('status', models.CharField(choices=[
                     ('active', 'Доступна'), ('maintenance', 'На обслуживании'),
                     ('closed', 'Закрыта')], default='active', max_length=15,
                     verbose_name='Статус')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('photo', models.ImageField(blank=True, null=True,
                     upload_to='rooms/', verbose_name='Фотография')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создана')),
                # Поле equipment (M2M через RoomEquipment) добавляется отдельной
                # операцией AddField ниже — ПОСЛЕ создания модели-посредника,
                # иначе миграция падает на create_model.
            ],
            options={
                'verbose_name': 'Аудитория', 'verbose_name_plural': 'Аудитории',
                'ordering': ('building', 'floor', 'number'),
            },
        ),
        migrations.CreateModel(
            name='RoomEquipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                     serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField(default=1,
                     verbose_name='Количество')),
                ('equipment', models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='room_links', to='rooms.equipment',
                     verbose_name='Оборудование')),
                ('room', models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='room_equipment', to='rooms.room',
                     verbose_name='Аудитория')),
            ],
            options={
                'verbose_name': 'Оборудование аудитории',
                'verbose_name_plural': 'Оборудование аудиторий',
                'unique_together': {('room', 'equipment')},
            },
        ),
        migrations.AddField(
            model_name='room', name='equipment',
            field=models.ManyToManyField(
                related_name='rooms', through='rooms.RoomEquipment',
                to='rooms.equipment', verbose_name='Оборудование'),
        ),
        migrations.AddIndex(
            model_name='room', index=models.Index(
                fields=['building', 'floor'], name='rooms_buildi_floor_idx')),
        migrations.AddIndex(
            model_name='room', index=models.Index(fields=['capacity'],
                name='rooms_capaci_idx')),
        migrations.AddIndex(
            model_name='room', index=models.Index(fields=['room_type'],
                name='rooms_room_type_idx')),
        migrations.AddConstraint(
            model_name='room', constraint=models.CheckConstraint(
                check=models.Q(floor__gte=0), name='room_floor_gte_0')),
        migrations.AddConstraint(
            model_name='room', constraint=models.CheckConstraint(
                check=models.Q(capacity__gt=0), name='room_capacity_gt_0')),
        migrations.AddConstraint(
            model_name='roomequipment', constraint=models.CheckConstraint(
                check=models.Q(quantity__gt=0), name='room_equipment_qty_gt_0')),
    ]
