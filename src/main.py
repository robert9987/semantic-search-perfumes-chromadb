from __future__ import annotations

import argparse

from src.config import (
    DEFAULT_QUERY,
    DOCUMENTOS_INICIALES_PATH,
    DOCUMENTOS_NUEVOS_PATH,
)
from src.data_loader import cargar_documentos
from src.vector_store import (
    buscar_resultados,
    crear_cliente,
    crear_coleccion,
    insertar_documentos,
)


def buscar(collection, query: str, n_resultados: int) -> None:
    print(f"\nQuery: {query!r}")
    print("-" * 80)

    for posicion, resultado in enumerate(
        buscar_resultados(collection, query, n_resultados), start=1
    ):
        print(f"{posicion}. similitud ~= {resultado['similitud']:.3f}")
        print(
            f"   producto: {resultado['producto']} | familia: {resultado['familia_olfativa']} | subfamilia: {resultado['subfamilia']}"
        )
        print(f"   notas: {resultado['notas']}")
        print(f"   etiquetas: {resultado['etiquetas']}")
        print(f"   comentario: {resultado['comentario']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Demo de busqueda semantica con ChromaDB para comentarios de perfumeria."
    )
    parser.add_argument(
        "--query",
        default=DEFAULT_QUERY,
        help="Consulta semantica a ejecutar.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Cantidad de resultados a mostrar.",
    )
    parser.add_argument(
        "--persist-dir",
        default=None,
        help="Carpeta opcional para guardar la base ChromaDB. Si se omite, usa una base temporal.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    documentos_iniciales = cargar_documentos(DOCUMENTOS_INICIALES_PATH)
    documentos_nuevos = cargar_documentos(DOCUMENTOS_NUEVOS_PATH)

    print("1. Crear base vectorial y coleccion")
    client = crear_cliente(args.persist_dir)
    collection = crear_coleccion(client)

    print("\n2. Insertar comentarios iniciales")
    insertar_documentos(collection, documentos_iniciales)
    print(f"Documentos indexados: {collection.count()}")

    print("\n3. Busqueda semantica inicial")
    buscar(collection, args.query, args.top_k)

    print("\n4. Insertar nueva data y repetir la misma query")
    insertar_documentos(collection, documentos_nuevos)
    print(f"Documentos indexados: {collection.count()}")
    buscar(collection, args.query, args.top_k)


if __name__ == "__main__":
    main()
