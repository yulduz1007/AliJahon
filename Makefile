mig:
	./manage.py makemigrations
	./manage.py migrate

admin:
	./manage.py createsuperuser

app:
	./manage.py startapp apps