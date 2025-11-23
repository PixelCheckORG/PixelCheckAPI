# Plantilla de Arquitectura DDD/CQRS para nuevos servicios Spring Boot

Usa este esquema como guía base para cualquier backend nuevo. Completa cada seccion con la informacion de tu dominio y manten consistencia entre bounded contexts (BC), capas y contratos.

## 1. Vision general
- Dominio dividido en bounded contexts independientes (ej. `iam`, `billing`, `catalog`, etc.).
- Cada BC expone API propia y se comunica con otros via ACL (Anti-Corruption Layer) o mensajeria.
- Capas por BC: `interfaces` (entradas REST/ACL), `application` (casos de uso/handlers), `domain` (modelo y puertos), `infrastructure` (adaptadores tecnicos), `shared` (cross-cutting).
- CQRS: comandos y queries separados; cada caso de uso se modela como handler que recibe un `Command` o `Query` record.

## 2. Estructura de paquetes
```
src/main/java/<basepackage>/
  shared/
    domain/model/aggregates|entities|valueobjects
    infrastructure/... (configuracion comun, naming strategy, auditoria)
  <boundedcontext>/
    domain/
      model/aggregates|entities|valueobjects
      model/commands|queries (records)
      services (puertos: *CommandService, *QueryService)
      exceptions (opcional)
    application/
      commandservices|queryservices (implementaciones de puertos)
      acl (adaptadores hacia otros BC)
      eventhandlers (seeders/listeners)
    infrastructure/
      persistence/jpa/repositories
      authorization|tokens|hashing|messaging (segun necesidad)
    interfaces/
      rest/
        Controller.java
        resources/ (DTOs request/response en record)
        transform/ (assemblers recurso <-> comando/recurso <- entidad)
      acl/ (ContextFacade para exponer servicios a otros BC)
```

## 3. Contratos de dominio (CQRS)
- **Comandos**: acciones que modifican estado. Modelo: `public record CreateXCommand(...){}`.
- **Queries**: lectura sin side-effects. Modelo: `public record GetXByIdQuery(Long id){}`.
- **Puertos**: `XCommandService` y `XQueryService` definen `handle(Command|Query)`; la capa `application` implementa la logica y valida invariantes basicas.

## 4. Controladores y DTOs
- Controladores REST en `interfaces/rest` versionados (`/api/v1/...`), sin logica de dominio.
- DTOs de entrada/salida como `record` en `interfaces/rest/resources`.
- Ensambladores en `interfaces/rest/transform` convierten DTO -> comando y entidad -> DTO; no reusar entidades fuera del dominio.
- CORS y seguridad configurables por BC o globalmente (ver seccion Seguridad).

## 5. ACL (Anti-Corruption Layer) entre BC
- Cada BC que expone operaciones a otros define un `*ContextFacade` en `interfaces/acl`.
- Los BC consumidores usan adaptadores en `application/acl` (`ExternalXService`) para invocar el facade, evitando dependencias directas al dominio remoto.
- Asegura que los comandos/queries cruzando BC se traduzcan a tipos del BC destino; no compartas entidades.

## 6. Seguridad y autenticacion
- JWT recomendado: `TokenService` (puerto) y `TokenServiceImpl` (adaptador).
- Filtro de autorizacion (OncePerRequestFilter) que extrae y valida bearer tokens; setea el SecurityContext.
- Configuracion de `SecurityFilterChain`: stateless, CORS, CSRF off, rutas publicas (auth, docs) y resto protegido.
- Hashing de passwords (BCrypt) implementando un `HashingService` para inversion de dependencias.

## 7. Persistencia y configuracion
- Repositorios JPA por agregado en `infrastructure/persistence/jpa/repositories`.
- Naming strategy y auditoria en `shared/infrastructure` + `@EnableJpaAuditing` en la clase `Application`.
- `application.properties` con: datasource, `spring.jpa.hibernate.ddl-auto`, `jwt.secret`, `jwt.expiration`, CORS.
- Considera migraciones (Flyway/Liquibase) si el proyecto lo requiere.

## 8. Observabilidad y docs
- OpenAPI con `springdoc-openapi` y una configuracion base (`OpenApiConfig`).
- Logging coherente por BC; captura de errores en filtros/handlers globales.

## 9. Checklist para arrancar un BC nuevo
1) Crear paquetes base del BC siguiendo la estructura anterior.
2) Modelar agregados/VOs y comandos/queries iniciales.
3) Definir puertos `CommandService`/`QueryService`; implementar en `application`.
4) Crear repositorios JPA y wiring de infraestructura necesario (tokens, hashing, messaging).
5) Exponer endpoints REST con DTOs y ensambladores.
6) Añadir `ContextFacade` si se compartira funcionalidad con otros BC.
7) Configurar seguridad (whitelist de rutas de autenticacion y docs).
8) Documentar endpoints en OpenAPI y ajustar CORS/domains permitidos.
9) Agregar pruebas unitarias y de web layer (mockmvc) para handlers y controllers.

## 10. Extensiones opcionales
- Mensajeria/eventos de dominio: publicar eventos desde `AggregateRoot` y manejar en `application`.
- Multi-tenant o multi-DB: encapsular en `shared/infrastructure` la seleccion de datasource y resolver en los repositorios.
- Versionado de API: planificar `/api/v1`, `/api/v2` y deprecacion de endpoints.
