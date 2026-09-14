# 🚀 GitHub Issues - Épicas Restantes

## ÉPICA 3: Testing Exhaustivo 🔴 CRÍTICA
- [ ] **#301 Configurar Pytest con Cobertura**
  - Instalar `pytest`, `pytest-cov`, `pytest-asyncio`.
  - Configurar `pytest.ini` y `.coveragerc`.
  - Meta: >90% cobertura en backend.
- [ ] **#302 Tests de Integración API (FastAPI)**
  - Usar `TestClient` de Starlette.
  - Probar flujos completos: Crear -> Unir -> Mover -> Sugerir -> Acusar.
  - Validar códigos de error y JWT.
- [ ] **#303 Tests E2E con Playwright**
  - Configurar Playwright para React.
  - Escenario: 2 jugadores completan una partida.
  - Validar actualizaciones en tiempo real vía WebSocket.
- [ ] **#304 Visual Regression Tests**
  - Configurar comparaciones de screenshots para componentes clave.

## ÉPICA 4: DevOps y CI/CD 🟠 ALTA
- [ ] **#401 Dockerización Multi-stage**
  - `Dockerfile.backend`: Python slim, solo prod deps.
  - `Dockerfile.frontend`: Node build + Nginx serve.
  - `docker-compose.yml`: Orquestación completa con redes.
- [ ] **#402 GitHub Actions CI Pipeline**
  - Workflow: Lint -> Test (Backend & Frontend) -> Build Docker.
  - Ejecutar en cada push/PR a `main`.
- [ ] **#403 Deploy Automático (CD)**
  - Push de imágenes a GHCR o Docker Hub.
  - Despliegue en Railway/Render/Vercel (configuración base).

## ÉPICA 5: Documentación Enterprise ⚪ MEDIA
- [ ] **#501 README Maestro**
  - Arquitectura del sistema (Diagrama Mermaid).
  - Guía de inicio rápido (Docker vs Local).
  - Variables de entorno explicadas.
- [ ] **#502 Docs de API y Contribución**
  - Link a Swagger/OpenAPI.
  - Guía de estilos de código y PRs.

---
*Generado automáticamente por el Agente Senior*
