# utils.py
import numpy as np
import random
import os

# -----------------------
# Limpiar pantalla
# -----------------------
def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

# -----------------------
# Crear tablero
# -----------------------
def crear_tablero(tamaño=12):
    return np.full((tamaño, tamaño), "_")

# -----------------------
# Colocar barco en posiciones dadas
# -----------------------
def colocar_barco(barco, tablero):
    for (f, c) in barco: # fila y columna
        tablero[f, c] = "O"

# -----------------------
# Crear un barco de tamaño "eslora" aleatorio
# -----------------------
def crear_barco(eslora, tablero):
    n = tablero.shape[0]
    while True:
        fila = random.randint(0, n-1)
        col = random.randint(0, n-1)
        direccion = random.choice(["N", "S", "E", "O"])
        posiciones = []
        valido = True
        for i in range(eslora):
            if direccion == "N":
                f, c = fila - i, col
            elif direccion == "S":
                f, c = fila + i, col
            elif direccion == "E":
                f, c = fila, col + i
            elif direccion == "O":
                f, c = fila, col - i
            if f < 0 or f >= n or c < 0 or c >= n or tablero[f, c] != "_":
                valido = False
                break
            posiciones.append((f, c))
        if valido:
            return posiciones

# -----------------------
# Colocar lista de barcos
# -----------------------
def colocar_barcos(tablero):
    barcos = []
    lista_esloras = [2,2,3,3,4]  # 5 barcos posicionados
    for eslora in lista_esloras:
        barco = crear_barco(eslora, tablero)
        colocar_barco(barco, tablero)
        barcos.append(barco)
    return barcos

# -----------------------
# Disparo
# -----------------------
def disparar(casilla, tablero):
    f, c = casilla
    if tablero[f, c] == "O":
        tablero[f, c] = "X"
        return "impacto"
    elif tablero[f, c] == "_":
        tablero[f, c] = "A"
        return "agua"
    else:
        return "repetido"

# -----------------------
# Mostrar tablero
# -----------------------
def mostrar_2_tableros(tab_jugador, tab_maquina):
    n = tab_jugador.shape[0]

    print("\n        🚢 TU FLOTA                    👾 FLOTA ENEMIGA")
    
    # Encabezado columnas
    columnas = " " + " ".join([str(i) for i in range(n)])
    print(columnas + "        " + columnas)

    for i in range(n):

        # TABLERO JUGADOR (mostrar todo)
        fila_j = []
        for celda in tab_jugador[i]:
            if celda == " ":
                fila_j.append(".")
            else:
                fila_j.append(celda)

        # TABLERO MAQUINA (ocultar barcos)
        fila_m = []
        for celda in tab_maquina[i]:
            if celda == "O":
                fila_m.append("_")  # ocultar barco
            elif celda == " ":
                fila_m.append(".")
            else:
                fila_m.append(celda)  # mostrar X o A

        letra = chr(65 + i)

        print(
            f"{letra}  {' '.join(fila_j)}      "
            f"{letra}  {' '.join(fila_m)}"
        )

    print("\nO = barco | X = impacto | A = agua | . = sin disparar\n")