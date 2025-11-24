# PixelCheck API (Django + DRF + Celery)

Implementación del backend descrito en `PixelCheckAPI_Arquitectura.md`, basada en DDD + Clean Architecture sobre Django 5, DRF, Celery y MySQL.

## Estructura

```
PixelCheck/
├── config/              # settings Django, Celery, excepciones
├── iam/                 # IAM (usuarios, roles, JWT)
├── ingestion/           # Upload/validación de imágenes + eventos Celery
├── analysis/            # Worker de inferencia (stub determinístico)
├── results/             # Resultados y reportes PDF/CSV
├── sysmgmt/             # Auditoría básica
├── shared/              # Utilidades cross-cutting (VOs, utils, permisos)
└── tests/               # Smoke tests mínimos
```

Cada bounded context sigue carpetas `domain/`, `application/`, `infrastructure/`, `interface/`.

## Requisitos

- Python 3.11
- MySQL 8 (o SQLite en dev)
- Redis 5+ para broker/resultados Celery

Instala dependencias:

```bash
pip install -r requirements.txt
```

## Configuración

1. Duplica `.env.example` a `.env` y ajusta credenciales (`DATABASE_URL`, `REDIS_URL`, `DJANGO_SECRET_KEY`, etc.).
2. Ejecuta migraciones y crea roles base:

```bash
python manage.py makemigrations iam ingestion analysis results sysmgmt
python manage.py migrate
python manage.py seed_roles
```

3. Crea un superusuario y arranca servicios:

```bash
python manage.py createsuperuser
celery -A config worker -l info
python manage.py runserver
```

## Endpoints MVP

- `POST /api/v1/auth-sign-up` – Registro de usuarios.
- `POST /api/v1/auth-sign-in` – Obtención de tokens JWT.
- `POST /api/v1/images/upload` – Sube la imagen, valida y encola análisis.
- `GET /api/v1/results/{imageId}` – Consulta label/confidence/modelVersion.
- `GET /api/v1/reports/{reportId}` – Descarga reporte listo (se genera automático si eres ROLE_PROFESSIONAL o staff).
- `GET /api/v1/analysis/health` – Información del modelo.
- `POST /api/v1/system/audit` – Registra eventos (autenticado).
- `GET /api/v1/system/audit` – Solo staff (admin Django) para revisar auditoría.
- `GET /api/docs/` – Swagger UI (`/api/schema/` JSON, `/api/redoc/` ReDoc).

## Ejecución rápida en PyCharm

1. Selecciona el intérprete `.venv` y corre `pip install -r requirements.txt`.
2. Define una Run Configuration *Django server* (PyCharm detecta `manage.py`) con `DJANGO_SETTINGS_MODULE=config.settings` si no se autocompleta.
3. Ejecuta `python manage.py migrate` y `python manage.py seed_roles` desde la terminal integrada.
4. Usa el botón **Run** para iniciar `manage.py runserver`.
5. Crea otra configuración *Python* para Celery apuntando a `.venv/Scripts/celery.exe` con argumentos `-A config worker -l info` y ejecútala en paralelo.
6. Abre `http://127.0.0.1:8000/api/docs/` y prueba los endpoints directamente desde Swagger.
## Notas de arquitectura

- `shared/utils/image.py` centraliza validaciones (tipo, tamaño, dimensiones, checksum).
- `analysis/tasks/worker.py` expone `run_analysis_task` consumido por Celery; el stub usa el checksum para generar resultados determinísticos.
- Reportes almacenan el binario en DB (`results.models.Report`) y usan `shared/utils/reporting.py` para PDF/CSV.
- Excepción personalizada `config.exceptions.pixelcheck_exception_handler` mapea errores de dominio a respuestas DRF.

## Próximos pasos sugeridos

- Integrar almacenamiento externo para blobs.
- Añadir throttling y métricas avanzadas (Prometheus / OTEL).
- Sustituir el stub de ML por un modelo real y versionado.




