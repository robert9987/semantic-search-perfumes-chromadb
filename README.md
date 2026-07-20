# Busqueda semantica para perfumeria con ChromaDB

Proyecto practico de base de datos vectorial aplicado a comentarios ficticios de perfumes. La idea es simular un buscador semantico: el usuario escribe una necesidad en lenguaje natural y el sistema devuelve los comentarios/productos mas parecidos por significado.

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
- VS Code como entorno de trabajo recomendado

## Estructura

```text
.
├── data/
│   ├── perfumes_iniciales.json
│   └── perfumes_nuevos.json
├── ejercicio_0_chromadb.py
├── requirements.txt
└── README.md
```

## Preparacion en VS Code

Abri esta carpeta en Visual Studio Code:

```powershell
code "D:\OneDrive\Office importante\LLms - Profesor"
```

Si `code` no esta habilitado, abri VS Code manualmente y elegi:

```text
File > Open Folder
```

Luego selecciona:

```text
D:\OneDrive\Office importante\LLms - Profesor
```

## Crear entorno virtual

En la terminal integrada de VS Code:

```powershell
& "C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m venv .venv
```

Instala dependencias:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
```

## Ejecutar demo

```powershell
.\.venv\Scripts\python.exe .\ejercicio_0_chromadb.py
```

Si VS Code muestra `ModuleNotFoundError: No module named 'chromadb'`, significa que esta usando otro Python. Selecciona el interprete `.venv\Scripts\python.exe` desde `Python: Select Interpreter`, o ejecuta el script con el comando anterior desde la terminal integrada.

Ejemplo con una consulta propia:

```powershell
.\.venv\Scripts\python.exe .\ejercicio_0_chromadb.py --query "Quiero un perfume dulce con vainilla para la noche"
```

Otro ejemplo:

```powershell
.\.venv\Scripts\python.exe .\ejercicio_0_chromadb.py --query "Busco una fragancia elegante intensa y amaderada"
```

## Ejecutar interfaz web TOKIPICK II

El proyecto ahora incluye una interfaz web local sin dependencias extra de frontend. Usa el mismo motor de busqueda semantica y permite comparar resultados incluyendo o no los comentarios nuevos.

```powershell
.\.venv\Scripts\python.exe .\tokipick_web.py
```

Luego abri:

```text
http://127.0.0.1:8000
```

## Que observar

La misma query se ejecuta dos veces:

- Primero contra los comentarios iniciales.
- Despues de insertar nuevos comentarios.

Si el nuevo comentario esta cerca de la query, sube en el ranking. Por ejemplo, una consulta sobre perfume fresco y citrico deberia acercarse a comentarios con limon, bergamota, naranja, limpieza o uso de dia.

Cada perfume incluye metadata pensada para busqueda y analisis:

- `familia_olfativa`: familia principal, por ejemplo `floral`, `citrico`, `oriental`.
- `subfamilia`: detalle dentro de la familia, por ejemplo `floral suave`, `maderas secas`.
- `notas`: materias primas o acordes, por ejemplo `bergamota`, `vainilla`, `cedro`.
- `etiquetas`: sensaciones y posicionamiento, por ejemplo `sensual`, `alegre`, `masculino`.

## Como explicarlo en el CV

Proyecto de busqueda semantica con ChromaDB aplicado a comentarios de perfumeria. Modele textos como vectores usando una taxonomia inspirada en la rueda de fragancias, cree una coleccion vectorial, ejecute consultas por similitud y compare resultados antes y despues de insertar nuevos documentos.

## Proximas mejoras

- Reemplazar el embedding didactico por embeddings reales de un modelo.
- Agregar mas comentarios, subfamilias y notas olfativas.
- Crear una API con FastAPI.
- Separar la interfaz web en archivos estaticos cuando el proyecto crezca.
- Agregar filtros por ocasion, familia olfativa, intensidad y presupuesto.
- Guardar resultados en CSV para analizarlos.
