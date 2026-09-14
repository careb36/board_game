# 📋 Backlog del Proyecto - Misterio en la Mansión Blackwood

## 🚨 ÉPICA 1: API Backend (FastAPI + WebSocket)
### Issue #1: Configurar FastAPI con estructura de proyecto
- [ ] Crear estructura `backend/` con routers, models, schemas
- [ ] Configurar CORS para frontend
- [ ] Implementar health check endpoint
- [ ] Setup de logging estructurado

### Issue #2: Implementar endpoints REST del juego
- [ ] POST `/api/game/create` - Crear nueva partida
- [ ] GET `/api/game/{game_id}` - Obtener estado del juego
- [ ] POST `/api/game/{game_id}/join` - Unir jugador
- [ ] POST `/api/game/{game_id}/move` - Mover jugador a habitación
- [ ] POST `/api/game/{game_id}/suggest` - Hacer sugerencia
- [ ] POST `/api/game/{game_id}/accuse` - Hacer acusación final
- [ ] GET `/api/game/{game_id}/history` - Historial de acciones

### Issue #3: Implementar WebSocket para tiempo real
- [ ] Configurar WebSocket endpoint `/ws/game/{game_id}`
- [ ] Broadcast de eventos a todos los jugadores
- [ ] Manejo de reconexiones
- [ ] Sistema de rooms por partida

### Issue #4: Seguridad y validaciones
- [ ] Implementar JWT tokens por jugador
- [ ] Rate limiting en endpoints críticos
- [ ] Validación de todas las acciones en backend
- [ ] Sanitización de inputs

---

## 🎨 ÉPICA 2: Frontend Completo (React + Vite)
### Issue #5: Reemplazar template Vite con App real del juego
- [ ] Eliminar template por defecto de Vite
- [ ] Crear estructura de componentes (`components/`, `pages/`, `hooks/`)
- [ ] Configurar React Router para navegación
- [ ] Implementar contexto global del juego (GameContext)

### Issue #6: Componente Tablero Interactivo
- [ ] Grid 3x3 con las 9 habitaciones
- [ ] Conexiones visuales entre habitaciones adyacentes
- [ ] Animaciones de movimiento de fichas
- [ ] Highlight de habitación actual
- [ ] Tooltip con información de cada habitación

### Issue #7: Sistema de Cartas Coleccionables
- [ ] Componente Card con flip animation (Framer Motion)
- [ ] Mazos separados: Sospechosos, Habitaciones, Armas
- [ ] Vista de cartas propias del jugador
- [ ] Efecto de revelado al refutar sugerencias

### Issue #8: Panel de Jugadores y Turnos
- [ ] Lista de jugadores con avatares y colores
- [ ] Indicador visual de turno actual
- [ ] Estado de cada jugador (vivo, eliminado, ganador)
- [ ] Contador de cartas restantes por descubrir

### Issue #9: Sistema de Notas y Deducciones
- [ ] Grid de deducciones interactivo (Sospechoso x Habitación x Arma)
- [ ] Marcadores: ✅ (tiene), ❌ (no tiene), ❓ (desconocido)
- [ ] Guardado automático en localStorage
- [ ] Exportar/importar notas

### Issue #10: Modales de Sugerencia y Acusación
- [ ] Modal de sugerencia con selectores de cartas
- [ ] Validación visual antes de enviar
- [ ] Modal de acusación final con confirmación
- [ ] Animación de resultado (ganó/perdió)

### Issue #11: Efectos Visuales Avanzados
- [ ] Partículas animadas en eventos clave
- [ ] Transiciones entre pantallas
- [ ] Efecto de "sobre cerrado" para solución
- [ ] Confetti al ganar
- [ ] Efectos de sonido (opcional con Howler.js)

### Issue #12: Responsive Design y Accesibilidad
- [ ] Mobile-first design
- [ ] Soporte para tablets
- [ ] Navegación por teclado
- [ ] ARIA labels en todos los componentes
- [ ] Contraste de colores WCAG AA

---

## 🧪 ÉPICA 3: Testing Exhaustivo
### Issue #13: Tests de Integración API
- [ ] Configurar pytest-asyncio para tests asíncronos
- [ ] Tests de todos los endpoints REST
- [ ] Tests de conexiones WebSocket
- [ ] Mock de jugadores para tests automatizados

### Issue #14: Tests E2E con Playwright
- [ ] Configurar Playwright en el proyecto
- [ ] Test de flujo completo de partida
- [ ] Tests de múltiples jugadores simultáneos
- [ ] Screenshots automáticos en fallos

### Issue #15: Visual Regression Tests
- [ ] Configurar Percy o Chromatic
- [ ] Capturar estados clave de la UI
- [ ] Integrar con GitHub Actions

### Issue #16: Performance Testing
- [ ] Configurar Lighthouse CI
- [ ] Meta: Score >95 en todas las categorías
- [ ] Optimizar bundle size (<200KB gzipped)
- [ ] Lazy loading de componentes

---

## 📦 ÉPICA 4: DevOps y CI/CD
### Issue #17: Dockerización Completa
- [ ] Dockerfile multi-stage para backend (Python)
- [ ] Dockerfile multi-stage para frontend (Node)
- [ ] docker-compose.yml con servicios: backend, frontend, nginx
- [ ] Variables de entorno configurables

### Issue #18: GitHub Actions Pipeline
- [ ] Workflow para tests en cada push
- [ ] Workflow para build y lint
- [ ] Workflow para deploy automático a staging
- [ ] Badge de estado en README

### Issue #19: Deploy a Producción
- [ ] Configurar Railway o Render para backend
- [ ] Configurar Vercel o Netlify para frontend
- [ ] Dominio personalizado (opcional)
- [ ] SSL automático

---

## 📚 ÉPICA 5: Documentación y Onboarding
### Issue #20: Documentación para Desarrolladores
- [ ] README técnico con arquitectura
- [ ] Diagrama de secuencia de flujos principales
- [ ] Guía de contribución (CONTRIBUTING.md)
- [ ] API documentation con Swagger/OpenAPI

### Issue #21: Documentación para Usuarios
- [ ] Guía de cómo jugar
- [ ] Tutorial interactivo en el juego
- [ ] FAQ de preguntas frecuentes
- [ ] Video demo (opcional)

---

## 🎯 PRIORIDAD DE IMPLEMENTACIÓN

| Prioridad | Épica | Issues | Sprint |
|-----------|-------|--------|--------|
| 🔴 CRÍTICA | ÉPICA 1 | #1, #2, #3, #4 | Sprint 1 |
| 🔴 CRÍTICA | ÉPICA 2 | #5, #6, #7, #8 | Sprint 1-2 |
| 🟠 ALTA | ÉPICA 2 | #9, #10, #11, #12 | Sprint 2-3 |
| 🟡 MEDIA | ÉPICA 3 | #13, #14, #15, #16 | Sprint 3-4 |
| 🟢 BAJA | ÉPICA 4 | #17, #18, #19 | Sprint 4-5 |
| ⚪ OPCIONAL | ÉPICA 5 | #20, #21 | Sprint 5 |

---

## 📊 MÉTRICAS DE ÉXITO

- [ ] 100% de cobertura de tests en backend
- [ ] 80% de cobertura de tests en frontend
- [ ] Lighthouse score >95
- [ ] Tiempo de carga inicial <2s
- [ ] Soporte para 6 jugadores simultáneos sin lag
- [ ] 0 vulnerabilidades críticas en security scan

---

*Última actualización: $(date +%Y-%m-%d)*
*Autor: Super Ultra Senior Tech Lead*
