#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tasasweb.local')
    try:
        os.environ['MUNI_ID'] = '000'
        os.environ['MUNI_DB'] = 'gg_prueba'
        os.environ['MUNI_DIR'] = 'prueba'
        # os.environ['MUNI_DB_PASSWD'] = 'battlehome'
        # os.environ['ERROR_MAIL_USER'] = 'grupogua_errores'
        # os.environ['ERROR_MAIL_PASSWD'] = 'Sarasa1616'
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()