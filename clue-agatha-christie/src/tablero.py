"""
Misterio en la Mansión Blackwood - Tablero y Movimientos
Inspirado en Agatha Christie

Este módulo define la representación física de la mansión:
- HabitacionNombre: enumeración de las nueve habitaciones disponibles.
- Habitacion: modelo de una habitación individual con sus conexiones.
- Tablero: gestión completa del mapa de la mansión y la validación de
  movimientos entre habitaciones adyacentes.
"""

from typing import List, Dict, Optional, Tuple
from enum import Enum


class HabitacionNombre(Enum):
    """Nombres canónicos de las habitaciones de la Mansión Blackwood."""

    BIBLIOTECA = "Biblioteca"
    SALON = "Salón Principal"
    COMEDOR = "Comedor"
    COCINA = "Cocina"
    INVERNADERO = "Invernadero"
    GALERIA = "Galería de Arte"
    ESTUDIO = "Estudio"
    DORMITORIO = "Dormitorio Principal"
    SOTANO = "Sótano"


class Habitacion:
    """Representa una habitación individual dentro de la mansión.

    Attributes:
        nombre (HabitacionNombre): Identificador enumerado de la habitación.
        descripcion (str): Breve descripción narrativa de la habitación.
        conexiones (List[HabitacionNombre]): Habitaciones adyacentes a las
            que se puede acceder directamente desde ésta.
    """
    
    def __init__(self, nombre: HabitacionNombre, descripcion: str):
        """Inicializa la habitación con su nombre y descripción.

        Args:
            nombre: Identificador enumerado de la habitación.
            descripcion: Texto descriptivo de la habitación.
        """
        self.nombre = nombre
        self.descripcion = descripcion
        self.conexiones: List[HabitacionNombre] = []
    
    def agregar_conexion(self, habitacion: HabitacionNombre):
        """Registra una habitación adyacente si aún no está conectada.

        Args:
            habitacion: Habitación a la que se desea agregar la conexión.
        """
        if habitacion not in self.conexiones:
            self.conexiones.append(habitacion)
    
    def __repr__(self):
        return f"{self.nombre.value}"


class Tablero:
    """Gestiona el mapa completo de la Mansión Blackwood.

    Crea las nueve habitaciones y establece las conexiones bidireccionales
    entre ellas según el layout de la mansión.

    Attributes:
        habitaciones (Dict[HabitacionNombre, Habitacion]): Mapa de
            identificador → instancia de habitación.
    """
    
    def __init__(self):
        """Inicializa el tablero creando habitaciones y conexiones."""
        self.habitaciones: Dict[HabitacionNombre, Habitacion] = {}
        self._crear_habitaciones()
        self._crear_conexiones()
    
    def _crear_habitaciones(self):
        """Instancia las nueve habitaciones de la mansión con sus descripciones."""
        descripciones = {
            HabitacionNombre.BIBLIOTECA: "Llena de libros antiguos y secretos familiares",
            HabitacionNombre.SALON: "Elegante con muebles victorianos y candelabros",
            HabitacionNombre.COMEDOR: "Gran mesa de roble para cenas formales",
            HabitacionNombre.COCINA: "Donde el personal prepara los banquetes",
            HabitacionNombre.INVERNADERO: "Exóticas plantas y flores raras",
            HabitacionNombre.GALERIA: "Retratos de ancestros y obras de arte",
            HabitacionNombre.ESTUDIO: "Escritorio del Lord con documentos privados",
            HabitacionNombre.DORMITORIO: "Habitación principal con balcón",
            HabitacionNombre.SOTANO: "Oscuro, con bodega y calderas",
        }
        
        for nombre, desc in descripciones.items():
            self.habitaciones[nombre] = Habitacion(nombre, desc)
    
    def _crear_conexiones(self):
        """
        Crea las conexiones entre habitaciones
        Layout de la mansión Blackwood:
        
        [Invernadero] -- [Biblioteca] -- [Estudio]
              |               |              |
        [Salón] -------- [Comedor] ---- [Dormitorio]
              |               |
        [Galería] ------- [Cocina]
                              |
                          [Sótano]
        """
        conexiones = {
            HabitacionNombre.BIBLIOTECA: [
                HabitacionNombre.INVERNADERO,
                HabitacionNombre.ESTUDIO,
                HabitacionNombre.SALON,
                HabitacionNombre.COMEDOR,
            ],
            HabitacionNombre.SALON: [
                HabitacionNombre.BIBLIOTECA,
                HabitacionNombre.COMEDOR,
                HabitacionNombre.GALERIA,
            ],
            HabitacionNombre.COMEDOR: [
                HabitacionNombre.BIBLIOTECA,
                HabitacionNombre.SALON,
                HabitacionNombre.ESTUDIO,
                HabitacionNombre.DORMITORIO,
                HabitacionNombre.COCINA,
            ],
            HabitacionNombre.COCINA: [
                HabitacionNombre.COMEDOR,
                HabitacionNombre.GALERIA,
                HabitacionNombre.SOTANO,
            ],
            HabitacionNombre.INVERNADERO: [
                HabitacionNombre.BIBLIOTECA,
                HabitacionNombre.SALON,
            ],
            HabitacionNombre.GALERIA: [
                HabitacionNombre.SALON,
                HabitacionNombre.COCINA,
            ],
            HabitacionNombre.ESTUDIO: [
                HabitacionNombre.BIBLIOTECA,
                HabitacionNombre.COMEDOR,
                HabitacionNombre.DORMITORIO,
            ],
            HabitacionNombre.DORMITORIO: [
                HabitacionNombre.COMEDOR,
                HabitacionNombre.ESTUDIO,
            ],
            HabitacionNombre.SOTANO: [
                HabitacionNombre.COCINA,
            ],
        }
        
        # Aplicar conexiones bidireccionales
        for habitacion, conectadas in conexiones.items():
            for conectada in conectadas:
                self.habitaciones[habitacion].agregar_conexion(conectada)
                self.habitaciones[conectada].agregar_conexion(habitacion)
    
    def obtener_habitacion(self, nombre: HabitacionNombre) -> Optional[Habitacion]:
        """Devuelve la habitación asociada a un identificador.

        Args:
            nombre: Identificador enumerado de la habitación.

        Returns:
            La instancia de ``Habitacion`` o ``None`` si no existe.
        """
        return self.habitaciones.get(nombre)
    
    def es_movimiento_valido(
        self, 
        origen: HabitacionNombre, 
        destino: HabitacionNombre
    ) -> bool:
        """Indica si un jugador puede moverse directamente entre dos habitaciones.

        Args:
            origen: Habitación de partida.
            destino: Habitación de destino.

        Returns:
            ``True`` si las habitaciones existen y están directamente
            conectadas, ``False`` en caso contrario.
        """
        if origen not in self.habitaciones or destino not in self.habitaciones:
            return False
        
        return destino in self.habitaciones[origen].conexiones
    
    def obtener_vecinas(self, habitacion: HabitacionNombre) -> List[HabitacionNombre]:
        """Devuelve la lista de habitaciones adyacentes a una dada.

        Args:
            habitacion: Habitación de la que se quieren conocer las vecinas.

        Returns:
            Lista de identificadores de habitaciones adyacentes, o una
            lista vacía si la habitación no existe en el tablero.
        """
        if habitacion not in self.habitaciones:
            return []
        return self.habitaciones[habitacion].conexiones
    
    def mostrar_tablero(self) -> str:
        """Genera una representación legible del tablero con todas las conexiones.

        Returns:
            Cadena de texto con el mapa completo de la mansión, listando
            cada habitación junto a su descripción y habitaciones conectadas.
        """
        output = []
        output.append("🏰 MANSIÓN BLACKWOOD - Mapa de Habitaciones")
        output.append("=" * 50)
        
        for nombre, habitacion in self.habitaciones.items():
            vecinas = ", ".join([v.value for v in habitacion.conexiones])
            output.append(f"\n📍 {nombre.value}")
            output.append(f"   {habitacion.descripcion}")
            output.append(f"   → Conexiones: {vecinas}")
        
        return "\n".join(output)
    
    def get_todas_las_habitaciones(self) -> List[HabitacionNombre]:
        """Devuelve la lista de todos los identificadores de habitación.

        Returns:
            Lista de valores ``HabitacionNombre`` en el orden en que fueron
            registrados al construir el tablero.
        """
        return list(self.habitaciones.keys())


# Función de prueba
if __name__ == "__main__":
    tablero = Tablero()
    print(tablero.mostrar_tablero())
    
    # Probar validación de movimientos
    print("\n" + "=" * 50)
    print("Prueba de movimientos:")
    print(f"Biblioteca → Comedor: {tablero.es_movimiento_valido(HabitacionNombre.BIBLIOTECA, HabitacionNombre.COMEDOR)}")
    print(f"Biblioteca → Sótano: {tablero.es_movimiento_valido(HabitacionNombre.BIBLIOTECA, HabitacionNombre.SOTANO)}")
