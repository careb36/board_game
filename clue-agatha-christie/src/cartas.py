"""
Misterio en la Mansión Blackwood - Sistema de Cartas
Inspirado en Agatha Christie

Este módulo define las clases que representan las cartas del juego:
- TipoCarta: enumeración de los tres tipos de carta (sospechoso, habitación, arma).
- Carta: una carta individual con nombre, tipo y descripción opcional.
- Mazo: gestión del conjunto completo de cartas, incluyendo la selección del
  sobre del crimen y la distribución de cartas entre jugadores.
"""

import random
from typing import List, Dict
from enum import Enum


class TipoCarta(Enum):
    """Tipos de carta posibles en el juego."""

    SOSPECHOSO = "sospechoso"
    HABITACION = "habitacion"
    ARMA = "arma"


class Carta:
    """Representa una carta individual del mazo.

    Attributes:
        nombre (str): Nombre identificador de la carta.
        tipo (TipoCarta): Categoría a la que pertenece la carta.
        descripcion (str): Descripción narrativa opcional de la carta.
    """

    def __init__(self, nombre: str, tipo: TipoCarta, descripcion: str = ""):
        """Inicializa una carta.

        Args:
            nombre: Nombre de la carta (p. ej. "Victoria Sterling").
            tipo: Categoría de la carta (sospechoso, habitación o arma).
            descripcion: Texto descriptivo opcional sobre la carta.
        """
        self.nombre = nombre
        self.tipo = tipo
        self.descripcion = descripcion
    
    def __repr__(self):
        return f"{self.nombre} ({self.tipo.value})"
    
    def __eq__(self, other):
        if isinstance(other, Carta):
            return self.nombre == other.nombre and self.tipo == other.tipo
        return False
    
    def __hash__(self):
        return hash((self.nombre, self.tipo))


class Mazo:
    """Gestiona el mazo completo de cartas del juego.

    Attributes:
        cartas (List[Carta]): Todas las cartas del mazo (21 en total).
        sobre_crimen (Dict[TipoCarta, Carta]): Las tres cartas seleccionadas
            como solución del crimen (sospechoso, habitación y arma).
    """
    
    def __init__(self):
        """Inicializa el mazo vacío."""
        self.cartas: List[Carta] = []
        self.sobre_crimen: Dict[TipoCarta, Carta] = {}
        
    def crear_cartas_base(self):
        """Crea las 21 cartas estándar del juego.

        Genera 6 cartas de tipo sospechoso, 9 de tipo habitación y
        6 de tipo arma, almacenándolas en ``self.cartas``.
        """
        # Sospechosos
        sospechosos = [
            ("Victoria Sterling", "La sobrina ambiciosa del Lord"),
            ("Coronel Marcus Webb", "El socio militar con secretos"),
            ("Isabella Rossi", "La medium italiana misteriosa"),
            ("Arthur Pembroke", "El mayordomo leal por décadas"),
            ("Lady Catherine Moore", "La viuda con pasado oscuro"),
            ("Dr. Heinrich Wolf", "El médico personal discreto"),
        ]
        
        # Habitaciones
        habitaciones = [
            "Biblioteca",
            "Salón Principal",
            "Comedor",
            "Cocina",
            "Invernadero",
            "Galería de Arte",
            "Estudio",
            "Dormitorio Principal",
            "Sótano",
        ]
        
        # Armas
        armas = [
            ("Candelabro de bronce", "Pesado y ornamentado"),
            ("Daga ceremonial", "Antigua y afilada"),
            ("Veneno para ratas", "Silencioso y letal"),
            ("Cuerda de piano", "Improvisada pero efectiva"),
            ("Pistola antigua", "Reliquia familiar cargada"),
            ("Estatua de mármol", "Obra de arte mortal"),
        ]
        
        # Crear cartas
        for nombre, desc in sospechosos:
            self.cartas.append(Carta(nombre, TipoCarta.SOSPECHOSO, desc))
        
        for nombre in habitaciones:
            self.cartas.append(Carta(nombre, TipoCarta.HABITACION))
        
        for nombre, desc in armas:
            self.cartas.append(Carta(nombre, TipoCarta.ARMA, desc))
    
    def preparar_juego(self) -> Dict[TipoCarta, Carta]:
        """Prepara el mazo para una nueva partida.

        Si las cartas aún no han sido creadas, invoca ``crear_cartas_base``.
        A continuación selecciona aleatoriamente una carta de cada tipo para
        formar el sobre del crimen, y baraja el resto.

        Returns:
            Un diccionario con dos entradas:

            - ``"crimen"`` → ``Dict[TipoCarta, Carta]``: las tres cartas del
              sobre del crimen.
            - ``"juego"`` → ``List[Carta]``: las 18 cartas restantes
              barajadas, listas para repartir entre los jugadores.
        """
        if not self.cartas:
            self.crear_cartas_base()
        
        # Separar por tipos
        sospechosos = [c for c in self.cartas if c.tipo == TipoCarta.SOSPECHOSO]
        habitaciones = [c for c in self.cartas if c.tipo == TipoCarta.HABITACION]
        armas = [c for c in self.cartas if c.tipo == TipoCarta.ARMA]
        
        # Seleccionar carta del crimen de cada tipo
        self.sobre_crimen[TipoCarta.SOSPECHOSO] = random.choice(sospechosos)
        self.sobre_crimen[TipoCarta.HABITACION] = random.choice(habitaciones)
        self.sobre_crimen[TipoCarta.ARMA] = random.choice(armas)
        
        # Remover cartas del crimen del mazo jugable
        cartas_juego = [
            c for c in self.cartas 
            if c not in self.sobre_crimen.values()
        ]
        
        # Barajar
        random.shuffle(cartas_juego)
        
        return {
            "juego": cartas_juego,
            "crimen": self.sobre_crimen
        }
    
    def obtener_carta(self, nombre: str) -> "Carta":
        """Busca y devuelve una carta por su nombre (insensible a mayúsculas).

        Args:
            nombre: Nombre de la carta a buscar.

        Returns:
            La instancia de ``Carta`` encontrada, o ``None`` si no existe.
        """
        for carta in self.cartas:
            if carta.nombre.lower() == nombre.lower():
                return carta
        return None
    
    def get_cartas_por_tipo(self, tipo: TipoCarta) -> List[Carta]:
        """Devuelve todas las cartas que pertenecen a un tipo dado.

        Args:
            tipo: Tipo de carta a filtrar (``TipoCarta.SOSPECHOSO``,
                ``TipoCarta.HABITACION`` o ``TipoCarta.ARMA``).

        Returns:
            Lista de cartas del tipo solicitado.
        """
        return [c for c in self.cartas if c.tipo == tipo]


# Función de prueba
if __name__ == "__main__":
    mazo = Mazo()
    resultado = mazo.preparar_juego()
    
    print("🕵️ Misterio en la Mansión Blackwood")
    print("=" * 40)
    print("\n📁 Sobre del Crimen:")
    for tipo, carta in resultado["crimen"].items():
        print(f"   {tipo.value}: {carta.nombre}")
    
    print(f"\n🃏 Cartas para repartir: {len(resultado['juego'])}")
    print(f"   - Sospechosos: {len([c for c in resultado['juego'] if c.tipo == TipoCarta.SOSPECHOSO])}")
    print(f"   - Habitaciones: {len([c for c in resultado['juego'] if c.tipo == TipoCarta.HABITACION])}")
    print(f"   - Armas: {len([c for c in resultado['juego'] if c.tipo == TipoCarta.ARMA])}")
