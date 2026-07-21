from __future__ import annotations

import tempfile
from pathlib import Path

import chromadb

from src.config import COLLECTION_NAME
from src.embeddings import EmbeddingsPerfumeria


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
