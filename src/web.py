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
  <title>Mista | Familias olfativas</title>
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
    input,
    select {
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

    .family-controls {
      display: grid;
      gap: 12px;
      align-content: start;
    }

    .family-controls h2,
    .settings h2 {
      margin: 0 0 4px;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
    }

    .select-row {
      display: grid;
      gap: 6px;
      color: var(--muted);
      font-size: 13px;
    }

    .select-row select {
      width: 100%;
      min-height: 42px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 9px 10px;
      background: var(--panel);
      color: var(--ink);
      cursor: pointer;
    }

    .select-row select:focus {
      border-color: var(--green);
      outline: 3px solid rgba(47, 111, 94, 0.12);
    }

    .palette {
      display: grid;
      grid-template-columns: repeat(8, 1fr);
      gap: 5px;
    }

    .palette span {
      height: 8px;
      border-radius: 999px;
      background: var(--color);
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

      .family-controls {
        grid-template-columns: repeat(2, minmax(0, 1fr));
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

      .family-controls,
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
        <h1>Mista</h1>
      </section>

      <div class="wheel" aria-hidden="true"><span>Rueda de fragancias</span></div>

      <section class="family-controls" aria-label="Familias olfativas">
        <h2>Familias</h2>
        <label class="select-row">
          <span>Familia olfativa</span>
          <select id="familySelect">
            <option value="floral">Floral</option>
            <option value="frutal">Frutal</option>
            <option value="fougere">Fougere</option>
            <option value="citrico" selected>Citrico</option>
            <option value="aromatico">Aromatico</option>
            <option value="maderas">Maderas</option>
            <option value="oriental">Oriental</option>
            <option value="chipre">Chipre</option>
            <option value="acuatica">Acuatica</option>
          </select>
        </label>
        <label class="select-row">
          <span>Perfil / subfamilia</span>
          <select id="profileSelect"></select>
        </label>
        <div class="palette" aria-hidden="true">
          <span style="--color:var(--rose)"></span>
          <span style="--color:var(--orange)"></span>
          <span style="--color:var(--leaf)"></span>
          <span style="--color:var(--yellow)"></span>
          <span style="--color:var(--blue)"></span>
          <span style="--color:var(--wood)"></span>
          <span style="--color:var(--amber)"></span>
          <span style="--color:var(--violet)"></span>
        </div>
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
        <h2>Familias olfativas</h2>
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
    const familySelect = document.querySelector("#familySelect");
    const profileSelect = document.querySelector("#profileSelect");
    const includeNew = document.querySelector("#includeNew");
    const topK = document.querySelector("#topK");
    const results = document.querySelector("#results");
    const statusText = document.querySelector("#status");

    const familyProfiles = {
      floral: [
        {
          label: "Floral delicada",
          query: "Busco una fragancia floral delicada romantica con flores blancas rosa y jazmin"
        },
        {
          label: "Floral suave",
          query: "Quiero un perfume floral suave femenino con primavera flores frescas y aroma limpio"
        },
        {
          label: "Floral oriental",
          query: "Busco una fragancia floral oriental sensual con flores vainilla especias dulces y ambar"
        }
      ],
      frutal: [
        {
          label: "Frutal alegre",
          query: "Quiero una fragancia frutal alegre vibrante con durazno frutilla melon y frutos rojos"
        },
        {
          label: "Frutal jugosa",
          query: "Busco perfume frutal jugoso con anana sandia ciruela y personalidad jovial"
        }
      ],
      fougere: [
        {
          label: "Fougere verde",
          query: "Busco una fragancia fougere verde con lavanda musgo bergamota y bosque humedo"
        },
        {
          label: "Fougere tradicional",
          query: "Quiero un perfume fougere masculino con lavanda maderas humedas musgo y elegancia clasica"
        }
      ],
      citrico: [
        {
          label: "Citrico fresco",
          query: "Busco un perfume citrico fresco con bergamota limon naranja y sensacion limpia"
        },
        {
          label: "Citrico unisex",
          query: "Quiero una fragancia citrica unisex alegre para el dia con notas volatiles y flores suaves"
        }
      ],
      aromatico: [
        {
          label: "Aromatico herbal",
          query: "Quiero una fragancia aromatica intensa con salvia romero comino lavanda hierbas y especias"
        },
        {
          label: "Aromatico especiado",
          query: "Busco perfume aromatico masculino con hierbas especias notas citricas y caracter intenso"
        }
      ],
      maderas: [
        {
          label: "Maderas secas",
          query: "Busco maderas secas con cedro vetiver pachuli caracter elegante y masculino"
        },
        {
          label: "Maderas musgosas",
          query: "Quiero una fragancia de maderas musgosas con musgo vetiver pachuli y bosque humedo"
        },
        {
          label: "Maderas ambaradas",
          query: "Busco perfume de madera calida con cedro sandalo ambar y fondo intenso"
        }
      ],
      oriental: [
        {
          label: "Oriental ambarado",
          query: "Quiero una fragancia oriental sensual calida con ambar vainilla y resinas para la noche"
        },
        {
          label: "Oriental especiado",
          query: "Busco perfume oriental especiado con clavo cardamomo jengibre pimienta cacao y regaliz"
        },
        {
          label: "Oriental suave",
          query: "Quiero una fragancia oriental suave dulce con vainilla ambar calidez y aroma envolvente"
        }
      ],
      chipre: [
        {
          label: "Chipre fresco",
          query: "Quiero un chipre fresco juvenil con bergamota pachuli musgo ambar y almizcle"
        },
        {
          label: "Chipre floral",
          query: "Busco fragancia chipre con bergamota flores patchuli musgo y elegancia moderna"
        }
      ],
      acuatica: [
        {
          label: "Acuatica fresca",
          query: "Busco una fragancia acuatica fresca marina limpia ligera y alegre para dias calidos"
        },
        {
          label: "Verde acuatica",
          query: "Quiero perfume fresco verde con notas acuaticas bosque humedo lavanda y musgo"
        }
      ]
    };

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

    function populateProfileSelect(shouldSearch = true) {
      const profiles = familyProfiles[familySelect.value] || [];
      profileSelect.innerHTML = profiles
        .map((profile, index) => `<option value="${index}">${escapeHtml(profile.label)}</option>`)
        .join("");

      if (profiles[0]) {
        queryInput.value = profiles[0].query;
      }

      if (shouldSearch) {
        search();
      }
    }

    function applySelectedProfile() {
      const profiles = familyProfiles[familySelect.value] || [];
      const profile = profiles[Number(profileSelect.value)] || profiles[0];

      if (profile) {
        queryInput.value = profile.query;
        search();
      }
    }

    familySelect.addEventListener("change", () => populateProfileSelect());
    profileSelect.addEventListener("change", applySelectedProfile);

    populateProfileSelect(false);
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
