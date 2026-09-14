"""
Misterio en la Mansión Blackwood - Sistema de Cartas
Inspirado en Agatha Christie
"""

import random
from typing import List, Dict
from enum import Enum


class TipoCarta(Enum):
    SOSPECHOSO = "sospechoso"
    HABITACION = "habitacion"
    ARMA = "arma"


class Carta:
    def __init__(self, nombre: str, tipo: TipoCarta, descripcion: str = ""):
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
    """Gestiona el mazo de cartas del juego"""
    
    def __init__(self):
        self.cartas: List[Carta] = []
        self.sobre_crimen: Dict[TipoCarta, Carta] = {}
        
    def crear_cartas_base(self):
        """Crea las cartas estándar del juego"""
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
    
    def preparar_juego(self) -> Dict[str, object]:
        """
        Prepara el juego seleccionando las cartas del crimen
        y barajando el resto
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
    
    def obtener_carta(self, nombre: str) -> Carta:
        """Busca una carta por nombre"""
        for carta in self.cartas:
            if carta.nombre.lower() == nombre.lower():
                return carta
        return None
    
    def get_cartas_por_tipo(self, tipo: TipoCarta) -> List[Carta]:
        """Obtiene todas las cartas de un tipo"""
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
