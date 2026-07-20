from __future__ import annotations

import json
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import chromadb

from ejercicio_0_chromadb import (
    COLLECTION_NAME,
    DEFAULT_QUERY,
    DOCUMENTOS_INICIALES_PATH,
    DOCUMENTOS_NUEVOS_PATH,
    EmbeddingsPerfumeria,
    buscar_resultados,
    cargar_documentos,
    insertar_documentos,
)


HOST = "127.0.0.1"
PORT = 8000
TOP_K_DEFAULT = 5


def crear_coleccion_web(include_new: bool):
    db_path = Path(tempfile.mkdtemp(prefix="tokipick_chroma_db_"))
    client = chromadb.PersistentClient(path=str(db_path))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=EmbeddingsPerfumeria(),
        metadata={"hnsw:space": "cosine"},
    )

    insertar_documentos(collection, cargar_documentos(DOCUMENTOS_INICIALES_PATH))
    if include_new:
        insertar_documentos(collection, cargar_documentos(DOCUMENTOS_NUEVOS_PATH))

    return collection


def buscar_perfumes(query: str, top_k: int, include_new: bool) -> list[dict]:
    collection = crear_coleccion_web(include_new)
    return buscar_resultados(collection, query, top_k)


class TokipickHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/":
            self._send_html(INDEX_HTML)
            return

        if parsed_url.path == "/api/search":
            params = parse_qs(parsed_url.query)
            query = params.get("query", [DEFAULT_QUERY])[0].strip() or DEFAULT_QUERY
            include_new = params.get("include_new", ["1"])[0] == "1"
            top_k = _parse_top_k(params.get("top_k", [str(TOP_K_DEFAULT)])[0])
            resultados = buscar_perfumes(query, top_k, include_new)
            self._send_json(
                {
                    "query": query,
                    "include_new": include_new,
                    "top_k": top_k,
                    "results": resultados,
                }
            )
            return

        self.send_error(404, "Ruta no encontrada")

    def log_message(self, format: str, *args) -> None:
        return

    def _send_html(self, html: str) -> None:
        encoded = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_json(self, payload: dict) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def _parse_top_k(value: str) -> int:
    try:
        return max(1, min(10, int(value)))
    except ValueError:
        return TOP_K_DEFAULT


INDEX_HTML = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tokipick II | Busqueda semantica de perfumes</title>
  <style>
    :root {
      --bg: #f7f5f0;
      --panel: #ffffff;
      --ink: #22201c;
      --muted: #6f6a61;
      --line: #ded8cc;
      --green: #2f6f5e;
      --green-dark: #214e43;
      --rose: #b64b73;
      --amber: #c9822b;
      --blue: #447b9d;
      --violet: #6d5a94;
      --shadow: 0 16px 40px rgba(46, 39, 28, 0.12);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: "Segoe UI", Arial, sans-serif;
      letter-spacing: 0;
    }

    button,
    input {
      font: inherit;
    }

    .app {
      min-height: 100vh;
      display: grid;
      grid-template-columns: 280px minmax(0, 1fr);
    }

    .sidebar {
      border-right: 1px solid var(--line);
      background: #fbfaf7;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    .brand {
      display: grid;
      gap: 4px;
    }

    .brand h1 {
      margin: 0;
      font-size: 24px;
      line-height: 1.05;
      color: var(--green-dark);
    }

    .brand p {
      margin: 0;
      color: var(--muted);
      font-size: 13px;
    }

    .wheel {
      width: 184px;
      height: 184px;
      border-radius: 50%;
      margin: 4px auto 0;
      background:
        conic-gradient(
          #d84f7b 0 45deg,
          #e97937 45deg 90deg,
          #85a843 90deg 135deg,
          #f0c63a 135deg 180deg,
          #57a0bd 180deg 225deg,
          #8171a8 225deg 270deg,
          #9b7a44 270deg 315deg,
          #b9792e 315deg 360deg
        );
      display: grid;
      place-items: center;
      box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.08);
    }

    .wheel::after {
      content: "Rueda olfativa";
      width: 104px;
      height: 104px;
      border-radius: 50%;
      background: #fbfaf7;
      display: grid;
      place-items: center;
      text-align: center;
      padding: 14px;
      color: var(--green-dark);
      font-weight: 700;
      font-size: 14px;
      line-height: 1.15;
      box-shadow: 0 0 0 1px var(--line);
    }

    .families {
      display: grid;
      gap: 8px;
    }

    .families h2,
    .settings h2 {
      margin: 0 0 4px;
      font-size: 13px;
      text-transform: uppercase;
      color: var(--muted);
    }

    .family-button {
      width: 100%;
      min-height: 36px;
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--ink);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 10px;
      cursor: pointer;
    }

    .family-button:hover,
    .family-button:focus-visible {
      border-color: var(--green);
      outline: none;
    }

    .swatch {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: var(--swatch);
    }

    .settings {
      display: grid;
      gap: 12px;
      margin-top: auto;
    }

    .toggle-row,
    .topk-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      color: var(--muted);
      font-size: 14px;
    }

    .toggle-row input {
      width: 18px;
      height: 18px;
      accent-color: var(--green);
    }

    .topk-row input {
      width: 72px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 8px;
      background: var(--panel);
      color: var(--ink);
    }

    .main {
      padding: 28px;
      display: grid;
      grid-template-rows: auto auto minmax(0, 1fr);
      gap: 20px;
    }

    .toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      border-bottom: 1px solid var(--line);
      padding-bottom: 18px;
    }

    .toolbar h2 {
      margin: 0;
      font-size: 28px;
      line-height: 1.1;
      color: var(--ink);
    }

    .status {
      color: var(--muted);
      font-size: 14px;
      white-space: nowrap;
    }

    .search {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 12px;
      align-items: center;
    }

    .search input {
      width: 100%;
      min-height: 48px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px 14px;
      background: var(--panel);
      color: var(--ink);
      box-shadow: var(--shadow);
    }

    .search input:focus {
      border-color: var(--green);
      outline: 3px solid rgba(47, 111, 94, 0.16);
    }

    .search button {
      min-height: 48px;
      border: 0;
      border-radius: 8px;
      padding: 0 18px;
      color: #ffffff;
      background: var(--green);
      cursor: pointer;
      font-weight: 700;
    }

    .search button:hover,
    .search button:focus-visible {
      background: var(--green-dark);
      outline: none;
    }

    .results {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
      align-content: start;
    }

    .result-card {
      min-height: 260px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 16px;
      display: grid;
      grid-template-rows: auto auto auto 1fr auto;
      gap: 10px;
      box-shadow: var(--shadow);
    }

    .score {
      height: 8px;
      border-radius: 999px;
      background: #ebe6dc;
      overflow: hidden;
    }

    .score span {
      display: block;
      height: 100%;
      width: var(--score);
      background: var(--green);
    }

    .result-card h3 {
      margin: 0;
      font-size: 20px;
      line-height: 1.15;
      color: var(--green-dark);
    }

    .meta {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

    .pill {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 5px 8px;
      color: var(--muted);
      font-size: 12px;
      background: #fbfaf7;
    }

    .notes {
      margin: 0;
      color: var(--ink);
      font-size: 14px;
      line-height: 1.45;
    }

    .comment {
      margin: 0;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.45;
    }

    .match {
      color: var(--green-dark);
      font-weight: 700;
      font-size: 13px;
    }

    .empty {
      border: 1px dashed var(--line);
      border-radius: 8px;
      padding: 24px;
      color: var(--muted);
      background: rgba(255, 255, 255, 0.6);
    }

    @media (max-width: 1040px) {
      .app {
        grid-template-columns: 1fr;
      }

      .sidebar {
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }

      .wheel {
        display: none;
      }

      .families {
        grid-template-columns: repeat(4, minmax(0, 1fr));
      }

      .settings {
        margin-top: 0;
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      .results {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }

    @media (max-width: 680px) {
      .sidebar,
      .main {
        padding: 18px;
      }

      .toolbar,
      .search {
        grid-template-columns: 1fr;
        display: grid;
      }

      .toolbar h2 {
        font-size: 24px;
      }

      .families,
      .settings,
      .results {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside class="sidebar">
      <section class="brand">
        <h1>Tokipick II</h1>
        <p>Semantic perfume search</p>
      </section>

      <div class="wheel" aria-hidden="true"></div>

      <section class="families" aria-label="Familias olfativas">
        <h2>Familias</h2>
        <button class="family-button" data-query="Busco un perfume floral suave romantico con rosa jazmin y flores blancas"><span>Floral</span><span class="swatch" style="--swatch:#d84f7b"></span></button>
        <button class="family-button" data-query="Quiero una fragancia frutal alegre vibrante con durazno frutilla melon y frutos rojos"><span>Frutal</span><span class="swatch" style="--swatch:#e97937"></span></button>
        <button class="family-button" data-query="Busco una fragancia fougere verde con lavanda musgo bergamota y bosque humedo"><span>Fougere</span><span class="swatch" style="--swatch:#85a843"></span></button>
        <button class="family-button" data-query="Busco un perfume citrico fresco con bergamota limon naranja limpio para usar de dia"><span>Citrico</span><span class="swatch" style="--swatch:#f0c63a"></span></button>
        <button class="family-button" data-query="Quiero una fragancia aromatica intensa con salvia romero comino lavanda hierbas y especias"><span>Aromatico</span><span class="swatch" style="--swatch:#57a0bd"></span></button>
        <button class="family-button" data-query="Busco un perfume de maderas con cedro vetiver pachuli seco elegante y masculino"><span>Maderas</span><span class="swatch" style="--swatch:#9b7a44"></span></button>
        <button class="family-button" data-query="Quiero una fragancia oriental sensual calida con ambar y vainilla para la noche"><span>Oriental</span><span class="swatch" style="--swatch:#b9792e"></span></button>
        <button class="family-button" data-query="Quiero un chipre fresco juvenil con bergamota flores pachuli musgo ambar y almizcle"><span>Chipre</span><span class="swatch" style="--swatch:#8171a8"></span></button>
      </section>

      <section class="settings" aria-label="Ajustes">
        <h2>Busqueda</h2>
        <label class="toggle-row">
          <span>Incluir nuevos</span>
          <input id="includeNew" type="checkbox" checked>
        </label>
        <label class="topk-row">
          <span>Resultados</span>
          <input id="topK" type="number" min="1" max="10" value="5">
        </label>
      </section>
    </aside>

    <main class="main">
      <header class="toolbar">
        <h2>Recomendador de fragancias</h2>
        <span id="status" class="status">Listo</span>
      </header>

      <form id="searchForm" class="search">
        <input id="queryInput" type="search" autocomplete="off" value="Busco un perfume fresco citrico limpio y alegre para usar de dia" aria-label="Consulta">
        <button type="submit">Buscar</button>
      </form>

      <section id="results" class="results" aria-live="polite"></section>
    </main>
  </div>

  <script>
    const form = document.querySelector("#searchForm");
    const queryInput = document.querySelector("#queryInput");
    const includeNew = document.querySelector("#includeNew");
    const topK = document.querySelector("#topK");
    const results = document.querySelector("#results");
    const statusText = document.querySelector("#status");

    const escapeHtml = (value) => String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

    function resultTemplate(item) {
      const score = Math.round(item.similitud * 100);
      return `
        <article class="result-card">
          <div class="score" aria-label="Similitud ${score}%"><span style="--score:${score}%"></span></div>
          <h3>${escapeHtml(item.producto)}</h3>
          <div class="meta">
            <span class="pill">${escapeHtml(item.familia_olfativa)}</span>
            <span class="pill">${escapeHtml(item.subfamilia)}</span>
          </div>
          <p class="notes"><strong>Notas:</strong> ${escapeHtml(item.notas)}</p>
          <p class="comment">${escapeHtml(item.comentario)}</p>
          <span class="match">${score}% match</span>
        </article>
      `;
    }

    async function search() {
      const params = new URLSearchParams({
        query: queryInput.value,
        include_new: includeNew.checked ? "1" : "0",
        top_k: topK.value
      });

      statusText.textContent = "Buscando";
      results.innerHTML = "";

      try {
        const response = await fetch(`/api/search?${params.toString()}`);
        const payload = await response.json();
        statusText.textContent = `${payload.results.length} resultados`;
        results.innerHTML = payload.results.length
          ? payload.results.map(resultTemplate).join("")
          : `<div class="empty">Sin resultados</div>`;
      } catch (error) {
        statusText.textContent = "Error";
        results.innerHTML = `<div class="empty">No se pudo completar la busqueda</div>`;
      }
    }

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      search();
    });

    includeNew.addEventListener("change", search);
    topK.addEventListener("change", search);

    document.querySelectorAll(".family-button").forEach((button) => {
      button.addEventListener("click", () => {
        queryInput.value = button.dataset.query;
        search();
      });
    });

    search();
  </script>
</body>
</html>
"""


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), TokipickHandler)
    print(f"Tokipick II disponible en http://{HOST}:{PORT}")
    print("Presiona Ctrl+C para detener el servidor.")
    server.serve_forever()


if __name__ == "__main__":
    main()
