#!/usr/bin/env bash
echo ----------- Started release tasks
export DJANGO_SETTINGS_MODULE=maisha_service.settings
echo DJANGO_SETTINGS_MODULE
python3 manage.py makemigrations
python3 manage.py migrate
echo ----------- Completed release tasks