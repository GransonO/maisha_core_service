release: bash ./release-tasks.sh
web: daphne maisha_service.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: python manage.py runworker channel_layer