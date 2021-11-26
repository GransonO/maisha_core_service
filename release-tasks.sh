#!/usr/bin/env bash
echo ----------- Started release tasks
python3 manage.py makemigrations
python3 manage.py migrate
echo ----------- Completed release tasks