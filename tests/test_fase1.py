import networkx as nx
# Asegúrate de importar tus funciones desde tu módulo src.fase1 (o ajusta la ruta según organices tus carpetas)
from fase1 import bfs, dfs_iterativo, ucs

def crear_grafo_prueba():
    """
    Crea un grafo dirigido artificial y pequeño con pesos conocidos (length)
    para probar el comportamiento lógico de los algoritmos de búsqueda.
    """
    G = nx.DiGraph()
    # Definimos rutas con diferentes características:
    # Ruta 1: A -> B -> C -> D (3 saltos, pero distancias cortas: 10 + 10 + 10 = 30 metros)
    G.add_edge('A', 'B', length=10.0)
    G.add_edge('B', 'C', length=10.0)
    G.add_edge('C', 'D', length=10.0)
    
    # Ruta 2: A -> C -> D (2 saltos, pero un tramo inicial más largo: 30 + 10 = 40 metros)
    G.add_edge('A', 'C', length=30.0)
    G.add_edge('C', 'D', length=10.0)
    
    return G

def test_bfs_encuentra_menos_saltos():
    """
    Verifica que BFS prioriza estrictamente el menor número de arcos (saltos),
    aunque la distancia física en metros no sea la óptima.
    """
    G = crear_grafo_prueba()
    camino, _, _, _, arcos = bfs(G, 'A', 'D')
    
    # El camino A -> C -> D tiene 2 arcos, mientras que A -> B -> C -> D tiene 3. 
    # BFS debe elegir el de 2 arcos.
    assert camino == ['A', 'C', 'D']
    assert arcos == 2

def test_ucs_encuentra_menor_distancia():
    """
    Verifica que UCS prioriza estrictamente el menor costo acumulado en metros,
    ignorando si requiere más saltos.
    """
    G = crear_grafo_prueba()
    camino, _, _, distancia, _ = ucs(G, 'A', 'D')
    
    # Ruta A -> B -> C -> د suma 30 metros (óptimo para UCS).
    # Ruta A -> C -> D suma 40 metros.
    assert camino == ['A', 'B', 'C', 'D']
    assert distancia == 30.0

def test_dfs_encuentra_camino_valido():
    """
    Verifica que DFS Iterativo logra encontrar una ruta válida sin fallar 
    ni estancarse en grafos con bifurcaciones.
    """
    G = crear_grafo_prueba()
    camino, _, _, _, _ = dfs_iterativo(G, 'A', 'D')
    
    assert len(camino) > 0
    assert camino[0] == 'A'
    assert camino[-1] == 'D'