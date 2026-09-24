cat << 'EOF' > README.md
# Práctica 1: Algoritmos de Búsqueda y Optimización en Grafos Viales

Este proyecto implementa y compara diferentes algoritmos de búsqueda no informada, búsqueda informada, heurísticas personalizadas y optimización local (problema del viajante - TSP) sobre redes viales urbanas utilizando datos reales de OpenStreetMap (Gustavo A. Madero, CDMX).

---

## Estructura del Proyecto

El proyecto está organizado de manera modular para separar la lógica de negocio, los cuadernos interactivos y los resultados generados:

```text
prac1/
│
├── src/                  # Módulos de código backend de cada fase
│   ├── fase1.py          # Búsqueda no informada (BFS, DFS, UCS) y conectividad
│   ├── fase2.py          # Búsqueda informada (A*, Greedy) y heurísticas (H1, H2, H3)
│   └── fase3.py          # Búsqueda local (Recocido Simulado y Algoritmo Genético)
│
├── notebooks/            # Cuadernos interactivos para documentación y pruebas
│   ├── Fase_1.ipynb
│   ├── Fase_2.ipynb
│   └── Fase_3.ipynb
│
├── data/                 # Resultados generados automáticamente (Mapas HTML y Gráficas PNG)
│   ├── mapa_fase2.html
│   ├── convergencia_fase3.png
│   ├── temperaturas_fase3.png
│   └── optimos_locales_fase3.png
│
└── README.md             # Documentación del proyecto



## Instalación
1. Clonar o abrir la carpeta del proyecto en tu terminal y crear un entorno virtual:
python3 -m venv venv

2.Activar el entorno virtual
source venv/bin/activate

3.Instalar las dependencias necesarias dentro del entorno virtual:
pip install osmnx networkx matplotlib folium jupyter notebook nbformat

## Configuración
. Red y Mapas: El sistema descarga automáticamente la red vial utilizando la API de OpenStreetMap mediante osmnx. Asegúrate de contar con conexión a internet estable la primera vez que ejecutes la carga de grafos.

. Almacenamiento de Resultados: Los scripts y cuadernos están configurados para crear y gestionar automáticamente la carpeta data/ donde se almacenarán los mapas interactivos en HTML y las gráficas comparativas de rendimiento en formato PNG.

## Ejecución
Opción A: A través de Jupyter Notebook
1. Con tu entorno virtual activo, inicia el servidor de Jupyter:
 jupyter notebook
2. En la interfaz web que se abre en tu navegador, navega a la carpeta notebooks/.
3.Abre el cuaderno de la fase que deseas probar (Fase_1.ipynb, Fase_2.ipynb o Fase_3.ipynb) y ejecuta sus celdas secuencialmente.

Opción B: Ejecución directa de los módulos de Python
Si prefieres correr la lógica directamente desde la terminal como scripts de Python, puedes ejecutar las funciones principales de cada fase.
# Ejemplo para ejecutar la Fase 2
python3 src/fase2.py

## Resultados Generados
Tras la ejecución exitosa de los scripts, encontrarás los siguientes archivos en la carpeta data/:mapa_fase2.html: Mapa interactivo con Folium comparando las rutas generadas por A* y Greedy.convergencia_fase3.png: Gráfica comparativa de convergencia entre Recocido Simulado (SA) y Algoritmo Genético (GA).temperaturas_fase3.png: Análisis del efecto de la temperatura inicial (T0) en el Recocido Simulado.optimos_locales_fase3.png: Distribución y frecuencia de los óptimos locales mediante búsquedas 2-opt.EOF
