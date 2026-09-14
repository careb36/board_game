"""
Misterio en la Mansión Blackwood - Utilidades
Inspirado en Agatha Christie
"""

import os
import json
from typing import List, Dict, Any
from datetime import datetime


def limpiar_pantalla():
    """Limpia la pantalla de la terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


def esperar_enter(mensaje: str = "Presiona Enter para continuar..."):
    """Espera a que el usuario presione Enter"""
    input(mensaje)


def mostrar_menu(opciones: List[str], titulo: str = "Menú") -> int:
    """
    Muestra un menú con opciones numeradas
    Retorna el índice de la opción seleccionada (0-based)
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
    """
    Permite al usuario seleccionar un elemento de una lista
    Retorna el índice del elemento seleccionado (0-based)
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
    """
    Guarda el estado de una partida en JSON
    Retorna el nombre del archivo guardado
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
    """
    Carga el estado de una partida desde JSON
    Retorna los datos de la partida o None si falla
    """
    ruta = os.path.join("guardados", nombre_archivo)
    
    if not os.path.exists(ruta):
        return None
    
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)


def listar_partidas_guardadas() -> List[str]:
    """Retorna lista de archivos de partidas guardadas"""
    ruta = "guardados"
    if not os.path.exists(ruta):
        return []
    
    return [f for f in os.listdir(ruta) if f.endswith('.json')]


def formatear_nombre(nombre: str) -> str:
    """Formatea un nombre para comparación (minúsculas, sin espacios extra)"""
    return ' '.join(nombre.lower().split())


def es_nombre_valido(nombre: str, longitud_min: int = 3, longitud_max: int = 30) -> bool:
    """Verifica si un nombre es válido"""
    nombre = nombre.strip()
    return longitud_min <= len(nombre) <= longitud_max


def obtener_input_seguro(
    mensaje: str, 
    tipo: str = "str",
    minimo: Any = None,
    maximo: Any = None
) -> Any:
    """
    Obtiene input del usuario con validación
    tipo: "str", "int", "float"
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
    """Imprime las cartas de la mano de un jugador de forma legible"""
    output = []
    output.append("\n🃏 TUS CARTAS:")
    output.append("-" * 40)
    
    for carta in cartas:
        icono = "👤" if carta['tipo'] == 'sospechoso' else "📍" if carta['tipo'] == 'habitacion' else "🔪"
        output.append(f"  {icono} {carta['nombre']}")
    
    output.append("-" * 40)
    return "\n".join(output)


def imprimir_notas_investigacion(notas: Dict) -> str:
    """Imprime las notas de investigación de un jugador"""
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
