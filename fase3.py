# Fase 3 - Busqueda local

from fase2 import cargar_grafo_urbano
from fase2 import a_estrella
from fase2 import heuristica_haversine


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