import { useEffect, useState } from 'react'
import './App.css'
import ImmersiveRoomScene from './components/ImmersiveRoomScene'

const SUSPECTOS = [
  'Victoria Sterling',
  'Coronel Marcus Webb',
  'Isabella Rossi',
  'Arthur Pembroke',
  'Lady Catherine Moore',
  'Dr. Heinrich Wolf',
]

const ARMAS = [
  'Candelabro de bronce',
  'Daga ceremonial',
  'Veneno para ratas',
  'Cuerda de piano',
  'Pistola antigua',
  'Estatua de mármol',
]

const HABITACIONES = [
  'Biblioteca',
  'Salón Principal',
  'Comedor',
  'Cocina',
  'Invernadero',
  'Galería de Arte',
  'Estudio',
  'Dormitorio Principal',
  'Sótano',
]

const ROOM_ADJACENCY = {
  'Biblioteca': ['Invernadero', 'Estudio', 'Salón Principal', 'Comedor'],
  'Salón Principal': ['Biblioteca', 'Comedor', 'Galería de Arte'],
  'Comedor': ['Biblioteca', 'Salón Principal', 'Estudio', 'Dormitorio Principal', 'Cocina'],
  'Cocina': ['Comedor', 'Galería de Arte', 'Sótano'],
  'Invernadero': ['Biblioteca', 'Salón Principal'],
  'Galería de Arte': ['Salón Principal', 'Cocina'],
  'Estudio': ['Biblioteca', 'Comedor', 'Dormitorio Principal'],
  'Dormitorio Principal': ['Comedor', 'Estudio'],
  'Sótano': ['Cocina'],
}

const ROOM_LAYOUT = {
  'Invernadero': { left: '12%', top: '14%' },
  'Biblioteca': { left: '34%', top: '14%' },
  'Estudio': { left: '58%', top: '14%' },
  'Salón Principal': { left: '28%', top: '38%' },
  'Comedor': { left: '50%', top: '38%' },
  'Dormitorio Principal': { left: '72%', top: '38%' },
  'Galería de Arte': { left: '26%', top: '68%' },
  'Cocina': { left: '50%', top: '68%' },
  'Sótano': { left: '72%', top: '68%' },
}

const ROOM_SCENES = {
  'Biblioteca': 'scene-library',
  'Salón Principal': 'scene-salon',
  'Comedor': 'scene-dining',
  'Cocina': 'scene-kitchen',
  'Invernadero': 'scene-greenhouse',
  'Galería de Arte': 'scene-gallery',
  'Estudio': 'scene-study',
  'Dormitorio Principal': 'scene-bedroom',
  'Sótano': 'scene-basement',
}

const ROOM_DETAILS = {
  'Biblioteca': {
    title: 'Biblioteca',
    atmosphere: 'Silencio, polvo y secretos familiares en cada estante.',
    clue: 'Los volúmenes más antiguos revelan murmullos sobre una herencia oculta.',
    items: ['Estanterías altas', 'Mesa de lectura', 'Libro con páginas arrancadas'],
  },
  'Salón Principal': {
    title: 'Salón Principal',
    atmosphere: 'La elegancia victoriana reina en un salón de baile frío.',
    clue: 'Un candelabro aún humea y se siente una presencia reciente.',
    items: ['Candelabros', 'Piano de cola', 'Muebles de caoba'],
  },
  'Comedor': {
    title: 'Comedor',
    atmosphere: 'La mesa larga y la tensión de la cena aún permanecen en el aire.',
    clue: 'Hay un sitio marcado con una servilleta recién arrugada.',
    items: ['Mesa de roble', 'Sillas de terciopelo', 'Servilletero de plata'],
  },
  'Cocina': {
    title: 'Cocina',
    atmosphere: 'Huele a humo, especias y a algo que no termina de cocinarse.',
    clue: 'La bandeja del servicio está tibia, como si alguien hubiera salido corriendo.',
    items: ['Fogones', 'Bandeja de servicio', 'Armario de utensilios'],
  },
  'Invernadero': {
    title: 'Invernadero',
    atmosphere: 'La humedad y el perfume tropical empapan el aire.',
    clue: 'Un sendero de tierra recién removida atraviesa los macizos.',
    items: ['Palmeras', 'Jardineras', 'Puerta de cristal'],
  },
  'Galería de Arte': {
    title: 'Galería de Arte',
    atmosphere: 'Retratos severos observan cada paso como si fueran testigos.',
    clue: 'Una pintura está ligeramente desplazada sobre su pared.',
    items: ['Cuadros antiguos', 'Pilar de mármol', 'Escalera lateral'],
  },
  'Estudio': {
    title: 'Estudio',
    atmosphere: 'La intimidad de la oficina privada se siente casi claustrofóbica.',
    clue: 'Un documento importante está a medio ocultar detrás del escritorio.',
    items: ['Escritorio', 'Archivadores', 'Lámpara de lectura'],
  },
  'Dormitorio Principal': {
    title: 'Dormitorio Principal',
    atmosphere: 'La habitación acoge un silencio de sospecha y movimiento reciente.',
    clue: 'La cama está deshecha, como si alguien hubiera abandonado la escena deprisa.',
    items: ['Cama de cuatro columnas', 'Baúl', 'Ventana con cortinas'],
  },
  'Sótano': {
    title: 'Sótano',
    atmosphere: 'La oscuridad y el frío se sienten incluso antes de entrar.',
    clue: 'Hay marcas de pasos húmedos que se dirigen a la bodega.',
    items: ['Calderas', 'Bodega', 'Esquinas de piedra'],
  },
}

const API_BASE = '/api'

const randomFrom = (items) => items[Math.floor(Math.random() * items.length)]

const getPlayerNameForSession = (activeName, fallbackName) =>
  (activeName || fallbackName || 'Detective').trim() || 'Detective'

const getPlayerRoom = (game, playerName) => {
  if (!game?.jugadores?.length) return null
  const jugador = game.jugadores.find((item) => item.nombre === playerName)
  return jugador?.habitacion || null
}

const canMoveToRoom = (game, playerName, destination) => {
  const currentRoom = getPlayerRoom(game, playerName)
  if (!currentRoom || !destination) return false
  return (ROOM_ADJACENCY[currentRoom] || []).includes(destination)
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })

  const body = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(body.detail || body.message || 'La petición falló')
  }

  return body
}

function createLocalMachineGame(playerName) {
  const displayName = playerName.trim() || 'Detective'

  return {
    game_id: 'local-machine',
    estado: 'en_curso',
    turno_actual: 0,
    jugadores: [
      { nombre: displayName, es_ia: false, habitacion: 'Biblioteca' },
      { nombre: 'Holmes', es_ia: true, habitacion: 'Cocina' },
      { nombre: 'Marple', es_ia: true, habitacion: 'Galería de Arte' },
    ],
    habitaciones: HABITACIONES,
    historial: [
      `Partida local creada para ${displayName}.`,
      'El crimen está oculto en la mansión. Investiga y resuelve.',
    ],
    secret: {
      sospechoso: randomFrom(SUSPECTOS),
      habitacion: randomFrom(HABITACIONES),
      arma: randomFrom(ARMAS),
    },
    modo: 'machine',
  }
}

function App() {
  const [mode, setMode] = useState('machine')
  const [gameId, setGameId] = useState(localStorage.getItem('mansion-game-id') || '')
  const [hostName, setHostName] = useState('Detective')
  const [playerName, setPlayerName] = useState('')
  const [numPlayers, setNumPlayers] = useState(2)
  const [token, setToken] = useState(localStorage.getItem('mansion-token') || '')
  const [game, setGame] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [activeRoom, setActiveRoom] = useState('Biblioteca')
  const [useImmersive3D, setUseImmersive3D] = useState(true)
  const [suggestion, setSuggestion] = useState({
    sospechoso: SUSPECTOS[0],
    habitacion: HABITACIONES[0],
    arma: ARMAS[0],
  })

  useEffect(() => {
    if (gameId) {
      localStorage.setItem('mansion-game-id', gameId)
    } else {
      localStorage.removeItem('mansion-game-id')
    }
  }, [gameId])

  useEffect(() => {
    if (token) {
      localStorage.setItem('mansion-token', token)
    } else {
      localStorage.removeItem('mansion-token')
    }
  }, [token])

  useEffect(() => {
    if (!gameId || mode === 'machine') return

    let ignore = false

    const loadGame = async () => {
      try {
        const data = await fetchJson(`${API_BASE}/game/${gameId}`)
        if (!ignore) {
          setGame(data)
        }
      } catch (err) {
        if (!ignore) {
          setError(err.message)
        }
      }
    }

    loadGame()
    const interval = setInterval(loadGame, 2500)

    return () => {
      ignore = true
      clearInterval(interval)
    }
  }, [gameId, mode])

  const appendHistory = (entry) => {
    setGame((prev) => ({
      ...prev,
      historial: [...(prev?.historial || []), entry],
    }))
  }

  const currentPlayerName = getPlayerNameForSession(playerName, hostName)
  const currentRoomInGame = getPlayerRoom(game, currentPlayerName)

  useEffect(() => {
    if (currentRoomInGame) {
      setActiveRoom(currentRoomInGame)
    }
  }, [currentRoomInGame])

  const handleCreateGame = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    setMessage('')

    if (mode === 'machine') {
      const localPlayerName = (hostName || 'Detective').trim() || 'Detective'
      const localGame = createLocalMachineGame(localPlayerName)
      setGame(localGame)
      setGameId(localGame.game_id)
      setPlayerName(localPlayerName)
      setToken('local-machine-session')
      setMessage('Modo contra la máquina activado.')
      setLoading(false)
      return
    }

    try {
      const data = await fetchJson(`${API_BASE}/game/create`, {
        method: 'POST',
        body: JSON.stringify({
          nombre_anfitrion: hostName,
          num_jugadores: Number(numPlayers),
        }),
      })

      setGameId(data.game_id)
      setMessage(`Partida creada. Comparte este código: ${data.game_id}`)
      setPlayerName(hostName)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleJoinGame = async (event) => {
    event.preventDefault()

    if (mode === 'machine') {
      const localPlayerName = (playerName || hostName || 'Detective').trim() || 'Detective'
      const localGame = createLocalMachineGame(localPlayerName)
      setGame(localGame)
      setGameId(localGame.game_id)
      setToken('local-machine-session')
      setMessage(`¡Listo! ${localPlayerName} juega contra la máquina.`)
      return
    }

    if (!gameId || !playerName.trim()) {
      setError('Completa el nombre del jugador y la partida')
      return
    }

    setLoading(true)
    setError('')
    setMessage('')

    try {
      const data = await fetchJson(`${API_BASE}/game/${gameId}/join`, {
        method: 'POST',
        body: JSON.stringify({ jugador_nombre: playerName.trim() }),
      })

      setToken(data.access_token)
      setMessage(`Te uniste como ${playerName.trim()}`)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleMove = async (habitacion) => {
    const activeName = getPlayerNameForSession(playerName, hostName)

    if (mode === 'machine') {
      if (!game || !canMoveToRoom(game, activeName, habitacion)) {
        setError('Solo puedes moverte a una habitación adyacente.')
        return
      }

      setGame((prev) => ({
        ...prev,
        jugadores: prev.jugadores.map((jugador) =>
          jugador.nombre === activeName ? { ...jugador, habitacion } : jugador,
        ),
      }))
      appendHistory(`${activeName} se mueve a ${habitacion}.`)
      setMessage(`Te moviste a ${habitacion}.`)
      return
    }

    if (!gameId || !token) {
      setError('Primero únete a la partida')
      return
    }

    if (!game || !canMoveToRoom(game, activeName, habitacion)) {
      setError('Esa habitación no está conectada con tu posición actual.')
      return
    }

    try {
      const response = await fetchJson(`${API_BASE}/game/${gameId}/move`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ habitacion_destino: habitacion }),
      })

      setActiveRoom(habitacion)
      setMessage(response.message)
      const state = await fetchJson(`${API_BASE}/game/${gameId}`)
      setGame(state)
    } catch (err) {
      setError(err.message)
    }
  }

  const handleSuggestion = async () => {
    if (mode === 'machine') {
      const activeName = (playerName || hostName || 'Detective').trim() || 'Detective'
      const isCorrect =
        suggestion.sospechoso === game.secret.sospechoso &&
        suggestion.habitacion === game.secret.habitacion &&
        suggestion.arma === game.secret.arma

      appendHistory(`${activeName} sospecha: ${suggestion.sospechoso} en ${suggestion.habitacion} con ${suggestion.arma}.`)

      if (isCorrect) {
        setGame((prev) => ({
          ...prev,
          estado: 'finalizado',
          ganador: activeName,
          historial: [...(prev?.historial || []), `🏆 ¡${activeName} resuelve el caso!`],
        }))
        setMessage(`🏆 ¡${activeName} ganó!`)
      } else {
        const machineRefute = randomFrom(['Holmes', 'Marple', 'Poirot'])
        const machineCard = randomFrom(['Victoria Sterling', 'Biblioteca', 'Candelabro de bronce'])
        appendHistory(`${machineRefute} refuta con: ${machineCard}.`)
        setMessage('La máquina refuta la pista. Sigue investigando.')
      }
      return
    }

    if (!gameId || !token) {
      setError('Primero únete a la partida')
      return
    }

    try {
      const response = await fetchJson(`${API_BASE}/game/${gameId}/suggest`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          sospechoso: suggestion.sospechoso,
          habitacion: suggestion.habitacion,
          arma: suggestion.arma,
        }),
      })

      setMessage(response.message)
      const state = await fetchJson(`${API_BASE}/game/${gameId}`)
      setGame(state)
    } catch (err) {
      setError(err.message)
    }
  }

  const handleAccuse = async () => {
    if (mode === 'machine') {
      const activeName = (playerName || hostName || 'Detective').trim() || 'Detective'
      const isCorrect =
        suggestion.sospechoso === game.secret.sospechoso &&
        suggestion.habitacion === game.secret.habitacion &&
        suggestion.arma === game.secret.arma

      if (isCorrect) {
        setGame((prev) => ({
          ...prev,
          estado: 'finalizado',
          ganador: activeName,
          historial: [...(prev?.historial || []), `🏆 ¡${activeName} ha resuelto el caso!`],
        }))
        setMessage(`🏆 ¡${activeName} ha resuelto el caso!`)
      } else {
        setGame((prev) => ({
          ...prev,
          estado: 'finalizado',
          ganador: 'La máquina',
          historial: [...(prev?.historial || []), `❌ ${activeName} se equivoca. La máquina gana.`],
        }))
        setMessage('❌ Te equivocaste. La máquina gana.')
      }
      return
    }

    if (!gameId || !token) {
      setError('Primero únete a la partida')
      return
    }

    try {
      const response = await fetchJson(`${API_BASE}/game/${gameId}/accuse`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          sospechoso: suggestion.sospechoso,
          habitacion: suggestion.habitacion,
          arma: suggestion.arma,
        }),
      })

      setMessage(response.message)
      const state = await fetchJson(`${API_BASE}/game/${gameId}`)
      setGame(state)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <span className="eyebrow">MANSIÓN BLACKWOOD</span>
          <h1>Misterio en la mansión</h1>
        </div>
        {gameId && (
          <div className="game-code-box">
            <span>{mode === 'machine' ? 'Modo' : 'Código'}</span>
            <strong>{mode === 'machine' ? 'Contra la máquina' : gameId}</strong>
          </div>
        )}
      </header>

      {!gameId ? (
        <main className="lobby-panel">
          <section className="card form-card">
            <p className="section-tag">Modo de juego</p>
            <h2>Elige tu partida</h2>

            <div className="mode-grid">
              <button
                type="button"
                className={`mode-card ${mode === 'machine' ? 'active' : ''}`}
                onClick={() => setMode('machine')}
              >
                <strong>Jugar contra la máquina</strong>
                <span>Partida local, sin esperar otro jugador.</span>
              </button>

              <button
                type="button"
                className={`mode-card ${mode === 'multiplayer' ? 'active' : ''}`}
                onClick={() => setMode('multiplayer')}
              >
                <strong>Modo sala</strong>
                <span>Crear o entrar a una partida compartida.</span>
              </button>
            </div>

            <form onSubmit={handleCreateGame} className="stack-form" style={{ marginTop: 22 }}>
              <label>
                Nombre del jugador
                <input
                  value={hostName}
                  onChange={(event) => setHostName(event.target.value)}
                  placeholder="Detective"
                />
              </label>

              {mode === 'multiplayer' && (
                <label>
                  Número de jugadores
                  <select
                    value={numPlayers}
                    onChange={(event) => setNumPlayers(Number(event.target.value))}
                  >
                    <option value={2}>2</option>
                    <option value={3}>3</option>
                    <option value={4}>4</option>
                    <option value={5}>5</option>
                    <option value={6}>6</option>
                  </select>
                </label>
              )}

              <button type="submit" disabled={loading}>
                {loading ? 'Preparando...' : mode === 'machine' ? 'Comenzar partida' : 'Crear partida'}
              </button>
            </form>
          </section>
        </main>
      ) : (
        <main className="game-layout">
          <section className="board-panel card">
            <div className="panel-header">
              <p className="section-tag">Tablero</p>
              <h2>Habitaciones</h2>
            </div>

            <div className="mansion-map">
              <div className="map-grid" />
              {HABITACIONES.map((habitacion) => {
                const jugadoresEnHabitacion = game?.jugadores?.filter(
                  (jugador) => jugador.habitacion === habitacion,
                )
                const playerNameInSession = getPlayerNameForSession(playerName, hostName)
                const isCurrentRoom = currentRoomInGame === habitacion || activeRoom === habitacion
                const isSelectable =
                  !!game &&
                  game.estado !== 'esperando' &&
                  game.estado !== 'finalizado' &&
                  (mode === 'machine'
                    ? canMoveToRoom(game, playerNameInSession, habitacion)
                    : !!token && canMoveToRoom(game, playerNameInSession, habitacion))

                return (
                  <button
                    key={habitacion}
                    type="button"
                    className={`room-node ${isSelectable ? 'movable' : ''} ${isCurrentRoom ? 'current' : ''}`}
                    onClick={() => handleMove(habitacion)}
                    disabled={!isSelectable}
                    style={ROOM_LAYOUT[habitacion]}
                  >
                    <span>{habitacion}</span>
                    {isCurrentRoom && <small>Estás aquí</small>}
                    {jugadoresEnHabitacion?.length > 0 && (
                      <small>{jugadoresEnHabitacion.map((j) => j.nombre).join(', ')}</small>
                    )}
                  </button>
                )
              })}
            </div>
          </section>

          <aside className="sidebar-column">
            <section className="card immersive-room-card">
              <div className="immersive-toolbar">
                <button
                  type="button"
                  className={`tiny-button ${useImmersive3D ? 'active' : ''}`}
                  onClick={() => setUseImmersive3D((prev) => !prev)}
                >
                  {useImmersive3D ? 'Usar vista clásica' : 'Entrar en vista 3D'}
                </button>
              </div>

              {useImmersive3D ? (
                <ImmersiveRoomScene roomName={activeRoom} />
              ) : (
                <div className={`room-scene ${ROOM_SCENES[activeRoom] || 'scene-default'}`}>
                  <div className="scene-glow" />
                  <div className="room-character" />
                  <div className="furniture furniture-a" />
                  <div className="furniture furniture-b" />
                  <div className="furniture furniture-c" />
                </div>
              )}

              <p className="section-tag">Habitación</p>
              <h3>{ROOM_DETAILS[activeRoom]?.title || activeRoom}</h3>
              <p className="room-atmosphere">{ROOM_DETAILS[activeRoom]?.atmosphere}</p>

              <div className="room-clue-box">
                <strong>Pista</strong>
                <p>{ROOM_DETAILS[activeRoom]?.clue}</p>
              </div>

              <div className="room-items">
                <strong>Objetos visibles</strong>
                <ul>
                  {(ROOM_DETAILS[activeRoom]?.items || []).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>

              <div className="room-links">
                <strong>Conexiones</strong>
                <div className="room-link-actions">
                  {(ROOM_ADJACENCY[activeRoom] || []).map((nextRoom) => (
                    <button
                      key={nextRoom}
                      type="button"
                      className="tiny-button"
                      onClick={() => handleMove(nextRoom)}
                    >
                      {nextRoom}
                    </button>
                  ))}
                </div>
              </div>
            </section>
            <section className="card">
              <p className="section-tag">Jugador</p>
              <h3>{mode === 'machine' ? 'Jugar contra la máquina' : 'Unirte a la partida'}</h3>
              {mode === 'multiplayer' ? (
                <form onSubmit={handleJoinGame} className="stack-form compact">
                  <label>
                    Tu nombre
                    <input
                      value={playerName}
                      onChange={(event) => setPlayerName(event.target.value)}
                      placeholder="Tu nombre"
                    />
                  </label>
                  <button type="submit" disabled={loading}>
                    {loading ? 'Entrando...' : 'Unirme'}
                  </button>
                </form>
              ) : (
                <div className="stack-form compact">
                  <label>
                    Tu nombre
                    <input
                      value={playerName || hostName}
                      onChange={(event) => setPlayerName(event.target.value)}
                      placeholder="Tu nombre"
                    />
                  </label>
                  <button type="button" onClick={() => setGame(createLocalMachineGame(playerName || hostName))}>
                    Reiniciar partida
                  </button>
                </div>
              )}
            </section>

            <section className="card">
              <p className="section-tag">Estado</p>
              <h3>{game?.estado || 'Esperando'}</h3>
              <ul className="player-list">
                {game?.jugadores?.length ? (
                  game.jugadores.map((jugador) => (
                    <li key={`${jugador.nombre}-${jugador.habitacion}`}>
                      <span>{jugador.nombre}</span>
                      <small>{jugador.habitacion || 'Sin habitación'}</small>
                    </li>
                  ))
                ) : (
                  <li><span>Aún no hay jugadores</span></li>
                )}
              </ul>
            </section>
          </aside>

          <aside className="sidebar-column">
            <section className="card">
              <p className="section-tag">Acciones</p>
              <h3>Declaración</h3>

              <div className="stack-form compact">
                <label>
                  Sospechoso
                  <select
                    value={suggestion.sospechoso}
                    onChange={(event) =>
                      setSuggestion((prev) => ({ ...prev, sospechoso: event.target.value }))
                    }
                  >
                    {SUSPECTOS.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </label>

                <label>
                  Habitación
                  <select
                    value={suggestion.habitacion}
                    onChange={(event) =>
                      setSuggestion((prev) => ({ ...prev, habitacion: event.target.value }))
                    }
                  >
                    {HABITACIONES.map((h) => (
                      <option key={h} value={h}>{h}</option>
                    ))}
                  </select>
                </label>

                <label>
                  Arma
                  <select
                    value={suggestion.arma}
                    onChange={(event) =>
                      setSuggestion((prev) => ({ ...prev, arma: event.target.value }))
                    }
                  >
                    {ARMAS.map((a) => (
                      <option key={a} value={a}>{a}</option>
                    ))}
                  </select>
                </label>

                <button type="button" onClick={handleSuggestion}>
                  Hacer sugerencia
                </button>
                <button type="button" className="danger" onClick={handleAccuse}>
                  Acusación final
                </button>
              </div>
            </section>

            <section className="card">
              <p className="section-tag">Historial</p>
              <ul className="history-list">
                {game?.historial?.length ? (
                  game.historial.slice(-8).reverse().map((entry, index) => (
                    <li key={`${entry}-${index}`}>{entry}</li>
                  ))
                ) : (
                  <li>La partida aún no registra movimientos.</li>
                )}
              </ul>
            </section>
          </aside>
        </main>
      )}

      {(message || error) && (
        <div className={`banner ${error ? 'error' : 'success'}`}>
          {error || message}
        </div>
      )}
    </div>
  )
}

export default App
