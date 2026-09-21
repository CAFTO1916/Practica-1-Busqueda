import networkx as nx
import math
import random

from fase1 import ucs
from fase2 import (heuristica_euclidiana,
heuristica_haversine, a_estrella, estimar_giros,
heuristica_combinada, greedy, verificar_admisibilidad)

def crear_grafo_prueba():
    """
    Crea un pequeño grafo con coordenadas conocidas.
    """

    G = nx.DiGraph()
    G.add_node("A", x=-99.2000, y=19.4000)
    G.add_node("B", x=-99.1900, y=19.4000)
    G.add_node("C", x=-99.1900, y=19.4100)

    return G

def crear_grafo_a_estrella():
    """
    Crea un pequeño grafo para comprobar A*.
    El grafo tiene dos posibles caminos:

    A -> B -> D = 20 metros
    A -> C -> D = 30 metros

    Por lo tanto, el camino óptimo debe ser:
    A -> B -> D
    """

    G = nx.DiGraph()
    G.add_node("A", x=0.0, y=0.0)
    G.add_node("B", x=10.0, y=0.0)
    G.add_node("C", x=0.0, y=20.0)
    G.add_node("D", x=20.0, y=0.0)

    # Camino óptimo
    G.add_edge("A", "B", length=10.0)
    G.add_edge("B", "D", length=10.0)

    # Camino más largo
    G.add_edge("A", "C", length=15.0)
    G.add_edge("C", "D", length=15.0)

    return G

def crear_grafo_greedy():
    """
    Crea un grafo donde Greedy puede elegir
    un camino aparentemente más cercano,
    pero más costoso.

    Camino óptimo:
    A -> B -> D = 20 metros

    Camino que puede elegir Greedy:
    A -> C -> D = 101 metros
    """

    G = nx.DiGraph()
    G.add_node("A", x=0.0, y=0.0)
    G.add_node("B", x=5.0, y=0.0)
    G.add_node("C", x=9.0, y=0.0)
    G.add_node("D", x=10.0, y=0.0)
    # Camino Óptimo
    G.add_edge("A", "B", length=10.0)
    G.add_edge("B", "D", length=10.0)

    # Camino alternativo mucho más costoso
    G.add_edge("A", "C", length=1.0)
    G.add_edge("C", "D", length=100.0)

    return G

def test_a_estrella():
    G = crear_grafo_a_estrella()

    # Utilizamos la distancia Euclidiana como heurística.
    def h(nodo, destino):
        return heuristica_euclidiana(G, nodo, destino)
    resultado = a_estrella(G,"A", "D", h)
    camino = resultado[0]
    distancia = resultado[3]

    # El camino óptimo debe ser A -> B -> D
    assert camino == ["A", "B", "D"]

    # Su costo debe ser 20 metros.
    assert math.isclose(distancia, 20.0)

    print("A*: CORRECTO")
    print(f"  Camino: {camino}")
    print(f"  Distancia: {distancia:.2f} metros")
    print(f"  Nodos expandidos: {resultado[1]}")

def test_a_estrella_vs_ucs():
    G = crear_grafo_a_estrella()
    def h(nodo, destino):
        return heuristica_euclidiana(G, nodo, destino)

    resultado_ucs = ucs(G, "A", "D")
    camino_ucs = resultado_ucs[0]
    distancia_ucs = resultado_ucs[3]

    resultado_a_estrella = a_estrella(G, "A", "D", h)
    camino_a_estrella = resultado_a_estrella[0]
    distancia_a_estrella = resultado_a_estrella[3]

    # Ambos deben encontrar la misma distancia óptima.
    assert math.isclose(distancia_ucs, distancia_a_estrella)

    # En este grafo ambos deben encontrar A -> B -> D.
    assert camino_ucs == ["A", "B", "D"]
    assert camino_a_estrella == ["A", "B", "D"]

    print("A* vs UCS: CORRECTO")
    print(f"  Camino UCS:   {camino_ucs}")
    print(f"  Distancia UCS: {distancia_ucs:.2f} metros")
    print(f"  Camino A*:    {camino_a_estrella}")
    print(f"  Distancia A*: {distancia_a_estrella:.2f} metros")
    print(f"  Nodos UCS:    {resultado_ucs[1]}")
    print(f"  Nodos A*:     {resultado_a_estrella[1]}")

def test_a_estrella_h3():

    G = crear_grafo_a_estrella()
    def h3(nodo, destino):
        return heuristica_combinada(G, G,
        nodo, destino)

    resultado = a_estrella(G, "A", "D", h3)
    camino = resultado[0]
    distancia = resultado[3]

    assert camino == ["A", "B", "D"]
    assert math.isclose(distancia, 20.0)

    print("A* + H3: CORRECTO")
    print(f"  Camino: {camino}")
    print(f"  Distancia: {distancia:.2f} metros")
    print(f"  Nodos expandidos: {resultado[1]}")

def test_a_estrella_heuristicas():
    G = crear_grafo_a_estrella()
    def h1(nodo, destino):
        return heuristica_euclidiana(G, nodo, destino)

    def h2(nodo, destino):
        return heuristica_haversine(G, nodo, destino)

    def h3(nodo, destino):
        return heuristica_combinada(G, G, nodo, destino)

    resultado_h1 = a_estrella(G, "A", "D", h1)
    resultado_h2 = a_estrella(G, "A", "D", h2)
    resultado_h3 = a_estrella(G, "A", "D", h3)

    assert math.isclose(resultado_h1[3], 20.0)
    assert math.isclose(resultado_h2[3], 20.0)
    assert math.isclose(resultado_h3[3], 20.0)

    print("A* con las tres heurísticas: CORRECTO")
    print(f"H1 -> distancia: "
    f"{resultado_h1[3]:.2f} m | "
    f"nodos: {resultado_h1[1]}")
    print(f"H2 -> distancia: "
    f"{resultado_h2[3]:.2f} m | "
    f"nodos: {resultado_h2[1]}")
    print(f"H3 -> distancia: "
    f"{resultado_h3[3]:.2f} m | "
    f"nodos: {resultado_h3[1]}")

def test_admisibilidad():
    G = nx.DiGraph()
    G_proyectado = nx.DiGraph()

    G.add_node("A", x=-99.2000, y=19.4000)
    G.add_node("B", x=-99.1900, y=19.4000)
    G.add_node("C", x=-99.1900, y=19.4100)
    G.add_node("D", x=-99.2000, y=19.4100)

    G_proyectado.add_node("A", x=0.0, y=0.0)
    G_proyectado.add_node("B", x=1050.0, y=0.0)
    G_proyectado.add_node("C", x=1050.0, y=1111.0)
    G_proyectado.add_node("D", x=0.0, y=1111.0)

    G.add_edge("A", "B", length=1200.0)
    G.add_edge("B", "C", length=1200.0)
    G.add_edge("C", "D", length=1200.0)
    G.add_edge("A", "D", length=1200.0)

    destino = "D"
    nodos_prueba = ["A", "B", "C"]
    resultados = verificar_admisibilidad(
    G, G_proyectado, destino, nodos_prueba)

    print("Verificación de admisibilidad")
    for nombre, resultado in resultados.items():
        print(nombre)
        print(f"Nodos evaluados: "
        f"{resultado['evaluados']}")
        print(f"Violaciones: "
        f"{resultado['violaciones']}")

        assert resultado["violaciones"] == 0
        print("  Resultado: ADMISIBLE")

    print("Admisibilidad: CORRECTA")

def test_greedy_vs_a_estrella():
    G = crear_grafo_greedy()
    def h(nodo, destino):
        return heuristica_euclidiana(G, nodo, destino)

    resultado_a_estrella = a_estrella(G, "A", "D", h)
    resultado_greedy = greedy(G, "A", "D", h)
    distancia_a_estrella = resultado_a_estrella[3]
    distancia_greedy = resultado_greedy[3]

    print("Comparación A* vs Greedy")
    print(f"A* -> {resultado_a_estrella[0]}")
    print(f"Distancia A*: "
    f"{distancia_a_estrella:.2f} metros")
    print(f"Greedy -> {resultado_greedy[0]}")
    print(f"  Distancia Greedy: "
    f"{distancia_greedy:.2f} metros")

    assert math.isclose(distancia_a_estrella, 20.0)

    assert resultado_greedy[0] is not None

def test_haversine():
    G = crear_grafo_prueba()
    distancia = heuristica_haversine(G, "A", "B")
    assert distancia > 0

    print("H2 Haversine: CORRECTA")
    print(f"  Distancia A -> B: {distancia:.2f} metros")

def test_euclidiana():
    G = nx.DiGraph()
    G.add_node("A", x=0.0, y=0.0)
    G.add_node("B", x=3.0, y=4.0)
    distancia = heuristica_euclidiana(G, "A", "B")
    assert math.isclose(distancia, 5.0)

    print("H1 Euclidiana: CORRECTA")
    print(f"  Distancia A -> B: {distancia:.2f} metros")

def test_h3():
    G = crear_grafo_a_estrella()
    giros = estimar_giros(G, "A", "D")
    h3 = heuristica_combinada(G, G, "A", "D")
    assert giros >= 0
    assert h3 >= 0
    h1 = heuristica_euclidiana(G, "A", "D")
    h2 = heuristica_haversine(G, "A", "D")
    distancia_base = min(h1, h2)
    assert h3 <= distancia_base

    print("H3 Distancia + Giros: CORRECTA")
    print(f"  Giros estimados: {giros}")
    print(f"  H3: {h3:.2f} metros")

print("========================================")
print("PRUEBAS FASE 2")
print("========================================\n")

test_euclidiana()
print()
test_haversine()
print()
test_h3()
print()
test_a_estrella()
print()
test_a_estrella_vs_ucs()
print()
test_a_estrella_h3()
print()
test_a_estrella_heuristicas()
print()
test_greedy_vs_a_estrella()
print()
test_admisibilidad()