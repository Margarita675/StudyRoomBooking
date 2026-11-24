#!/usr/bin/env python
"""Django management utility for the StudyRoomBooking project."""
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            'Не найден Django. Активируйте виртуальное окружение: venv\\Scripts\\activate'
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
