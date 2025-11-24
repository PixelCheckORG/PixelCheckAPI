# PixelCheck API — Arquitectura (DDD + Clean) para Django/DRF

Esta guía resume cómo está estructurado el backend de PixelCheck siguiendo DDD + Clean Architecture, adaptando la plantilla usada en proyectos Spring Boot a este stack (Django 5, DRF, Celery, MySQL, Redis).

## 1. Visión general
- Bounded Contexts: `iam`, `ingestion`, `analysis`, `results`, `sysmgmt`.
- Capas por BC: `interface` (endpoints DRF/serializers), `application` (casos de uso), `domain` (modelo/políticas/puertos), `infrastructure` (ORM/adaptadores), `shared` (cross-cutting).
- Comunicación: llamadas síncronas (DRF) y asíncronas via Celery/Redis (`AnalysisRequested` implícito al subir imagen).
- Seguridad: JWT (SimpleJWT), permisos por rol (`ROLE_USER`, `ROLE_PROFESSIONAL`) y `is_staff` para auditoría.

## 2. Estructura de carpetas
```
PixelCheck/
  config/             # settings, urls, celery, exception handler
  shared/             # utils cross-cutting (VOs, permisos, reporting)
  iam/                # Identity & Access
    domain/           # entidades VO (RoleNameVO), repos (puertos)
    application/      # casos de uso (SignUp, SignIn)
    interface/        # serializers, views, urls
    infrastructure/   # repositorios Django ORM
  ingestion/          # Upload/validación de imágenes
    domain/ | application/ | interface/ | infrastructure/
  analysis/           # Orquestación de inferencia (stub) + tasks Celery
  results/            # Consultas y reportes PDF/CSV
  sysmgmt/            # Auditoría
  tests/              # Smoke/integración (APITestCase)
```

## 3. Contratos y casos de uso
- **IAM**: `RegisterUserUseCase`, `SignInUseCase` (JWT). Puertos: `UserRepository`.
- **Ingestion**: `UploadImageUseCase` valida tipo/tamaño/dimensiones/checksum y encola `run_analysis_task`.
- **Analysis**: `AnalyzeImageUseCase` (stub determinístico) guarda `AnalysisResult`.
- **Results**: `GetResultUseCase`, `CreateReportUseCase`, `GetReportFileUseCase`. Puertos: `ResultsQueryRepository`, `ReportRepository`.
- **SysMgmt**: `RecordAuditEventUseCase`, `ListAuditLogsUseCase`.
- Comandos/queries explícitos no se modelan como clases separadas; cada caso de uso recibe parámetros tipados desde serializers/adaptadores.

## 4. Endpoints (v1)
- Auth: `POST /api/v1/auth/sign-up`, `POST /api/v1/auth/sign-in`.
- Ingesta: `POST /api/v1/images/upload` (multipart).
- Resultados: `GET /api/v1/results/{imageId}`.
- Reportes: `POST /api/v1/reports` (ROLE_PROFESSIONAL o staff), `GET /api/v1/reports/{reportId}` (descarga binaria).
- Salud modelo: `GET /api/v1/analysis/health`.
- Auditoría: `POST /api/v1/system/audit`, `GET /api/v1/system/audit` (solo staff).
- Docs: `GET /api/docs/` (Swagger UI), `/api/schema/` (OpenAPI JSON), `/api/redoc/`.

## 5. DTOs y Serializers
- Entrada/salida definidos en `interface/serializers` de cada BC. Ejemplos:
  - IAM: `SignUpSerializer`, `SignInSerializer`, `SignInResponseSerializer`.
  - Ingestion: `UploadImageSerializer`, `UploadImageResponseSerializer`.
  - Results: `ImageResultSerializer`, `ReportRequestSerializer`, `ReportResponseSerializer`.
  - Analysis: `ModelHealthSerializer`.
  - SysMgmt: `AuditLogSerializer`, `AuditLogEntrySerializer`.

## 6. Persistencia
- MySQL 8 para runtime (tabla por agregado); separación de `image_data` (BLOB) y metadatos.
- SQLite automático para pruebas (`manage.py test`) gracias al flag en `config/settings.py`.

## 7. Seguridad
- JWT (SimpleJWT) como autenticación por defecto en DRF.
- Roles: VO `RoleNameVO` con `ROLE_USER` y `ROLE_PROFESSIONAL`; `is_staff` para funciones admin/auditoría.
- Permiso custom `IsProfessional` en `shared/application/permissions.py`.

## 8. Observabilidad y documentación
- OpenAPI via `drf-spectacular` configurado en `config/settings.py` y rutas en `config/urls.py`.
- Exception handler central en `config/exceptions.py`.
- Logs básicos via consola (Django/Celery).

## 9. Checklist para un nuevo BC (adaptado a Django)
1) Crear app Django y carpetas `domain/application/interface/infrastructure`.
2) Definir entidades/VOs y puertos en `domain`.
3) Implementar casos de uso en `application`.
4) Serializers y views DRF en `interface`; repos/adaptadores ORM en `infrastructure`.
5) Añadir URLs al router global (`config/api_urls.py`).
6) Exponer esquemas con `drf-spectacular` (`@extend_schema` en vistas).
7) Agregar pruebas APITestCase en `tests/`.
8) Documentar nuevas variables de entorno si aplica.
