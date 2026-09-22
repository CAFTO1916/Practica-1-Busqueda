# Fase 3 - Busqueda local

import random
import networkx as nx

from fase2 import cargar_grafo_urbano
from fase2 import a_estrella
from fase2 import heuristica_haversine

def seleccionar_puntos_entrega(G, cantidad=10):
    componentes = list(nx.strongly_connected_components(G))
    componente_mayor = max(componentes, key=len)
    nodos = list(componente_mayor)

    random.seed(42)
    puntos = random.sample(nodos, cantidad)

    return puntos


def distancia_entre_nodos(G, origen, destino):
    def h(nodo, destino):
        return heuristica_haversine(G, nodo, destino)

    resultado = a_estrella(G, origen, destino, h)
    return resultado[3]

def costo_ruta(G, ruta):
    total = 0.0

    for i in range(len(ruta) - 1):
        origen = ruta[i]
        destino = ruta[i + 1]
        distancia = distancia_entre_nodos(G, origen, destino)
        total = total + distancia

    return total

if __name__ == "__main__":
    G, G_proyectado = cargar_grafo_urbano()
    print("Grafo cargado desde Fase 3")

    puntos_entrega = seleccionar_puntos_entrega(G, 10)

    print("Puntos de entrega:")
    print(puntos_entrega)
    
    costo_inicial = costo_ruta(G, puntos_entrega)
    print("Costo inicial de los 10 puntos:", costo_inicial, "metros")

    origen, destino = next(iter(G.edges()))

    distancia = distancia_entre_nodos(G, origen, destino)

    print("Origen:", origen)
    print("Destino:", destino)
    print("Distancia:", distancia, "metros")

    ruta_prueba = [origen, destino]
    costo = costo_ruta(G, ruta_prueba)

    print("Costo de la ruta:", costo, "metros")

    tercer_nodo = next(iter(G.successors(destino)))

    ruta_tres_puntos = [origen, destino, tercer_nodo]
    costo_tres_puntos = costo_ruta(G, ruta_tres_puntos)

    print("Ruta de tres puntos:", ruta_tres_puntos)
    print("Costo de tres puntos:", costo_tres_puntos, "metros")