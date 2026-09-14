"""
Misterio en la Mansión Blackwood - Gestión de Jugadores
Inspirado en Agatha Christie

Este módulo define las clases que modelan a los participantes de la partida:
- Jugador: representa a un jugador (humano o IA) con su mano de cartas,
  posición en el tablero y notas de investigación.
- GestorJugadores: coordina el turno de juego y las operaciones colectivas
  sobre el conjunto de jugadores (reparto de cartas, eliminación, etc.).
"""

from typing import List, Dict, Optional, Set
from src.cartas import Carta, TipoCarta
from src.tablero import HabitacionNombre


class Jugador:
    """Representa a un jugador dentro de la partida.

    Attributes:
        nombre (str): Nombre del jugador.
        es_ia (bool): ``True`` si el jugador está controlado por la IA.
        cartas (List[Carta]): Cartas repartidas a este jugador.
        habitacion_actual (Optional[HabitacionNombre]): Habitación en la que
            se encuentra el jugador, o ``None`` antes de iniciar la partida.
        notas (Dict[TipoCarta, Set[str]]): Pistas positivas anotadas durante
            la investigación (cartas confirmadas que pertenecen a alguien).
        eliminados (Dict[TipoCarta, Set[str]]): Cartas descartadas como
            posibles componentes del crimen por haber sido mostradas.
    """
    
    def __init__(self, nombre: str, es_ia: bool = False):
        """Inicializa un jugador con mano y notas vacías.

        Args:
            nombre: Nombre identificador del jugador.
            es_ia: Si es ``True``, el jugador es controlado por la IA.
        """
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
        """Añade una carta a la mano del jugador.

        Args:
            carta: Carta que se entrega al jugador.
        """
        self.cartas.append(carta)
    
    def tiene_carta(self, carta: Carta) -> bool:
        """Comprueba si el jugador posee una carta concreta.

        Args:
            carta: Carta cuya presencia se quiere verificar.

        Returns:
            ``True`` si la carta está en la mano del jugador.
        """
        return carta in self.cartas
    
    def mostrar_cartas(self) -> List[str]:
        """Devuelve los nombres de todas las cartas en mano.

        Returns:
            Lista de cadenas con los nombres de las cartas.
        """
        return [c.nombre for c in self.cartas]
    
    def puede_refutar(self, sospechoso: str, habitacion: str, arma: str) -> Optional[Carta]:
        """Determina si el jugador puede refutar una acusación.

        Recorre la mano del jugador y devuelve la primera carta cuyo nombre
        coincida con alguno de los tres elementos de la acusación.

        Args:
            sospechoso: Nombre del sospechoso acusado.
            habitacion: Nombre de la habitación acusada.
            arma: Nombre del arma acusada.

        Returns:
            La primera ``Carta`` que refuta la acusación, o ``None`` si el
            jugador no puede refutar ninguno de los tres elementos.
        """
        for carta in self.cartas:
            if carta.nombre in [sospechoso, habitacion, arma]:
                return carta
        return None
    
    def agregar_nota(self, tipo: TipoCarta, nombre: str, es_negativo: bool = False):
        """Registra una nota en la hoja de investigación del jugador.

        Args:
            tipo: Tipo de carta al que pertenece la pista.
            nombre: Nombre de la carta sobre la que se toma la nota.
            es_negativo: Si es ``True``, la nota indica que esa carta
                **no** forma parte del crimen (fue mostrada por otro jugador).
                Si es ``False``, la nota es una pista positiva de interés.
        """
        if es_negativo:
            self.eliminados[tipo].add(nombre)
        else:
            self.notas[tipo].add(nombre)
    
    def obtener_eliminatorias(self, tipo: TipoCarta) -> Set[str]:
        """Devuelve el conjunto de cartas descartadas para un tipo dado.

        Args:
            tipo: Tipo de carta a consultar.

        Returns:
            Conjunto de nombres de cartas que han sido descartadas como
            posibles componentes del crimen para ese tipo.
        """
        return self.eliminados[tipo]
    
    def __repr__(self):
        return f"Jugador({self.nombre}, IA={self.es_ia})"


class GestorJugadores:
    """Coordina a todos los jugadores durante la partida.

    Mantiene el orden de turnos, reparte las cartas y proporciona métodos
    de búsqueda y manipulación del conjunto de jugadores activos.

    Attributes:
        jugadores (List[Jugador]): Lista ordenada de jugadores activos.
        turno_actual (int): Índice del jugador cuyo turno está en curso.
    """
    
    def __init__(self):
        """Inicializa el gestor sin jugadores y con el turno en la posición 0."""
        self.jugadores: List[Jugador] = []
        self.turno_actual: int = 0
    
    def agregar_jugador(self, nombre: str, es_ia: bool = False) -> Jugador:
        """Crea un nuevo jugador y lo añade a la partida.

        Args:
            nombre: Nombre del jugador.
            es_ia: Si es ``True``, el jugador es controlado por la IA.

        Returns:
            La instancia de ``Jugador`` recién creada.
        """
        jugador = Jugador(nombre, es_ia)
        self.jugadores.append(jugador)
        return jugador
    
    def repartir_cartas(self, cartas: List[Carta]):
        """Distribuye las cartas equitativamente en orden circular.

        Las cartas se asignan de forma rotativa (estilo round-robin) entre
        todos los jugadores activos. Si no hay jugadores, no se hace nada.

        Args:
            cartas: Lista de cartas a repartir (habitualmente las 18 cartas
                que no forman parte del sobre del crimen).
        """
        num_jugadores = len(self.jugadores)
        if num_jugadores == 0:
            return
        
        for i, carta in enumerate(cartas):
            jugador_idx = i % num_jugadores
            self.jugadores[jugador_idx].agregar_carta(carta)
    
    def siguiente_turno(self):
        """Avanza el turno al siguiente jugador de la lista (rotación circular)."""
        self.turno_actual = (self.turno_actual + 1) % len(self.jugadores)
    
    def jugador_actual(self) -> Optional[Jugador]:
        """Devuelve el jugador cuyo turno está activo.

        Returns:
            El ``Jugador`` en el turno actual, o ``None`` si no hay jugadores.
        """
        if not self.jugadores:
            return None
        return self.jugadores[self.turno_actual]
    
    def obtener_jugador(self, nombre: str) -> Optional[Jugador]:
        """Busca un jugador por nombre (insensible a mayúsculas).

        Args:
            nombre: Nombre del jugador a buscar.

        Returns:
            La instancia de ``Jugador`` encontrada, o ``None`` si no existe.
        """
        for jugador in self.jugadores:
            if jugador.nombre.lower() == nombre.lower():
                return jugador
        return None
    
    def colocar_jugador_en_habitacion(
        self, 
        jugador: Jugador, 
        habitacion: HabitacionNombre
    ):
        """Asigna la habitación inicial a un jugador al arrancar la partida.

        Args:
            jugador: Jugador al que se asigna la posición.
            habitacion: Habitación donde se coloca al jugador.
        """
        jugador.habitacion_actual = habitacion
    
    def get_todos_los_jugadores(self) -> List[Jugador]:
        """Devuelve una copia de la lista de jugadores activos.

        Returns:
            Lista de instancias ``Jugador`` actualmente en la partida.
        """
        return self.jugadores.copy()
    
    def remover_jugador(self, jugador: Jugador):
        """Elimina un jugador de la partida por acusación final incorrecta.

        Ajusta el índice de turno si es necesario para que no apunte fuera
        de los límites de la lista actualizada.

        Args:
            jugador: Jugador que debe ser eliminado.
        """
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
