# PixelCheck — Backend (Django + DRF) — Arquitectura Propuesta (DDD + Clean)

> Objetivo: consolidar una arquitectura pragmática basada en DDD + Clean Architecture sobre Django 5 + DRF, Celery + Redis y MySQL, alineada con el Informe y la base existente, priorizando un MVP funcional que podamos codear de inmediato.

---

## 1) Alcance del MVP

- Subir una imagen (JWT requerido) y validarla (tamaño, tipo, dimensiones, checksum).
- Encolar una tarea de análisis (Celery) consumida por un worker (stub de ML en MVP).
- Persistir resultado del análisis con `label ∈ {AI, REAL}`, `confidence ∈ [0..1]` y `model_version`.
- Consultar resultados por `imageId` y generar reportes básicos (PDF/CSV) para rol PROFESSIONAL.
- Auditoría/métricas simples de llamadas.

No-funcionales (MVP):
- p95 upload→result ≤ 10s (CPU), logging básico, versionado de modelo por análisis, separación metadatos/contenido.

---

## 2) Stack Técnico

- Core: Python 3.11.x (recomendado), Django 5, Django REST Framework.
- Jobs: Celery + Redis (broker), tareas idempotentes cuando aplique.
- DB: MySQL 8 (metadatos en tablas normales, BLOBs en tablas separadas).
- Auth: JWT (djangorestframework-simplejwt o PyJWT + capa propia).
- ML: Inference stub (carga real posterior), SavedModel CPU (fuera del alcance MVP).

Dependencias clave (pip):
- django~=5.1, djangorestframework~=3.15
- djangorestframework-simplejwt~=5.3
- mysqlclient~=2.2 (o alternativa: pymysql~=1.1)
- celery~=5.4, redis~=5.0
- pillow~=10.4 (validación de imágenes)
- django-environ~=0.11 (variables de entorno)

---

## 3) Bounded Contexts (DDD)

1) IAM (Identity & Access Management)
- Responsabilidad: usuarios, roles, autenticación JWT, autorización simple por roles.
- Agregados/Entidades: User, Role; VOs: Email, Username, PasswordHash.
- Eventos: UserRegistered, UserSignedIn.

2) Ingestion & Validation
- Responsabilidad: carga, validación, persistencia de metadatos y contenido (BLOB) y encolado de análisis.
- Agregados: Image; VOs: Checksum, ValidationPolicy.
- Eventos: AnalysisRequested (hacia Analysis), ImageValidated.

3) Image Analysis (ML)
- Responsabilidad: orquestar inferencia, producir AnalysisResult, versionado de modelo.
- Agregados: AnalysisJob, AnalysisResult, ModelVersion.
- Servicios dominio: InferenceService (puerto), post-procesado.
- Eventos: AnalysisCompleted, AnalysisFailed.

4) Results & Reporting
- Responsabilidad: consultas de resultados, generación de reportes (PDF/CSV) en BLOB.
- Agregados: Result (read model), Report.
- Servicios: ReportBuilder, PdfGenerator, CsvExporter.
- Eventos: ReportGenerated.

5) System Management
- Responsabilidad: auditoría, métricas, ACL transversal mínima.
- Agregados: AuditLog, Metric, RetentionPolicy.

Context Mapping (resumen):
- IAM ↔ Ingestion: Customer/Supplier (permisos).
- Ingestion → Analysis: evento AnalysisRequested(imageId).
- Analysis → Results: Conformist (Results no altera salida ML).
- IAM ↔ Results: Shared Kernel (roles/claims).
- System Mgmt ↔ todos: ACL/Anti-Corruption para logs/métricas.

---

## 4) Modelo de Datos (MVP / MySQL)

Separar metadatos y contenido de imagen.

- users(id PK, username UNIQUE, email UNIQUE, password_hash, created_at)
- roles(id PK, name UNIQUE in {USER, PROFESSIONAL, ADMIN})
- user_roles(user_id FK→users, role_id FK→roles)
- images(image_id PK, uploader_id, filename, mime_type, size_bytes, width, height, checksum UNIQUE, status ENUM('REJECTED','VALIDATED','QUEUED','DONE'), created_at)
- image_data(image_id PK FK→images, content LONGBLOB)
- analysis_results(result_id PK, image_id UNIQUE, owner_id, label ENUM('AI','REAL'), confidence DECIMAL(5,4), model_version VARCHAR(64), processed_at)
- reports(report_id PK, owner_id, scope ENUM('SINGLE','BATCH'), format ENUM('PDF','CSV'), status ENUM('REQUESTED','GENERATING','READY','FAILED'), created_at, content LONGBLOB, content_mime, filename)
- audit_logs(log_id PK, actor_id NULL, action, target, payload_json JSON, occurred_at)

---

## 5) Contratos de API (MVP)

- POST /api/v1/auth/sign-up → 201
- POST /api/v1/auth/sign-in → 200 {jwt}
- POST /api/v1/images/upload (multipart, JWT) → 202 {imageId, status}
- GET  /api/v1/results/{imageId} (JWT) → 200 {label, confidence, modelVersion}
- POST /api/v1/reports (JWT role=PROFESSIONAL) → 202 {reportId}
- GET  /api/v1/reports/{reportId} (JWT) → 200 file/blob
- (Opcional) GET /api/v1/ml/health, GET /api/v1/ml/model-version → 200
- System Mgmt: POST /api/v1/system/audit, POST/GET /api/v1/system/metrics

Seguridad:
- Autenticación: JWT bearer.
- Autorización: permisos DRF por rol (USER, PROFESSIONAL, ADMIN). Filtro por owner en consultas.

---

## 6) Flujo End-to-End

1. Sign-in (JWT) → Upload imagen → valida → guarda metadatos + image_data → encola AnalysisRequested(imageId).
2. Worker Celery consume → carga BLOB → preprocess → inferencia stub → guarda analysis_results.
3. Cliente consulta `GET /results/{imageId}` → devuelve label, confidence, modelVersion.
4. Profesional solicita reporte → tarea genera PDF/CSV mínimo → persiste en `reports.content` → descarga.

---

## 7) Estructura de Código (Monorepo Django + Clean)

```
pixelcheck/
  manage.py
  pyproject.toml / requirements.txt
  .env.example
  config/
    __init__.py
    settings.py
    urls.py
    wsgi.py
    celery.py
  shared/
    kernel/            # VOs/Enums estables (RoleName, Label)
    adapters/          # comunes (Queue, PDF, CSV, JWT, Hasher)
    utils/
  iam/
    domain/
    application/
    interface/         # DRF serializers/views/routers, ACL facade
    infrastructure/    # ORM, repos concretos, jwt/hasher
  ingestion/
    domain/
    application/
    interface/
    infrastructure/    # ImageORM, ImageDataORM, CeleryQueueAdapter
  analysis/
    domain/
    application/       # AnalysisOrchestrator
    interface/
    infrastructure/    # AnalysisResultORM, tasks.py
    ml/                # loader SavedModel, preprocess/postprocess (stub)
  results/
    domain/
    application/
    interface/
    infrastructure/    # ResultsRepo, ReportsRepo, PDF/CSV adapters
  sysmgmt/
    domain/
    application/
    interface/
    infrastructure/
```

Reglas Clean:
- domain no importa de Django/DRF.
- application orquesta casos de uso y depende de interfaces (puertos).
- interface e infrastructure implementan puertos.

---

## 8) Validación de Imágenes (Política MVP)

- Tipos: image/jpeg, image/png, image/webp.
- Tamaño máximo: 10MB (`DATA_UPLOAD_MAX_MEMORY_SIZE=10485760`).
- Dimensiones máximas: 4096×4096 (resize a 224×224 solo para ML, no para guardar).
- Duplicados: rechazar o referenciar si `checksum` sha256 ya existe para el mismo usuario.

---

## 9) Variables de Entorno

- DATABASE_URL=mysql://user:pass@host:3306/pixelcheck
- REDIS_URL=redis://localhost:6379/0
- DJANGO_SECRET_KEY=...
- JWT_SECRET=...
- PIXELCHECK_MODEL_PATH=models/pixelcheck/v1
- PIXELCHECK_MODEL_VERSION=v1
- PIXELCHECK_THRESHOLD=0.50

Ejemplo `.env.example`:
```
DATABASE_URL=mysql://pixel:pixel@127.0.0.1:3306/pixelcheck
REDIS_URL=redis://127.0.0.1:6379/0
DJANGO_SECRET_KEY=dev-secret
JWT_SECRET=dev-jwt-secret
PIXELCHECK_MODEL_PATH=./models/pixelcheck/v1
PIXELCHECK_MODEL_VERSION=v1
PIXELCHECK_THRESHOLD=0.50
DATA_UPLOAD_MAX_MEMORY_SIZE=10485760
```

---

## 10) Plan de Trabajo para Codegen/Scaffolding

1) Config base Django
- Crear proyecto `config`, apps por BC, DRF, SimpleJWT (o adapter propio), Celery con autodiscovery, MySQL.
- Registrar `INSTALLED_APPS = [iam, ingestion, analysis, results, sysmgmt]`.

2) IAM
- ORM: users, roles, user_roles; repos e interfaces; services de sign-up/sign-in (hash + jwt); endpoints DRF.

3) Ingestion & Validation
- ORM: images, image_data; endpoint upload multipart; validación (tipo, tamaño, dimensiones), checksum; encolar Celery.

4) Analysis (ML)
- ORM: analysis_results; task `analyze_image(image_id)` invoca InferenceService (stub determinístico); persistencia.

5) Results & Reporting
- Query results por `imageId` (filtro owner/rol); reportes (crear PDF/CSV mínimos a memoria, guardar LONGBLOB).

6) System Management
- auditoría/métricas mínimas; endpoints de registro y consulta.

7) Pruebas mínimas
- smoke tests: auth (201/200), upload (202), results (404/200), reports (202/200), celery mock.

---

## 11) Recomendación de Entorno y Versiones

- Python recomendado: 3.11.x. Django 5 soporta 3.11 y 3.12; 3.11 es estable y ampliamente soportado por dependencias.
- En Windows, `mysqlclient` puede requerir compiladores; si complica, usa `pymysql` (instalación pura Python) como alternativa.
- Node no es requerido para el backend.

Pasos iniciales (local):
```
# 1) Crear venv
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# en Windows PowerShell:
# .venv\\Scripts\\Activate.ps1

# 2) Instalar deps
pip install --upgrade pip
pip install django djangorestframework djangorestframework-simplejwt \
            celery redis pillow django-environ mysqlclient
# si falla mysqlclient en Windows:
# pip install pymysql

# 3) Crear proyecto y apps (luego codegen rellena)
django-admin startproject config .
python manage.py startapp iam
python manage.py startapp ingestion
python manage.py startapp analysis
python manage.py startapp results
python manage.py startapp sysmgmt

# 4) Crear archivo config/celery.py y configurar settings/urls
# 5) migrate, createsuperuser y runserver
```

---

## 12) Definition of Done (MVP)

- Endpoints: /auth/sign-up, /auth/sign-in, /images/upload, /results/{imageId}, /reports (+ descarga), /system/*.
- Persistencia: users/roles, images/image_data, analysis_results, reports.
- Celery integrado con tarea analyze_image.
- Seguridad por roles y filtro de owner.
- README con pasos de ejecución local y variables de entorno.

---

## 13) Roadmap Post-MVP (rápido)

- Sustituir BLOB por storage externo (S3/MinIO) y URL firmadas.
- Cachear consultas de resultados (Redis) y throttling por usuario.
- Métricas con Prometheus/OpenTelemetry, dashboards.
- Cargas por lote y reportes incrementales.
- InferenceService real + gestión de modelos/versiones.

---

Con esta propuesta cerramos la arquitectura base enfocada en bounded contexts, datos y contratos. El siguiente paso es scaffolding del proyecto Django y generación de los módulos/puertos/implementaciones según este diseño.
