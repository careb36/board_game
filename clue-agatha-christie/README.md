# 🕵️ Misterio en la Mansión Blackwood

### Un juego de mesa inspirado en Agatha Christie

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 Historia

**Año 1934.** Lord Blackwood ha sido encontrado muerto en su biblioteca. Seis sospechosos están bajo custodia, cada uno con motivos ocultos. Los investigadores deben descubrir:

- **¿Quién cometió el crimen?**
- **¿En qué habitación?**
- **¿Con qué arma?**

## 🚀 Instalación Rápida

```bash
cd clue-agatha-christie
python main.py
```

No se requieren dependencias externas - ¡solo Python 3.10+!

## 🎮 Cómo Jugar

### Opción 1: Modo Consola (Interactivo)

```bash
python main.py
```

Sigue las instrucciones en pantalla para:
1. Configurar jugadores (2-6 jugadores)
2. Moverte por la mansión
3. Hacer acusaciones
4. ¡Resolver el misterio!

### Opción 2: Como Módulo Python

```python
from src.juego import Juego

juego = Juego()
juego.configurar_juego([
    ("Holmes", False),  # Jugador humano
    ("Marple", False),  # Jugador humano
    ("Poirot", True),   # IA
])
juego.iniciar_partida()

# Ver estado del juego
print(juego.mostrar_tablero_completo())
```

## 📋 Componentes del Juego

### Personajes (6 sospechosos)
| Nombre | Descripción |
|--------|-------------|
| Victoria Sterling | La sobrina ambiciosa |
| Coronel Marcus Webb | El socio militar |
| Isabella Rossi | La medium italiana |
| Arthur Pembroke | El mayordomo leal |
| Lady Catherine Moore | La viuda misteriosa |
| Dr. Heinrich Wolf | El médico personal |

### Habitaciones (9 ubicaciones)
Biblioteca, Salón Principal, Comedor, Cocina, Invernadero, Galería de Arte, Estudio, Dormitorio Principal, Sótano

### Armas (6 posibilidades)
Candelabro de bronce, Daga ceremonial, Veneno para ratas, Cuerda de piano, Pistola antigua, Estatua de mármol

## 🧪 Ejecutar Tests

```bash
cd clue-agatha-christie
python tests/test_juego.py
```

## 📁 Estructura del Proyecto

```
clue-agatha-christie/
├── main.py               # Punto de entrada principal
├── README.md             # Este archivo
├── requirements.txt      # Dependencias (ninguna externa)
├── src/
│   ├── __init__.py
│   ├── cartas.py         # Sistema de cartas y mazo
│   ├── tablero.py        # Tablero y movimientos
│   ├── jugadores.py      # Gestión de jugadores
│   ├── juego.py          # Lógica principal del juego
│   └── utils.py          # Utilidades
├── tests/
│   └── test_juego.py     # Tests unitarios
└── docs/
    └── reglas.md         # Reglas detalladas
```

## 🛠️ Desarrollado con

Este proyecto fue implementado utilizando herramientas de IA avanzadas:

- **[context-mode](https://github.com/mksglu/context-mode)** - Optimización de ventana de contexto para agentes de IA
- **[aider](https://github.com/Aider-AI/aider)** - Desarrollo asistido por IA en terminal
- **[pi-subagents](https://github.com/nicobailon/pi-subagents)** - Agentes especializados delegados

## 📜 Licencia

MIT License - ver [LICENSE](../LICENSE) para más detalles.

---

*Inspirado en las obras de Agatha Christie*  
*¡Buena suerte, detective! 🕵️‍♂️**
