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
```

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



celery -A config worker -l info


## correr el back
python manage.py runserver




```gitignore

### git ignore

# Environment variables
.env
.env.*
!.env.example
!.env.template

# Python
*.py[cod]
*$py.class
*.so
.Python
__pycache__/
*.pyc
*.pyo
*.pyd

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/
static_root/

# Virtual environments
venv/
env/
ENV/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Celery
celerybeat-schedule
celerybeat.pid

# ML Models (si son muy grandes)
*.h5
*.pkl
*.joblib
models/*.h5
models/*.pkl

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Distribution
dist/
build/
*.egg-info/
```