import osmnx as ox
import networkx as nx
import math
import heapq
import random
import time
import folium
import os

from fase1 import ucs
os.makedirs('data', exist_ok=True)

def cargar_grafo_urbano():
    """
    Descarga el grafo vial de Gustavo A. Madero.

    Retorna:
    - G: grafo original con coordenadas geográficas
    - G_proyectado: grafo con coordenadas cartesianas en metros
    """

    lugar = "Gustavo A. Madero, Ciudad de Mexico, Mexico"
    print("Descargando grafo urbano...")

    G = ox.graph_from_place(lugar,
    network_type="drive")
    print("Proyectando grafo...")

    G_proyectado = ox.project_graph(G)
    print("Grafo cargado correctamente.")

    return G, G_proyectado

# Creacion de las Heuristicas
def heuristica_euclidiana(G_proyectado, nodo, destino):
    """
    Calcula la distancia Euclidiana entre dos nodos.

    Utiliza las coordenadas cartesianas proyectadas
    y devuelve la distancia en metros.
    """

    x1 = G_proyectado.nodes[nodo]["x"]
    y1 = G_proyectado.nodes[nodo]["y"]
    x2 = G_proyectado.nodes[destino]["x"]
    y2 = G_proyectado.nodes[destino]["y"]
    dx = x2 - x1
    dy = y2 - y1
    distancia = math.sqrt(dx ** 2 + dy ** 2)

    return distancia

def heuristica_haversine(G, nodo, destino):
    """
    Calcula la distancia Haversine entre dos nodos.

    Utiliza latitud y longitud y devuelve la distancia
    aproximada sobre la superficie terrestre en metros.
    """

    lon1 = G.nodes[nodo]["x"]
    lat1 = G.nodes[nodo]["y"]
    lon2 = G.nodes[destino]["x"]
    lat2 = G.nodes[destino]["y"]

    # Radio medio de la Tierra en metros
    R = 6371000.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Fórmula de Haversine
    a = (math.sin(delta_phi / 2) ** 2
    + math.cos(phi1) * math.cos(phi2)
    * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a),
    math.sqrt(1 - a))
    distancia = R * c

    return distancia

    # Auxiliares de H3
def calcular_angulo(p1, p2, p3):
    """
    Calcula el ángulo formado por tres puntos.

    p1, p2 y p3 son tuplas (x, y).

    El punto p2 representa el nodo donde se realiza
    el posible giro.
    """

    v1 = (p1[0] - p2[0], p1[1] - p2[1])
    v2 = (p3[0] - p2[0], p3[1] - p2[1])
    producto = (v1[0] * v2[0] + v1[1] * v2[1])
    magnitud1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
    magnitud2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)
    if magnitud1 == 0 or magnitud2 == 0:
        return 0.0

    cos_angulo = producto / (magnitud1 * magnitud2)
    cos_angulo = max(-1.0, min(1.0, cos_angulo))
    angulo = math.degrees(math.acos(cos_angulo))

    return angulo

def estimar_giros(G_proyectado, nodo, destino):
    """
    Estima la cantidad de cambios de dirección necesarios
    para orientarse desde el nodo hacia el destino.

    La estimación se basa en la diferencia entre las
    direcciones de los vecinos del nodo y la dirección
    directa hacia el destino.

    Retorna:
    - 0 si existe un vecino aproximadamente alineado
      con el destino.
    - 1 en caso contrario.
    """

    if nodo == destino:
        return 0

    x_nodo = G_proyectado.nodes[nodo]["x"]
    y_nodo = G_proyectado.nodes[nodo]["y"]
    x_destino = G_proyectado.nodes[destino]["x"]
    y_destino = G_proyectado.nodes[destino]["y"]
    dx_destino = x_destino - x_nodo
    dy_destino = y_destino - y_nodo

    magnitud_destino = math.sqrt(
    dx_destino ** 2 + dy_destino ** 2)
    if magnitud_destino == 0:
        return 0

    mejor_angulo = 180.0
    for vecino in G_proyectado.neighbors(nodo):
        x_vecino = G_proyectado.nodes[vecino]["x"]
        y_vecino = G_proyectado.nodes[vecino]["y"]
        dx_vecino = x_vecino - x_nodo
        dy_vecino = y_vecino - y_nodo
        magnitud_vecino = math.sqrt(
        dx_vecino ** 2 + dy_vecino ** 2)
        if magnitud_vecino == 0:
            continue

        producto = (dx_vecino * dx_destino +
        dy_vecino * dy_destino)
        cos_angulo = producto / (magnitud_vecino *
        magnitud_destino)
        cos_angulo = max(-1.0, min(1.0, cos_angulo))
        angulo = math.degrees(math.acos(cos_angulo))
        mejor_angulo = min(mejor_angulo, angulo)

    if mejor_angulo <= 45:
        return 0

    return 1

def heuristica_combinada(G, G_proyectado, nodo,
    destino, peso_distancia=0.9, peso_giros=0.1):
    """
    Heurística H3.

    Combina una estimación de distancia con una estimación
    del número de giros.

    La heurística se limita a la distancia mínima estimada
    para conservar una cota inferior sobre el costo real.

    Retorna una estimación en metros.
    """

    h1 = heuristica_euclidiana(G_proyectado,
    nodo, destino)
    h2 = heuristica_haversine(G, nodo, destino)
    distancia = min(h1, h2)
    giros = estimar_giros(G_proyectado,
    nodo, destino)
    factor_giros = 1 / (1 + giros)
    h3 = distancia * (peso_distancia +
    peso_giros * factor_giros)
    h3 = min(h3, distancia)

    return h3

def verificar_admisibilidad(G, G_proyectado,
destino, nodos_prueba):
    """
    Verifica experimentalmente la admisibilidad de H1, H2 y H3.

    Para cada nodo de prueba se compara el valor de la heurística
    contra el costo óptimo obtenido mediante UCS.
    """

    resultados = {
    "H1 Euclidiana":
    {"evaluados": 0, "violaciones": 0},
    "H2 Haversine":
    {"evaluados": 0, "violaciones": 0},
    "H3 Distancia + Giros":
    {"evaluados": 0, "violaciones": 0}}

    for nodo in nodos_prueba:
        if nodo == destino:
            continue

        resultado_ucs = ucs(G, nodo, destino)
        costo_optimo = resultado_ucs[3]
        if costo_optimo == float("inf"):
            continue

        h1 = heuristica_euclidiana(
        G_proyectado, nodo, destino)
        h2 = heuristica_haversine(
        G, nodo, destino)
        h3 = heuristica_combinada(
        G, G_proyectado, nodo, destino)
        heuristicas = {
        "H1 Euclidiana": h1,
        "H2 Haversine": h2,
        "H3 Distancia + Giros": h3}

        for nombre, valor in heuristicas.items():
            resultados[nombre]["evaluados"] += 1
            if valor > costo_optimo + 1e-9:
                resultados[nombre]["violaciones"] += 1

    return resultados

def obtener_peso_arista(G, origen, destino):
    """
    Obtiene el costo de recorrer una arista.

    En nuestro caso el costo es la longitud de la calle
    almacenada en el atributo 'length'.
    """

    datos = G.get_edge_data(origen, destino)
    if datos is None:
        return float("inf")

    if G.is_multigraph():
        return min(datos_arista.get("length", 0.0)
            for datos_arista in datos.values())

    return datos.get("length", 0.0)


def a_estrella(G, origen, destino, heuristica):
    """
    Implementa el algoritmo A*.

    Parámetros:
    - G: grafo sobre el que se realiza la búsqueda.
    - origen: nodo inicial.
    - destino: nodo objetivo.
    - heuristica: función que calcula h(n).

    Retorna:
    - camino
    - nodos_expandidos
    - max_frontera
    - distancia_total
    - num_arcos
    """

    frontera = []
    g_costos = {origen: 0.0}
    # Guarda el nodo anterior para reconstruir el camino.
    padres = {origen: None}
    explorados = set()
    # Calculamos f(n) = g(n) + h(n)
    h_inicial = heuristica(origen, destino)

    heapq.heappush(frontera,(h_inicial, 0.0, origen))
    max_frontera = 1
    nodos_expandidos = 0
    while frontera:
        f_actual, g_actual, actual = heapq.heappop(frontera)
        if actual in explorados:
            continue
        explorados.add(actual)
        nodos_expandidos += 1

        if actual == destino:
            camino = []
            nodo = destino
            while nodo is not None:
                camino.append(nodo)
                nodo = padres[nodo]
            camino.reverse()
            distancia_total = g_costos[destino]
            num_arcos = len(camino) - 1

            return (camino, nodos_expandidos,
            max_frontera, distancia_total, num_arcos)

        for vecino in G.neighbors(actual):
            peso = obtener_peso_arista(G,
            actual, vecino)
            nuevo_g = g_actual + peso

            if nuevo_g < g_costos.get(vecino,
            float("inf")):
                g_costos[vecino] = nuevo_g
                padres[vecino] = actual
                h = heuristica(vecino, destino)
                f = nuevo_g + h
                heapq.heappush(frontera,
                (f, nuevo_g, vecino))

        max_frontera = max(max_frontera, len(frontera))

    return (None, nodos_expandidos, max_frontera,
    float("inf"), 0)

def greedy(G, origen, destino, heuristica):
    """
    Implementa Greedy Best-First Search.

    La prioridad de cada nodo depende únicamente
    de h(n).

    A diferencia de A*, no utiliza g(n) para
    determinar qué nodo explorar primero.

    Retorna:
    - camino
    - nodos_expandidos
    - max_frontera
    - distancia_total
    - num_arcos
    """

    frontera = []
    padres = {origen: None}
    g_costos = {origen: 0.0}
    explorados = set()
    h_inicial = heuristica(origen, destino)
    heapq.heappush(frontera, (h_inicial, origen))
    max_frontera = 1
    nodos_expandidos = 0
    while frontera:
        h_actual, actual = heapq.heappop(frontera)
        if actual in explorados:
            continue
        explorados.add(actual)
        nodos_expandidos += 1

        if actual == destino:
            camino = []
            nodo = destino
            while nodo is not None:
                camino.append(nodo)
                nodo = padres[nodo]
            camino.reverse()
            distancia_total = g_costos[destino]
            num_arcos = len(camino) - 1

            return (camino, nodos_expandidos,
            max_frontera, distancia_total, num_arcos)

        for vecino in G.neighbors(actual):
            if vecino in explorados:
                continue
            peso = obtener_peso_arista(G,
            actual, vecino)
            nuevo_g = (g_costos[actual] + peso)

            if nuevo_g < g_costos.get(vecino,
            float("inf")):
                g_costos[vecino] = nuevo_g
                padres[vecino] = actual
                h = heuristica(vecino, destino)
                heapq.heappush(frontera, (h, vecino))
        max_frontera = max(max_frontera, len(frontera))

    return (None, nodos_expandidos, max_frontera,
    float("inf"), 0)

def comparar_algoritmos(G, G_proyectado, origen, destino):
    """
    Compara UCS y A* utilizando las tres heurísticas.

    Mide:
    - nodos expandidos
    - distancia total
    - tiempo de ejecución
    """

    resultados = []
    #UCS
    inicio = time.perf_counter()
    resultado_ucs = ucs(G, origen, destino)
    tiempo_ucs = time.perf_counter() - inicio
    resultados.append({"algoritmo": "UCS",
    "heuristica": "Ninguna",
    "nodos_expandidos": resultado_ucs[1],
    "distancia": resultado_ucs[3],
    "tiempo": tiempo_ucs})

    #A*
    h1 = lambda nodo, destino: heuristica_euclidiana(
    G_proyectado, nodo, destino)
    inicio = time.perf_counter()
    resultado_h1 = a_estrella(G, origen, destino, h1)
    tiempo_h1 = time.perf_counter() - inicio
    resultados.append({"algoritmo": "A*",
    "heuristica": "H1 Euclidiana",
    "nodos_expandidos": resultado_h1[1],
    "distancia": resultado_h1[3],
    "tiempo": tiempo_h1})

    h2 = lambda nodo, destino: heuristica_haversine(
    G, nodo, destino)
    inicio = time.perf_counter()
    resultado_h2 = a_estrella(G, origen, destino, h2)
    tiempo_h2 = time.perf_counter() - inicio
    resultados.append({"algoritmo": "A*",
    "heuristica": "H2 Haversine",
    "nodos_expandidos": resultado_h2[1],
    "distancia": resultado_h2[3],
    "tiempo": tiempo_h2})

    h3 = lambda nodo, destino: heuristica_combinada(
    G, G_proyectado, nodo, destino)
    inicio = time.perf_counter()
    resultado_h3 = a_estrella(G, origen, destino, h3)
    tiempo_h3 = time.perf_counter() - inicio
    resultados.append({"algoritmo": "A*",
    "heuristica": "H3 Distancia + Giros",
    "nodos_expandidos": resultado_h3[1],
    "distancia": resultado_h3[3],
    "tiempo": tiempo_h3})

    #Greedy
    h1 = lambda nodo, destino: heuristica_euclidiana(
    G_proyectado, nodo, destino)
    inicio = time.perf_counter()
    resultado_greedy_h1 = greedy(
    G, origen, destino, h1)
    tiempo_greedy_h1 = time.perf_counter() - inicio
    resultados.append({"algoritmo": "Greedy",
    "heuristica": "H1 Euclidiana",
    "nodos_expandidos": resultado_greedy_h1[1],
    "distancia": resultado_greedy_h1[3],
    "tiempo": tiempo_greedy_h1})

    h2 = lambda nodo, destino: heuristica_haversine(
    G, nodo, destino)
    inicio = time.perf_counter()
    resultado_greedy_h2 = greedy(
    G, origen, destino, h2)
    tiempo_greedy_h2 = time.perf_counter() - inicio
    resultados.append({"algoritmo": "Greedy",
    "heuristica": "H2 Haversine",
    "nodos_expandidos": resultado_greedy_h2[1],
    "distancia": resultado_greedy_h2[3],
    "tiempo": tiempo_greedy_h2})

    h3 = lambda nodo, destino: heuristica_combinada(
    G, G_proyectado, nodo, destino)
    inicio = time.perf_counter()
    resultado_greedy_h3 = greedy(
    G, origen, destino, h3)
    tiempo_greedy_h3 = time.perf_counter() - inicio
    resultados.append({"algoritmo": "Greedy",
    "heuristica": "H3 Distancia + Giros",
    "nodos_expandidos": resultado_greedy_h3[1],
    "distancia": resultado_greedy_h3[3],
    "tiempo": tiempo_greedy_h3})

    return resultados

def ejecutar_experimentos(G, G_proyectado, origen, destinos):
    resultados = []
    for i, destino in enumerate(destinos, start=1):
        resultados_instancia = comparar_algoritmos(
        G, G_proyectado, origen, destino)
        for resultado in resultados_instancia:
            resultado["instancia"] = i
            resultados.append(resultado)

    return resultados

def mostrar_tabla_resultados(resultados):
    print()
    print("TABLA COMPARATIVA")

    print(f"{'Inst.':<8}"
    f"{'Algoritmo':<13}"
    f"{'Heurística':<28}"
    f"{'Nodos':>10}"
    f"{'Distancia (m)':>17}"
    f"{'Tiempo (s)':>14}")

    instancia_anterior = None
    for resultado in resultados:
        instancia = resultado["instancia"]
        if instancia == instancia_anterior:
            instancia_texto = ""
        else:
            instancia_texto = str(instancia)
        print(f"{instancia_texto:<8}"
        f"{resultado['algoritmo']:<13}"
        f"{resultado['heuristica']:<28}"
        f"{resultado['nodos_expandidos']:>10}"
        f"{resultado['distancia']:>17.2f}"
        f"{resultado['tiempo']:>14.6f}")
        instancia_anterior = instancia

def mostrar_admisibilidad(resultados):
    print()
    print("VERIFICACIÓN EXPERIMENTAL DE ADMISIBILIDAD")
    for nombre, resultado in resultados.items():
        print(f"{nombre:<28}"
        f"Evaluados: {resultado['evaluados']:>4}    "
        f"Violaciones: {resultado['violaciones']:>3}")
        if resultado["violaciones"] == 0:
            print(" " * 28 + "Resultado: ADMISIBLE")
        else:
            print(" " * 28 + "Resultado: NO ADMISIBLE")

def visualizar_rutas(G, G_proyectado, origen, destino):
    """
    Genera un mapa Folium con las rutas de A* y Greedy.
    """

    def h1(nodo, destino):
        return heuristica_euclidiana(
        G_proyectado, nodo, destino)

    def obtener_coordenadas(camino):
        coordenadas = []
        for nodo in camino:
            lat = G.nodes[nodo]["y"]
            lon = G.nodes[nodo]["x"]
            coordenadas.append((lat, lon))

        return coordenadas

    resultado_a_estrella = a_estrella(
    G, origen, destino, h1)
    resultado_greedy = greedy(G, origen, destino, h1)
    camino_astar = resultado_a_estrella[0]
    camino_greedy = resultado_greedy[0]
    lat_origen = G.nodes[origen]["y"]
    lon_origen = G.nodes[origen]["x"]

    mapa = folium.Map(
        location=[lat_origen, lon_origen],
        zoom_start=14, tiles="OpenStreetMap")

    folium.Marker([lat_origen, lon_origen],
    tooltip="Origen").add_to(mapa)

    lat_destino = G.nodes[destino]["y"]
    lon_destino = G.nodes[destino]["x"]

    folium.Marker([lat_destino, lon_destino],
    tooltip="Destino").add_to(mapa)

    if camino_astar is not None:
        folium.PolyLine(
        obtener_coordenadas(camino_astar),
        tooltip=(f"A* - "
        f"{resultado_a_estrella[3]:.2f} m"),
        weight=6).add_to(mapa)

    if camino_greedy is not None:
        folium.PolyLine(
        obtener_coordenadas(camino_greedy),
        tooltip=(f"Greedy - "
        f"{resultado_greedy[3]:.2f} m"),
        weight=4).add_to(mapa)

        nombre_archivo = os.path.join('data', "mapa_fase2.html")
        mapa.save(nombre_archivo)
        print("VISUALIZACIÓN FASE 2 - Mapa guardado exitosamente en la carpeta data/")

    print(f"A*: {resultado_a_estrella[3]:.2f} metros")
    print(f"Greedy: {resultado_greedy[3]:.2f} metros")
    print(f"Mapa guardado como: {nombre_archivo}")

def main():
    G, G_proyectado = cargar_grafo_urbano()
    nodos = list(G.nodes)
    random.seed(42) # Para tener un mismo grafo cada vez
    origen = random.choice(nodos)
    alcanzables = list(nx.descendants(G, origen))
    alcanzables = [nodo for nodo in alcanzables
    if nodo != origen]
    destinos = random.sample(alcanzables, 5)
    resultados = ejecutar_experimentos(
    G, G_proyectado, origen, destinos)
    mostrar_tabla_resultados(resultados)
    nodos_admisibilidad = random.sample(
    alcanzables, 30)
    resultados_admisibilidad = verificar_admisibilidad(
    G, G_proyectado, destinos[0], nodos_admisibilidad)
    mostrar_admisibilidad(resultados_admisibilidad)
    visualizar_rutas(G, G_proyectado, origen, destinos[0])


if __name__ == "__main__":
    main()