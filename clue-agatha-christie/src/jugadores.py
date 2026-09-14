"""
Misterio en la Mansión Blackwood - Gestión de Jugadores
Inspirado en Agatha Christie
"""

from typing import List, Dict, Optional, Set
from src.cartas import Carta, TipoCarta
from src.tablero import HabitacionNombre


class Jugador:
    """Representa un jugador en el juego"""
    
    def __init__(self, nombre: str, es_ia: bool = False):
        self.nombre = nombre
        self.es_ia = es_ia
        self.cartas: List[Carta] = []
        self.habitacion_actual: Optional[HabitacionNombre] = None
        self.notas: Dict[TipoCarta, Set[str]] = {
            TipoCarta.SOSPECHOSO: set(),
            TipoCarta.HABITACION: set(),
            TipoCarta.ARMA: set(),
        }
        self.eliminados: Dict[TipoCarta, Set[str]] = {
            TipoCarta.SOSPECHOSO: set(),  # Cartas que NO tiene el crimen
            TipoCarta.HABITACION: set(),
            TipoCarta.ARMA: set(),
        }
    
    def agregar_carta(self, carta: Carta):
        """Agrega una carta a la mano del jugador"""
        self.cartas.append(carta)
    
    def tiene_carta(self, carta: Carta) -> bool:
        """Verifica si el jugador tiene una carta específica"""
        return carta in self.cartas
    
    def mostrar_cartas(self) -> List[str]:
        """Retorna lista de nombres de cartas"""
        return [c.nombre for c in self.cartas]
    
    def puede_refutar(self, sospechoso: str, habitacion: str, arma: str) -> Optional[Carta]:
        """
        Verifica si el jugador puede refutar una acusación
        Retorna la carta que refuta o None si no puede
        """
        for carta in self.cartas:
            if carta.nombre in [sospechoso, habitacion, arma]:
                return carta
        return None
    
    def agregar_nota(self, tipo: TipoCarta, nombre: str, es_negativo: bool = False):
        """
        Agrega una nota a la hoja de investigación
        Si es_negativo=True, significa que esa carta NO es del crimen
        """
        if es_negativo:
            self.eliminados[tipo].add(nombre)
        else:
            self.notas[tipo].add(nombre)
    
    def obtener_eliminatorias(self, tipo: TipoCarta) -> Set[str]:
        """Obtiene las cartas eliminadas para un tipo"""
        return self.eliminados[tipo]
    
    def __repr__(self):
        return f"Jugador({self.nombre}, IA={self.es_ia})"


class GestorJugadores:
    """Gestiona todos los jugadores en la partida"""
    
    def __init__(self):
        self.jugadores: List[Jugador] = []
        self.turno_actual: int = 0
    
    def agregar_jugador(self, nombre: str, es_ia: bool = False) -> Jugador:
        """Agrega un nuevo jugador"""
        jugador = Jugador(nombre, es_ia)
        self.jugadores.append(jugador)
        return jugador
    
    def repartir_cartas(self, cartas: List[Carta]):
        """Reparte las cartas equitativamente entre los jugadores"""
        num_jugadores = len(self.jugadores)
        if num_jugadores == 0:
            return
        
        for i, carta in enumerate(cartas):
            jugador_idx = i % num_jugadores
            self.jugadores[jugador_idx].agregar_carta(carta)
    
    def siguiente_turno(self):
        """Avanza al siguiente turno"""
        self.turno_actual = (self.turno_actual + 1) % len(self.jugadores)
    
    def jugador_actual(self) -> Optional[Jugador]:
        """Retorna el jugador cuyo turno es"""
        if not self.jugadores:
            return None
        return self.jugadores[self.turno_actual]
    
    def obtener_jugador(self, nombre: str) -> Optional[Jugador]:
        """Busca un jugador por nombre"""
        for jugador in self.jugadores:
            if jugador.nombre.lower() == nombre.lower():
                return jugador
        return None
    
    def colocar_jugador_en_habitacion(
        self, 
        jugador: Jugador, 
        habitacion: HabitacionNombre
    ):
        """Coloca un jugador en una habitación inicial"""
        jugador.habitacion_actual = habitacion
    
    def get_todos_los_jugadores(self) -> List[Jugador]:
        """Retorna lista de todos los jugadores"""
        return self.jugadores.copy()
    
    def remover_jugador(self, jugador: Jugador):
        """Remueve un jugador del juego"""
        if jugador in self.jugadores:
            self.jugadores.remove(jugador)
            if self.turno_actual >= len(self.jugadores):
                self.turno_actual = 0


# Función de prueba
if __name__ == "__main__":
    from src.cartas import Mazo, TipoCarta
    
    gestor = GestorJugadores()
    
    # Crear jugadores
    gestor.agregar_jugador("Detective Holmes")
    gestor.agregar_jugador("Inspector Clouseau", es_ia=True)
    gestor.agregar_jugador("Miss Marple")
    
    # Preparar y repartir cartas
    mazo = Mazo()
    resultado = mazo.preparar_juego()
    gestor.repartir_cartas(resultado["juego"])
    
    print("🕵️ Jugadores en la partida:")
    print("=" * 40)
    for jugador in gestor.get_todos_los_jugadores():
        print(f"\n{jugador.nombre} (IA: {jugador.es_ia})")
        print(f"   Cartas: {len(jugador.cartas)}")
        if jugador.cartas:
            for carta in jugador.cartas[:3]:  # Mostrar solo primeras 3
                print(f"      - {carta.nombre}")
            if len(jugador.cartas) > 3:
                print(f"      ... y {len(jugador.cartas) - 3} más")
