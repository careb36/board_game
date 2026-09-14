"""
Misterio en la Mansión Blackwood - Utilidades
Inspirado en Agatha Christie

Funciones de apoyo para la interfaz de consola y la gestión de partidas:
entrada/salida del usuario, menús numerados, persistencia de partidas en JSON
y helpers de formato y validación de cadenas.
"""

import os
import json
from typing import List, Dict, Any
from datetime import datetime


def limpiar_pantalla():
    """Limpia la pantalla de la terminal de forma compatible con Windows y Unix."""
    os.system('cls' if os.name == 'nt' else 'clear')


def esperar_enter(mensaje: str = "Presiona Enter para continuar..."):
    """Detiene la ejecución hasta que el usuario pulse Enter.

    Args:
        mensaje: Texto que se muestra antes de esperar la entrada del usuario.
    """
    input(mensaje)


def mostrar_menu(opciones: List[str], titulo: str = "Menú") -> int:
    """Muestra un menú numerado e interpreta la opción elegida por el usuario.

    Repite la solicitud hasta que el usuario introduzca un número válido.

    Args:
        opciones: Lista de cadenas con los textos de cada opción.
        titulo: Título que encabeza el menú.

    Returns:
        Índice base-0 de la opción seleccionada.
    """
    print(f"\n{'=' * 40}")
    print(f"📋 {titulo}")
    print('=' * 40)
    
    for i, opcion in enumerate(opciones, 1):
        print(f"  {i}. {opcion}")
    
    print('=' * 40)
    
    while True:
        try:
            eleccion = int(input("Selecciona una opción: "))
            if 1 <= eleccion <= len(opciones):
                return eleccion - 1
            else:
                print(f"❌ Opción inválida. Elige entre 1 y {len(opciones)}")
        except ValueError:
            print("❌ Por favor, ingresa un número")


def seleccionar_de_lista(elementos: List[str], mensaje: str = "Selecciona:") -> int:
    """Muestra una lista numerada y pide al usuario que elija un elemento.

    Repite la solicitud hasta que el usuario introduzca un número válido.

    Args:
        elementos: Lista de cadenas con los elementos disponibles.
        mensaje: Texto introductorio que se muestra antes de la lista.

    Returns:
        Índice base-0 del elemento seleccionado.
    """
    print(f"\n{mensaje}")
    print('-' * 40)
    
    for i, elemento in enumerate(elementos, 1):
        print(f"  {i}. {elemento}")
    
    print('-' * 40)
    
    while True:
        try:
            eleccion = int(input("Tu elección: "))
            if 1 <= eleccion <= len(elementos):
                return eleccion - 1
            else:
                print(f"❌ Opción inválida. Elige entre 1 y {len(elementos)}")
        except ValueError:
            print("❌ Por favor, ingresa un número")


def guardar_partida(datos: Dict[str, Any], nombre_archivo: str = None) -> str:
    """Persiste el estado de una partida en un fichero JSON.

    Si no se indica nombre de archivo, genera uno automáticamente con la
    marca de tiempo actual. El archivo se guarda en el directorio
    ``guardados/`` (creándolo si no existe).

    Args:
        datos: Diccionario con el estado de la partida a guardar.
        nombre_archivo: Nombre del fichero de destino (p. ej.
            ``"partida_manual.json"``). Si es ``None`` se genera
            automáticamente.

    Returns:
        Ruta relativa al fichero JSON guardado.
    """
    if nombre_archivo is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"partida_{timestamp}.json"
    
    ruta = os.path.join("guardados", nombre_archivo)
    os.makedirs("guardados", exist_ok=True)
    
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
    
    return ruta


def cargar_partida(nombre_archivo: str) -> Dict[str, Any]:
    """Carga el estado de una partida desde un fichero JSON.

    Args:
        nombre_archivo: Nombre del fichero dentro del directorio ``guardados/``.

    Returns:
        Diccionario con los datos de la partida, o ``None`` si el archivo no
        existe.
    """
    ruta = os.path.join("guardados", nombre_archivo)
    
    if not os.path.exists(ruta):
        return None
    
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)


def listar_partidas_guardadas() -> List[str]:
    """Lista los ficheros de partidas guardadas disponibles.

    Returns:
        Lista de nombres de ficheros ``.json`` en el directorio ``guardados/``,
        o una lista vacía si el directorio no existe.
    """
    ruta = "guardados"
    if not os.path.exists(ruta):
        return []
    
    return [f for f in os.listdir(ruta) if f.endswith('.json')]


def formatear_nombre(nombre: str) -> str:
    """Normaliza un nombre para comparaciones insensibles a mayúsculas/espacios.

    Convierte el texto a minúsculas y colapsa espacios múltiples en uno solo.

    Args:
        nombre: Nombre original a normalizar.

    Returns:
        Nombre normalizado.
    """
    return ' '.join(nombre.lower().split())


def es_nombre_valido(nombre: str, longitud_min: int = 3, longitud_max: int = 30) -> bool:
    """Comprueba si un nombre de jugador cumple los requisitos de longitud.

    Args:
        nombre: Nombre a validar (se eliminarán espacios iniciales/finales).
        longitud_min: Longitud mínima permitida (por defecto 3).
        longitud_max: Longitud máxima permitida (por defecto 30).

    Returns:
        ``True`` si la longitud del nombre (tras strip) está dentro del rango.
    """
    nombre = nombre.strip()
    return longitud_min <= len(nombre) <= longitud_max


def obtener_input_seguro(
    mensaje: str, 
    tipo: str = "str",
    minimo: Any = None,
    maximo: Any = None
) -> Any:
    """Solicita al usuario un valor con validación de tipo y rango.

    Repite la solicitud en bucle hasta obtener un valor válido.

    Args:
        mensaje: Texto que se muestra al pedir el input.
        tipo: Tipo esperado del valor: ``"str"``, ``"int"`` o ``"float"``.
        minimo: Valor mínimo permitido (inclusivo) para tipos numéricos.
        maximo: Valor máximo permitido (inclusivo) para tipos numéricos.

    Returns:
        El valor introducido por el usuario, convertido al tipo solicitado.
    """
    while True:
        valor = input(mensaje).strip()
        
        if tipo == "str":
            if valor:
                return valor
            print("❌ El valor no puede estar vacío")
        
        elif tipo == "int":
            try:
                num = int(valor)
                if minimo is not None and num < minimo:
                    print(f"❌ El valor debe ser >= {minimo}")
                    continue
                if maximo is not None and num > maximo:
                    print(f"❌ El valor debe ser <= {maximo}")
                    continue
                return num
            except ValueError:
                print("❌ Por favor, ingresa un número entero")
        
        elif tipo == "float":
            try:
                num = float(valor)
                if minimo is not None and num < minimo:
                    print(f"❌ El valor debe ser >= {minimo}")
                    continue
                if maximo is not None and num > maximo:
                    print(f"❌ El valor debe ser <= {maximo}")
                    continue
                return num
            except ValueError:
                print("❌ Por favor, ingresa un número")
    
    return None


# Funciones de ayuda para el juego
def imprimir_cartas_mano(cartas: List[Dict]) -> str:
    """Genera una representación legible de las cartas en mano de un jugador.

    Args:
        cartas: Lista de diccionarios con las claves ``"nombre"`` y ``"tipo"``
            (``"sospechoso"``, ``"habitacion"`` o ``"arma"``).

    Returns:
        Cadena de texto multilínea con las cartas formateadas e iconos.
    """
    output = []
    output.append("\n🃏 TUS CARTAS:")
    output.append("-" * 40)
    
    for carta in cartas:
        icono = "👤" if carta['tipo'] == 'sospechoso' else "📍" if carta['tipo'] == 'habitacion' else "🔪"
        output.append(f"  {icono} {carta['nombre']}")
    
    output.append("-" * 40)
    return "\n".join(output)


def imprimir_notas_investigacion(notas: Dict) -> str:
    """Genera una representación de las notas de investigación de un jugador.

    Args:
        notas: Diccionario con claves ``"sospechoso"``, ``"habitacion"`` y
            ``"arma"``, cada una mapeando a un iterable de nombres.

    Returns:
        Cadena de texto multilínea con las notas organizadas por categoría.
    """
    output = []
    output.append("\n📝 NOTAS DE INVESTIGACIÓN:")
    output.append("=" * 40)
    
    categorias = {
        'sospechoso': ('👤 Sospechosos', 'Eliminados'),
        'habitacion': ('📍 Habitaciones', 'Eliminadas'),
        'arma': ('🔪 Armas', 'Eliminadas'),
    }
    
    for tipo, (titulo, eliminado_titulo) in categorias.items():
        if tipo in notas:
            output.append(f"\n{titulo}:")
            if notas[tipo]:
                for item in notas[tipo]:
                    output.append(f"   • {item}")
            else:
                output.append("   (sin notas)")
    
    output.append("=" * 40)
    return "\n".join(output)


if __name__ == "__main__":
    # Demo de utilidades
    print("🛠️ Demo de Utilidades")
    print("=" * 40)
    
    # Test de menú
    opciones = ["Nueva Partida", "Cargar Partida", "Opciones", "Salir"]
    seleccion = mostrar_menu(opciones, "Menú Principal")
    print(f"Seleccionaste: {opciones[seleccion]}")
    
    # Test de selección
    elementos = ["Victoria Sterling", "Coronel Webb", "Isabella Rossi"]
    idx = seleccionar_de_lista(elementos, "Elige un sospechoso:")
    print(f"Elegiste: {elementos[idx]}")
