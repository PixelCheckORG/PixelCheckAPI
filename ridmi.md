# PixelCheck - Guía rápida de ejecución

## 1. Prerrequisitos
- Python 3.11 instalado.
- Docker Desktop corriendo (tus servicios MySQL/Redis ya están definidos).
- Repositorio del proyecto descargado y abierto en PowerShell en la carpeta raíz.

pip install -r requirements.txt

## 2. Activar el entorno virtual
```powershell
.\.venv\Scripts\activate

.\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
.\.venv\Scripts\activate
celery -A config worker -l info

## 3. instalar depenendicas


pip install --upgrade pip
pip install -r requirements.txt


## Migracviones

python manage.py makemigrations
python manage.py migrate
python manage.py seed_roles
python manage.py createsuperuser   # opcional pero útil


## corre dyjango
python manage.py runserver 0.0.0.0:8000


## worer en otr terminal


.\.venv\Scripts\activate
celery -A config worker -l info

## para windows 
celery -A config worker -l info -P solo -n worker1@%h