import osmnx as ox
import networkx as nx
import time
from collections import deque
import heapq
import random
import time

# 1. Función para descargar el mapa de prueba (ej. zona centro/norte de CDMX)
def cargar_grafo_urbano():
    # Descarga un grafo dirigido de la zona norte/centro de la CDMX
    place_name = "Delegación Gustavo A. Madero, Ciudad de Mexico, Mexico" # Ejemplo
    G = ox.graph_from_place(place_name, network_type="drive")
    return G

from collections import deque

# 2. Implementación de BFS
def bfs(G, origen, destino):
    # TODO: Implementar lógica de BFS con cola (deque), control de visitados y reconstrucción de ruta
    """
    Implementación de BFS (Breadth-First Search) para un grafo urbano (DiGraph / MultiDiGraph).
    
    Parámetros:
    - G: El grafo de osmnx / networkx.
    - origen: ID del nodo de inicio (depósito).
    - destino: ID del nodo objetivo (punto de entrega).
    
    Retorna:
    - camino: Lista de nodos que conforman la ruta óptima en saltos.
    - nodos_expandidos: Cantidad de nodos extraídos de la frontera.
    - max_frontera: Tamaño máximo que alcanzó la cola durante la búsqueda.
    - distancia_total: Suma de las longitudes físicas de los arcos en metros.
    - num_arcos: Cantidad de saltos (aristas) del camino.
    """
    
    # 2.1. Validación inicial: si el origen y el destino son el mismo
    if origen == destino:
        return [origen], 0, 1, 0.0, 0

    # 2.2. Inicialización de estructuras de datos
    # Usamos una cola FIFO (deque) para garantizar la exploración por niveles (menor número de saltos)
    frontera = deque([origen])
    
    # Conjunto de visitados (lista cerrada) para evitar ciclos infinitos en el grafo urbano
    visitados = {origen}
    
    # Diccionario para rastrear los padres y poder reconstruir el camino al finalizar
    padres = {origen: None}
    
    # Contadores para las métricas solicitadas
    nodos_expandidos = 0
    max_frontera = 1

    # 2.3. Ciclo principal de exploración
    while frontera:
        # Registrar el tamaño máximo que va tomando la cola (frontera)
        if len(frontera) > max_frontera:
            max_frontera = len(frontera)

        # Extraer el primer nodo de la cola (FIFO: First In, First Out)
        nodo_actual = frontera.popleft()
        nodos_expandidos += 1

        # Condición de parada: si llegamos al destino buscado
        if nodo_actual == destino:
            break

        # Explorar los vecinos salientes del nodo actual (interconexiones viales)
        # G.successors(nodo) obtiene los nodos vecinos dirigidos en osmnx
        for vecino in G.successors(nodo_actual):
            if vecino not in visitados:
                visitados.add(vecino)
                padres[vecino] = nodo_actual  # Guardamos de qué nodo vino
                frontera.append(vecino)       # Añadimos el vecino al final de la cola

    # 2.4. Reconstrucción del camino (si el destino nunca fue alcanzado)
    if destino not in padres:
        return [], nodos_expandidos, max_frontera, 0.0, 0  # No hay ruta conectada

    camino = []
    actual = destino
    while actual is not None:
        camino.append(actual)
        actual = padres[actual]
    
    # Invertir el camino para que vaya desde el origen hasta el destino
    camino.reverse()

    # 2.5. Cálculo de métricas finales del camino encontrado (Metros y Arcos)
    distancia_total = 0.0
    for i in range(len(camino) - 1):
        u = camino[i]
        v = camino[i+1]
        
        # En osmnx (que usa MultiDiGraph), un arco puede tener múltiples sub-segmentos o datos.
        # Obtenemos los datos de la arista entre u y v sumando su longitud en metros ('length').
        datos_arista = G.get_edge_data(u, v)
        if datos_arista:
            # Si es un MultiDiGraph, tomamos la primera opción de la llave 0
            if isinstance(datos_arista, dict) and 0 in datos_arista:
                distancia_total += datos_arista[0].get('length', 0.0)
            else:
                distancia_total += datos_arista.get('length', 0.0)

    num_arcos = len(camino) - 1

    return camino, nodos_expandidos, max_frontera, distancia_total, num_arcos

# 3. Implementación de DFS Iterativo con lista cerrada
def dfs_iterativo(G, origen, destino):

    # TODO: Implementar DFS con pila y manejo de ciclos

    """
    Implementación de DFS (Depth-First Search) Iterativo para un grafo urbano.
    Utiliza una pila (Stack) y un conjunto de visitados (lista cerrada) para prevenir ciclos.
    
    Parámetros:
    - G: El grafo de osmnx / networkx.
    - origen: ID del nodo de inicio (depósito).
    - destino: ID del nodo objetivo (punto de entrega).
    
    Retorna:
    - camino: Lista de nodos que conforman la ruta encontrada.
    - nodos_expandidos: Cantidad de nodos procesados.
    - max_frontera: Tamaño máximo que alcanzó la pila durante la búsqueda.
    - distancia_total: Suma de las longitudes físicas de los arcos en metros.
    - num_arcos: Cantidad de saltos (aristas) del camino.
    """
    
    # 3.1. Validación inicial si el origen y el destino son idénticos
    if origen == destino:
        return [origen], 0, 1, 0.0, 0

    # 3.2. Inicialización de estructuras
    # En Python, una lista normal con .append() y .pop() actúa perfectamente como una Pila (LIFO: Last In, First Out)
    frontera = [origen]
    
    # Lista cerrada (visitados) obligatoria para evitar ciclos infinitos en grafos urbanos cíclicos[cite: 1]
    visitados = set()
    
    # Diccionario para rastrear los padres y reconstruir el camino
    padres = {origen: None}
    
    # Contadores de métricas
    nodos_expandidos = 0
    max_frontera = 1

    # 3.3. Ciclo principal de exploración
    while frontera:
        # Registrar el tamaño máximo que va alcanzando la frontera (pila)
        if len(frontera) > max_frontera:
            max_frontera = len(frontera)

        # Extraer el último elemento añadido (LIFO)
        nodo_actual = frontera.pop()

        # Si el nodo ya fue visitado completamente, lo ignoramos para evitar reprocesos o ciclos
        if nodo_actual in visitados:
            continue

        # Marcamos como visitado al extraerlo de la frontera
        visitados.add(nodo_actual)
        nodos_expandidos += 1

        # Condición de parada: si llegamos al punto de entrega deseado
        if nodo_actual == destino:
            break

        # Explorar los vecinos salientes del nodo actual
        vecinos = list(G.successors(nodo_actual))
        
        # Invertimos la lista de vecinos antes de meterlos a la pila. 
        # Como la pila extrae el último, invertir asegura que el primer vecino natural 
        # sea procesado primero (comportamiento estándar de DFS).
        for vecino in reversed(vecinos):
            if vecino not in visitados and vecino not in padres:
                padres[vecino] = nodo_actual
                frontera.append(vecino)

    # 3.4. Reconstrucción del camino (si el destino nunca fue alcanzado)
    if destino not in padres:
        return [], nodos_expandidos, max_frontera, 0.0, 0

    camino = []
    actual = destino
    while actual is not None:
        camino.append(actual)
        actual = padres[actual]
    
    # Invertir para ordenar de origen a destino
    camino.reverse()

    # 3.5. Cálculo de métricas finales del camino (Metros y Arcos)
    distancia_total = 0.0
    for i in range(len(camino) - 1):
        u = camino[i]
        v = camino[i+1]
        
        datos_arista = G.get_edge_data(u, v)
        if datos_arista:
            if isinstance(datos_arista, dict) and 0 in datos_arista:
                distancia_total += datos_arista[0].get('length', 0.0)
            else:
                distancia_total += datos_arista.get('length', 0.0)

    num_arcos = len(camino) - 1

    return camino, nodos_expandidos, max_frontera, distancia_total, num_arcos

# 4. Implementación de UCS

def ucs(G, origen, destino):

    # TODO: Implementar UCS con heapq evaluando pesos en metros (w='length')

    """
    Implementación de UCS (Uniform Cost Search) para un grafo urbano ponderado.
    Utiliza una cola de prioridad (min-heap) basada en la longitud física de las calles en metros[cite: 1].
    
    Parámetros:
    - G: El grafo de osmnx / networkx.
    - origen: ID del nodo de inicio (depósito).
    - destino: ID del nodo objetivo (punto de entrega).
    
    Retorna:
    - camino: Lista de nodos que conforman la ruta de menor distancia.
    - nodos_expandidos: Cantidad de nodos extraídos de la frontera.
    - max_frontera: Tamaño máximo que alcanzó la cola de prioridad.
    - distancia_total: Costo real mínimo acumulado (en metros).
    - num_arcos: Cantidad de saltos (aristas) del camino óptimo.
    """
    
    # 4.1. Validación inicial si el origen y el destino son idénticos
    if origen == destino:
        return [origen], 0, 1, 0.0, 0

    # 4.2. Inicialización de estructuras
    # La frontera es una cola de prioridad (min-heap) que almacena tuplas: (costo_acumulado_g, nodo_actual)
    frontera = [(0.0, origen)]
    
    # Diccionario para almacenar el costo g(n) más bajo conocido para llegar a cada nodo
    g_costos = {origen: 0.0}
    
    # Diccionario de padres para la reconstrucción del camino final
    padres = {origen: None}
    
    # Conjunto de nodos ya expandidos definitivamente (lista cerrada)
    explorados = set()
    
    # Contadores de métricas
    nodos_expandidos = 0
    max_frontera = 1

    # 4.3. Ciclo principal de exploración
    while frontera:
        # Registrar el tamaño máximo que va alcanzando la cola de prioridad
        if len(frontera) > max_frontera:
            max_frontera = len(frontera)

        # Extraer el nodo que tiene el menor costo acumulado g(n) actual
        costo_actual, nodo_actual = heapq.heappop(frontera)

        # Si el nodo ya fue explorado por un camino más óptimo o igual, lo omitimos
        if nodo_actual in explorados:
            continue

        # Marcamos como explorado al sacarlo de la frontera
        explorados.add(nodo_actual)
        nodos_expandidos += 1

        # Condición de parada: si alcanzamos el punto de entrega objetivo
        if nodo_actual == destino:
            break

        # Explorar los vecinos salientes del nodo actual
        for vecino in G.successors(nodo_actual):
            
            # Obtener el peso real del arco (longitud en metros 'length' provista por osmnx)
            datos_arista = G.get_edge_data(nodo_actual, vecino)
            peso_arco = 0.0
            if datos_arista:
                if isinstance(datos_arista, dict) and 0 in datos_arista:
                    peso_arco = datos_arista[0].get('length', 0.0)
                else:
                    peso_arco = datos_arista.get('length', 0.0)

            # Calcular el nuevo costo acumulado (g de n) hacia el vecino
            nuevo_costo = costo_actual + peso_arco

            # Si encontramos un camino nuevo al vecino y su costo es menor al registrado previamente
            if vecino not in g_costos or nuevo_costo < g_costos[vecino]:
                g_costos[vecino] = nuevo_costo
                padres[vecino] = nodo_actual
                # Insertamos el nuevo costo y nodo en la cola de prioridad
                heapq.heappush(frontera, (nuevo_costo, vecino))

    # 4.4. Reconstrucción del camino (si el destino nunca fue alcanzado)
    if destino not in padres:
        return [], nodos_expandidos, max_frontera, 0.0, 0

    camino = []
    actual = destino
    while actual is not None:
        camino.append(actual)
        actual = padres[actual]
    
    # Invertir para ordenar la ruta desde el origen hasta el destino
    camino.reverse()

    # 4.5. Métricas finales del camino óptimo
    distancia_total = g_costos[destino]  # El costo acumulado final es la distancia exacta en metros
    num_arcos = len(camino) - 1

    return camino, nodos_expandidos, max_frontera, distancia_total, num_arcos

# 5 Verificación sobre puntos de entrega alcanzables
def verificar_conectividad(G, deposito, puntos_entrega):
    """
    Verifica qué puntos de entrega son alcanzables desde el depósito central 
    utilizando el algoritmo BFS.
    
    Parámetros:
    - G: El grafo urbano (NetworkX DiGraph).
    - deposito: ID del nodo que funge como almacén/depósito.
    - puntos_entrega: Lista de IDs de nodos correspondientes a los destinos.
    
    Retorna:
    - alcanzables: Lista de puntos de entrega que SÍ se pueden alcanzar.
    - inalcanzables: Lista de puntos de entrega que NO tienen ruta desde el depósito.
    """
    alcanzables = []
    inalcanzables = []

    print(f"Verificando accesibilidad desde el depósito (Nodo: {deposito})...")
    
    for destino in puntos_entrega:
        # Ejecutamos BFS para ver si existe un camino hacia el destino
        camino, _, _, _, _ = bfs(G, deposito, destino)
        
        if camino:
            alcanzables.append(destino)
        else:
            inalcanzables.append(destino)
            
    print(f"-> Total alcanzables: {len(alcanzables)}")
    print(f"-> Total inalcanzables: {len(inalcanzables)}")
    
    return alcanzables, inalcanzables

    
# 6 Generación pruebas
def ejecutar_experimentos(G, origen, alcanzables, num_pruebas=5):
    """
    Ejecuta BFS, DFS y UCS sobre al menos 5 pares origen-destino distintos 
    y recopila todas las métricas solicitadas por la rúbrica.
    
    Parámetros:
    - G: El grafo urbano.
    - origen: Nodo depósito de inicio.
    - alcanzables: Lista de nodos destino válidos.
    - num_pruebas: Número de instancias a probar (mínimo 5).
    """
    import random
    
    if len(alcanzables) < num_pruebas:
        print(f"Advertencia: Solo hay {len(alcanzables)} nodos alcanzables. Se ajustarán las pruebas.")
        num_pruebas = len(alcanzables)

    # Seleccionar aleatoriamente los destinos de prueba
    destinos_prueba = random.sample(alcanzables, num_pruebas)
    
    print(f"\n==================================================")
    print(f" INICIANDO EXPERIMENTOS (Origen: {origen})")
    print(f"==================================================")
    
    for i, destino in enumerate(destinos_prueba, 1):
        print(f"\n--- Instancia {i} (Destino: {destino}) ---")
        
        # 1. Evaluar BFS
        inicio = time.perf_counter()
        camino_bfs, exp_bfs, max_f_bfs, dist_bfs, arcos_bfs = bfs(G, origen, destino)
        tiempo_bfs = (time.perf_counter() - inicio) * 1000  # Convertir a milisegundos
        
        # 2. Evaluar DFS
        inicio = time.perf_counter()
        camino_dfs, exp_dfs, max_f_dfs, dist_dfs, arcos_dfs = dfs_iterativo(G, origen, destino)
        tiempo_dfs = (time.perf_counter() - inicio) * 1000
        
        # 3. Evaluar UCS
        inicio = time.perf_counter()
        camino_ucs, exp_ucs, max_f_ucs, dist_ucs, arcos_ucs = ucs(G, origen, destino)
        tiempo_ucs = (time.perf_counter() - inicio) * 1000
        
        # Mostrar resultados formateados por algoritmo
        print(f"{'Algoritmo':<10} | {'Nodos Exp.':<10} | {'Max Frontera':<12} | {'Arcos':<6} | {'Distancia (m)':<14} | {'Tiempo (ms)'}")
        print("-" * 75)
        print(f"{'BFS':<10} | {exp_bfs:<10} | {max_f_bfs:<12} | {arcos_bfs:<6} | {dist_bfs:<14.2f} | {tiempo_bfs:.4f}")
        print(f"{'DFS':<10} | {exp_dfs:<10} | {max_f_dfs:<12} | {arcos_dfs:<6} | {dist_dfs:<14.2f} | {tiempo_dfs:.4f}")
        print(f"{'UCS':<10} | {exp_ucs:<10} | {max_f_ucs:<12} | {arcos_ucs:<6} | {dist_ucs:<14.2f} | {tiempo_ucs:.4f}")

if __name__ == "__main__":
    print("1. Descargando grafo urbano de prueba...")
    lugar = "Gustavo A. Madero, Ciudad de Mexico, Mexico"
    G = ox.graph_from_place(lugar, network_type="drive")
    
    nodos = list(G.nodes)
    deposito = random.choice(nodos)
    puntos_entrega = random.sample(nodos, 15) # Muestra de 15 puntos
    
    # Paso 1: Verificar conectividad
    alcanzables, inalcanzables = verificar_conectividad(G, deposito, puntos_entrega)
    
    # Paso 2: Ejecutar experimentos con 5 pares origen-destino alcanzables
    if alcanzables:
        ejecutar_experimentos(G, deposito, alcanzables, num_pruebas=5)
    else:
        print("Error: No se encontraron nodos alcanzables para realizar los experimentos.")