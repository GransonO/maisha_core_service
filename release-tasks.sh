#!/usr/bin/env bash
set DJANGO_SETTINGS_MODULE=maisha_service.settings
export DJANGO_SETTINGS_MODULE=maisha_service.settings
python manage.py shell
python3 manage.py makemigrations
python3 manage.py migrate