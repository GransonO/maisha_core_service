#!/usr/bin/env bash
echo ----------- Started release tasks
export DJANGO_SETTINGS_MODULE=maisha_service.settings
python3 manage.py makemigrations
python3 manage.py migrate
echo ----------- Completed release tasks