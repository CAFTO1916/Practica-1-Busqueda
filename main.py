"""
Programa principal.

Solo importa (referencia) los módulos de cada fase y llama a la
función main() de la fase que el usuario elija en el menú. Toda la
lógica de búsqueda vive en fase1.py, fase2.py y fase3.py; este
archivo no la duplica.
"""

from src import fase1
from src import fase2
from src import fase3


OPCIONES = {
    "1": ("Fase 1 - Búsqueda no informada (BFS, DFS, UCS)", fase1.main),
    "2": ("Fase 2 - Búsqueda informada (A*, Greedy, heurísticas)", fase2.main),
    "3": ("Fase 3 - Búsqueda local (Recocido simulado, algoritmo genético)", fase3.main),
}


def mostrar_menu():
    print("\n==================================================")
    print(" PRÁCTICA 1 - BÚSQUEDA")
    print("==================================================")
    for clave, (titulo, _) in OPCIONES.items():
        print(f" {clave}. {titulo}")
    print(" 0. Salir")


def main():
    while True:
        mostrar_menu()
        eleccion = input("\nSeleccione una opción: ").strip()

        if eleccion == "0":
            print("Saliendo del programa.")
            break

        opcion = OPCIONES.get(eleccion)
        if opcion is None:
            print("Opción no válida, intente de nuevo.")
            continue

        titulo, funcion = opcion
        print(f"\nEjecutando: {titulo}\n")
        funcion()


if __name__ == "__main__":
    main()
