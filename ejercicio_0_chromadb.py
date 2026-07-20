from __future__ import annotations

import argparse
import json
import math
import tempfile
import unicodedata
from pathlib import Path
from typing import Iterable

import chromadb


COLLECTION_NAME = "comentarios_perfumeria"
DEFAULT_QUERY = "Busco un perfume fresco citrico limpio y alegre para usar de dia"
DATA_DIR = Path("data")
DOCUMENTOS_INICIALES_PATH = DATA_DIR / "perfumes_iniciales.json"
DOCUMENTOS_NUEVOS_PATH = DATA_DIR / "perfumes_nuevos.json"


class EmbeddingsPerfumeria:
    """Embedding didactico basado en familias de la rueda de fragancias.

    Cada dimension representa una familia olfativa, sensacion o contexto de uso.
    En un proyecto real se usaria un modelo de embeddings, pero esta version
    ayuda a entender el flujo texto -> vector -> similitud.
    """

    dimensiones = [
        (
            "floral",
            {
                "floral",
                "flores",
                "rosa",
                "jazmin",
                "primavera",
                "primaveral",
                "suave",
                "delicada",
                "romantica",
                "femenina",
            },
        ),
        (
            "frutal",
            {
                "frutal",
                "durazno",
                "frutilla",
                "anana",
                "melon",
                "sandia",
                "rojos",
                "ciruela",
                "alegre",
                "vibrante",
                "jovial",
            },
        ),
        (
            "fougere",
            {
                "fougere",
                "lavanda",
                "musgo",
                "encina",
                "bergamota",
                "bosque",
                "humedo",
                "verde",
                "tradicional",
            },
        ),
        (
            "citrico_fresco",
            {
                "citrico",
                "citrica",
                "citricos",
                "bergamota",
                "limon",
                "naranja",
                "fresco",
                "fresca",
                "limpio",
                "limpia",
                "volatil",
                "dia",
            },
        ),
        (
            "aromatico",
            {
                "aromatico",
                "aromatica",
                "salvia",
                "romero",
                "comino",
                "lavanda",
                "hierbas",
                "especias",
                "herbal",
                "intenso",
            },
        ),
        (
            "maderas",
            {
                "madera",
                "maderas",
                "amaderado",
                "cedro",
                "abedul",
                "sandalo",
                "vetiver",
                "pachuli",
                "oud",
                "seco",
                "elegante",
                "distinguido",
            },
        ),
        (
            "oriental",
            {
                "oriental",
                "ambar",
                "ambarado",
                "vainilla",
                "resinas",
                "clavo",
                "cardamomo",
                "jengibre",
                "cacao",
                "regaliz",
                "calido",
                "sensual",
                "dulce",
            },
        ),
        (
            "chipre",
            {
                "chipre",
                "bergamota",
                "flores",
                "pachuli",
                "musgo",
                "ambar",
                "almizcle",
                "juvenil",
                "informal",
                "sofisticada",
                "sofisticado",
            },
        ),
        (
            "acuatico_diario",
            {
                "acuatico",
                "acuatica",
                "marinas",
                "agua",
                "limpia",
                "liviana",
                "liviano",
                "diario",
                "dias",
                "oficina",
            },
        ),
        (
            "genero_estilo",
            {
                "femenino",
                "femenina",
                "masculino",
                "unisex",
                "juvenil",
                "formal",
                "informal",
                "tradicional",
                "moderno",
            },
        ),
        (
            "noche_sensualidad",
            {
                "noche",
                "salida",
                "sensual",
                "calido",
                "calida",
                "envolvente",
                "elegante",
            },
        ),
    ]

    def name(self) -> str:
        return "embeddings_perfumeria_didacticos"

    def __call__(self, input: Iterable[str]) -> list[list[float]]:
        return [self._vectorizar(texto) for texto in input]

    def embed_query(self, input: Iterable[str]) -> list[list[float]]:
        return self.__call__(input)

    def _vectorizar(self, texto: str) -> list[float]:
        tokens = set(_tokenizar(texto))

        vector = []
        for _, palabras_clave in self.dimensiones:
            coincidencias = len(tokens & palabras_clave)
            vector.append(float(coincidencias))

        norma = math.sqrt(sum(valor * valor for valor in vector))
        if norma == 0:
            return vector

        return [valor / norma for valor in vector]


def _tokenizar(texto: str) -> list[str]:
    texto_normalizado = unicodedata.normalize("NFD", texto.lower())
    texto_sin_tildes = "".join(
        caracter
        for caracter in texto_normalizado
        if unicodedata.category(caracter) != "Mn"
    )

    return [
        palabra.strip(".,;:!?()[]{}\"'")
        for palabra in texto_sin_tildes.split()
        if palabra.strip(".,;:!?()[]{}\"'")
    ]


def cargar_documentos(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def crear_cliente(persist_dir: str | None):
    if persist_dir:
        db_path = Path(persist_dir)
        print(f"Base persistente: {db_path.resolve()}")
    else:
        db_path = Path(tempfile.mkdtemp(prefix="perfumeria_chroma_db_"))
        print(f"Base temporal: {db_path}")

    return chromadb.PersistentClient(path=str(db_path))


def crear_coleccion(client):
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=EmbeddingsPerfumeria(),
        metadata={"hnsw:space": "cosine"},
    )


def insertar_documentos(collection, items: list[dict]) -> None:
    collection.upsert(
        ids=[item["id"] for item in items],
        documents=[item["documento"] for item in items],
        metadatas=[item["metadata"] for item in items],
    )


def buscar_resultados(collection, query: str, n_resultados: int) -> list[dict]:
    resultados = collection.query(
        query_texts=[query],
        n_results=n_resultados,
        include=["documents", "metadatas", "distances"],
    )

    items = []
    for documento, metadata, distancia in zip(
        resultados["documents"][0],
        resultados["metadatas"][0],
        resultados["distances"][0],
    ):
        similitud_aproximada = max(0.0, min(1.0, 1 - distancia))
        items.append(
            {
                "producto": metadata["producto"],
                "familia_olfativa": metadata.get(
                    "familia_olfativa", metadata.get("categoria", "sin familia")
                ),
                "subfamilia": metadata.get("subfamilia", "sin subfamilia"),
                "notas": metadata.get("notas", "sin notas"),
                "etiquetas": metadata.get("etiquetas", "sin etiquetas"),
                "comentario": documento,
                "similitud": similitud_aproximada,
            }
        )

    return items


def buscar(collection, query: str, n_resultados: int) -> None:
    print(f"\nQuery: {query!r}")
    print("-" * 80)

    for posicion, resultado in enumerate(buscar_resultados(collection, query, n_resultados), start=1):
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
