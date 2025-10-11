// GraphsPage.js — Unificado CLARO/OSCURO según preferencia (localStorage/cookie)
// Detecta el tema desde localStorage('vite-ui-theme') o cookie y renderiza
// una sola página que aplica estilos, íconos y Plotly layout por tema.

console.log("📊 GraphsPage unificado — inicia");

// ======== Estado global ========
let graphSizes = {}; // { [graphId]: 1|2|3 }
let originalGraphsData = []; // respuesta de /api/pinned-graphs
let graphPositions = []; // orden actual de los gráficos
const selectedGraphs = new Set(); // gráficos elegidos para el PPT

// ======== Tema ========
function readTheme() {
    // 1) localStorage (preferente)
    try {
        const v = localStorage.getItem("vite-ui-theme");
        if (v === "dark" || v === "light") return v;
    } catch {}
    // 2) cookie (fallback) => vite-ui-theme=dark|light
    try {
        const m = document.cookie.match(/(?:^|; )vite-ui-theme=([^;]*)/);
        if (m) {
            const v = decodeURIComponent(m[1]);
            if (v === "dark" || v === "light") return v;
        }
    } catch {}
    // 3) media query (último recurso)
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

let THEME = readTheme();
console.log("🎨 Tema detectado:", THEME);

// Re-Render si el tema cambia (p. ej. otra pestaña cambia localStorage)
window.addEventListener("storage", (e) => {
    if (e.key === "vite-ui-theme") {
        const newTheme = readTheme();
        if (newTheme !== THEME) {
            THEME = newTheme;
            console.log("🎨 Tema cambió → re-render:", THEME);
            // Re-render completo para que cambien íconos/estilos/plotly
            renderGraphsUnified();
        }
    }
});

// ======== Utilidades de íconos por tema ========
// En el repo existen variantes para LIGHT con sufijos "-light" (y algunos "-ligth").
// Para mantener compatibilidad, hacemos un mapeo por icono lógico.
function asset(icon) {
    const light = THEME === "light";
    const map = {
        presentation: light ? "public/presentation-light.svg" : "public/presentation.svg",
        calendar: light ? "public/calendar-black.svg" : "public/calendar.svg",
        grip: light ? "public/grip-ligth.svg" : "public/grip.svg", // nota: archivo existente con "ligth"
        zoomOut: light ? "public/zoom-out-ligth.svg" : "public/zoom-out.svg",
        zoomMid: light ? "public/search-ligth.svg" : "public/search.svg",
        zoomIn: light ? "public/zoom-in-ligth.svg" : "public/zoom-in.svg",
        trash: light ? "public/trash-light.svg" : "public/trash.svg",
        clipPlus: light ? "public/clipboard-plus-light.svg" : "public/clipboard-plus.svg",
        clipCheck: "public/clipboard-check.svg",
        download: "public/download.svg",
    };
    return map[icon];
}

// ======== Patch global de Plotly según tema ========
(function patchPlotly() {
    if (window.__plotlyPatched) return; // patch una vez; decide por THEME en cada invocación
    const originalNewPlot = Plotly.newPlot;

    const LIGHT_LAYOUT = {
        template: "plotly_white",
        paper_bgcolor: "rgba(255,255,255,1)",
        plot_bgcolor: "rgba(255,255,255,1)",
        font: { color: "#111827" },
        colorway: ["#2563eb", "#16a34a", "#db2777", "#d97706", "#7c3aed", "#dc2626", "#0891b2", "#ca8a04"],
        xaxis: {
            gridcolor: "#e5e7eb",
            zerolinecolor: "#e5e7eb",
            linecolor: "#9ca3af",
            tickfont: { color: "#374151" },
            titlefont: { color: "#111827" },
        },
        yaxis: {
            gridcolor: "#e5e7eb",
            zerolinecolor: "#e5e7eb",
            linecolor: "#9ca3af",
            tickfont: { color: "#374151" },
            titlefont: { color: "#111827" },
        },
        legend: { font: { color: "#111827" } },
    };

    const DARK_LAYOUT = {
        template: "plotly_dark",
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: "#e5e7eb" },
        colorway: ["#60a5fa", "#34d399", "#f472b6", "#f59e0b", "#a78bfa", "#f87171", "#22d3ee", "#fde047"],
        xaxis: {
            gridcolor: "#2f2f2f",
            zerolinecolor: "#2f2f2f",
            linecolor: "#444",
            tickfont: { color: "#cbd5e1" },
            titlefont: { color: "#9ca3af" },
        },
        yaxis: {
            gridcolor: "#2f2f2f",
            zerolinecolor: "#2f2f2f",
            linecolor: "#444",
            tickfont: { color: "#cbd5e1" },
            titlefont: { color: "#9ca3af" },
        },
        legend: { font: { color: "#e5e7eb" } },
    };

    const DEFAULT_CONFIG = { responsive: true, displaylogo: false, locale: "es" };

    function mergeDeep(target, source) {
        const t = target || {};
        for (const k in source) {
            const v = source[k];
            if (v && typeof v === "object" && !Array.isArray(v)) t[k] = mergeDeep(t[k] || {}, v);
            else if (v !== undefined) t[k] = v;
        }
        return t;
    }

    function tweakTraceForTheme(trace) {
        const t = { ...trace };
        if (t.type === "pie" || t.type === "treemap" || t.type === "sunburst") {
            if (THEME === "dark") {
                t.textfont = { color: "#e5e7eb", ...(t.textfont || {}) };
                t.insidetextfont = { color: "#ffffff", ...(t.insidetextfont || {}) };
                t.outsidetextfont = { color: "#e5e7eb", ...(t.outsidetextfont || {}) };
            } else {
                t.textfont = { color: "#111827", ...(t.textfont || {}) };
                t.insidetextfont = { color: "#111827", ...(t.insidetextfont || {}) };
                t.outsidetextfont = { color: "#111827", ...(t.outsidetextfont || {}) };
            }
        }
        return t;
    }

    Plotly.newPlot = function (container, data, layout = {}, config = {}) {
        // Permite saltar el tema si layout.__skipTheme === true
        if (!(layout && layout.__skipTheme)) {
            layout = mergeDeep(mergeDeep({}, THEME === "dark" ? DARK_LAYOUT : LIGHT_LAYOUT), layout || {});
        }
        const dataPatched = (data || []).map(tweakTraceForTheme);
        const configPatched = { ...DEFAULT_CONFIG, ...(config || {}) };
        return originalNewPlot(container, dataPatched, layout, configPatched);
    };

    window.__plotlyPatched = true;
})();

function redirectToLoginPreservandoDestino() {
    const destino = encodeURIComponent(location.pathname || "/graphs");
    location.href = `/login?next=${destino}`;
}

// ======== Render principal ========
async function renderGraphsUnified() {
    const root = document.getElementById("root");
    const isLight = THEME === "light";

    root.innerHTML = `
    <div style="background:${
        isLight ? "#ffffff" : "#212121"
    }; min-height:100vh; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; ${
        isLight ? "color:#111827" : ""
    }">
      <header style="background:${isLight ? "#ffffff" : "#212121"}; border-bottom:1px solid ${
        isLight ? "#e5e7eb" : "#3c3c3c"
    }; padding:20px 0; box-shadow:${isLight ? "0 4px 8px rgba(0,0,0,0.03)" : "0 4px 8px rgba(0,0,0,0.3)"};">
        <div style="max-width:1400px; margin:0 auto; padding:0 24px; display:flex; align-items:center; justify-content:space-between;">
          <div style="display:flex; align-items:center; gap:16px;">
            <img src="public/avatar.png" alt="Avatar" style="height:32px; width:32px; border-radius:50%;"/>
            <h1 style="margin:0; font-size:24px; font-weight:600; color:${
                isLight ? "#111827" : "#ffffff"
            };">Mis Gráficos</h1>
          </div>
          <div style="display:flex; align-items:center; gap:12px;">
            <span id="graphs-count" style="font-size:14px; color:${isLight ? "#374151" : "#ffffff"};">Cargando...</span>

            <button
                onclick="handleDownloadSelectedGraphs()"
                title="Generar reporte PowerPoint"
                style="
                display: flex;
                align-items: center;
                gap: 6px;
                background: transparent;
                border: 1px solid ${isLight ? "rgba(0,0,0,0.15)" : "rgba(255,255,255,0.3)"};
                color: ${isLight ? "#374151" : "#ffffff"};
                font-size: 14px;
                padding: 6px 10px;
                border-radius: 8px;
                cursor: pointer;
                transition: background 0.2s, border-color 0.2s;
                "
                onmouseover="this.style.background='${isLight ? "rgba(0,0,0,0.05)" : "rgba(255,255,255,0.1)"}'"
                onmouseout="this.style.background='transparent'"
            >
                <img 
                src="${asset("presentation")}" 
                width="20" 
                height="20" 
                alt="PowerPoint icon"
                />
                <span>Generar PowerPoint</span>
            </button>
            </div>

        </div>
      </header>
      <main style="max-width:1900px; margin:0 auto; padding:32px 24px;">
        <div id="graphs-container-new">
          <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:400px;">
            <div style="width:32px; height:32px; border:2px solid #e5e7eb; border-top:2px solid ${
                isLight ? "#2563eb" : "#3b82f6"
            }; border-radius:50%; animation:spin 1s linear infinite; margin-bottom:16px;"></div>
            <p style="color:${isLight ? "#6b7280" : "#9ca3af"}; font-size:16px; margin:0;">Cargando gráficos...</p>
          </div>
        </div>
      </main>
    </div>
    <style>
      @keyframes spin { from{transform:rotate(0)} to{transform:rotate(360deg)} }
      .graph-card{ background:${isLight ? "#ffffff" : "#171717"}; border-radius:10px; border:1px solid ${
        isLight ? "#e5e7eb" : "#161a1d"
    }; overflow:hidden; transition:all .3s ease; box-shadow:${
        isLight ? "0 1px 3px rgba(0,0,0,.06)" : "0 1px 3px rgba(222,222,222,.1)"
    }; }
      .graph-card:hover{ box-shadow:${
          isLight ? "0 4px 16px rgba(0,0,0,.08)" : "0 4px 12px rgba(0,0,0,.1)"
      }; border-color:${isLight ? "#e5e7eb" : "rgb(60,60,61)"}; }
      .graph-grid{ display:grid; grid-template-columns:repeat(3,1fr); gap:24px; }
      .graph-item-1{grid-column:span 1}.graph-item-2{grid-column:span 2}.graph-item-3{grid-column:span 3}
      @media (max-width:1024px){ .graph-grid{grid-template-columns:repeat(2,1fr)} .graph-item-2,.graph-item-3{grid-column:span 2} }
      @media (max-width:640px){ .graph-grid{grid-template-columns:1fr} .graph-item-1,.graph-item-2,.graph-item-3{grid-column:span 1} }
      .graph-card [id^="graph-new-"] .js-plotly-plot,.graph-card [id^="graph-new-"] .plotly{border-radius:8px!important}
      .graph-card [id^="graph-new-"] .svg-container{border-radius:8px!important; overflow:visible!important}
      .graph-card [id^="graph-new-"] .main-svg{border-radius:8px!important}
      .graph-card .modebar{position:absolute!important; top:8px!important; right:8px!important; z-index:10!important}
      .js-plotly-plot{background:transparent!important}
      .modebar-btn--logo{display:none!important}
      .fade-out-up{opacity:0; transform:translateY(-12px); transition:opacity .5s ease, transform .5s ease}
      .drag-handle{cursor:grab; display:flex; align-items:center; justify-content:center; opacity:.6; transition:opacity .2s}
      .drag-handle:hover{opacity:1} .drag-handle:active{cursor:grabbing}
    </style>
  `;

    try {
        const response = await fetch("/api/pinned-graphs", {
            credentials: "include",
            headers: { Accept: "application/json" },
        });
        if (!response.ok) {
            // usar status, no statusText, y tolerar respuestas no-JSON
            if (response.status === 401) {
                redirectToLoginPreservandoDestino();
                return;
            }
            let data = {};
            const ct = (response.headers.get("content-type") || "").toLowerCase();
            if (ct.includes("application/json")) {
                data = await response.json();
            } else {
                const raw = await response.text();
                try {
                    data = JSON.parse(raw);
                } catch {
                    data = { error: raw.slice(0, 400) + (raw.length > 400 ? "…" : "") };
                }
            }
            showErrorUnified("Error: " + (data.error || "Error desconocido"));
            return;
        }

        const data = await response.json();
        originalGraphsData = data.graphs || [];

        const container = document.getElementById("graphs-container-new");
        const countElement = document.getElementById("graphs-count");
        countElement.textContent = `${originalGraphsData.length} gráficos`;

        if (originalGraphsData.length === 0) {
            container.innerHTML = `
        <div style="display:flex; justify-content:center; align-items:center; height:70vh;">
          <div style="max-width:860px; text-align:center; padding:80px 20px; background:${
              isLight ? "#ffffff" : "#212121"
          }; border-radius:12px; border:1px solid ${isLight ? "#e5e7eb" : "#3c3c3c"};">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="${
                isLight ? "#9ca3af" : "#d1d5db"
            }" stroke-width="1" style="margin:0 auto 24px;"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
            <h3 style="margin:0 0 8px; font-size:20px; font-weight:600; color:${
                isLight ? "#111827" : "#ffffff"
            };">No hay gráficos fijados</h3>
            <p style="margin:0; color:${
                isLight ? "#6b7280" : "#ffffff"
            }; font-size:16px;">Fija algunos gráficos desde el chat para verlos aquí</p>
          </div>
        </div>`;
            return;
        }

        // Cargar config previa (orden/tamaños)
        const configLoaded = loadGraphConfiguration();
        if (!configLoaded || graphPositions.length === 0) {
            graphPositions = originalGraphsData.map((g) => g.id);
        } else {
            // sincronizar posiciones con ids actuales
            const currentIds = originalGraphsData.map((g) => g.id);
            graphPositions = graphPositions.filter((id) => currentIds.includes(id));
            currentIds.forEach((id) => {
                if (!graphPositions.includes(id)) graphPositions.push(id);
            });
        }
        originalGraphsData.forEach((g) => {
            if (!graphSizes[g.id]) graphSizes[g.id] = 1;
        });

        renderGraphsInOrderUnified();
    } catch (err) {
        console.error("💥 Error:", err);
        showErrorUnified("Error: " + err.message);
    }
}

function renderGraphsInOrderUnified() {
    const isLight = THEME === "light";
    const container = document.getElementById("graphs-container-new");

    container.innerHTML = `
    <div class="graph-grid" id="graph-grid">
      ${graphPositions
          .map((graphId) => {
              const graph = originalGraphsData.find((g) => g.id === graphId);
              if (!graph) return "";
              const size = graphSizes[graph.id] || 1;

              // Fecha: usar la que viene (ya viene formateada por backend para created_at)
              let dateString = "";
              if (graph.display_date) dateString = graph.display_date;
              else if (graph.created_at) dateString = graph.created_at;

              return `
            <div class="graph-card graph-item-${size}" data-graph-id="${graph.id}">
                <div style="padding:20px 24px 16px; border-bottom:1px solid ${isLight ? "#f3f4f6" : "#3c3c3c"};">
                    <!-- Fila 1: fecha + botones -->
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:12px;">
                    <!-- Columna izquierda: FECHA -->
                    <p style="margin:0; font-size:14px; color:${
                        isLight ? "#6b7280" : "#6b7280"
                    }; display:flex; align-items:center; gap:6px;">
                        <img src="${asset("calendar")}" width="14" height="14" alt="Calendario" style="opacity:0.7;"/>
                        ${dateString || ""}
                    </p>

                    <!-- Columna derecha: BOTONES -->
                    <div style="display:flex; gap:12px; align-items:center;">
                        <div class="drag-handle" title="Arrastrar para cambiar de lugar">
                        <img src="${asset("grip")}" width="20" height="20" style="opacity:.6; transition:opacity .2s;"/>
                        </div>
                        <div style="width:1px; height:20px; background:${isLight ? "#e5e7eb" : "#e5e7eb"};"></div>
                        <div class="size-controls" style="display:flex; gap:8px;">
                        <img src="${asset(
                            "zoomOut"
                        )}" width="20" height="20" style="cursor:pointer;" title="Zoom pequeño" onclick="changeGraphSize('${
                  graph.id
              }', 1)"/>
                        <img src="${asset(
                            "zoomMid"
                        )}" width="20" height="20" style="cursor:pointer;" title="Zoom medio" onclick="changeGraphSize('${
                  graph.id
              }', 2)"/>
                        <img src="${asset(
                            "zoomIn"
                        )}" width="20" height="20" style="cursor:pointer;" title="Zoom grande" onclick="changeGraphSize('${
                  graph.id
              }', 3)"/>
                        <div style="width:1px; height:20px; background:${isLight ? "#e5e7eb" : "#e5e7eb"};"></div>
                        <img src="${asset(
                            "clipPlus"
                        )}" width="20" height="20" class="clipboard-toggle" data-graph-id="${
                  graph.id
              }" style="cursor:pointer;" title="Agregar al reporte" onclick="toggleGraphSelection(this)"/>
                        </div>
                        <div style="width:1px; height:20px; background:${isLight ? "#e5e7eb" : "#e5e7eb"};"></div>
                        <div class="size-controls" style="display:flex; gap:8px;">
                        <img src="${asset(
                            "trash"
                        )}" width="20" height="20" style="cursor:pointer;" title="Eliminar gráfico" onclick="deleteGraph('${
                  graph.id
              }', 1)"/>
                        </div>
                    </div>
                    </div>

                    <!-- Fila 2: TÍTULO a todo el ancho -->
                    <h3 class="graph-title" style="margin:10px 0 0; font-size:14px; font-weight:600; color:${
                        isLight ? "#111827" : "#6b7280"
                    }; line-height:1.4; cursor:text;" data-graph-id="${graph.id}" ondblclick="enableTitleEdit(this)">
                    ${graph.pin_title ? graph.pin_title : graph.figure?.layout?.title?.text || "Gráfico sin título"}
                    </h3>
                </div>

                <!-- Área del gráfico -->
                <div style="padding:16px; padding-top:8px;">
                    <div id="graph-new-${graph.id}" style="width:100%; height:${getGraphHeight(
                  size
              )}px; border-radius:8px; background:${isLight ? "#fafafa" : "#0f0f0f"}; position:relative;"></div>
                </div>
                </div>
              `;
          })
          .join("")}
    </div>`;

    // Render Plotly
    graphPositions.forEach((graphId) => {
        const graph = originalGraphsData.find((g) => g.id === graphId);
        if (graph?.figure) {
            const size = graphSizes[graph.id] || 1;
            renderPlotlyGraphUnified(graph, size);
        }
    });

    // Drag & drop (dragula)
    const grid = document.getElementById("graph-grid");
    if (grid && typeof dragula !== "undefined") {
        dragula([grid], {
            moves: (el, _container, handle) =>
                handle.classList.contains("drag-handle") || handle.closest(".drag-handle"),
        }).on("drop", () => {
            const cards = Array.from(grid.children);
            graphPositions = cards.map((card) => card.getAttribute("data-graph-id"));
            saveGraphConfiguration();
        });
    }
}

function getGraphHeight(size) {
    return size === 3 ? 500 : size === 2 ? 400 : 300;
}

function renderPlotlyGraphUnified(graph, size) {
    const containerId = `graph-new-${graph.id}`;
    const container = document.getElementById(containerId);
    if (!container) return;

    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;

    let margins;
    switch (size) {
        case 3:
            margins = { t: 60, r: 70, b: 55, l: 65 };
            break;
        case 2:
            margins = { t: 50, r: 60, b: 45, l: 55 };
            break;
        default:
            margins = { t: 40, r: 50, b: 35, l: 45 };
    }

    const layout = { ...(graph.figure?.layout || {}), margin: { ...(graph.figure?.layout?.margin || {}), ...margins } };
    Plotly.newPlot(containerId, graph.figure.data, layout);

    setTimeout(() => {
        const graphDiv = document.getElementById(containerId);
        if (graphDiv && graphDiv._fullLayout) {
            Plotly.relayout(graphDiv, { width: containerWidth, height: containerHeight });
        }
    }, 150);
}

// ======== Acciones UI ========
window.changeGraphSize = (graphId, newSize) => {
    graphSizes[graphId] = newSize;
    const card = document.querySelector(`[data-graph-id="${graphId}"]`);
    if (card) card.className = `graph-card graph-item-${newSize}`;
    const graphContainer = document.getElementById(`graph-new-${graphId}`);
    if (graphContainer) graphContainer.style.height = getGraphHeight(newSize) + "px";
    setTimeout(() => {
        const graph = originalGraphsData.find((g) => g.id === graphId);
        if (graph?.figure) renderPlotlyGraphUnified(graph, newSize);
        saveGraphConfiguration();
    }, 100);
};

window.moveGraphUp = (graphId) => {
    const idx = graphPositions.indexOf(graphId);
    if (idx > 0) {
        [graphPositions[idx - 1], graphPositions[idx]] = [graphPositions[idx], graphPositions[idx - 1]];
        renderGraphsInOrderUnified();
        saveGraphConfiguration();
    }
};

window.moveGraphDown = (graphId) => {
    const idx = graphPositions.indexOf(graphId);
    if (idx >= 0 && idx < graphPositions.length - 1) {
        [graphPositions[idx + 1], graphPositions[idx]] = [graphPositions[idx], graphPositions[idx + 1]];
        renderGraphsInOrderUnified();
        saveGraphConfiguration();
    }
};

// ======== Persistencia de layout ========
function saveGraphConfiguration() {
    try {
        const cfg = { positions: graphPositions, sizes: graphSizes, timestamp: new Date().toISOString() };
        localStorage.setItem("graphsConfiguration", JSON.stringify(cfg));
    } catch (e) {
        console.error("❌ Error guardando configuración:", e);
    }
}

function loadGraphConfiguration() {
    try {
        const saved = localStorage.getItem("graphsConfiguration");
        if (!saved) return false;
        const cfg = JSON.parse(saved);
        if (cfg.positions && Array.isArray(cfg.positions)) graphPositions = cfg.positions;
        if (cfg.sizes && typeof cfg.sizes === "object") graphSizes = cfg.sizes;
        return true;
    } catch (e) {
        console.error("❌ Error cargando configuración:", e);
        return false;
    }
}

// ======== CRUD de gráficos ========
window.deleteGraph = async (graphId, confirmFlag = 1) => {
    const isLight = THEME === "light";
    if (confirmFlag) {
        const result = await Swal.fire({
            title: "¿Eliminar gráfico?",
            text: "Esta acción no se puede deshacer.",
            icon: "warning",
            showCancelButton: true,
            confirmButtonText: "Sí, eliminar",
            cancelButtonText: "Cancelar",
            background: isLight ? "#ffffff" : "#1e1e1e",
            color: isLight ? "#111827" : "#ffffff",
            confirmButtonColor: isLight ? "#dc2626" : "#d33",
            cancelButtonColor: isLight ? "#6b7280" : "#3085d6",
        });
        if (!result.isConfirmed) return;
    }
    try {
        const res = await fetch("/api/delete-graph", {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json", Accept: "application/json" },
            body: JSON.stringify({ id: graphId }),
        });
        const data = await res.json();
        console.log("🧹 Respuesta backend:", data);

        const card = document.querySelector(`[data-graph-id="${graphId}"]`);
        if (card) {
            card.classList.add("fade-out-up");
            setTimeout(() => card.remove(), 500);
        }

        const idx = graphPositions.indexOf(graphId);
        if (idx !== -1) {
            graphPositions.splice(idx, 1);
            saveGraphConfiguration();
        }

        const countEl = document.getElementById("graphs-count");
        if (countEl) countEl.textContent = `${graphPositions.length} gráficos`;
    } catch (e) {
        await Swal.fire({
            icon: "error",
            title: "Error",
            text: "Hubo un error al intentar eliminar el gráfico.",
            background: isLight ? "#ffffff" : "#1e1e1e",
            color: isLight ? "#111827" : "#ffffff",
        });
    }
};

window.enableTitleEdit = (h3) => {
    const isLight = THEME === "light";
    const originalText = h3.textContent;
    const graphId = h3.dataset.graphId;
    const input = document.createElement("input");
    input.type = "text";
    input.value = originalText;
    input.style = `font-size:18px; font-weight:600; color:${
        isLight ? "#111827" : "#6b7280"
    }; width:100%; background:transparent; border:none; border-bottom:1px solid ${
        isLight ? "#d1d5db" : "#4b5563"
    }; outline:none;`;
    h3.replaceWith(input);
    input.focus();

    const save = async () => {
        const newTitle = (input.value || "").trim() || "Gráfico sin título";
        const newH3 = document.createElement("h3");
        newH3.className = "graph-title";
        newH3.textContent = newTitle;
        newH3.setAttribute("data-graph-id", graphId);
        newH3.setAttribute("style", h3.getAttribute("style"));
        newH3.setAttribute("ondblclick", "enableTitleEdit(this)");
        input.replaceWith(newH3);
        try {
            const res = await fetch("/api/update-graph", {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/json", Accept: "application/json" },
                body: JSON.stringify({ id: graphId, title: newTitle }),
            });
            const data = await res.json();
            if (!res.ok) {
                await Swal.fire({
                    icon: "error",
                    title: "Error al actualizar",
                    text: data.error || "Ocurrió un error inesperado",
                    background: isLight ? "#ffffff" : "#1e1e1e",
                    color: isLight ? "#111827" : "#ffffff",
                    confirmButtonColor: isLight ? "#dc2626" : "#d33",
                });
            } else {
                console.log("📝 Título actualizado:", data.message);
            }
        } catch (e) {
            await Swal.fire({
                icon: "error",
                title: "Error de red",
                text: "No se pudo conectar con el servidor",
                background: isLight ? "#ffffff" : "#1e1e1e",
                color: isLight ? "#111827" : "#ffffff",
                confirmButtonColor: isLight ? "#dc2626" : "#d33",
            });
        }
    };
    input.addEventListener("blur", save);
    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") input.blur();
    });
};

window.toggleGraphSelection = function (el) {
    const graphId = el.getAttribute("data-graph-id");
    const wasSelected = selectedGraphs.has(graphId);
    if (wasSelected) {
        selectedGraphs.delete(graphId);
        el.src = asset("clipPlus");
        el.title = "Agregar al reporte";
    } else {
        selectedGraphs.add(graphId);
        el.src = asset("clipCheck");
        el.title = "Quitar del reporte";
    }
    console.log("📋 Seleccionados:", Array.from(selectedGraphs));
};

// Reemplaza TODO el bloque de handleDownloadSelectedGraphs por este:
window.handleDownloadSelectedGraphs = async function () {
    const isLight = THEME === "light";

    if (selectedGraphs.size === 0) {
        await Swal.fire({
            icon: "warning",
            title: "Ningún gráfico seleccionado",
            text: "Por favor selecciona algún gráfico para crear el reporte",
            confirmButtonText: "OK",
            background: isLight ? "#ffffff" : "#1f1f1f",
            color: isLight ? "#111827" : "#e0e0e0",
        });
        return;
    }

    const confirmed = await Swal.fire({
        icon: "question",
        title: "¿Crear reporte PowerPoint?",
        text: "¿Estás seguro de que quieres generar un PowerPoint con los gráficos seleccionados?",
        showCancelButton: true,
        confirmButtonText: "Sí, crear",
        cancelButtonText: "Cancelar",
        background: isLight ? "#ffffff" : "#1f1f1f",
        color: isLight ? "#111827" : "#e0e0e0",
    });
    if (!confirmed.isConfirmed) return;

    // ⚠️ NO usar await aquí, para no bloquear la ejecución
    Swal.fire({
        title: "Generando reporte...",
        background: isLight ? "#ffffff" : "#1f1f1f",
        color: isLight ? "#111827" : "#e0e0e0",
        showConfirmButton: false,
        allowOutsideClick: false,
        allowEscapeKey: false,
        didOpen: () => Swal.showLoading(),
    });

    try {
        const res = await fetch("/api/create_powerpoint", {
            method: "POST",
            credentials: "include", // ← importante si usas cookies
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
            },
            body: JSON.stringify({ graph_ids: Array.from(selectedGraphs) }),
        });

        // Tolerar contenido no-JSON (p.ej., HTML de error del proxy)
        const ct = (res.headers.get("content-type") || "").toLowerCase();
        let data = {};
        if (ct.includes("application/json")) {
            data = await res.json();
        } else {
            const raw = await res.text();
            try {
                data = JSON.parse(raw);
            } catch {
                data = { error: raw.slice(0, 400) + (raw.length > 400 ? "…" : "") };
            }
        }

        if (res.ok && data.url) {
            await Swal.fire({
                icon: "success",
                title: "Reporte generado",
                html: `<p>El Power Point fue creado exitosamente.</p><br>
               <div style="display:flex;justify-content:center;align-items:center;gap:8px;">
                 <img src="${asset("download")}" width="20" height="20" alt="descargar">
                 <a href="${data.url}" download style="${
                    isLight ? "color:#2563eb" : "color:#60a5fa"
                };text-decoration:none;font-weight:500;">Descargar ahora</a>
               </div>`,
                background: isLight ? "#fff" : "#1f1f1f",
                color: isLight ? "#1f1f1f" : "#fff",
                confirmButtonText: "Cerrar",
            });

            // Reset de selección/íconos
            selectedGraphs.clear();
            document.querySelectorAll(".clipboard-toggle").forEach((el) => {
                el.src = asset("clipPlus");
                el.title = "Agregar al reporte";
            });
        } else {
            throw new Error(data.error || "No se pudo generar el archivo.");
        }
    } catch (e) {
        await Swal.fire({
            icon: "error",
            title: "Error",
            text: e.message || "Falla desconocida",
            background: isLight ? "#ffffff" : "#1f1f1f",
            color: isLight ? "#111827" : "#e0e0e0",
        });
    }
};

// ======== Helper de error ========
function showErrorUnified(message) {
    const isLight = THEME === "light";
    const container = document.getElementById("graphs-container-new");
    if (!container) return;
    container.innerHTML = `
    <div style="text-align:center; padding:80px 20px; background:${
        isLight ? "#ffffff" : "#1e1e1e"
    }; border-radius:12px; border:1px solid ${isLight ? "#fee2e2" : "#5a1f1f"};">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" style="margin:0 auto 16px;"><circle cx="12" cy="12" r="10"/><path d="M15 9l-6 6"/><path d="M9 9l6 6"/></svg>
      <h3 style="margin:0 0 8px; font-size:18px; font-weight:600; color:#dc2626;">Error</h3>
      <p style="margin:0; color:${isLight ? "#6b7280" : "#cbd5e1"}; font-size:14px;">${message}</p>
    </div>`;
}

// ======== Bootstrap ========
document.addEventListener("DOMContentLoaded", renderGraphsUnified);
console.log("✅ GraphsPage unificado cargado -", new Date().toLocaleTimeString());
