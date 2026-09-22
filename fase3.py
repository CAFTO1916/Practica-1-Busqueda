# Fase 3 - Busqueda local

import math
import random
import time
import networkx as nx
import matplotlib.pyplot as plt

from fase2 import cargar_grafo_urbano
from fase2 import a_estrella
from fase2 import heuristica_haversine


# --------------------------------------------------
# SELECCION DE PUNTOS
# --------------------------------------------------

def seleccionar_puntos_entrega(G, cantidad=10):
    componente_mayor = max(nx.strongly_connected_components(G), key=len)
    nodos = list(componente_mayor)

    puntos = random.sample(nodos, cantidad)

    return puntos


# --------------------------------------------------
# DISTANCIAS CON A*
# --------------------------------------------------

def distancia_entre_nodos(G, origen, destino):

    def h(nodo, destino):
        return heuristica_haversine(G, nodo, destino)

    resultado = a_estrella(G, origen, destino, h)

    return resultado[3]


def calcular_distancias(G, puntos):
    distancias = {}

    total = len(puntos) * (len(puntos) - 1)
    contador = 0

    print("\nCalculando distancias entre los puntos...")

    for origen in puntos:

        for destino in puntos:

            if origen != destino:
                distancia = distancia_entre_nodos(G, origen, destino)

                distancias[(origen, destino)] = distancia

                contador = contador + 1

                print(
                    "Distancia",
                    contador,
                    "de",
                    total,
                    end="\r"
                )

    print("\nDistancias calculadas correctamente.")

    return distancias


# --------------------------------------------------
# COSTO DE UNA RUTA
# --------------------------------------------------

def costo_ruta(ruta, distancias):
    total = 0.0

    for i in range(len(ruta) - 1):
        origen = ruta[i]
        destino = ruta[i + 1]

        total = total + distancias[(origen, destino)]

    return total


# --------------------------------------------------
# OPERADOR 2-OPT
# --------------------------------------------------

def vecino_2opt(ruta):
    nueva_ruta = ruta.copy()

    i, j = random.sample(range(len(ruta)), 2)

    if i > j:
        i, j = j, i

    nueva_ruta[i:j + 1] = reversed(nueva_ruta[i:j + 1])

    return nueva_ruta


# --------------------------------------------------
# RECOCIDO SIMULADO
# --------------------------------------------------

def recocido_simulado(
    ruta_inicial,
    distancias,
    temperatura_inicial=5000,
    alpha=0.995,
    temperatura_minima=1
):
    ruta_actual = ruta_inicial.copy()
    costo_actual = costo_ruta(ruta_actual, distancias)

    mejor_ruta = ruta_actual.copy()
    mejor_costo = costo_actual

    temperatura = temperatura_inicial

    historial = [mejor_costo]

    while temperatura > temperatura_minima:

        ruta_vecina = vecino_2opt(ruta_actual)

        costo_vecino = costo_ruta(
            ruta_vecina,
            distancias
        )

        diferencia = costo_vecino - costo_actual

        if diferencia < 0:
            aceptar = True

        else:
            probabilidad = math.exp(
                -diferencia / temperatura
            )

            aceptar = random.random() < probabilidad

        if aceptar:
            ruta_actual = ruta_vecina
            costo_actual = costo_vecino

        if costo_actual < mejor_costo:
            mejor_ruta = ruta_actual.copy()
            mejor_costo = costo_actual

        historial.append(mejor_costo)

        temperatura = temperatura * alpha

    return mejor_ruta, mejor_costo, historial


# --------------------------------------------------
# CRUCE OX
# --------------------------------------------------

def cruce_ox(padre1, padre2):
    cantidad = len(padre1)

    i, j = random.sample(range(cantidad), 2)

    if i > j:
        i, j = j, i

    hijo = [None] * cantidad

    hijo[i:j + 1] = padre1[i:j + 1]

    posicion = (j + 1) % cantidad

    orden_padre2 = padre2[j + 1:] + padre2[:j + 1]

    for punto in orden_padre2:

        if punto not in hijo:

            hijo[posicion] = punto

            posicion = (posicion + 1) % cantidad

    return hijo


# --------------------------------------------------
# MUTACION POR INTERCAMBIO
# --------------------------------------------------

def mutacion_swap(ruta, probabilidad=0.10):
    nueva_ruta = ruta.copy()

    if random.random() < probabilidad:

        i, j = random.sample(
            range(len(nueva_ruta)),
            2
        )

        nueva_ruta[i], nueva_ruta[j] = (
            nueva_ruta[j],
            nueva_ruta[i]
        )

    return nueva_ruta


# --------------------------------------------------
# SELECCION POR TORNEO
# --------------------------------------------------

def seleccion_torneo(
    poblacion,
    distancias,
    cantidad=3
):
    candidatos = random.sample(
        poblacion,
        cantidad
    )

    mejor = candidatos[0]

    for candidato in candidatos[1:]:

        if costo_ruta(candidato, distancias) < costo_ruta(mejor, distancias):
            mejor = candidato

    return mejor.copy()


# --------------------------------------------------
# ALGORITMO GENETICO
# --------------------------------------------------

def algoritmo_genetico(
    puntos,
    distancias,
    tamano_poblacion=50,
    generaciones=200,
    probabilidad_mutacion=0.10
):
    poblacion = []

    poblacion.append(puntos.copy())

    for _ in range(tamano_poblacion - 1):

        individuo = puntos.copy()

        random.shuffle(individuo)

        poblacion.append(individuo)

    mejor_ruta = min(
        poblacion,
        key=lambda ruta: costo_ruta(ruta, distancias)
    ).copy()

    mejor_costo = costo_ruta(
        mejor_ruta,
        distancias
    )

    historial = [mejor_costo]

    for _ in range(generaciones):

        elite = min(
            poblacion,
            key=lambda ruta: costo_ruta(ruta, distancias)
        ).copy()

        nueva_poblacion = [elite]

        while len(nueva_poblacion) < tamano_poblacion:

            padre1 = seleccion_torneo(
                poblacion,
                distancias
            )

            padre2 = seleccion_torneo(
                poblacion,
                distancias
            )

            hijo1 = cruce_ox(
                padre1,
                padre2
            )

            hijo2 = cruce_ox(
                padre2,
                padre1
            )

            hijo1 = mutacion_swap(
                hijo1,
                probabilidad_mutacion
            )

            hijo2 = mutacion_swap(
                hijo2,
                probabilidad_mutacion
            )

            nueva_poblacion.append(hijo1)

            if len(nueva_poblacion) < tamano_poblacion:
                nueva_poblacion.append(hijo2)

        poblacion = nueva_poblacion

        mejor_generacion = min(
            poblacion,
            key=lambda ruta: costo_ruta(ruta, distancias)
        )

        costo_generacion = costo_ruta(
            mejor_generacion,
            distancias
        )

        if costo_generacion < mejor_costo:
            mejor_costo = costo_generacion
            mejor_ruta = mejor_generacion.copy()

        historial.append(mejor_costo)

    return mejor_ruta, mejor_costo, historial


# --------------------------------------------------
# RUTAS ALEATORIAS
# --------------------------------------------------

def evaluar_rutas_aleatorias(
    puntos,
    distancias,
    cantidad=100
):
    mejor_ruta = None
    mejor_costo = float("inf")

    suma_costos = 0.0

    for _ in range(cantidad):

        ruta = puntos.copy()

        random.shuffle(ruta)

        costo = costo_ruta(
            ruta,
            distancias
        )

        suma_costos = suma_costos + costo

        if costo < mejor_costo:
            mejor_costo = costo
            mejor_ruta = ruta.copy()

    promedio = suma_costos / cantidad

    return mejor_ruta, mejor_costo, promedio


# --------------------------------------------------
# GRAFICA DE CONVERGENCIA
# --------------------------------------------------

def guardar_grafica(historial_sa, historial_ga):

    plt.figure(figsize=(10, 5))

    plt.plot(
        historial_sa,
        label="Recocido Simulado"
    )

    plt.plot(
        historial_ga,
        label="Algoritmo Genetico"
    )

    plt.xlabel("Iteracion")
    plt.ylabel("Distancia en metros")

    plt.title(
        "Convergencia de los algoritmos"
    )

    plt.legend()

    plt.grid()

    plt.savefig(
        "convergencia_fase3.png",
        dpi=150
    )

    plt.close()


# --------------------------------------------------
# PROGRAMA PRINCIPAL
# --------------------------------------------------

if __name__ == "__main__":

    random.seed(42)

    G, G_proyectado = cargar_grafo_urbano()

    print("\nGrafo cargado desde Fase 3.")

    puntos_entrega = seleccionar_puntos_entrega(
        G,
        10
    )

    print("\nPuntos de entrega:")

    print(puntos_entrega)

    distancias = calcular_distancias(
        G,
        puntos_entrega
    )

    costo_inicial = costo_ruta(
        puntos_entrega,
        distancias
    )

    print(
        "\nCosto de la ruta inicial:",
        round(costo_inicial, 2),
        "metros"
    )

    # ----------------------------------------------
    # RUTAS ALEATORIAS
    # ----------------------------------------------

    random.seed(100)

    mejor_aleatoria, costo_aleatorio, promedio_aleatorio = evaluar_rutas_aleatorias(
        puntos_entrega,
        distancias,
        100
    )

    print(
        "\nPromedio de 100 rutas aleatorias:",
        round(promedio_aleatorio, 2),
        "metros"
    )

    print(
        "Mejor ruta aleatoria:",
        round(costo_aleatorio, 2),
        "metros"
    )

    # ----------------------------------------------
    # RECOCIDO SIMULADO
    # ----------------------------------------------

    random.seed(200)

    inicio_sa = time.perf_counter()

    ruta_sa, costo_sa, historial_sa = recocido_simulado(
        puntos_entrega,
        distancias
    )

    fin_sa = time.perf_counter()

    tiempo_sa = fin_sa - inicio_sa

    print("\n--- RECOCIDO SIMULADO ---")

    print("Ruta:")
    print(ruta_sa)

    print(
        "Costo:",
        round(costo_sa, 2),
        "metros"
    )

    print(
        "Tiempo:",
        round(tiempo_sa, 4),
        "segundos"
    )

    # ----------------------------------------------
    # ALGORITMO GENETICO
    # ----------------------------------------------

    random.seed(300)

    inicio_ga = time.perf_counter()

    ruta_ga, costo_ga, historial_ga = algoritmo_genetico(
        puntos_entrega,
        distancias
    )

    fin_ga = time.perf_counter()

    tiempo_ga = fin_ga - inicio_ga

    print("\n--- ALGORITMO GENETICO ---")

    print("Ruta:")
    print(ruta_ga)

    print(
        "Costo:",
        round(costo_ga, 2),
        "metros"
    )

    print(
        "Tiempo:",
        round(tiempo_ga, 4),
        "segundos"
    )

    # ----------------------------------------------
    # MEJORAS
    # ----------------------------------------------

    mejora_sa = (
        (costo_inicial - costo_sa)
        / costo_inicial
    ) * 100

    mejora_ga = (
        (costo_inicial - costo_ga)
        / costo_inicial
    ) * 100

    mejora_sa_aleatorio = (
        (promedio_aleatorio - costo_sa)
        / promedio_aleatorio
    ) * 100

    mejora_ga_aleatorio = (
        (promedio_aleatorio - costo_ga)
        / promedio_aleatorio
    ) * 100

    print("\n--- RESULTADOS ---")

    print(
        "Mejora SA contra ruta inicial:",
        round(mejora_sa, 2),
        "%"
    )

    print(
        "Mejora GA contra ruta inicial:",
        round(mejora_ga, 2),
        "%"
    )

    print(
        "Mejora SA contra promedio aleatorio:",
        round(mejora_sa_aleatorio, 2),
        "%"
    )

    print(
        "Mejora GA contra promedio aleatorio:",
        round(mejora_ga_aleatorio, 2),
        "%"
    )

    guardar_grafica(
        historial_sa,
        historial_ga
    )

    print(
        "\nGrafica guardada como:"
    )

    print(
        "convergencia_fase3.png"
    )