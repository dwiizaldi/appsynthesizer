python manage.py /home/synthesizer/components/django-celery-example/manage.py migrate
celery -A mysite worker -l info
