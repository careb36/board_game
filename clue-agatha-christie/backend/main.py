"""
FastAPI Backend para Misterio en la Mansión Blackwood
API REST + WebSocket para juego en tiempo real
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import jwt
import uuid
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar lógica del juego existente
import sys
sys.path.append('..')
from juego import Juego, Jugador, Carta, TipoCarta

# Configuración
SECRET_KEY = "tu-clave-secreta-muy-segura-cambiar-en-produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Instancia FastAPI
app = FastAPI(
    title="Misterio en la Mansión Blackwood API",
    description="API REST + WebSocket para el juego de mesa inspirado en Agatha Christie",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
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


# ==================== SCHEMAS ====================

class GameCreate(BaseModel):
    num_jugadores: int = Field(2, ge=2, le=6)
    nombre_anfitrion: str

class GameJoin(BaseModel):
    jugador_nombre: str
    token: Optional[str] = None

class PlayerMove(BaseModel):
    habitacion_destino: str

class Suggestion(BaseModel):
    sospechoso: str
    habitacion: str
    arma: str

class Accusation(BaseModel):
    sospechoso: str
    habitacion: str
    arma: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    player_id: str

class GameStatus(BaseModel):
    game_id: str
    estado: str
    turno_actual: int
    jugadores: List[Dict[str, Any]]
    habitaciones: List[str]
    historial: List[Dict[str, Any]]


# ==================== UTILIDADES ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
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
    return verify_token(credentials.credentials)


# ==================== ENDPOINTS REST ====================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/game/create", response_model=Dict[str, Any])
async def create_game(game_data: GameCreate):
    """Crear una nueva partida"""
    game_id = str(uuid.uuid4())
    
    # Crear instancia del juego
    juego = Juego()
    juego.num_jugadores = game_data.num_jugadores
    
    # Guardar en memoria
    games[game_id] = juego
    connection_manager[game_id] = []
    
    logger.info(f"Juego creado: {game_id} con {game_data.num_jugadores} jugadores")
    
    return {
        "game_id": game_id,
        "message": "Juego creado exitosamente",
        "num_jugadores": game_data.num_jugadores,
        "anfitrion": game_data.nombre_anfitrion
    }

@app.get("/api/game/{game_id}", response_model=GameStatus)
async def get_game_status(game_id: str):
    """Obtener estado actual del juego"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    juego = games[game_id]
    
    return GameStatus(
        game_id=game_id,
        estado="en_curso",
        turno_actual=juego.turno_actual if hasattr(juego, 'turno_actual') else 0,
        jugadores=[{"nombre": j.nombre, "id": j.id} for j in juego.jugadores] if hasattr(juego, 'jugadores') else [],
        habitaciones=juego.habitaciones if hasattr(juego, 'habitaciones') else [],
        historial=juego.historial if hasattr(juego, 'historial') else []
    )

@app.post("/api/game/{game_id}/join")
async def join_game(game_id: str, join_data: GameJoin):
    """Unirse a una partida existente"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    juego = games[game_id]
    
    # Crear jugador
    player_id = str(uuid.uuid4())
    
    # Generar token JWT
    token = create_access_token(
        data={"sub": player_id, "game_id": game_id, "nombre": join_data.jugador_nombre},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    player_tokens[token] = player_id
    
    logger.info(f"Jugador {join_data.jugador_nombre} se unió al juego {game_id}")
    
    return {
        "player_id": player_id,
        "token": token,
        "game_id": game_id,
        "message": f"Bienvenido {join_data.jugador_nombre}"
    }

@app.post("/api/game/{game_id}/move")
async def move_player(
    game_id: str,
    move_data: PlayerMove,
    current_player: dict = Depends(get_current_player)
):
    """Mover jugador a una habitación"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    # Validar movimiento en backend
    juego = games[game_id]
    
    # TODO: Implementar lógica real de movimiento
    return {
        "success": True,
        "message": f"Jugador movido a {move_data.habitacion_destino}",
        "habitacion": move_data.habitacion_destino
    }

@app.post("/api/game/{game_id}/suggest")
async def make_suggestion(
    game_id: str,
    suggestion: Suggestion,
    current_player: dict = Depends(get_current_player)
):
    """Hacer una sugerencia"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    # TODO: Implementar lógica de sugerencia
    return {
        "success": True,
        "suggestion": suggestion.dict(),
        "message": "Sugerencia realizada"
    }

@app.post("/api/game/{game_id}/accuse")
async def make_accusation(
    game_id: str,
    accusation: Accusation,
    current_player: dict = Depends(get_current_player)
):
    """Hacer acusación final"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    # TODO: Implementar lógica de acusación
    return {
        "success": True,
        "accusation": accusation.dict(),
        "message": "Acusación realizada"
    }

@app.get("/api/game/{game_id}/history")
async def get_game_history(game_id: str):
    """Obtener historial de acciones del juego"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    juego = games[game_id]
    historial = juego.historial if hasattr(juego, 'historial') else []
    
    return {"game_id": game_id, "historial": historial}


# ==================== WEBSOCKET ====================

@app.websocket("/ws/game/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    """WebSocket para comunicación en tiempo real"""
    await websocket.accept()
    
    if game_id not in connection_manager:
        await websocket.close(code=4004, reason="Juego no encontrado")
        return
    
    # Agregar conexión
    connection_manager[game_id].append(websocket)
    logger.info(f"Player {player_id} connected to game {game_id}")
    
    try:
        # Enviar estado inicial
        initial_state = {
            "type": "init",
            "player_id": player_id,
            "game_id": game_id
        }
        await websocket.send_json(initial_state)
        
        # Escuchar mensajes
        while True:
            data = await websocket.receive_json()
            
            # Broadcast a todos los jugadores
            await broadcast_to_game(game_id, {
                "type": "action",
                "player_id": player_id,
                "data": data
            })
            
    except WebSocketDisconnect:
        connection_manager[game_id].remove(websocket)
        logger.info(f"Player {player_id} disconnected from game {game_id}")
        
        # Notificar a otros jugadores
        await broadcast_to_game(game_id, {
            "type": "player_left",
            "player_id": player_id
        })

async def broadcast_to_game(game_id: str, message: dict):
    """Enviar mensaje a todos los jugadores de una partida"""
    if game_id not in connection_manager:
        return
    
    disconnected = []
    for connection in connection_manager[game_id]:
        try:
            await connection.send_json(message)
        except Exception:
            disconnected.append(connection)
    
    # Limpiar conexiones cerradas
    for conn in disconnected:
        connection_manager[game_id].remove(conn)


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
