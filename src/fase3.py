# Fase 3 - Busqueda local
# Agente planificador de rutas

import math
import random
import time
import os

import matplotlib.pyplot as plt
import networkx as nx
os.makedirs('data', exist_ok=True)

from fase2 import cargar_grafo_urbano
from fase2 import a_estrella
from fase2 import heuristica_haversine


# ==================================================
# 1. SELECCION DE PUNTOS DE ENTREGA
# ==================================================

def seleccionar_puntos_entrega(G, cantidad=10):
    componente_mayor = max(
        nx.strongly_connected_components(G),
        key=len
    )

    nodos = sorted(list(componente_mayor))

    random.seed(42)

    puntos = random.sample(
        nodos,
        cantidad
    )

    return puntos


# ==================================================
# 2. DISTANCIA ENTRE DOS PUNTOS USANDO A*
# ==================================================

def distancia_entre_nodos(G, origen, destino):

    def h(nodo, destino):
        return heuristica_haversine(
            G,
            nodo,
            destino
        )

    resultado = a_estrella(
        G,
        origen,
        destino,
        h
    )

    return resultado[3]


# ==================================================
# 3. PRECALCULO DE DISTANCIAS
# ==================================================

def calcular_distancias(G, puntos):
    distancias = {}

    total = len(puntos) * (
        len(puntos) - 1
    )

    contador = 0

    print(
        "\nCalculando distancias entre los puntos..."
    )

    for origen in puntos:

        for destino in puntos:

            if origen != destino:

                distancia = distancia_entre_nodos(
                    G,
                    origen,
                    destino
                )

                distancias[
                    (origen, destino)
                ] = distancia

                contador = contador + 1

                print(
                    "Distancia",
                    contador,
                    "de",
                    total,
                    end="\r"
                )

    print(
        "\nDistancias calculadas correctamente."
    )

    return distancias


# ==================================================
# 4. COSTO TOTAL DE UNA RUTA
# ==================================================

def costo_ruta(ruta, distancias):
    total = 0.0

    for i in range(
        len(ruta) - 1
    ):

        origen = ruta[i]

        destino = ruta[i + 1]

        total = total + distancias[
            (origen, destino)
        ]

    return total


# ==================================================
# 5. OPERADOR DE VECINDAD 2-OPT
# ==================================================

def vecino_2opt(ruta):
    nueva_ruta = ruta.copy()

    i, j = random.sample(
        range(len(ruta)),
        2
    )

    if i > j:
        i, j = j, i

    nueva_ruta[i:j + 1] = reversed(
        nueva_ruta[i:j + 1]
    )

    return nueva_ruta


# ==================================================
# 6. RECOCIDO SIMULADO
# ==================================================

def recocido_simulado(
    ruta_inicial,
    distancias,
    temperatura_inicial=5000,
    alpha=0.995,
    temperatura_minima=1
):

    ruta_actual = ruta_inicial.copy()

    costo_actual = costo_ruta(
        ruta_actual,
        distancias
    )

    mejor_ruta = ruta_actual.copy()

    mejor_costo = costo_actual

    temperatura = temperatura_inicial

    historial = [
        mejor_costo
    ]

    while temperatura > temperatura_minima:

        ruta_vecina = vecino_2opt(
            ruta_actual
        )

        costo_vecino = costo_ruta(
            ruta_vecina,
            distancias
        )

        diferencia = (
            costo_vecino
            - costo_actual
        )

        if diferencia < 0:

            aceptar = True

        else:

            probabilidad = math.exp(
                -diferencia
                / temperatura
            )

            numero_aleatorio = random.random()

            aceptar = (
                numero_aleatorio
                < probabilidad
            )

        if aceptar:

            ruta_actual = ruta_vecina

            costo_actual = costo_vecino

        if costo_actual < mejor_costo:

            mejor_ruta = ruta_actual.copy()

            mejor_costo = costo_actual

        historial.append(
            mejor_costo
        )

        temperatura = (
            temperatura * alpha
        )

    return (
        mejor_ruta,
        mejor_costo,
        historial
    )


# ==================================================
# 7. CRUCE OX
# ==================================================

def cruce_ox(padre1, padre2):
    cantidad = len(padre1)

    i, j = random.sample(
        range(cantidad),
        2
    )

    if i > j:
        i, j = j, i

    hijo = [
        None
    ] * cantidad

    hijo[i:j + 1] = padre1[
        i:j + 1
    ]

    posicion = (
        j + 1
    ) % cantidad

    orden_padre2 = (
        padre2[j + 1:]
        + padre2[:j + 1]
    )

    for punto in orden_padre2:

        if punto not in hijo:

            hijo[posicion] = punto

            posicion = (
                posicion + 1
            ) % cantidad

    return hijo


# ==================================================
# 8. MUTACION SWAP
# ==================================================

def mutacion_swap(
    ruta,
    probabilidad=0.10
):

    nueva_ruta = ruta.copy()

    if random.random() < probabilidad:

        i, j = random.sample(
            range(len(nueva_ruta)),
            2
        )

        temporal = nueva_ruta[i]

        nueva_ruta[i] = nueva_ruta[j]

        nueva_ruta[j] = temporal

    return nueva_ruta


# ==================================================
# 9. SELECCION POR TORNEO
# ==================================================

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

        costo_candidato = costo_ruta(
            candidato,
            distancias
        )

        costo_mejor = costo_ruta(
            mejor,
            distancias
        )

        if costo_candidato < costo_mejor:

            mejor = candidato

    return mejor.copy()


# ==================================================
# 10. ALGORITMO GENETICO
# ==================================================

def algoritmo_genetico(
    puntos,
    distancias,
    tamano_poblacion=50,
    generaciones=200,
    probabilidad_mutacion=0.10
):

    poblacion = []

    poblacion.append(
        puntos.copy()
    )

    for _ in range(
        tamano_poblacion - 1
    ):

        individuo = puntos.copy()

        random.shuffle(
            individuo
        )

        poblacion.append(
            individuo
        )

    mejor_ruta = min(
        poblacion,
        key=lambda ruta: costo_ruta(
            ruta,
            distancias
        )
    ).copy()

    mejor_costo = costo_ruta(
        mejor_ruta,
        distancias
    )

    historial = [
        mejor_costo
    ]

    for _ in range(
        generaciones
    ):

        elite = min(
            poblacion,
            key=lambda ruta: costo_ruta(
                ruta,
                distancias
            )
        ).copy()

        nueva_poblacion = [
            elite
        ]

        while len(
            nueva_poblacion
        ) < tamano_poblacion:

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

            nueva_poblacion.append(
                hijo1
            )

            if len(
                nueva_poblacion
            ) < tamano_poblacion:

                nueva_poblacion.append(
                    hijo2
                )

        poblacion = nueva_poblacion

        mejor_generacion = min(
            poblacion,
            key=lambda ruta: costo_ruta(
                ruta,
                distancias
            )
        )

        costo_generacion = costo_ruta(
            mejor_generacion,
            distancias
        )

        if costo_generacion < mejor_costo:

            mejor_costo = costo_generacion

            mejor_ruta = (
                mejor_generacion.copy()
            )

        historial.append(
            mejor_costo
        )

    return (
        mejor_ruta,
        mejor_costo,
        historial
    )


# ==================================================
# 11. RUTAS ALEATORIAS
# ==================================================

def evaluar_rutas_aleatorias(
    puntos,
    distancias,
    cantidad=100
):

    mejor_ruta = None

    mejor_costo = float(
        "inf"
    )

    suma_costos = 0.0

    for _ in range(
        cantidad
    ):

        ruta = puntos.copy()

        random.shuffle(
            ruta
        )

        costo = costo_ruta(
            ruta,
            distancias
        )

        suma_costos = (
            suma_costos + costo
        )

        if costo < mejor_costo:

            mejor_costo = costo

            mejor_ruta = ruta.copy()

    promedio = (
        suma_costos / cantidad
    )

    return (
        mejor_ruta,
        mejor_costo,
        promedio
    )


# ==================================================
# 12. BUSQUEDA LOCAL 2-OPT
#     PARA ANALIZAR OPTIMOS LOCALES
# ==================================================

def busqueda_local_2opt(
    ruta_inicial,
    distancias
):

    ruta_actual = (
        ruta_inicial.copy()
    )

    costo_actual = costo_ruta(
        ruta_actual,
        distancias
    )

    continuar = True

    while continuar:

        continuar = False

        mejor_ruta = (
            ruta_actual.copy()
        )

        mejor_costo = (
            costo_actual
        )

        for i in range(
            len(ruta_actual) - 1
        ):

            for j in range(
                i + 1,
                len(ruta_actual)
            ):

                vecino = (
                    ruta_actual.copy()
                )

                vecino[i:j + 1] = reversed(
                    vecino[i:j + 1]
                )

                costo_vecino = costo_ruta(
                    vecino,
                    distancias
                )

                if costo_vecino < mejor_costo:

                    mejor_costo = costo_vecino

                    mejor_ruta = (
                        vecino.copy()
                    )

        if mejor_costo < costo_actual:

            ruta_actual = (
                mejor_ruta.copy()
            )

            costo_actual = (
                mejor_costo
            )

            continuar = True

    return (
        ruta_actual,
        costo_actual
    )


# ==================================================
# 13. EXPERIMENTO DE TEMPERATURA INICIAL
# ==================================================

def experimento_temperaturas(
    puntos,
    distancias
):

    temperaturas = [
        500,
        1000,
        5000,
        10000
    ]

    resultados = []

    print(
        "\n--- EFECTO DE LA TEMPERATURA INICIAL ---"
    )

    for temperatura in temperaturas:

        costos = []

        for prueba in range(10):

            random.seed(
                1000 + prueba
            )

            ruta, costo, historial = recocido_simulado(
                puntos,
                distancias,
                temperatura_inicial=temperatura
            )

            costos.append(
                costo
            )

        mejor = min(
            costos
        )

        peor = max(
            costos
        )

        promedio = (
            sum(costos)
            / len(costos)
        )

        resultados.append(
            (
                temperatura,
                mejor,
                promedio,
                peor
            )
        )

        print(
            "T0 =",
            temperatura,
            "| Mejor:",
            round(mejor, 2),
            "| Promedio:",
            round(promedio, 2),
            "| Peor:",
            round(peor, 2)
        )

    return resultados


# ==================================================
# 14. EXPERIMENTO DE OPTIMOS LOCALES
# ==================================================

def experimento_optimos_locales(
    puntos,
    distancias,
    cantidad=20
):

    costos = []

    print(
        "\n--- ANALISIS DE OPTIMOS LOCALES ---"
    )

    for prueba in range(
        cantidad
    ):

        random.seed(
            2000 + prueba
        )

        ruta_inicial = (
            puntos.copy()
        )

        random.shuffle(
            ruta_inicial
        )

        ruta_final, costo_final = busqueda_local_2opt(
            ruta_inicial,
            distancias
        )

        costos.append(
            costo_final
        )

        print(
            "Ejecucion",
            prueba + 1,
            ":",
            round(
                costo_final,
                2
            ),
            "metros"
        )

    mejor = min(
        costos
    )

    peor = max(
        costos
    )

    promedio = (
        sum(costos)
        / len(costos)
    )

    distintos = len(
        set(
            round(
                costo,
                2
            )
            for costo in costos
        )
    )

    print(
        "\nMejor optimo local:",
        round(
            mejor,
            2
        ),
        "metros"
    )

    print(
        "Peor optimo local:",
        round(
            peor,
            2
        ),
        "metros"
    )

    print(
        "Promedio:",
        round(
            promedio,
            2
        ),
        "metros"
    )

    print(
        "Resultados locales diferentes:",
        distintos
    )

    return costos


# ==================================================
# 15. GRAFICA DE CONVERGENCIA
# ==================================================

def guardar_grafica_convergencia(
    historial_sa,
    historial_ga
):

    plt.figure(
        figsize=(10, 5)
    )

    plt.plot(
        historial_sa,
        label="Recocido Simulado"
    )

    plt.plot(
        historial_ga,
        label="Algoritmo Genetico"
    )

    plt.xlabel(
        "Iteracion / generacion"
    )

    plt.ylabel(
        "Mejor distancia en metros"
    )

    plt.title(
        "Convergencia de los algoritmos"
    )

    plt.legend()

    plt.grid()

    plt.tight_layout()

    plt.savefig(
        os.path.join('data', "convergencia_fase3.png"),
        dpi=150
    )
    print("Gráfica de convergencia guardada en la carpeta data/")

    plt.close()


# ==================================================
# 16. GRAFICA DE TEMPERATURAS
# ==================================================

def guardar_grafica_temperaturas(
    resultados
):

    temperaturas = []

    mejores = []

    promedios = []

    peores = []

    for resultado in resultados:

        temperaturas.append(
            resultado[0]
        )

        mejores.append(
            resultado[1]
        )

        promedios.append(
            resultado[2]
        )

        peores.append(
            resultado[3]
        )

    plt.figure(
        figsize=(9, 5)
    )

    plt.plot(
        temperaturas,
        mejores,
        marker="o",
        label="Mejor"
    )

    plt.plot(
        temperaturas,
        promedios,
        marker="o",
        label="Promedio"
    )

    plt.plot(
        temperaturas,
        peores,
        marker="o",
        label="Peor"
    )

    plt.xlabel(
        "Temperatura inicial T0"
    )

    plt.ylabel(
        "Distancia final en metros"
    )

    plt.title(
        "Efecto de la temperatura inicial"
    )

    plt.legend()

    plt.grid()

    plt.tight_layout()

    plt.savefig(
        os.path.join('data', "temperaturas_fase3.png"),
        dpi=150
    )
    print("Gráfica de temperaturas guardada en la carpeta data/")
    plt.close()


# ==================================================
# 17. GRAFICA DE OPTIMOS LOCALES
# ==================================================

def guardar_grafica_optimos(costos):
    costos_redondeados = []

    for costo in costos:
        costos_redondeados.append(round(costo, 2))

    valores = sorted(set(costos_redondeados))

    frecuencias = []

    for valor in valores:
        frecuencias.append(costos_redondeados.count(valor))

    etiquetas = []

    for valor in valores:
        etiquetas.append(str(valor))

    plt.figure(figsize=(10, 5))

    plt.bar(
        etiquetas,
        frecuencias
    )

    plt.xlabel("Costo del optimo local en metros")
    plt.ylabel("Frecuencia")
    plt.title("Distribucion de costos en los optimos locales")

    plt.grid(axis="y")
    plt.tight_layout()

    plt.savefig(
        os.path.join('data', "optimos_locales_fase3.png"),
        dpi=150
    )
    print("Gráfica guardada exitosamente en la carpeta data/")

    plt.close()


# ==================================================
# 18. PROGRAMA PRINCIPAL
# ==================================================

def main():

    random.seed(42)

    # ----------------------------------------------
    # CARGA DEL GRAFO
    # ----------------------------------------------

    G, G_proyectado = cargar_grafo_urbano()

    print(
        "\nGrafo cargado desde Fase 3."
    )

    # ----------------------------------------------
    # SELECCION DE 10 PUNTOS
    # ----------------------------------------------

    puntos_entrega = seleccionar_puntos_entrega(
        G,
        10
    )

    print(
        "\nPuntos de entrega:"
    )

    print(
        puntos_entrega
    )

    # ----------------------------------------------
    # PRECALCULO DE DISTANCIAS CON A*
    # ----------------------------------------------

    inicio_distancias = (
        time.perf_counter()
    )

    distancias = calcular_distancias(
        G,
        puntos_entrega
    )

    fin_distancias = (
        time.perf_counter()
    )

    tiempo_distancias = (
        fin_distancias
        - inicio_distancias
    )

    print(
        "\nTiempo de precalculo A*:",
        round(
            tiempo_distancias,
            4
        ),
        "segundos"
    )

    # ----------------------------------------------
    # RUTA INICIAL
    # ----------------------------------------------

    costo_inicial = costo_ruta(
        puntos_entrega,
        distancias
    )

    print(
        "\nCosto de la ruta inicial:",
        round(
            costo_inicial,
            2
        ),
        "metros"
    )

    # ----------------------------------------------
    # 100 RUTAS ALEATORIAS
    # ----------------------------------------------

    random.seed(100)

    mejor_aleatoria, costo_aleatorio, promedio_aleatorio = evaluar_rutas_aleatorias(
        puntos_entrega,
        distancias,
        100
    )

    print(
        "\n--- RUTAS ALEATORIAS ---"
    )

    print(
        "Promedio de 100 rutas aleatorias:",
        round(
            promedio_aleatorio,
            2
        ),
        "metros"
    )

    print(
        "Mejor ruta aleatoria:",
        round(
            costo_aleatorio,
            2
        ),
        "metros"
    )

    # ----------------------------------------------
    # RECOCIDO SIMULADO
    # ----------------------------------------------

    random.seed(200)

    inicio_sa = (
        time.perf_counter()
    )

    ruta_sa, costo_sa, historial_sa = recocido_simulado(
        puntos_entrega,
        distancias,
        temperatura_inicial=5000,
        alpha=0.995,
        temperatura_minima=1
    )

    fin_sa = (
        time.perf_counter()
    )

    tiempo_sa = (
        fin_sa - inicio_sa
    )

    print(
        "\n--- RECOCIDO SIMULADO ---"
    )

    print(
        "Parametros:"
    )

    print(
        "T0 = 5000"
    )

    print(
        "alpha = 0.995"
    )

    print(
        "Tmin = 1"
    )

    print(
        "\nRuta:"
    )

    print(
        ruta_sa
    )

    print(
        "Costo:",
        round(
            costo_sa,
            2
        ),
        "metros"
    )

    print(
        "Tiempo de optimizacion:",
        round(
            tiempo_sa,
            4
        ),
        "segundos"
    )

    # ----------------------------------------------
    # ALGORITMO GENETICO
    # ----------------------------------------------

    random.seed(300)

    inicio_ga = (
        time.perf_counter()
    )

    ruta_ga, costo_ga, historial_ga = algoritmo_genetico(
        puntos_entrega,
        distancias,
        tamano_poblacion=50,
        generaciones=200,
        probabilidad_mutacion=0.10
    )

    fin_ga = (
        time.perf_counter()
    )

    tiempo_ga = (
        fin_ga - inicio_ga
    )

    print(
        "\n--- ALGORITMO GENETICO ---"
    )

    print(
        "Parametros:"
    )

    print(
        "Poblacion = 50"
    )

    print(
        "Generaciones = 200"
    )

    print(
        "Mutacion = 0.10"
    )

    print(
        "\nRuta:"
    )

    print(
        ruta_ga
    )

    print(
        "Costo:",
        round(
            costo_ga,
            2
        ),
        "metros"
    )

    print(
        "Tiempo de optimizacion:",
        round(
            tiempo_ga,
            4
        ),
        "segundos"
    )

    # ----------------------------------------------
    # PORCENTAJES DE MEJORA
    # ----------------------------------------------

    mejora_sa_inicial = (
        (
            costo_inicial
            - costo_sa
        )
        / costo_inicial
    ) * 100

    mejora_ga_inicial = (
        (
            costo_inicial
            - costo_ga
        )
        / costo_inicial
    ) * 100

    mejora_sa_aleatorio = (
        (
            promedio_aleatorio
            - costo_sa
        )
        / promedio_aleatorio
    ) * 100

    mejora_ga_aleatorio = (
        (
            promedio_aleatorio
            - costo_ga
        )
        / promedio_aleatorio
    ) * 100

    print(
        "\n--- RESULTADOS PRINCIPALES ---"
    )

    print(
        "Ruta inicial:",
        round(
            costo_inicial,
            2
        ),
        "metros"
    )

    print(
        "Promedio aleatorio:",
        round(
            promedio_aleatorio,
            2
        ),
        "metros"
    )

    print(
        "Recocido Simulado:",
        round(
            costo_sa,
            2
        ),
        "metros"
    )

    print(
        "Algoritmo Genetico:",
        round(
            costo_ga,
            2
        ),
        "metros"
    )

    print(
        "\nMejora SA contra ruta inicial:",
        round(
            mejora_sa_inicial,
            2
        ),
        "%"
    )

    print(
        "Mejora GA contra ruta inicial:",
        round(
            mejora_ga_inicial,
            2
        ),
        "%"
    )

    print(
        "Mejora SA contra promedio aleatorio:",
        round(
            mejora_sa_aleatorio,
            2
        ),
        "%"
    )

    print(
        "Mejora GA contra promedio aleatorio:",
        round(
            mejora_ga_aleatorio,
            2
        ),
        "%"
    )

    # ----------------------------------------------
    # GRAFICA DE CONVERGENCIA
    # ----------------------------------------------

    guardar_grafica_convergencia(
        historial_sa,
        historial_ga
    )

    # ----------------------------------------------
    # EXPERIMENTO DE T0
    # ----------------------------------------------

    resultados_temperaturas = experimento_temperaturas(
        puntos_entrega,
        distancias
    )

    guardar_grafica_temperaturas(
        resultados_temperaturas
    )

    # ----------------------------------------------
    # EXPERIMENTO DE OPTIMOS LOCALES
    # ----------------------------------------------

    costos_optimos = experimento_optimos_locales(
        puntos_entrega,
        distancias,
        20
    )

    guardar_grafica_optimos(
        costos_optimos
    )

    # ----------------------------------------------
    # ARCHIVOS GENERADOS
    # ----------------------------------------------

    print(
        "\n--- ARCHIVOS GENERADOS ---"
    )

    print(
        "convergencia_fase3.png"
    )

    print(
        "temperaturas_fase3.png"
    )

    print(
        "optimos_locales_fase3.png"
    )

    print(
        "\nFase 3 terminada correctamente."
    )


if __name__ == "__main__":
    main()