#!/bin/sh


python manage.py flush --no-input
python manage.py migrate
python manage.py load_trash

exec "$@"