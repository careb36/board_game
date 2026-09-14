"""
Misterio en la Mansión Blackwood - Lógica Principal del Juego
Inspirado en Agatha Christie
"""

import random
from typing import List, Dict, Optional, Tuple
from src.cartas import Mazo, Carta, TipoCarta
from src.tablero import Tablero, HabitacionNombre
from src.jugadores import GestorJugadores, Jugador


class Acusacion:
    """Representa una acusación formulada por un jugador"""
    
    def __init__(self, sospechoso: str, habitacion: str, arma: str):
        self.sospechoso = sospechoso
        self.habitacion = habitacion
        self.arma = arma
    
    def __repr__(self):
        return f"{self.sospechoso} en {self.habitacion} con {self.arma}"


class Juego:
    """Clase principal que gestiona toda la partida"""
    
    def __init__(self):
        self.mazo = Mazo()
        self.tablero = Tablero()
        self.gestor_jugadores = GestorJugadores()
        self.carta_crimen: Dict[TipoCarta, Carta] = {}
        self.juego_iniciado = False
        self.ganador: Optional[Jugador] = None
        self.historial: List[str] = []
    
    def configurar_juego(self, nombres_jugadores: List[Tuple[str, bool]]) -> bool:
        """
        Configura el juego con los jugadores dados
        nombres_jugadores: lista de tuplas (nombre, es_ia)
        """
        if len(nombres_jugadores) < 2 or len(nombres_jugadores) > 6:
            self.historial.append("❌ Error: Se requieren 2-6 jugadores")
            return False
        
        for nombre, es_ia in nombres_jugadores:
            self.gestor_jugadores.agregar_jugador(nombre, es_ia)
        
        self.historial.append(f"✅ {len(nombres_jugadores)} jugadores configurados")
        return True
    
    def iniciar_partida(self) -> bool:
        """Inicializa una nueva partida"""
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
        # self.historial.append(f"📁 Crimen: {self._obtener_resumen_crimen()}")
        
        return True
    
    def _obtener_resumen_crimen(self) -> str:
        """Retorna resumen del crimen (solo para debugging/testing)"""
        return (
            f"{self.carta_crimen[TipoCarta.SOSPECHOSO].nombre} + "
            f"{self.carta_crimen[TipoCarta.HABITACION].nombre} + "
            f"{self.carta_crimen[TipoCarta.ARMA].nombre}"
        )
    
    def mover_jugador(self, jugador: Jugador, destino: HabitacionNombre) -> bool:
        """Mueve un jugador a una habitación válida"""
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
        """
        Un jugador formula una acusación
        Retorna (exitosa, carta_revelada o None)
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
        """
        Un jugador hace una acusación final para ganar
        Retorna True si gana, False si pierde
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
        """Retorna el estado actual del juego"""
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
        """Muestra el estado completo del tablero"""
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
