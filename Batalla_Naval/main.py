import numpy as np
import random
from utils import crear_tablero, colocar_barcos, disparar, mostrar_2_tableros, limpiar_pantalla


def main():

    tamaño = 12

    limpiar_pantalla()
    print("==== BATALLA NAVAL ====\n")

    tablero_jugador = crear_tablero(tamaño)
    tablero_maquina = crear_tablero(tamaño)

    print("📌 Colocando barcos...")
    colocar_barcos(tablero_jugador)
    colocar_barcos(tablero_maquina)

    print("✅ Barcos colocados!\n")
    input("Presiona Enter para comenzar...")

    turno = 1

    while True:

        limpiar_pantalla()
        print(f"==== TURNO {turno} ====\n")

        mostrar_2_tableros(tablero_jugador, tablero_maquina)

        # -----------------------
        # TURNO DEL JUGADOR
        # -----------------------
        while True:

            entrada = input("Ingresa fila+col (ej: A3) o S para salir: ").strip().upper()

            if entrada == "S":
                print("\n👋 Volviendo al menú mostrando tableros actuales...")
                mostrar_2_tableros(tablero_jugador, tablero_maquina)
                return

            if len(entrada) < 2:
                print("❌ Formato inválido")
                continue

            fila = ord(entrada[0]) - 65
            col = int(entrada[1:])

            if fila < 0 or fila >= tamaño or col < 0 or col >= tamaño:
                print("❌ Coordenadas fuera de rango")
                continue

            res = disparar((fila, col), tablero_maquina)

            print(f"\n🎯 Tu disparo en {chr(65+fila)}{col}: {res.upper()}")

            break

        # comprobar victoria jugador
        if not any("O" in row for row in tablero_maquina):
            print("\n🏆 ¡FELICIDADES! GANASTE 🏆")
            mostrar_2_tableros(tablero_jugador, tablero_maquina)
            break

        # -----------------------
        # TURNO DE LA MÁQUINA
        # -----------------------
        while True:

            f = random.randint(0, tamaño - 1)
            c = random.randint(0, tamaño - 1)

            if tablero_jugador[f, c] not in ["X", "A"]:
                break

        res_maq = disparar((f, c), tablero_jugador)

        print(f"\n🤖 Máquina disparó en {chr(65+f)}{c}: {res_maq.upper()}")

        # comprobar victoria máquina
        if not any("O" in row for row in tablero_jugador):
            print("\n🤖 LA MÁQUINA GANÓ 🤖")
            mostrar_2_tableros(tablero_jugador, tablero_maquina)
            break

        turno += 1

        input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    main()