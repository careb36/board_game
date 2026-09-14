"""
Misterio en la Mansión Blackwood - Tablero y Movimientos
Inspirado en Agatha Christie
"""

from typing import List, Dict, Optional, Tuple
from enum import Enum


class HabitacionNombre(Enum):
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
    """Representa una habitación en la mansión"""
    
    def __init__(self, nombre: HabitacionNombre, descripcion: str):
        self.nombre = nombre
        self.descripcion = descripcion
        self.conexiones: List[HabitacionNombre] = []
    
    def agregar_conexion(self, habitacion: HabitacionNombre):
        """Agrega una conexión a otra habitación"""
        if habitacion not in self.conexiones:
            self.conexiones.append(habitacion)
    
    def __repr__(self):
        return f"{self.nombre.value}"


class Tablero:
    """Gestiona el tablero de la mansión"""
    
    def __init__(self):
        self.habitaciones: Dict[HabitacionNombre, Habitacion] = {}
        self._crear_habitaciones()
        self._crear_conexiones()
    
    def _crear_habitaciones(self):
        """Crea todas las habitaciones de la mansión"""
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
        """Obtiene una habitación por su nombre"""
        return self.habitaciones.get(nombre)
    
    def es_movimiento_valido(
        self, 
        origen: HabitacionNombre, 
        destino: HabitacionNombre
    ) -> bool:
        """Verifica si un movimiento entre habitaciones es válido"""
        if origen not in self.habitaciones or destino not in self.habitaciones:
            return False
        
        return destino in self.habitaciones[origen].conexiones
    
    def obtener_vecinas(self, habitacion: HabitacionNombre) -> List[HabitacionNombre]:
        """Obtiene las habitaciones adyacentes"""
        if habitacion not in self.habitaciones:
            return []
        return self.habitaciones[habitacion].conexiones
    
    def mostrar_tablero(self) -> str:
        """Muestra el layout del tablero"""
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
        """Retorna lista de todas las habitaciones"""
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
