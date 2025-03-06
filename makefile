runserver:
	python manage.py runserver 8000
test:
	pytest --verbose
coverage:
	pytest --cov=apps/users --cov-report=html
makemigrations:
	python manage.py makemigrations
migrate:
	python manage.py migrate
superuser:
	python manage.py createsuperuser
shell:
	python manage.py shell
