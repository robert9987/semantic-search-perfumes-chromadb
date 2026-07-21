from src.config import (
    COLLECTION_NAME,
    DEFAULT_QUERY,
    DOCUMENTOS_INICIALES_PATH,
    DOCUMENTOS_NUEVOS_PATH,
)
from src.data_loader import cargar_documentos
from src.embeddings import EmbeddingsPerfumeria
from src.main import main
from src.vector_store import (
    buscar_resultados,
    crear_cliente,
    crear_coleccion,
    insertar_documentos,
)


if __name__ == "__main__":
    main()
