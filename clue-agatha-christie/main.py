"""
Misterio en la Mansión Blackwood - Módulo Principal
Inspirado en Agatha Christie
"""

from src.juego import Juego, Acusacion
from src.tablero import HabitacionNombre
from src.utils import mostrar_menu, esperar_enter, limpiar_pantalla


def configurar_jugadores() -> list:
    """Configura los jugadores para la partida"""
    print("\n" + "=" * 50)
    print("👥 CONFIGURACIÓN DE JUGADORES")
    print("=" * 50)
    
    jugadores = []
    
    while True:
        nombre = input(f"\nNombre del jugador {len(jugadores) + 1} (o 'inicio' para comenzar): ").strip()
        
        if nombre.lower() == 'inicio':
            if len(jugadores) < 2:
                print("❌ Se necesitan al menos 2 jugadores")
                continue
            break
        
        if not nombre:
            print("❌ Nombre inválido")
            continue
        
        # Preguntar si es IA
        es_ia = input(f"¿{nombre} es controlado por la IA? (s/n): ").lower() == 's'
        jugadores.append((nombre, es_ia))
        print(f"✅ {nombre} agregado {'(IA)' if es_ia else ''}")
        
        if len(jugadores) >= 6:
            print("⚠️ Máximo de jugadores alcanzado (6)")
            break
    
    return jugadores


def turno_jugador(juego: Juego):
    """Gestiona el turno de un jugador humano"""
    jugador = juego.gestor_jugadores.jugador_actual()
    
    if not jugador:
        return
    
    print("\n" + "=" * 50)
    print(f"🎲 TURNO DE: {jugador.nombre}")
    print("=" * 50)
    print(f"📍 Ubicación actual: {jugador.habitacion_actual.value if jugador.habitacion_actual else 'N/A'}")
    
    opciones = [
        "Ver habitaciones conectadas",
        "Moverse a otra habitación",
        "Hacer una acusación",
        "Ver mis cartas",
        "ACUSACIÓN FINAL (¡Ganar!)",
        "Pasar turno",
    ]
    
    seleccion = mostrar_menu(opciones, f"Acciones de {jugador.nombre}")
    
    if seleccion == 0:  # Ver habitaciones conectadas
        vecinas = juego.tablero.obtener_vecinas(jugador.habitacion_actual)
        print("\n🚪 Habitaciones conectadas:")
        for v in vecinas:
            print(f"   • {v.value}")
        esperar_enter()
    
    elif seleccion == 1:  # Moverse
        vecinas = juego.tablero.obtener_vecinas(jugador.habitacion_actual)
        if not vecinas:
            print("❌ No hay habitaciones conectadas")
            esperar_enter()
            return
        
        print("\n¿A qué habitación quieres moverte?")
        for i, hab in enumerate(vecinas, 1):
            print(f"   {i}. {hab.value}")
        
        try:
            eleccion = int(input("Tu elección: ")) - 1
            if 0 <= eleccion < len(vecinas):
                destino = vecinas[eleccion]
                if juego.mover_jugador(jugador, destino):
                    print(f"✅ Te has movido a {destino.value}")
                else:
                    print("❌ Movimiento no válido")
            else:
                print("❌ Opción inválida")
        except ValueError:
            print("❌ Entrada inválida")
        
        esperar_enter()
    
    elif seleccion == 2:  # Hacer acusación
        hacer_acusacion(juego, jugador)
    
    elif seleccion == 3:  # Ver cartas
        print("\n🃏 TUS CARTAS:")
        for carta in jugador.cartas:
            print(f"   • {carta.nombre}")
        esperar_enter()
    
    elif seleccion == 4:  # Acusación final
        hacer_acusacion_final(juego, jugador)
    
    elif seleccion == 5:  # Pasar turno
        print("⏭️ Turno pasado")
        esperar_enter()
    
    # Avanzar al siguiente turno
    juego.gestor_jugadores.siguiente_turno()


def hacer_acusacion(juego: Juego, jugador):
    """Permite al jugador hacer una acusación normal"""
    print("\n🔍 FORMULAR ACUSACIÓN")
    print("-" * 40)
    
    # Obtener sospechoso
    sospechosos = [c.nombre for c in juego.mazo.get_cartas_por_tipo('sospechoso')]
    print("\nSospechosos:")
    for i, s in enumerate(sospechosos, 1):
        print(f"   {i}. {s}")
    
    try:
        idx_s = int(input("\nSelecciona sospechoso: ")) - 1
        if not (0 <= idx_s < len(sospechosos)):
            print("❌ Opción inválida")
            esperar_enter()
            return
        sospechoso = sospechosos[idx_s]
    except ValueError:
        print("❌ Entrada inválida")
        esperar_enter()
        return
    
    # Obtener arma
    armas = [c.nombre for c in juego.mazo.get_cartas_por_tipo('arma')]
    print("\nArmas:")
    for i, a in enumerate(armas, 1):
        print(f"   {i}. {a}")
    
    try:
        idx_a = int(input("\nSelecciona arma: ")) - 1
        if not (0 <= idx_a < len(armas)):
            print("❌ Opción inválida")
            esperar_enter()
            return
        arma = armas[idx_a]
    except ValueError:
        print("❌ Entrada inválida")
        esperar_enter()
        return
    
    # La habitación es la actual
    habitacion = jugador.habitacion_actual.value
    
    exito, refutacion = juego.hacer_acusacion(jugador, sospechoso, habitacion, arma)
    
    if exito:
        if refutacion:
            print(f"\n🛑 Tu acusación fue REFUTADA con: {refutacion}")
        else:
            print("\n✅ Nadie pudo refutar tu acusación")
    else:
        print("\n❌ No puedes hacer esa acusación desde aquí")
    
    esperar_enter()


def hacer_acusacion_final(juego: Juego, jugador):
    """Permite al jugador hacer una acusación final para ganar"""
    print("\n🎯 ¡ACUSACIÓN FINAL!")
    print("=" * 40)
    print("⚠️ Si fallas, quedarás eliminado del juego")
    
    confirm = input("\n¿Estás seguro? (s/n): ").lower()
    if confirm != 's':
        print("❌ Acusación cancelada")
        esperar_enter()
        return
    
    # Obtener sospechoso
    sospechosos = [c.nombre for c in juego.mazo.get_cartas_por_tipo('sospechoso')]
    print("\nSospechosos:")
    for i, s in enumerate(sospechosos, 1):
        print(f"   {i}. {s}")
    
    try:
        idx_s = int(input("\nSelecciona sospechoso: ")) - 1
        sospechoso = sospechosos[idx_s]
    except (ValueError, IndexError):
        print("❌ Opción inválida")
        esperar_enter()
        return
    
    # Obtener habitación
    habitaciones = [h.value for h in HabitacionNombre]
    print("\nHabitaciones:")
    for i, h in enumerate(habitaciones, 1):
        print(f"   {i}. {h}")
    
    try:
        idx_h = int(input("\nSelecciona habitación: ")) - 1
        habitacion = habitaciones[idx_h]
    except (ValueError, IndexError):
        print("❌ Opción inválida")
        esperar_enter()
        return
    
    # Obtener arma
    armas = [c.nombre for c in juego.mazo.get_cartas_por_tipo('arma')]
    print("\nArmas:")
    for i, a in enumerate(armas, 1):
        print(f"   {i}. {a}")
    
    try:
        idx_a = int(input("\nSelecciona arma: ")) - 1
        arma = armas[idx_a]
    except (ValueError, IndexError):
        print("❌ Opción inválida")
        esperar_enter()
        return
    
    acusacion = Acusacion(sospechoso, habitacion, arma)
    gano = juego.acusacion_final(jugador, acusacion)
    
    if gano:
        print("\n" + "🎉" * 20)
        print("¡FELICIDADES! Has resuelto el misterio de la Mansión Blackwood")
        print("🎉" * 20)
    else:
        print("\n❌ Tu acusación era incorrecta. Quedas eliminado.")
    
    esperar_enter()


def main():
    """Función principal del juego"""
    print("\n" + "=" * 50)
    print("🕵️ MISTERIO EN LA MANSIÓN BLACKWOOD")
    print("   Un juego inspirado en Agatha Christie")
    print("=" * 50)
    
    juego = Juego()
    
    # Menú principal
    while True:
        opciones = [
            "Nueva Partida",
            "Créditos",
            "Salir",
        ]
        
        seleccion = mostrar_menu(opciones, "Menú Principal")
        
        if seleccion == 0:  # Nueva Partida
            jugadores = configurar_jugadores()
            
            if juego.configurar_juego(jugadores):
                if juego.iniciar_partida():
                    print("\n✅ ¡Partida iniciada!")
                    print(juego.mostrar_tablero_completo())
                    
                    # Bucle principal del juego
                    while not juego.ganador:
                        turno_jugador(juego)
                        
                        # Verificar si quedan jugadores
                        if not juego.gestor_jugadores.get_todos_los_jugadores():
                            print("\n❌ No quedan jugadores. El juego termina sin ganador.")
                            break
                    
                    if juego.ganador:
                        print(f"\n🏆 ¡{juego.ganador.nombre} ha ganado!")
        
        elif seleccion == 1:  # Créditos
            print("\n" + "=" * 50)
            print("📜 CRÉDITOS")
            print("=" * 50)
            print("""
            MISTERIO EN LA MANSIÓN BLACKWOOD
            
            Inspirado en las obras de Agatha Christie
            
            Desarrollado con:
            - Python 3.10+
            - context-mode (gestión de contexto)
            - aider (desarrollo asistido por IA)
            - pi-subagents (agentes especializados)
            
            ¡Gracias por jugar!
            """)
            esperar_enter()
        
        elif seleccion == 2:  # Salir
            print("\n👋 ¡Gracias por jugar!")
            print("   Hasta pronto, detective...")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Juego interrumpido. ¡Hasta pronto!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("   Por favor, reporta este error.")
