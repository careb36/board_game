"""
FastAPI Backend para Misterio en la Mansión Blackwood
API REST + WebSocket para juego en tiempo real
Arquitectura Enterprise Senior-Level
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import jwt
import uuid
import logging
import json
from enum import Enum
import asyncio

# Configuración de logging mejorada
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Importar lógica del juego existente
import sys
sys.path.append('..')
from src.juego import Juego, Acusacion
from src.tablero import HabitacionNombre
from src.cartas import TipoCarta

# Configuración Security
SECRET_KEY = "tu-clave-secreta-muy-segura-cambiar-en-produccion-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
RATE_LIMIT_ACTIONS = 10  # acciones por minuto por jugador

# Almacenamiento en memoria con rate limiting (en producción usar Redis/DB)
games: Dict[str, Juego] = {}
player_tokens: Dict[str, str] = {}  # token -> player_id
player_games: Dict[str, str] = {}  # player_id -> game_id
connection_manager: Dict[str, List[WebSocket]] = {}  # game_id -> websockets
rate_limit_tracker: Dict[str, List[datetime]] = {}  # player_id -> timestamps

# Lifespan manager para cleanup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Iniciando servidor Mystery Mansion API...")
    yield
    # Shutdown
    logger.info("🛑 Cerrando servidor...")
    # Limpiar conexiones WebSocket
    for game_id in list(connection_manager.keys()):
        for ws in connection_manager[game_id]:
            try:
                await ws.close()
            except:
                pass
    connection_manager.clear()
    games.clear()
    player_tokens.clear()

app = FastAPI(
    title="Misterio en la Mansión Blackwood API",
    description="API REST + WebSocket para el juego de mesa inspirado en Agatha Christie",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS - Permitir frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seguridad
security = HTTPBearer()

# Almacenamiento en memoria (en producción usar Redis/DB)
games: Dict[str, Juego] = {}
player_tokens: Dict[str, str] = {}  # token -> player_id
connection_manager: Dict[str, List[WebSocket]] = {}  # game_id -> websockets


# ==================== SCHEMAS MEJORADOS ====================

class GameCreate(BaseModel):
    num_jugadores: int = Field(2, ge=2, le=6)
    nombre_anfitrion: str = Field(..., min_length=1, max_length=50)
    
    @validator('nombre_anfitrion')
    def validate_nombre(cls, v):
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()

class GameJoin(BaseModel):
    jugador_nombre: str = Field(..., min_length=1, max_length=50)
    token: Optional[str] = None
    
    @validator('jugador_nombre')
    def validate_nombre(cls, v):
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()

class PlayerMove(BaseModel):
    habitacion_destino: str
    
    @validator('habitacion_destino')
    def validate_habitacion(cls, v):
        valid_habs = [h.value for h in HabitacionNombre]
        if v not in valid_habs:
            raise ValueError(f'Habitación inválida. Válidas: {valid_habs}')
        return v

class Suggestion(BaseModel):
    sospechoso: str
    habitacion: str
    arma: str
    
    @validator('sospechoso', 'habitacion', 'arma')
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('El campo no puede estar vacío')
        return v.strip()

class Accusation(BaseModel):
    sospechoso: str
    habitacion: str
    arma: str
    
    @validator('sospechoso', 'habitacion', 'arma')
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('El campo no puede estar vacío')
        return v.strip()

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    player_id: str
    game_id: str
    expires_in: int

class GameStatus(BaseModel):
    game_id: str
    estado: Literal["esperando", "en_curso", "finalizado"]
    turno_actual: int
    jugadores: List[Dict[str, Any]]
    habitaciones: List[str]
    historial: List[Dict[str, Any]]
    carta_crimen_resumen: Optional[Dict[str, str]] = None

class ActionResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None


# ==================== UTILIDADES MEJORADAS ====================

def check_rate_limit(player_id: str) -> bool:
    """Verifica rate limiting para prevenir abuso"""
    now = datetime.utcnow()
    one_minute_ago = now - timedelta(minutes=1)
    
    if player_id not in rate_limit_tracker:
        rate_limit_tracker[player_id] = []
    
    # Limpiar timestamps antiguos
    rate_limit_tracker[player_id] = [
        ts for ts in rate_limit_tracker[player_id] 
        if ts > one_minute_ago
    ]
    
    # Verificar límite
    if len(rate_limit_tracker[player_id]) >= RATE_LIMIT_ACTIONS:
        return False
    
    # Agregar timestamp actual
    rate_limit_tracker[player_id].append(now)
    return True

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

async def get_current_player(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    token = credentials.credentials
    payload = verify_token(token)
    
    # Verificar que el jugador existe
    if payload.get("sub") not in player_tokens.values():
        raise HTTPException(status_code=401, detail="Jugador no encontrado")
    
    return payload


# ==================== ENDPOINTS REST ====================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "games_active": len(games),
        "players_connected": len(player_tokens)
    }

@app.post("/api/game/create", response_model=Dict[str, Any])
async def create_game(game_data: GameCreate):
    """Crear una nueva partida"""
    try:
        game_id = str(uuid.uuid4())
        
        # Crear instancia del juego
        juego = Juego()
        juego.num_jugadores = game_data.num_jugadores
        
        # Guardar en memoria
        games[game_id] = juego
        connection_manager[game_id] = []
        
        logger.info(f"🎮 Juego creado: {game_id} con {game_data.num_jugadores} jugadores")
        
        return {
            "game_id": game_id,
            "message": "Juego creado exitosamente",
            "num_jugadores": game_data.num_jugadores,
            "anfitrion": game_data.nombre_anfitrion,
            "estado": "esperando"
        }
    except Exception as e:
        logger.error(f"Error creando juego: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/api/game/{game_id}", response_model=GameStatus)
async def get_game_status(game_id: str):
    """Obtener estado actual del juego"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    juego = games[game_id]
    
    # Obtener resumen del crimen (solo si el juego terminó)
    carta_crimen_resumen = None
    if hasattr(juego, 'ganador') and juego.ganador:
        carta_crimen_resumen = {
            "sospechoso": juego.carta_crimen[TipoCarta.SOSPECHOSO].nombre,
            "habitacion": juego.carta_crimen[TipoCarta.HABITACION].nombre,
            "arma": juego.carta_crimen[TipoCarta.ARMA].nombre
        }
    
    return GameStatus(
        game_id=game_id,
        estado="finalizado" if hasattr(juego, 'ganador') and juego.ganador else "en_curso" if juego.juego_iniciado else "esperando",
        turno_actual=juego.gestor_jugadores.turno_actual if hasattr(juego, 'gestor_jugadores') else 0,
        jugadores=[
            {
                "nombre": j.nombre, 
                "id": j.id,
                "habitacion": j.habitacion_actual.value if j.habitacion_actual else None,
                "cartas": len(j.cartas),
                "es_ia": j.es_ia
            } 
            for j in juego.gestor_jugadores.get_todos_los_jugadores()
        ] if hasattr(juego, 'gestor_jugadores') else [],
        habitaciones=[h.value for h in juego.tablero.get_todas_las_habitaciones()] if hasattr(juego, 'tablero') else [],
        historial=juego.historial[-20:] if hasattr(juego, 'historial') else [],
        carta_crimen_resumen=carta_crimen_resumen
    )

@app.post("/api/game/{game_id}/join", response_model=TokenResponse)
async def join_game(game_id: str, join_data: GameJoin):
    """Unirse a una partida existente"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    juego = games[game_id]
    
    # Verificar que haya espacio
    if hasattr(juego, 'gestor_jugadores'):
        jugadores_actuales = len(juego.gestor_jugadores.get_todos_los_jugadores())
        if jugadores_actuales >= juego.num_jugadores:
            raise HTTPException(status_code=400, detail="Juego lleno")
    
    # Crear jugador
    player_id = str(uuid.uuid4())
    
    # Generar token JWT
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": player_id, "game_id": game_id, "nombre": join_data.jugador_nombre},
        expires_delta=expires_delta
    )
    
    player_tokens[token] = player_id
    player_games[player_id] = game_id
    
    logger.info(f"👤 Jugador {join_data.jugador_nombre} se unió al juego {game_id}")
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        player_id=player_id,
        game_id=game_id,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@app.post("/api/game/{game_id}/move", response_model=ActionResponse)
async def move_player(
    game_id: str,
    move_data: PlayerMove,
    current_player: dict = Depends(get_current_player)
):
    """Mover jugador a una habitación"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    player_id = current_player.get("sub")
    
    # Rate limiting
    if not check_rate_limit(player_id):
        raise HTTPException(status_code=429, detail="Demasiadas acciones. Espere un momento.")
    
    juego = games[game_id]
    
    # Validar que el juego esté iniciado
    if not juego.juego_iniciado:
        return ActionResponse(
            success=False,
            message="El juego aún no ha iniciado",
            error_code="GAME_NOT_STARTED"
        )
    
    # Obtener jugador actual
    jugadores = juego.gestor_jugadores.get_todos_los_jugadores()
    jugador_actual = None
    for j in jugadores:
        if j.nombre == current_player.get("nombre"):
            jugador_actual = j
            break
    
    if not jugador_actual:
        raise HTTPException(status_code=404, detail="Jugador no encontrado en el juego")
    
    # Validar turno
    if jugadores[juego.gestor_jugadores.turno_actual % len(jugadores)] != jugador_actual:
        return ActionResponse(
            success=False,
            message="No es tu turno",
            error_code="NOT_YOUR_TURN"
        )
    
    # Convertir nombre de habitación a enum
    try:
        destino_enum = HabitacionNombre(move_data.habitacion_destino)
    except ValueError:
        return ActionResponse(
            success=False,
            message=f"Habitación inválida: {move_data.habitacion_destino}",
            error_code="INVALID_ROOM"
        )
    
    # Ejecutar movimiento
    exito = juego.mover_jugador(jugador_actual, destino_enum)
    
    if exito:
        # Notificar por WebSocket
        await broadcast_to_game(game_id, {
            "type": "player_moved",
            "player_id": player_id,
            "player_name": jugador_actual.nombre,
            "habitacion": move_data.habitacion_destino,
            "turno_siguiente": juego.gestor_jugadores.jugador_actual().nombre if juego.gestor_jugadores.jugador_actual() else None
        })
        
        return ActionResponse(
            success=True,
            message=f"Jugador movido a {move_data.habitacion_destino}",
            data={"habitacion": move_data.habitacion_destino}
        )
    else:
        return ActionResponse(
            success=False,
            message="Movimiento inválido (la habitación no es adyacente)",
            error_code="INVALID_MOVE"
        )

@app.post("/api/game/{game_id}/suggest", response_model=ActionResponse)
async def make_suggestion(
    game_id: str,
    suggestion: Suggestion,
    current_player: dict = Depends(get_current_player)
):
    """Hacer una sugerencia"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    player_id = current_player.get("sub")
    
    # Rate limiting
    if not check_rate_limit(player_id):
        raise HTTPException(status_code=429, detail="Demasiadas acciones. Espere un momento.")
    
    juego = games[game_id]
    
    # Validar que el juego esté iniciado
    if not juego.juego_iniciado:
        return ActionResponse(
            success=False,
            message="El juego aún no ha iniciado",
            error_code="GAME_NOT_STARTED"
        )
    
    # Obtener jugador actual
    jugadores = juego.gestor_jugadores.get_todos_los_jugadores()
    jugador_actual = None
    for j in jugadores:
        if j.nombre == current_player.get("nombre"):
            jugador_actual = j
            break
    
    if not jugador_actual:
        raise HTTPException(status_code=404, detail="Jugador no encontrado en el juego")
    
    # Validar turno
    if jugadores[juego.gestor_jugadores.turno_actual % len(jugadores)] != jugador_actual:
        return ActionResponse(
            success=False,
            message="No es tu turno",
            error_code="NOT_YOUR_TURN"
        )
    
    # Ejecutar sugerencia
    exito, carta_revelada = juego.hacer_acusacion(
        jugador_actual,
        suggestion.sospechoso,
        suggestion.habitacion,
        suggestion.arma
    )
    
    # Notificar por WebSocket
    await broadcast_to_game(game_id, {
        "type": "suggestion_made",
        "player_id": player_id,
        "player_name": jugador_actual.nombre,
        "suggestion": suggestion.dict(),
        "carta_revelada": carta_revelada
    })
    
    return ActionResponse(
        success=exito,
        message="Sugerencia realizada" if exito else "Sugerencia inválida",
        data={
            "suggestion": suggestion.dict(),
            "carta_revelada": carta_revelada
        }
    )

@app.post("/api/game/{game_id}/accuse", response_model=ActionResponse)
async def make_accusation(
    game_id: str,
    accusation: Accusation,
    current_player: dict = Depends(get_current_player)
):
    """Hacer acusación final"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    player_id = current_player.get("sub")
    
    # Rate limiting
    if not check_rate_limit(player_id):
        raise HTTPException(status_code=429, detail="Demasiadas acciones. Espere un momento.")
    
    juego = games[game_id]
    
    # Validar que el juego esté iniciado
    if not juego.juego_iniciado:
        return ActionResponse(
            success=False,
            message="El juego aún no ha iniciado",
            error_code="GAME_NOT_STARTED"
        )
    
    # Obtener jugador actual
    jugadores = juego.gestor_jugadores.get_todos_los_jugadores()
    jugador_actual = None
    for j in jugadores:
        if j.nombre == current_player.get("nombre"):
            jugador_actual = j
            break
    
    if not jugador_actual:
        raise HTTPException(status_code=404, detail="Jugador no encontrado en el juego")
    
    # Ejecutar acusación final
    acusacion_obj = Acusacion(acusation.sospechoso, acusation.habitacion, acusation.arma)
    es_correcto = juego.acusacion_final(jugador_actual, acusacion_obj)
    
    # Determinar mensaje
    if es_correcto:
        mensaje = f"¡{jugador_actual.nombre} GANA! El crimen fue cometido por {acusation.sospechoso} en {acusation.habitacion} con {acusation.arma}"
        tipo_evento = "game_won"
    else:
        mensaje = f"{jugador_actual.nombre} se equivocó y queda eliminado"
        tipo_evento = "accusation_failed"
    
    # Notificar por WebSocket
    await broadcast_to_game(game_id, {
        "type": tipo_evento,
        "player_id": player_id,
        "player_name": jugador_actual.nombre,
        "accusation": accusation.dict(),
        "correcto": es_correcto,
        "ganador": jugador_actual.nombre if es_correcto else None
    })
    
    return ActionResponse(
        success=es_correcto,
        message=mensaje,
        data={
            "accusation": accusation.dict(),
            "correcto": es_correcto,
            "juego_finalizado": es_correcto
        }
    )

@app.get("/api/game/{game_id}/history")
async def get_game_history(game_id: str):
    """Obtener historial de acciones del juego"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    juego = games[game_id]
    historial = juego.historial if hasattr(juego, 'historial') else []
    
    return {"game_id": game_id, "historial": historial}


# ==================== WEBSOCKET MEJORADO ====================

@app.websocket("/ws/game/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    """WebSocket para comunicación en tiempo real"""
    await websocket.accept()
    
    if game_id not in connection_manager:
        await websocket.close(code=4004, reason="Juego no encontrado")
        return
    
    # Verificar autenticación (opcional)
    if player_id not in [v for v in player_tokens.values()]:
        await websocket.close(code=4003, reason="No autorizado")
        return
    
    # Agregar conexión
    connection_manager[game_id].append(websocket)
    logger.info(f"🔌 Player {player_id} connected to game {game_id}")
    
    try:
        # Enviar estado inicial completo
        juego = games[game_id]
        initial_state = {
            "type": "init",
            "player_id": player_id,
            "game_id": game_id,
            "estado": "en_curso" if juego.juego_iniciado else "esperando",
            "turno_actual": juego.gestor_jugadores.turno_actual if hasattr(juego, 'gestor_jugadores') else 0,
            "mensaje": "Conexión exitosa. ¡Que comience el misterio!"
        }
        await websocket.send_json(initial_state)
        
        # Broadcast de nuevo jugador
        await broadcast_to_game(game_id, {
            "type": "player_connected",
            "player_id": player_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Escuchar mensajes del cliente
        while True:
            data = await websocket.receive_json()
            logger.info(f"📩 Message from {player_id}: {data.get('type', 'unknown')}")
            
            # Procesar según tipo de mensaje
            action_type = data.get("type")
            
            if action_type == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})
            
            # Los demás eventos se manejan vía REST API
            
    except WebSocketDisconnect:
        connection_manager[game_id].remove(websocket)
        logger.info(f"🔌 Player {player_id} disconnected from game {game_id}")
        
        # Notificar a otros jugadores
        await broadcast_to_game(game_id, {
            "type": "player_disconnected",
            "player_id": player_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        connection_manager[game_id].remove(websocket)

async def broadcast_to_game(game_id: str, message: dict):
    """Enviar mensaje a todos los jugadores de una partida"""
    if game_id not in connection_manager:
        return
    
    message["timestamp"] = datetime.utcnow().isoformat()
    
    disconnected = []
    for connection in connection_manager[game_id]:
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.warning(f"Failed to send to connection: {e}")
            disconnected.append(connection)
    
    # Limpiar conexiones cerradas
    for conn in disconnected:
        try:
            connection_manager[game_id].remove(conn)
        except ValueError:
            pass


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    logger.info("🎭 Iniciando Mystery Mansion Blackwood API Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
