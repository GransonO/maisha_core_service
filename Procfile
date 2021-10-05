release: bash ./release-tasks.sh
web: gunicorn maisha_service.wsgi —-log-file -
worker: python manage.py qcluster