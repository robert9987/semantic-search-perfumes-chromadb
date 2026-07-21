from __future__ import annotations

import math
import unicodedata
from typing import Iterable


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

    def is_legacy(self) -> bool:
        return True

    def __call__(self, input: Iterable[str]) -> list[list[float]]:
        return [self._vectorizar(texto) for texto in input]

    def embed_query(self, input: Iterable[str]) -> list[list[float]]:
        return self.__call__(input)

    def _vectorizar(self, texto: str) -> list[float]:
        tokens = set(tokenizar(texto))

        vector = []
        for _, palabras_clave in self.dimensiones:
            coincidencias = len(tokens & palabras_clave)
            vector.append(float(coincidencias))

        norma = math.sqrt(sum(valor * valor for valor in vector))
        if norma == 0:
            return vector

        return [valor / norma for valor in vector]


def tokenizar(texto: str) -> list[str]:
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
