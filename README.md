 Busqueda semantica para perfumeria con ChromaDB

Proyecto practico de base de datos vectorial aplicado a comentarios ficticios de perfumes. Simula un buscador semantico: el usuario escribe una necesidad en lenguaje natural y el sistema devuelve los productos mas parecidos por significado.

Los datos estan organizados con una taxonomia inspirada en la rueda de fragancias: floral, frutal, fougere, citrico, aromatico, maderas, oriental, chipre y subfamilias frescas/acuatica.

 Objetivo

Construir una demo simple que muestre el flujo principal de una base vectorial:

1. Crear una base ChromaDB.
2. Crear una coleccion de comentarios de perfumeria.
3. Convertir textos en vectores con una funcion de embeddings didactica basada en familias olfativas.
4. Ejecutar una busqueda semantica.
5. Insertar nuevos comentarios y repetir la misma busqueda.

 Tecnologias

- Python
- ChromaDB
- JSON como fuente de datos
- VS Code como entorno recomendado

 Estructura

```text
.
|-- data/
|   |-- perfumes_iniciales.json
|   `-- perfumes_nuevos.json
|-- src/
|   |-- config.py
|   |-- data_loader.py
|   |-- embeddings.py
|   |-- main.py
|   `-- vector_store.py
|-- tests/
|   `-- test_search.py
|-- examples/
|   `-- queries.md
|-- ejercicio_0_chromadb.py
|-- requirements.txt
|-- README.md
`-- .gitignore
```
Preparacion en VS Code

Abrir esta carpeta en Visual Studio Code:

```powershell
code "D:\OneDrive\Office importante\semantic-search-perfumes-chromadb"
```

Si `code` no esta habilitado, abrir VS Code manualmente y elegir:

```text
File > Open Folder
```

Luego seleccionar:

```text
D:\OneDrive\Office importante\semantic-search-perfumes-chromadb
```

Crear entorno virtual

En la terminal integrada de VS Code:

```powershell
& "C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m venv .venv
```

Instalar dependencias:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
```

Ejecutar demo por consola

```powershell
.\.venv\Scripts\python.exe -m src.main
```

Ejemplo con una consulta propia:

```powershell
.\.venv\Scripts\python.exe -m src.main --query "Quiero una fragancia oriental sensual calida con ambar y vainilla para la noche"
```

Tambien se mantiene el script original como acceso rapido:

```powershell
.\.venv\Scripts\python.exe .\ejercicio_0_chromadb.py
```

Ejecutar tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Los tests validan que algunas consultas semanticas devuelvan primero la familia esperada. Por ejemplo, una busqueda con `ambar`, `vainilla`, `oriental` y `sensual` debe rankear primero `Familia Oriental`.

Ejemplos de consultas

Ver ejemplos listos para copiar en:

```text
examples/queries.md
```
¿Qué observar?

La misma query se ejecuta dos veces en la demo de consola:

- Primero contra los comentarios iniciales.
- Despues de insertar nuevos comentarios.

Si el nuevo comentario esta cerca de la query, sube en el ranking. Por ejemplo, una consulta sobre perfume fresco y citrico deberia acercarse a comentarios con limon, bergamota, naranja, limpieza o uso de dia.

Cada perfume incluye metadata pensada para busqueda y analisis:

- `familia_olfativa`: familia principal, por ejemplo `floral`, `citrico`, `oriental`.
- `subfamilia`: detalle dentro de la familia, por ejemplo `floral suave`, `maderas secas`.
- `notas`: materias primas o acordes, por ejemplo `bergamota`, `vainilla`, `cedro`.
- `etiquetas`: sensaciones y posicionamiento, por ejemplo `sensual`, `alegre`, `masculino`.

 Aprendizajes

- Una base vectorial permite buscar por similitud semantica, no solo por coincidencia exacta.
- ChromaDB guarda documentos, metadata y vectores.
- Insertar nuevos documentos puede cambiar el ranking de resultados.
- La calidad de la busqueda depende mucho del embedding.
- Un embedding manual ayuda a entender el mecanismo, pero no reemplaza un modelo real.

 Limitaciones

- El embedding actual usa palabras clave.
- Si la query usa sinonimos que no estan en el vocabulario, puede fallar.
- No hay embeddings reales todavia.
- No hay interfaz web ni API.

Proximas mejoras

- Reemplazar el embedding didactico por embeddings reales de un modelo.
- Agregar mas comentarios, subfamilias y notas olfativas.
- Crear una API con FastAPI.
- Crear una interfaz web simple cuando el proyecto crezca.
- Agregar filtros por ocasion, familia olfativa, intensidad y presupuesto.
- Guardar resultados en CSV para analizarlos.
