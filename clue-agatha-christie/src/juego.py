"""
Misterio en la Mansión Blackwood - Lógica Principal del Juego
Inspirado en Agatha Christie

Este módulo contiene las clases centrales que orquestan toda la partida:
- Acusacion: modelo inmutable de una acusación (sospechoso, habitación y arma).
- Juego: controlador principal que inicializa la partida, gestiona los turnos,
  valida movimientos, procesa acusaciones y determina el ganador.
"""

import random
from typing import List, Dict, Optional, Tuple
from src.cartas import Mazo, Carta, TipoCarta
from src.tablero import Tablero, HabitacionNombre
from src.jugadores import GestorJugadores, Jugador


class Acusacion:
    """Modelo de datos para una acusación formulada en el juego.

    Attributes:
        sospechoso (str): Nombre del sospechoso acusado.
        habitacion (str): Nombre de la habitación donde se cometió el crimen.
        arma (str): Nombre del arma utilizada.
    """
    
    def __init__(self, sospechoso: str, habitacion: str, arma: str):
        """Inicializa la acusación con sus tres componentes.

        Args:
            sospechoso: Nombre del sospechoso acusado.
            habitacion: Nombre de la habitación del crimen.
            arma: Nombre del arma empleada.
        """
        self.sospechoso = sospechoso
        self.habitacion = habitacion
        self.arma = arma
    
    def __repr__(self):
        return f"{self.sospechoso} en {self.habitacion} con {self.arma}"


class Juego:
    """Controlador principal de la partida.

    Orquesta el ciclo de vida completo del juego: configuración de jugadores,
    preparación del mazo, asignación de posiciones iniciales, validación de
    movimientos y procesamiento de acusaciones.

    Attributes:
        mazo (Mazo): Mazo de cartas del juego.
        tablero (Tablero): Tablero con las habitaciones y conexiones.
        gestor_jugadores (GestorJugadores): Gestor de jugadores y turnos.
        carta_crimen (Dict[TipoCarta, Carta]): Las tres cartas secretas que
            forman la solución del crimen.
        juego_iniciado (bool): ``True`` después de llamar a ``iniciar_partida``.
        ganador (Optional[Jugador]): Jugador que ha ganado, o ``None`` si la
            partida no ha terminado.
        historial (List[str]): Registro cronológico de todas las acciones
            realizadas durante la partida.
    """
    
    def __init__(self):
        """Inicializa el juego con todos los componentes en estado inicial."""
        self.mazo = Mazo()
        self.tablero = Tablero()
        self.gestor_jugadores = GestorJugadores()
        self.carta_crimen: Dict[TipoCarta, Carta] = {}
        self.juego_iniciado = False
        self.ganador: Optional[Jugador] = None
        self.historial: List[str] = []
    
    def configurar_juego(self, nombres_jugadores: List[Tuple[str, bool]]) -> bool:
        """Registra a los jugadores que participarán en la partida.

        Valida que el número de jugadores esté entre 2 y 6 antes de
        añadirlos al gestor.

        Args:
            nombres_jugadores: Lista de tuplas ``(nombre, es_ia)`` con los
                datos de cada jugador.

        Returns:
            ``True`` si la configuración fue exitosa, ``False`` si el número
            de jugadores es inválido.
        """
        if len(nombres_jugadores) < 2 or len(nombres_jugadores) > 6:
            self.historial.append("❌ Error: Se requieren 2-6 jugadores")
            return False
        
        for nombre, es_ia in nombres_jugadores:
            self.gestor_jugadores.agregar_jugador(nombre, es_ia)
        
        self.historial.append(f"✅ {len(nombres_jugadores)} jugadores configurados")
        return True
    
    def iniciar_partida(self) -> bool:
        """Inicializa todos los elementos de la partida y la pone en marcha.

        Prepara el mazo, selecciona las cartas del crimen, reparte las cartas
        restantes entre los jugadores y los coloca en habitaciones iniciales
        aleatorias.

        Returns:
            ``True`` si la partida se inició correctamente, ``False`` si no
            hay jugadores configurados.
        """
        if not self.gestor_jugadores.get_todos_los_jugadores():
            self.historial.append("❌ Error: No hay jugadores configurados")
            return False
        
        # Preparar mazo y seleccionar cartas del crimen
        resultado = self.mazo.preparar_juego()
        self.carta_crimen = resultado["crimen"]
        
        # Repartir cartas
        self.gestor_jugadores.repartir_cartas(resultado["juego"])
        
        # Colocar jugadores en habitaciones iniciales aleatorias
        habitaciones = self.tablero.get_todas_las_habitaciones()
        for jugador in self.gestor_jugadores.get_todos_los_jugadores():
            habitacion_inicial = random.choice(habitaciones)
            self.gestor_jugadores.colocar_jugador_en_habitacion(
                jugador, 
                habitacion_inicial
            )
        
        self.juego_iniciado = True
        self.historial.append("✅ Partida iniciada")
        self.historial.append(f"📁 Crimen: {self._obtener_resumen_crimen()}")
        
        return True
    
    def _obtener_resumen_crimen(self) -> str:
        """Genera un texto resumen de las cartas del crimen (solo para depuración).

        Returns:
            Cadena con el nombre del sospechoso, habitación y arma separados
            por " + ".
        """
        return (
            f"{self.carta_crimen[TipoCarta.SOSPECHOSO].nombre} + "
            f"{self.carta_crimen[TipoCarta.HABITACION].nombre} + "
            f"{self.carta_crimen[TipoCarta.ARMA].nombre}"
        )
    
    def mover_jugador(self, jugador: Jugador, destino: HabitacionNombre) -> bool:
        """Mueve a un jugador a una habitación adyacente válida.

        Verifica que la partida esté en marcha, que el jugador tenga una
        posición asignada y que el movimiento sea válido según las conexiones
        del tablero.

        Args:
            jugador: Jugador que se quiere mover.
            destino: Habitación de destino.

        Returns:
            ``True`` si el movimiento fue ejecutado correctamente, ``False``
            en caso de error (partida no iniciada, jugador sin posición o
            movimiento inválido).
        """
        if not self.juego_iniciado:
            return False
        
        origen = jugador.habitacion_actual
        if origen is None:
            self.historial.append(f"❌ {jugador.nombre} no está en ninguna habitación")
            return False
        
        if not self.tablero.es_movimiento_valido(origen, destino):
            self.historial.append(
                f"❌ Movimiento inválido: {origen.value} → {destino.value}"
            )
            return False
        
        jugador.habitacion_actual = destino
        self.historial.append(
            f"🚶 {jugador.nombre} se mueve a {destino.value}"
        )
        return True
    
    def hacer_acusacion(
        self, 
        jugador: Jugador, 
        sospechoso: str, 
        habitacion: str, 
        arma: str
    ) -> Tuple[bool, Optional[str]]:
        """Procesa una acusación normal formulada por un jugador.

        Comprueba que el jugador esté en la habitación acusada y recorre al
        resto de jugadores (en orden de turno) para ver si alguno puede
        refutar la acusación mostrando una de sus cartas.

        Args:
            jugador: Jugador que formula la acusación.
            sospechoso: Nombre del sospechoso acusado.
            habitacion: Nombre de la habitación acusada.
            arma: Nombre del arma acusada.

        Returns:
            Tupla ``(exitosa, carta_revelada)``:

            - ``exitosa`` es ``True`` si la acusación fue procesada
              correctamente (independientemente de si fue refutada).
            - ``carta_revelada`` es el nombre de la carta con la que se
              refutó, o ``None`` si nadie pudo refutar.
        """
        if not self.juego_iniciado:
            return False, None
        
        # Verificar que el jugador está en la habitación acusada
        if jugador.habitacion_actual.value != habitacion:
            self.historial.append(
                f"❌ {jugador.nombre} debe estar en {habitacion} para acusar"
            )
            return False, None
        
        acusacion = Acusacion(sospechoso, habitacion, arma)
        self.historial.append(f"🔍 {jugador.nombre} acusa: {acusacion}")
        
        # Verificar si otros jugadores pueden refutar
        carta_refutada = None
        refutador = None
        
        for otro_jugador in self.gestor_jugadores.get_todos_los_jugadores():
            if otro_jugador == jugador:
                continue
            
            carta = otro_jugador.puede_refutar(sospechoso, habitacion, arma)
            if carta:
                carta_refutada = carta
                refutador = otro_jugador
                self.historial.append(
                    f"🛑 {otro_jugador.nombre} refuta mostrando: {carta.nombre}"
                )
                
                # El jugador que acusó elimina esa carta de sus notas
                jugador.agregar_nota(carta.tipo, carta.nombre, es_negativo=True)
                break
        
        if not carta_refutada:
            self.historial.append("✅ Nadie puede refutar la acusación")
        
        return True, carta_refutada.nombre if carta_refutada else None
    
    def acusacion_final(self, jugador: Jugador, acusacion: Acusacion) -> bool:
        """Procesa la acusación final con la que un jugador intenta ganar.

        Compara los tres elementos de la acusación con las cartas secretas del
        sobre del crimen. Si acierta, declara al jugador como ganador. Si
        falla, lo elimina de la partida.

        Args:
            jugador: Jugador que realiza la acusación final.
            acusacion: Acusación con el sospechoso, habitación y arma elegidos.

        Returns:
            ``True`` si la acusación era correcta y el jugador ha ganado,
            ``False`` si era incorrecta y el jugador queda eliminado.
        """
        if not self.juego_iniciado:
            return False
        
        self.historial.append(
            f"🎯 {jugador.nombre} hace acusación FINAL: {acusacion}"
        )
        
        # Verificar si la acusación es correcta
        es_correcto = (
            acusacion.sospechoso == self.carta_crimen[TipoCarta.SOSPECHOSO].nombre and
            acusacion.habitacion == self.carta_crimen[TipoCarta.HABITACION].nombre and
            acusacion.arma == self.carta_crimen[TipoCarta.ARMA].nombre
        )
        
        if es_correcto:
            self.ganador = jugador
            self.historial.append(f"🏆 ¡{jugador.nombre} GANA!")
            self.historial.append(f"   El crimen fue cometido por:")
            self.historial.append(f"   👤 {self.carta_crimen[TipoCarta.SOSPECHOSO].nombre}")
            self.historial.append(f"   📍 en {self.carta_crimen[TipoCarta.HABITACION].nombre}")
            self.historial.append(f"   🔪 con {self.carta_crimen[TipoCarta.ARMA].nombre}")
        else:
            self.historial.append(f"❌ {jugador.nombre} se equivoca y queda eliminado")
            self.gestor_jugadores.remover_jugador(jugador)
        
        return es_correcto
    
    def obtener_estado(self) -> Dict:
        """Devuelve un resumen del estado actual de la partida.

        Returns:
            Diccionario con los campos:

            - ``"jugadores"``: lista de dicts con ``nombre``, ``es_ia``,
              ``habitacion`` y número de ``cartas`` de cada jugador.
            - ``"turno_actual"``: índice del turno en curso.
            - ``"ganador"``: nombre del ganador o ``None``.
            - ``"historial"``: últimas 10 acciones registradas.
        """
        return {
            "jugadores": [
                {
                    "nombre": j.nombre,
                    "es_ia": j.es_ia,
                    "habitacion": j.habitacion_actual.value if j.habitacion_actual else None,
                    "cartas": len(j.cartas),
                }
                for j in self.gestor_jugadores.get_todos_los_jugadores()
            ],
            "turno_actual": self.gestor_jugadores.turno_actual,
            "ganador": self.ganador.nombre if self.ganador else None,
            "historial": self.historial[-10:],  # Últimas 10 acciones
        }
    
    def mostrar_tablero_completo(self) -> str:
        """Genera una representación visual completa del estado de la partida.

        Muestra cada habitación con los jugadores que se encuentran en ella,
        el jugador en turno y el ganador si la partida ha concluido.

        Returns:
            Cadena de texto multilínea lista para imprimir en consola.
        """
        output = []
        output.append("\n" + "=" * 50)
        output.append("🏰 ESTADO DE LA MANSIÓN BLACKWOOD")
        output.append("=" * 50)
        
        # Mostrar habitaciones con jugadores
        for hab_nombre in self.tablero.get_todas_las_habitaciones():
            jugadores_aqui = [
                j.nombre for j in self.gestor_jugadores.get_todos_los_jugadores()
                if j.habitacion_actual == hab_nombre
            ]
            
            output.append(f"\n📍 {hab_nombre.value}")
            if jugadores_aqui:
                output.append(f"   👥 Jugadores: {', '.join(jugadores_aqui)}")
        
        output.append("\n" + "-" * 50)
        output.append(f"🎲 Turno: {self.gestor_jugadores.jugador_actual().nombre if self.gestor_jugadores.jugador_actual() else 'N/A'}")
        
        if self.ganador:
            output.append(f"🏆 GANADOR: {self.ganador.nombre}")
        
        return "\n".join(output)


# Función de prueba / Demo
if __name__ == "__main__":
    print("🕵️ Misterio en la Mansión Blackwood")
    print("=" * 50)
    
    juego = Juego()
    
    # Configurar jugadores
    juego.configurar_juego([
        ("Detective Holmes", False),
        ("Miss Marple", False),
        ("Inspector Clouseau", True),
    ])
    
    # Iniciar partida
    juego.iniciar_partida()
    
    # Mostrar estado inicial
    print(juego.mostrar_tablero_completo())
    
    # Simular algunos movimientos
    jugador1 = juego.gestor_jugadores.jugador_actual()
    if jugador1:
        # Mover jugador
        from src.tablero import HabitacionNombre
        juego.mover_jugador(jugador1, HabitacionNombre.BIBLIOTECA)
        
        # Hacer una acusación
        juego.hacer_acusacion(
            jugador1,
            "Victoria Sterling",
            "Biblioteca",
            "Candelabro de bronce"
        )
    
    # Mostrar historial
    print("\n" + "=" * 50)
    print("📜 HISTORIAL DE ACCIONES:")
    for accion in juego.historial:
        print(accion)
