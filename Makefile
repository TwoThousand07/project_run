
run:
	python manage.py runserver --settings=project_run.settings.local

makemigr:
	python manage.py makemigrations --settings=project_run.settings.local

migr:
	python manage.py migrate --settings=project_run.settings.local

superusr:
	python manage.py createsuperuser --settings=project_run.settings.local