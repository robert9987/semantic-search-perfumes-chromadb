from __future__ import annotations

import json
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import chromadb

from src.config import (
    COLLECTION_NAME,
    DEFAULT_QUERY,
    DOCUMENTOS_INICIALES_PATH,
    DOCUMENTOS_NUEVOS_PATH,
)
from src.data_loader import cargar_documentos
from src.embeddings import EmbeddingsPerfumeria
from src.vector_store import buscar_resultados, insertar_documentos


HOST = "127.0.0.1"
PORT = 8000


def crear_coleccion_web(include_new: bool):
    db_path = Path(tempfile.mkdtemp(prefix="perfume_web_chroma_db_"))
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


def buscar_familias(query: str, top_k: int, include_new: bool) -> list[dict]:
    collection = crear_coleccion_web(include_new)
    return buscar_resultados(collection, query, top_k)


class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/":
            self._send_html(INDEX_HTML)
            return

        if parsed_url.path == "/api/search":
            params = parse_qs(parsed_url.query)
            query = params.get("query", [DEFAULT_QUERY])[0].strip() or DEFAULT_QUERY
            include_new = params.get("include_new", ["1"])[0] == "1"
            top_k = parse_top_k(params.get("top_k", ["5"])[0])
            results = buscar_familias(query, top_k, include_new)
            self._send_json(
                {
                    "query": query,
                    "include_new": include_new,
                    "top_k": top_k,
                    "results": results,
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


def parse_top_k(value: str) -> int:
    try:
        return max(1, min(10, int(value)))
    except ValueError:
        return 5


INDEX_HTML = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Busqueda semantica de familias olfativas</title>
  <style>
    :root {
      --bg: #f6f3ec;
      --panel: #ffffff;
      --ink: #1f211f;
      --muted: #686d66;
      --line: #ddd7cb;
      --green: #2f6f5e;
      --green-dark: #214e43;
      --rose: #c84f78;
      --orange: #dd7d31;
      --leaf: #7e9f43;
      --yellow: #e5bd37;
      --blue: #4f91aa;
      --wood: #937142;
      --amber: #b46f2a;
      --violet: #70649c;
      --shadow: 0 14px 34px rgba(43, 37, 28, 0.12);
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

    .layout {
      min-height: 100vh;
      display: grid;
      grid-template-columns: 292px minmax(0, 1fr);
    }

    .sidebar {
      background: #fbfaf7;
      border-right: 1px solid var(--line);
      padding: 24px;
      display: grid;
      grid-template-rows: auto auto minmax(0, 1fr) auto;
      gap: 22px;
    }

    .brand h1 {
      margin: 0;
      color: var(--green-dark);
      font-size: 23px;
      line-height: 1.08;
    }

    .brand p {
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.35;
    }

    .wheel {
      width: 188px;
      height: 188px;
      border-radius: 50%;
      margin: 0 auto;
      background:
        conic-gradient(
          var(--rose) 0deg 45deg,
          var(--orange) 45deg 90deg,
          var(--leaf) 90deg 135deg,
          var(--yellow) 135deg 180deg,
          var(--blue) 180deg 225deg,
          var(--wood) 225deg 270deg,
          var(--amber) 270deg 315deg,
          var(--violet) 315deg 360deg
        );
      display: grid;
      place-items: center;
      box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.08), var(--shadow);
    }

    .wheel span {
      width: 104px;
      height: 104px;
      border-radius: 50%;
      display: grid;
      place-items: center;
      background: #fbfaf7;
      color: var(--green-dark);
      font-weight: 700;
      text-align: center;
      line-height: 1.15;
      padding: 14px;
    }

    .family-list {
      display: grid;
      gap: 8px;
      align-content: start;
    }

    .family-list h2,
    .settings h2 {
      margin: 0 0 4px;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
    }

    .family-button {
      min-height: 38px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 8px 10px;
      background: var(--panel);
      color: var(--ink);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }

    .family-button:hover,
    .family-button:focus-visible {
      border-color: var(--green);
      outline: 3px solid rgba(47, 111, 94, 0.12);
    }

    .dot {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      flex: 0 0 auto;
      background: var(--dot);
    }

    .settings {
      display: grid;
      gap: 12px;
    }

    .field-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      color: var(--muted);
      font-size: 14px;
    }

    .field-row input[type="checkbox"] {
      width: 18px;
      height: 18px;
      accent-color: var(--green);
    }

    .field-row input[type="number"] {
      width: 74px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 8px;
      background: var(--panel);
      color: var(--ink);
    }

    main {
      padding: 28px;
      display: grid;
      grid-template-rows: auto auto minmax(0, 1fr);
      gap: 20px;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      border-bottom: 1px solid var(--line);
      padding-bottom: 16px;
    }

    .topbar h2 {
      margin: 0;
      color: var(--ink);
      font-size: 28px;
      line-height: 1.12;
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
    }

    .search input {
      width: 100%;
      min-height: 50px;
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
      min-height: 50px;
      border: 0;
      border-radius: 8px;
      padding: 0 18px;
      background: var(--green);
      color: #ffffff;
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

    .result {
      min-height: 264px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 16px;
      display: grid;
      grid-template-rows: auto auto auto auto 1fr auto;
      gap: 10px;
      box-shadow: var(--shadow);
    }

    .score {
      height: 8px;
      border-radius: 999px;
      overflow: hidden;
      background: #ebe7dd;
    }

    .score span {
      display: block;
      width: var(--score);
      height: 100%;
      background: var(--green);
    }

    .result h3 {
      margin: 0;
      color: var(--green-dark);
      font-size: 20px;
      line-height: 1.15;
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
      background: #fbfaf7;
      font-size: 12px;
    }

    .notes,
    .comment {
      margin: 0;
      font-size: 14px;
      line-height: 1.45;
    }

    .comment {
      color: var(--muted);
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
      background: rgba(255, 255, 255, 0.68);
    }

    @media (max-width: 1080px) {
      .layout {
        grid-template-columns: 1fr;
      }

      .sidebar {
        border-right: 0;
        border-bottom: 1px solid var(--line);
        grid-template-columns: 1fr;
      }

      .wheel {
        display: none;
      }

      .family-list {
        grid-template-columns: repeat(4, minmax(0, 1fr));
      }

      .settings {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      .results {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }

    @media (max-width: 720px) {
      .sidebar,
      main {
        padding: 18px;
      }

      .topbar,
      .search {
        display: grid;
        grid-template-columns: 1fr;
      }

      .topbar h2 {
        font-size: 24px;
      }

      .family-list,
      .settings,
      .results {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="layout">
    <aside class="sidebar">
      <section class="brand">
        <h1>Familias olfativas</h1>
        <p>Busqueda semantica con ChromaDB</p>
      </section>

      <div class="wheel" aria-hidden="true"><span>Rueda de fragancias</span></div>

      <section class="family-list" aria-label="Familias olfativas">
        <h2>Familias</h2>
        <button class="family-button" data-query="Busco una fragancia floral suave romantica con rosa jazmin y flores blancas"><span>Floral</span><span class="dot" style="--dot:var(--rose)"></span></button>
        <button class="family-button" data-query="Quiero una fragancia frutal alegre vibrante con durazno frutilla melon y frutos rojos"><span>Frutal</span><span class="dot" style="--dot:var(--orange)"></span></button>
        <button class="family-button" data-query="Busco una fragancia fougere verde con lavanda musgo bergamota y bosque humedo"><span>Fougere</span><span class="dot" style="--dot:var(--leaf)"></span></button>
        <button class="family-button" data-query="Busco un perfume citrico fresco con bergamota limon y naranja"><span>Citrica</span><span class="dot" style="--dot:var(--yellow)"></span></button>
        <button class="family-button" data-query="Quiero una fragancia aromatica intensa con salvia romero comino lavanda hierbas y especias"><span>Aromatica</span><span class="dot" style="--dot:var(--blue)"></span></button>
        <button class="family-button" data-query="Busco maderas cedro vetiver pachuli seco elegante masculino"><span>Maderas</span><span class="dot" style="--dot:var(--wood)"></span></button>
        <button class="family-button" data-query="Quiero una fragancia oriental sensual calida con ambar y vainilla para la noche"><span>Oriental</span><span class="dot" style="--dot:var(--amber)"></span></button>
        <button class="family-button" data-query="Quiero un chipre fresco juvenil con bergamota pachuli musgo ambar"><span>Chipre</span><span class="dot" style="--dot:var(--violet)"></span></button>
      </section>

      <section class="settings" aria-label="Ajustes">
        <h2>Ajustes</h2>
        <label class="field-row">
          <span>Incluir nuevos</span>
          <input id="includeNew" type="checkbox" checked>
        </label>
        <label class="field-row">
          <span>Resultados</span>
          <input id="topK" type="number" min="1" max="10" value="5">
        </label>
      </section>
    </aside>

    <main>
      <header class="topbar">
        <h2>Recomendador semantico</h2>
        <span id="status" class="status">Listo</span>
      </header>

      <form id="searchForm" class="search">
        <input id="queryInput" type="search" autocomplete="off" value="Busco un perfume citrico fresco con bergamota limon y naranja" aria-label="Consulta">
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

    function renderResult(item) {
      const score = Math.round(item.similitud * 100);
      return `
        <article class="result">
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
          ? payload.results.map(renderResult).join("")
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
    server = ThreadingHTTPServer((HOST, PORT), WebHandler)
    print(f"Frontend disponible en http://{HOST}:{PORT}")
    print("Presiona Ctrl+C para detener el servidor.")
    server.serve_forever()


if __name__ == "__main__":
    main()
