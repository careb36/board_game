"""
Tests para Misterio en la Mansión Blackwood
"""

import unittest
import sys
import os

# Agregar el directorio raíz al path para importar los módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cartas import Mazo, Carta, TipoCarta
from src.tablero import Tablero, HabitacionNombre
from src.jugadores import Jugador, GestorJugadores
from src.juego import Juego, Acusacion


class TestCartas(unittest.TestCase):
    """Tests para el sistema de cartas"""
    
    def test_crear_mazo(self):
        mazo = Mazo()
        self.assertEqual(len(mazo.cartas), 0)
    
    def test_crear_cartas_base(self):
        mazo = Mazo()
        mazo.crear_cartas_base()
        
        # 6 sospechosos + 9 habitaciones + 6 armas = 21 cartas
        self.assertEqual(len(mazo.cartas), 21)
        
        sospechosos = [c for c in mazo.cartas if c.tipo == TipoCarta.SOSPECHOSO]
        habitaciones = [c for c in mazo.cartas if c.tipo == TipoCarta.HABITACION]
        armas = [c for c in mazo.cartas if c.tipo == TipoCarta.ARMA]
        
        self.assertEqual(len(sospechosos), 6)
        self.assertEqual(len(habitaciones), 9)
        self.assertEqual(len(armas), 6)
    
    def test_preparar_juego(self):
        mazo = Mazo()
        resultado = mazo.preparar_juego()
        
        # El sobre del crimen debe tener 3 cartas
        self.assertEqual(len(resultado["crimen"]), 3)
        
        # Las cartas para jugar deben ser 18 (21 - 3)
        self.assertEqual(len(resultado["juego"]), 18)
    
    def test_obtener_carta(self):
        mazo = Mazo()
        mazo.crear_cartas_base()
        
        carta = mazo.obtener_carta("Victoria Sterling")
        self.assertIsNotNone(carta)
        self.assertEqual(carta.tipo, TipoCarta.SOSPECHOSO)
        
        carta_inexistente = mazo.obtener_carta("No Existe")
        self.assertIsNone(carta_inexistente)


class TestTablero(unittest.TestCase):
    """Tests para el tablero"""
    
    def test_crear_tablero(self):
        tablero = Tablero()
        self.assertEqual(len(tablero.habitaciones), 9)
    
    def test_todas_las_habitaciones_existentes(self):
        tablero = Tablero()
        
        habitaciones_esperadas = [
            HabitacionNombre.BIBLIOTECA,
            HabitacionNombre.SALON,
            HabitacionNombre.COMEDOR,
            HabitacionNombre.COCINA,
            HabitacionNombre.INVERNADERO,
            HabitacionNombre.GALERIA,
            HabitacionNombre.ESTUDIO,
            HabitacionNombre.DORMITORIO,
            HabitacionNombre.SOTANO,
        ]
        
        for hab in habitaciones_esperadas:
            self.assertIn(hab, tablero.habitaciones)
    
    def test_conexiones_validas(self):
        tablero = Tablero()
        
        # Biblioteca debe estar conectada a Comedor
        self.assertTrue(tablero.es_movimiento_valido(
            HabitacionNombre.BIBLIOTECA,
            HabitacionNombre.COMEDOR
        ))
        
        # Biblioteca NO debe estar conectada directamente al Sótano
        self.assertFalse(tablero.es_movimiento_valido(
            HabitacionNombre.BIBLIOTECA,
            HabitacionNombre.SOTANO
        ))
    
    def test_conexiones_bidireccionales(self):
        tablero = Tablero()
        
        # Si A está conectado a B, entonces B debe estar conectado a A
        if tablero.es_movimiento_valido(HabitacionNombre.BIBLIOTECA, HabitacionNombre.SALON):
            self.assertTrue(tablero.es_movimiento_valido(HabitacionNombre.SALON, HabitacionNombre.BIBLIOTECA))


class TestJugadores(unittest.TestCase):
    """Tests para el sistema de jugadores"""
    
    def test_crear_jugador(self):
        jugador = Jugador("Detective Holmes")
        
        self.assertEqual(jugador.nombre, "Detective Holmes")
        self.assertFalse(jugador.es_ia)
        self.assertEqual(len(jugador.cartas), 0)
    
    def test_agregar_carta(self):
        jugador = Jugador("Test")
        mazo = Mazo()
        mazo.crear_cartas_base()
        
        carta = mazo.cartas[0]
        jugador.agregar_carta(carta)
        
        self.assertEqual(len(jugador.cartas), 1)
        self.assertTrue(jugador.tiene_carta(carta))
    
    def test_puede_refutar(self):
        jugador = Jugador("Test")
        mazo = Mazo()
        mazo.crear_cartas_base()
        
        # Agregar una carta específica
        carta_sospechoso = [c for c in mazo.cartas if c.tipo == TipoCarta.SOSPECHOSO][0]
        jugador.agregar_carta(carta_sospechoso)
        
        # Debe poder refutar con esa carta
        refutacion = jugador.puede_refutar(carta_sospechoso.nombre, "Otra Habitación", "Otra Arma")
        self.assertEqual(refutacion, carta_sospechoso)
    
    def test_gestor_jugadores(self):
        gestor = GestorJugadores()
        
        gestor.agregar_jugador("Jugador 1")
        gestor.agregar_jugador("Jugador 2", es_ia=True)
        
        self.assertEqual(len(gestor.get_todos_los_jugadores()), 2)
        
        jugador = gestor.obtener_jugador("Jugador 1")
        self.assertIsNotNone(jugador)
        self.assertFalse(jugador.es_ia)


class TestJuego(unittest.TestCase):
    """Tests para la lógica principal del juego"""
    
    def test_crear_juego(self):
        juego = Juego()
        
        self.assertFalse(juego.juego_iniciado)
        self.assertIsNone(juego.ganador)
    
    def test_configurar_juego(self):
        juego = Juego()
        
        resultado = juego.configurar_juego([
            ("Holmes", False),
            ("Marple", False),
        ])
        
        self.assertTrue(resultado)
        self.assertEqual(len(juego.gestor_jugadores.get_todos_los_jugadores()), 2)
    
    def test_configurar_juego_invalido(self):
        juego = Juego()
        
        # Menos de 2 jugadores
        resultado = juego.configurar_juego([("Solo", False)])
        self.assertFalse(resultado)
        
        # Más de 6 jugadores
        resultado = juego.configurar_juego([
            ("J1", False), ("J2", False), ("J3", False),
            ("J4", False), ("J5", False), ("J6", False),
            ("J7", False),
        ])
        self.assertFalse(resultado)
    
    def test_iniciar_partida(self):
        juego = Juego()
        juego.configurar_juego([
            ("Holmes", False),
            ("Marple", False),
            ("Poirot", True),
        ])
        
        resultado = juego.iniciar_partida()
        
        self.assertTrue(resultado)
        self.assertTrue(juego.juego_iniciado)
        self.assertIsNotNone(juego.carta_crimen)
    
    def test_movimiento_valido(self):
        juego = Juego()
        # Se requieren al menos 2 jugadores
        juego.configurar_juego([("Test1", False), ("Test2", False)])
        juego.iniciar_partida()
        
        # Obtener el primer jugador directamente de la lista
        jugadores = juego.gestor_jugadores.get_todos_los_jugadores()
        self.assertGreater(len(jugadores), 0)
        jugador = jugadores[0]
        
        # El jugador debe tener una habitación inicial asignada
        self.assertIsNotNone(jugador)
        self.assertIsNotNone(jugador.habitacion_actual)
        
        # Mover a una habitación válida desde la posición inicial
        vecinas = juego.tablero.obtener_vecinas(jugador.habitacion_actual)
        if vecinas:
            resultado = juego.mover_jugador(jugador, vecinas[0])
            self.assertTrue(resultado)
            self.assertEqual(jugador.habitacion_actual, vecinas[0])
    
    def test_acusacion(self):
        juego = Juego()
        juego.configurar_juego([
            ("Holmes", False),
            ("Marple", False),
        ])
        juego.iniciar_partida()
        
        jugador = juego.gestor_jugadores.jugador_actual()
        
        # Obtener nombres válidos para la acusación
        sospechoso = juego.carta_crimen[TipoCarta.SOSPECHOSO].nombre
        habitacion = jugador.habitacion_actual.value if jugador.habitacion_actual else "Biblioteca"
        arma = "Candelabro de bronce"
        
        # Mover jugador a la habitación correcta si es necesario
        from src.tablero import HabitacionNombre
        for hab in juego.tablero.get_todas_las_habitaciones():
            if hab.value == habitacion:
                jugador.habitacion_actual = hab
                break
        
        exito, refutacion = juego.hacer_acusacion(jugador, sospechoso, habitacion, arma)
        
        # La acusación debería ser procesada
        self.assertTrue(exito)


class TestAcusacion(unittest.TestCase):
    """Tests para la clase Acusacion"""
    
    def test_crear_acusacion(self):
        acusacion = Acusacion("Victoria Sterling", "Biblioteca", "Candelabro de bronce")
        
        self.assertEqual(acusacion.sospechoso, "Victoria Sterling")
        self.assertEqual(acusacion.habitacion, "Biblioteca")
        self.assertEqual(acusacion.arma, "Candelabro de bronce")
    
    def test_repr_acusacion(self):
        acusacion = Acusacion("Victoria Sterling", "Biblioteca", "Candelabro")
        
        esperado = "Victoria Sterling en Biblioteca con Candelabro"
        self.assertEqual(repr(acusacion), esperado)


if __name__ == "__main__":
    unittest.main()
