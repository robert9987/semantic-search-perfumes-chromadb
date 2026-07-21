from __future__ import annotations

import tempfile
import unittest
import warnings
from pathlib import Path

import chromadb

from src.config import (
    COLLECTION_NAME,
    DOCUMENTOS_INICIALES_PATH,
    DOCUMENTOS_NUEVOS_PATH,
)
from src.data_loader import cargar_documentos
from src.embeddings import EmbeddingsPerfumeria
from src.vector_store import (
    buscar_resultados,
    insertar_documentos,
)


warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module="chromadb.*",
)


class SearchRankingTest(unittest.TestCase):
    def setUp(self) -> None:
        db_path = Path(tempfile.mkdtemp(prefix="test_perfumeria_chroma_db_"))
        client = chromadb.PersistentClient(path=str(db_path))
        self.collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=EmbeddingsPerfumeria(),
            metadata={"hnsw:space": "cosine"},
        )

        documentos = cargar_documentos(DOCUMENTOS_INICIALES_PATH)
        documentos.extend(cargar_documentos(DOCUMENTOS_NUEVOS_PATH))
        insertar_documentos(self.collection, documentos)

    def assertTopProduct(self, query: str, expected_product: str) -> None:
        resultados = buscar_resultados(self.collection, query, n_resultados=3)

        self.assertGreater(len(resultados), 0)
        self.assertEqual(resultados[0]["producto"], expected_product)

    def test_citrico_query_returns_sol_citrico(self) -> None:
        self.assertTopProduct(
            "Busco un perfume citrico fresco con bergamota limon y naranja",
            "Sol Citrico",
        )

    def test_wood_query_returns_cedro_vetiver(self) -> None:
        self.assertTopProduct(
            "Busco maderas cedro vetiver pachuli seco elegante masculino",
            "Cedro Vetiver",
        )

    def test_oriental_query_returns_ambar_oriental(self) -> None:
        self.assertTopProduct(
            "Quiero una fragancia oriental sensual calida con ambar y vainilla",
            "Ambar Oriental",
        )

    def test_chypre_query_returns_chipre_luminoso(self) -> None:
        self.assertTopProduct(
            "Quiero un chipre fresco juvenil con bergamota pachuli musgo ambar",
            "Chipre Luminoso",
        )

    def test_aquatic_query_returns_agua_clara(self) -> None:
        self.assertTopProduct(
            "Busco una fragancia acuatica limpia liviana con notas marinas para diario",
            "Agua Clara",
        )


if __name__ == "__main__":
    unittest.main()
