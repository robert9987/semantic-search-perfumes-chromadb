# Busqueda semantica para perfumeria con ChromaDB

Proyecto practico de base de datos vectorial aplicado a comentarios ficticios de perfumes. Simula un buscador semantico: el usuario escribe una necesidad en lenguaje natural y el sistema devuelve las familias olfativas mas parecidas por significado.

Los datos estan organizados con una taxonomia inspirada en la rueda de fragancias: floral, frutal, fougere, citrico, aromatico, maderas, oriental, chipre y subfamilias frescas/acuatica.

## Objetivo

Construir una demo simple que muestre el flujo principal de una base vectorial:

1. Crear una base ChromaDB.
2. Crear una coleccion de comentarios de perfumeria.
3. Convertir textos en vectores con una funcion de embeddings didactica basada en familias olfativas.
4. Ejecutar una busqueda semantica.
5. Insertar nuevos comentarios y repetir la misma busqueda.

## Tecnologias

- Python
- ChromaDB
- JSON como fuente de datos
- VS Code como entorno recomendado

## Estructura

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
|   |-- vector_store.py
|   `-- web.py
|-- tests/
|   `-- test_search.py
|-- examples/
|   `-- queries.md
|-- ejercicio_0_chromadb.py
|-- requirements.txt
|-- README.md
`-- .gitignore
```

## Preparacion en VS Code

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

## Crear entorno virtual

En la terminal integrada de VS Code:

```powershell
& "C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m venv .venv
```

Instalar dependencias:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
```

## Ejecutar demo por consola

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

## Ejecutar frontend local

```powershell
.\.venv\Scripts\python.exe -m src.web
```

Luego abrir:

```text
http://127.0.0.1:8000
```

El frontend permite escribir una consulta, elegir familia olfativa y perfil/subfamilia desde listas desplegables, incluir o excluir los documentos nuevos y ver tarjetas con similitud, notas y metadata.

## Ejecutar tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Los tests validan que algunas consultas semanticas devuelvan primero la familia esperada. Por ejemplo, una busqueda con `ambar`, `vainilla`, `oriental` y `sensual` debe rankear primero `Familia Oriental`.

## Ejemplos de consultas

Ver ejemplos listos para copiar en:

```text
examples/queries.md
```

## Que observar

La misma query se ejecuta dos veces en la demo de consola:

- Primero contra los comentarios iniciales.
- Despues de insertar nuevos comentarios.

Si el nuevo comentario esta cerca de la query, sube en el ranking. Por ejemplo, una consulta sobre perfume fresco y citrico deberia acercarse a comentarios con limon, bergamota, naranja, limpieza o uso de dia.

Cada familia incluye metadata pensada para busqueda y analisis:

- `familia_olfativa`: familia principal, por ejemplo `floral`, `citrico`, `oriental`.
- `subfamilia`: detalle dentro de la familia, por ejemplo `floral suave`, `maderas secas`.
- `notas`: materias primas o acordes, por ejemplo `bergamota`, `vainilla`, `cedro`.
- `etiquetas`: sensaciones y posicionamiento, por ejemplo `sensual`, `alegre`, `masculino`.

## Aprendizajes

- Una base vectorial permite buscar por similitud semantica, no solo por coincidencia exacta de palabras.
- ChromaDB permite guardar documentos, metadata y vectores en una coleccion consultable.
- Insertar nuevos documentos puede cambiar el ranking de resultados para la misma query.
- La calidad de la busqueda depende directamente de la calidad del embedding.
- Separar datos, embeddings, vector store y CLI en modulos vuelve el proyecto mas mantenible y testeable.

## Limitaciones

- El embedding actual es didactico y esta basado en palabras clave por familia olfativa.
- Si la consulta usa sinonimos que no estan en el vocabulario, el ranking puede perder precision.
- Los datos son ficticios y estan pensados para aprendizaje, no para recomendacion comercial real.
- Todavia no usa embeddings reales de modelos especializados.
- La interfaz web es local y usa el servidor HTTP incluido en Python; no esta preparada todavia como aplicacion desplegable.

## Como explicarlo en el CV

Proyecto de busqueda semantica con ChromaDB aplicado a comentarios de perfumeria. Modele textos como vectores usando una taxonomia inspirada en la rueda de fragancias, cree una coleccion vectorial y ejecute consultas por similitud comparando resultados antes y despues de insertar nuevos documentos.

## Proximas mejoras

- Reemplazar el embedding didactico por embeddings reales de un modelo.
- Agregar mas comentarios, subfamilias y notas olfativas.
- Crear una API con FastAPI.
- Separar el frontend en archivos estaticos cuando el proyecto crezca.
- Agregar filtros por ocasion, familia olfativa, intensidad y presupuesto.
- Guardar resultados en CSV para analizarlos.
