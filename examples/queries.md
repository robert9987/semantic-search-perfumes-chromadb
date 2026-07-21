# Ejemplos de consultas

Estos ejemplos sirven para probar la busqueda semantica desde la terminal.

Formato general:

```powershell
.\.venv\Scripts\python.exe -m src.main --query "TU CONSULTA"
```

## Familia Citrica

Query:

```text
Busco un perfume citrico fresco con bergamota limon y naranja
```

Comando:

```powershell
.\.venv\Scripts\python.exe -m src.main --query "Busco un perfume citrico fresco con bergamota limon y naranja"
```

Resultado esperado:

```text
Familia Citrica
```

## Familia Oriental

Query:

```text
Quiero una fragancia oriental sensual calida con ambar y vainilla para la noche
```

Comando:

```powershell
.\.venv\Scripts\python.exe -m src.main --query "Quiero una fragancia oriental sensual calida con ambar y vainilla para la noche"
```

Resultado esperado despues de insertar nuevos documentos:

```text
Familia Oriental
```

## Familia Maderas

Query:

```text
Busco maderas cedro vetiver pachuli seco elegante masculino
```

Comando:

```powershell
.\.venv\Scripts\python.exe -m src.main --query "Busco maderas cedro vetiver pachuli seco elegante masculino"
```

Resultado esperado:

```text
Familia Maderas
```

## Familia Chipre

Query:

```text
Quiero un chipre fresco juvenil con bergamota pachuli musgo ambar
```

Comando:

```powershell
.\.venv\Scripts\python.exe -m src.main --query "Quiero un chipre fresco juvenil con bergamota pachuli musgo ambar"
```

Resultado esperado despues de insertar nuevos documentos:

```text
Familia Chipre
```

## Familia Acuatica

Query:

```text
Busco una fragancia acuatica limpia liviana con notas marinas para diario
```

Comando:

```powershell
.\.venv\Scripts\python.exe -m src.main --query "Busco una fragancia acuatica limpia liviana con notas marinas para diario"
```

Resultado esperado despues de insertar nuevos documentos:

```text
Familia Acuatica
```

## Como interpretar los resultados

El script muestra dos busquedas con la misma query:

1. Primero busca solo en `perfumes_iniciales.json`.
2. Despues inserta `perfumes_nuevos.json` y repite la busqueda.

Si una familia aparece solo despues del segundo paso, significa que esa familia estaba en los documentos nuevos y que ChromaDB pudo incorporarla al ranking.
