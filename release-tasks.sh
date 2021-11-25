#!/usr/bin/env bash
set DJANGO_SETTINGS_MODULE=maisha_service.settings
python3 manage.py makemigrations
python3 manage.py migrate