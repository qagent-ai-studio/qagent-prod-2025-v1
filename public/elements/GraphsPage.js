// 🔥 ARCHIVO NUEVO PARA TESTING - GraphsPageNEW.js
console.log("📊 Página de Gráficos - Versión QDark");

// Estado para controlar el tamaño de los gráficos
let graphSizes = {}; // {graphId: size} donde size puede ser 1, 2, o 3 (columnas)
const selectedGraphs = new Set(); // ← Aquí

const renderGraphsNew = async () => {
    const root = document.getElementById("root");

    // Diseño QAgent
    root.innerHTML = `
    <div style="background: #212121; min-height: 100vh; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
      
      <!-- Header elegante -->
      <header style="background:#212121; border-bottom: 1px #fff; padding: 20px 0;  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);">
      <div style="max-width: 1400px; margin: 0 auto; padding: 0 24px; display: flex; align-items: center; justify-content: space-between;">
      <div style="display: flex; align-items: center; gap: 16px;">
            
            <!-- Imagen al lado izquierdo -->
            <img src="public/avatar.png" alt="Avatar" style="height: 32px; width: 32px; border-radius: 50%;" />

            <h1 style="margin: 0; font-size: 24px; font-weight: 600; color: #fff;">Mis Gráficos</h1>
      </div>
      
      <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 14px; color: #fff;" id="graphs-count">Cargando...</span>
            <img 
            src="public/presentation.svg" 
            width="22" 
            height="22" 
            style="cursor: pointer; margin-left: 12px;" 
            title="Generar reporte PowerPoint"
            onclick="handleDownloadSelectedGraphs()" 
            />
      </div>


      </div>
      </header>


      <!-- Contenido principal -->
      <main style="max-width: 1900px; margin: 0 auto; padding: 32px 24px;">
        <div id="graphs-container-new">
          <!-- Loading state -->
          <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 400px;">
            <div style="width: 32px; height: 32px; border: 2px solid #e5e7eb; border-top: 2px solid #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 16px;"></div>
            <p style="color: #6b7280; font-size: 16px; margin: 0;">Cargando gráficos...</p>
          </div>
        </div>
      </main>
    </div>
    
    <style>
      @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }

     
      
      .graph-card {
        background: #171717;
        border-radius: 10px;
        border: 1px solid #161a1d;
        overflow: hidden;
        transition: all 0.3s ease;
        box-shadow: 0 1px 3px rgba(222, 222, 222, 0.1);
      }
      
      .graph-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-color:rgb(60, 60, 61);
      }
      
      .size-controls {
        display: flex;
        gap: 4px;
        opacity: 1;
        transition: opacity 0.2s;
      }
      
      .graph-card:hover .size-controls {
        opacity: 1;
      }
      
      .size-btn {
        width: 28px;
        height: 28px;
        border: 1px solid #d1d5db;
        background: white;
        border-radius: 6px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
        font-size: 12px;
        color: #6b7280;
      }
      
      .size-btn:hover {
        background: #f3f4f6;
        border-color: #9ca3af;
      }
      
      .size-btn.active {
        background: #3b82f6;
        border-color: #3b82f6;
        color: white;
      }
      
      .position-btn {
        width: 28px;
        height: 28px;
        border: 1px solid #d1d5db;
        background: white;
        border-radius: 6px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
        color: #6b7280;
      }
      
      .position-btn:hover:not(:disabled) {
        background: #f3f4f6;
        border-color: #9ca3af;
        color: #374151;
      }
      
      .position-btn:disabled {
        opacity: 0.4;
        cursor: not-allowed;
        background: #f9fafb;
      }
      
      .graph-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 24px;
      }
      
      .graph-item-1 { grid-column: span 1; }
      .graph-item-2 { grid-column: span 2; }
      .graph-item-3 { grid-column: span 3; }
      
      @media (max-width: 1024px) {
        .graph-grid {
          grid-template-columns: repeat(2, 1fr);
        }
        .graph-item-2, .graph-item-3 { grid-column: span 2; }
      }
      
      @media (max-width: 640px) {
        .graph-grid {
          grid-template-columns: 1fr;
        }
        .graph-item-1, .graph-item-2, .graph-item-3 { grid-column: span 1; }
      }
      
      /* Estilos adicionales para ajuste perfecto de Plotly */
      .graph-card [id^="graph-new-"] .js-plotly-plot,
      .graph-card [id^="graph-new-"] .plotly {
        border-radius: 8px !important;
      }
      
      .graph-card [id^="graph-new-"] .svg-container {
        border-radius: 8px !important;
        overflow: visible !important;
      }
      
      .graph-card [id^="graph-new-"] .main-svg {
        border-radius: 8px !important;
      }
      
      /* Estilos para el modebar */
      .graph-card .modebar {
        position: absolute !important;
        top: 8px !important;
        right: 8px !important;
        z-index: 10 !important;
      }

      .plot-container {
        filter: invert(91%) hue-rotate(180deg);
      }
      .graph-card [id^="graph-new-"] .main-svg {
          border-radius: 2px !important;
      }
      .js-plotly-plot {
            background: transparent !important;
       }

      .modebar-btn--logo{
            display:none !important;
      }

      .fade-out-up {
            opacity: 0;
            transform: translateY(-12px);
            transition: opacity 0.5s ease, transform 0.5s ease;
      }

      .drag-handle {
            cursor: grab;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0.6;
            transition: opacity 0.2s;
      }

      .drag-handle:hover {
            opacity: 1;
      }

      .drag-handle:active {
            cursor: grabbing;
      }

      .drag-handle {
  cursor: grab;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.drag-handle:hover {
  opacity: 1;
}

.drag-handle:active {
  cursor: grabbing;
}


.graph-card:hover {
    
    box-shadow: 0 0 30px rgba(255, 0, 89, 0.2); /* efecto glow */
    transition: opacity 0.5s ease;
}


        
    </style>
  `;

    try {
        console.log("🔄 Cargando gráficos...");
        const response = await fetch("/api/pinned-graphs", {
            credentials: "include",
            headers: { Accept: "application/json" },
        });

        if (!response.ok) {
            const data = await response.json();

            if (response.statusText === "Unauthorized") {
                // Redirigir a la página de inicio de sesión si no está autenticado
                window.location.href = "/login";
                return;
            }

            showErrorNew("Error: " + (data.error || "Error desconocido"));
            return;
        }

        const data = await response.json();
        const container = document.getElementById("graphs-container-new");
        const countElement = document.getElementById("graphs-count");

        // Actualizar contador
        countElement.textContent = `${data.graphs?.length || 0} gráficos`;

        if (!data.graphs || data.graphs.length === 0) {
            container.innerHTML = `
       <div style="display: flex; justify-content: center; align-items: center;height: 70vh;">
        <div style="max-width: 860px; text-align: center; padding: 80px 20px; background: #212121; border-radius: 12px; border: 1px solid #e5e7eb;">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#d1d5db" stroke-width="1" style="margin: 0 auto 24px;">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
          </svg>
          <h3 style="margin: 0 0 8px; font-size: 20px; font-weight: 600; color:rgb(255, 255, 255);">No hay gráficos fijados</h3>
          <p style="margin: 0; color:rgb(255, 255, 255); font-size: 16px;">Fija algunos gráficos desde el chat para verlos aquí</p>
        </div>
        </div>
        
      `;
            return;
        }

        // Almacenar datos originales
        originalGraphsData = data.graphs;

        // Cargar configuración guardada
        const configLoaded = loadGraphConfiguration();

        // Inicializar posiciones si es la primera vez o sincronizar con datos actuales
        if (!configLoaded || graphPositions.length === 0) {
            graphPositions = data.graphs.map((graph) => graph.id);
            console.log("🆕 Inicializando posiciones por primera vez");
        } else {
            // Sincronizar posiciones con gráficos actuales
            const currentIds = data.graphs.map((g) => g.id);

            // Filtrar posiciones que ya no existen
            graphPositions = graphPositions.filter((id) => currentIds.includes(id));

            // Agregar nuevos gráficos al final
            currentIds.forEach((id) => {
                if (!graphPositions.includes(id)) {
                    graphPositions.push(id);
                    console.log(`➕ Nuevo gráfico agregado: ${id}`);
                }
            });

            console.log("🔄 Posiciones sincronizadas");
        }

        // Inicializar tamaños por defecto para nuevos gráficos
        data.graphs.forEach((graph) => {
            if (!graphSizes[graph.id]) {
                graphSizes[graph.id] = 1; // Tamaño por defecto: 1 columna
            }
        });

        console.log("📊 Estado final - Posiciones:", graphPositions);
        console.log("📏 Estado final - Tamaños:", graphSizes);

        // Renderizar gráficos en el orden guardado/configurado
        renderGraphsInOrder();
    } catch (error) {
        console.error("💥 Error:", error);
        showErrorNew("Error: " + error.message);
    }
};

// Función para renderizar gráficos en el orden correcto
const renderGraphsInOrder = () => {
    const container = document.getElementById("graphs-container-new");

    // Renderizar grid de gráficos en el orden de las posiciones
    container.innerHTML = `
      <div class="graph-grid" id="graph-grid">
      ${graphPositions
          .map((graphId) => {
              const graph = originalGraphsData.find((g) => g.id === graphId);
              if (!graph) return "";

              const size = graphSizes[graph.id] || 1;

              // Manejar la fecha de forma segura
              let dateString = "Fecha no disponible";

              if (graph.created_at) {
                  try {
                      const date = new Date(graph.created_at);
                      if (!isNaN(date.getTime())) {
                          dateString = date.toLocaleDateString("es-ES", {
                              day: "2-digit",
                              month: "2-digit",
                              year: "numeric",
                          });
                      }
                  } catch (e) {
                      console.warn("Error parsing date:", graph.created_at);
                  }
              }

              return `
          <div class="graph-card graph-item-${size}" data-graph-id="${graph.id}">
            <!-- Header del gráfico -->
            <div style="padding: 20px 24px 16px; border-bottom: 1px solid #3c3c3c; display: flex; justify-content: space-between; align-items: flex-start;">
              <div style="flex: 1;">
                <h3 class="graph-title"
                  style="margin: 0 0 4px; font-size: 18px; font-weight: 600; color: #6b7280; line-height: 1.4; cursor: text;"
                  data-graph-id="${graph.id}"
                  ondblclick="enableTitleEdit(this)">
                  ${graph.pin_title ? graph.pin_title : graph.figure?.layout?.title?.text || "Gráfico sin título"}
                  </h3>

                <p style="margin: 0; font-size: 14px; color: #6b7280; display: flex; align-items: center; gap: 6px;">
                  <img src="public/calendar.svg" width="14" height="14" alt="Calendario" style="opacity: 0.7;" />
                  ${dateString}
                  </p>
              </div>
              
              <!-- Controles de posición y tamaño -->
              <div style="display: flex; gap: 12px; align-items: center;">
                <!-- Controles de posición -->
                <div style="display: flex; gap: 12px; align-items: center;">  
                <div class="drag-handle" title="Arrastrar para cambiar de lugar">
                        <img src="public/grip.svg" width="20" height="20" style="opacity: 0.6; transition: opacity 0.2s;" />
                  </div>
                  </div>

                
                <!-- Separador -->
                <div style="width: 1px; height: 20px; background: #e5e7eb;"></div>
                
             <!-- Controles de tamaño -->
              <div class="size-controls" style="display: flex; gap: 8px;">
                <img src="public/zoom-out.svg" width="20" height="20"
                    onclick="changeGraphSize('${graph.id}', 1)" 
                    style="cursor: pointer; transition: opacity 0.2s;" 
                    title="Zoom pequeño" />

                <img src="public/search.svg" width="20" height="20"
                    onclick="changeGraphSize('${graph.id}', 2)" 
                    style="cursor: pointer;  transition: opacity 0.2s;" 
                    title="Zoom medio" />

                <img src="public/zoom-in.svg" width="20" height="20"
                    onclick="changeGraphSize('${graph.id}', 3)" 
                    style="cursor: pointer;  transition: opacity 0.2s;" 
                    title="Zoom grande" />

                    <div style="width: 1px; height: 20px; background: #e5e7eb;"></div>

                 <img 
                        src="public/clipboard-plus.svg" 
                        width="20" 
                        height="20" 
                        style="cursor: pointer; transition: opacity 0.2s;" 
                        title="Agregar al reporte"
                        class="clipboard-toggle"
                        data-graph-id="${graph.id}"
                        onclick="toggleGraphSelection(this)"
                        />
              </div>

              <div style="width: 1px; height: 20px; background: #e5e7eb;"></div>

              <div class="size-controls" style="display: flex; gap: 8px;">        
              
            <img src="public/trash.svg" width="20" height="20"
                onclick="deleteGraph('${graph.id}', 1)"  
                style="cursor: pointer; transition: opacity 0.2s;" 
                title="Eliminar gráfico" />
               </div>        
              


              </div>
            </div>
            
            <!-- Área del gráfico -->
            <div style="padding: 16px; padding-top: 8px;">
              <div id="graph-new-${graph.id}" style="width: 100%; height: ${getGraphHeight(
                  size
              )}px; border-radius: 8px; background: #fafafa; position: relative;"></div>
            </div>
          </div>
        `;
          })
          .join("")}
    </div>
  `;

    // Renderizar gráficos con Plotly en el orden de las posiciones
    graphPositions.forEach((graphId) => {
        const graph = originalGraphsData.find((g) => g.id === graphId);
        if (graph && graph.figure) {
            const size = graphSizes[graph.id] || 1;
            renderPlotlyGraph(graph, size);
        }
    });

    // Habilitar Dragula con grip como handle
    const grid = document.getElementById("graph-grid");
    if (grid && typeof dragula !== "undefined") {
        dragula([grid], {
            moves: (el, container, handle) => {
                return handle.classList.contains("drag-handle") || handle.closest(".drag-handle");
            },
        }).on("drop", () => {
            const cards = Array.from(grid.children);
            graphPositions = cards.map((card) => card.getAttribute("data-graph-id"));
            console.log("🔀 Nuevo orden arrastrado:", graphPositions);
            saveGraphConfiguration();
        });
    }
};

// Función para cambiar el tamaño de un gráfico
window.changeGraphSize = (graphId, newSize) => {
    graphSizes[graphId] = newSize;

    // Actualizar la clase del contenedor
    const graphCard = document.querySelector(`[data-graph-id="${graphId}"]`);
    graphCard.className = `graph-card graph-item-${newSize}`;

    // Actualizar botones activos
    const buttons = graphCard.querySelectorAll(".size-btn");
    buttons.forEach((btn, index) => {
        btn.classList.toggle("active", index + 1 === newSize);
    });

    // Redimensionar el gráfico
    const graphContainer = document.getElementById(`graph-new-${graphId}`);
    const newHeight = getGraphHeight(newSize);
    graphContainer.style.height = newHeight + "px";

    // Re-renderizar el gráfico con nuevo tamaño
    setTimeout(() => {
        const graph = originalGraphsData.find((g) => g.id === graphId);
        if (graph && graph.figure) {
            renderPlotlyGraph(graph, newSize);
        }

        // Guardar configuración al cambiar tamaño
        saveGraphConfiguration();
    }, 100);
};

// Función para obtener la altura del gráfico según el tamaño
const getGraphHeight = (size) => {
    switch (size) {
        case 1:
            return 300;
        case 2:
            return 400;
        case 3:
            return 500;
        default:
            return 300;
    }
};

// Función para renderizar un gráfico con Plotly
const renderPlotlyGraph = (graph, size) => {
    const height = getGraphHeight(size);
    const containerId = `graph-new-${graph.id}`;
    const container = document.getElementById(containerId);

    if (!container) return;

    // Obtener las dimensiones exactas del contenedor
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;

    // Configuración mejorada de márgenes con espacio para modebar
    let margins;
    switch (size) {
        case 1:
            // Más espacio en la parte superior y derecha para el modebar
            margins = { t: 40, r: 50, b: 35, l: 45 };
            break;
        case 2:
            margins = { t: 50, r: 60, b: 45, l: 55 };
            break;
        case 3:
            margins = { t: 60, r: 70, b: 55, l: 65 };
            break;
        default:
            margins = { t: 40, r: 50, b: 35, l: 45 };
    }

    Plotly.newPlot(containerId, graph.figure.data);

    // Ajuste adicional para asegurar que se mantiene dentro del contenedor
    setTimeout(() => {
        const graphDiv = document.getElementById(containerId);
        if (graphDiv && graphDiv._fullLayout) {
            // Forzar el redimensionamiento exacto al contenedor
            Plotly.relayout(graphDiv, {
                width: containerWidth,
                height: containerHeight,
            });
        }
    }, 150);
};

const showErrorNew = (message) => {
    const container = document.getElementById("graphs-container-new");
    if (container) {
        container.innerHTML = `
      <div style="text-align: center; padding: 80px 20px; background: white; border-radius: 12px; border: 1px solid #fee2e2;">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" style="margin: 0 auto 16px;">
          <circle cx="12" cy="12" r="10"/>
          <path d="M15 9l-6 6"/>
          <path d="M9 9l6 6"/>
        </svg>
        <h3 style="margin: 0 0 8px; font-size: 18px; font-weight: 600; color: #dc2626;">Error</h3>
        <p style="margin: 0; color: #6b7280; font-size: 14px;">${message}</p>
      </div>
    `;
    }
};

// Inicializar cuando el documento esté listo
document.addEventListener("DOMContentLoaded", renderGraphsNew);

console.log("✅ GraphsPage Profesional cargado -", new Date().toLocaleTimeString());

// Función para mover un gráfico hacia arriba
window.moveGraphUp = (graphId) => {
    const currentIndex = graphPositions.indexOf(graphId);

    if (currentIndex > 0) {
        // Intercambiar posiciones
        [graphPositions[currentIndex], graphPositions[currentIndex - 1]] = [
            graphPositions[currentIndex - 1],
            graphPositions[currentIndex],
        ];

        console.log(`📈 Movido gráfico ${graphId} hacia arriba`);
        console.log("📊 Nueva posición:", graphPositions);

        // Re-renderizar los gráficos en el nuevo orden
        renderGraphsInOrder();

        // Guardar configuración
        saveGraphConfiguration();
    }
};

// Función para mover un gráfico hacia abajo
window.moveGraphDown = (graphId) => {
    const currentIndex = graphPositions.indexOf(graphId);

    if (currentIndex < graphPositions.length - 1) {
        // Intercambiar posiciones
        [graphPositions[currentIndex], graphPositions[currentIndex + 1]] = [
            graphPositions[currentIndex + 1],
            graphPositions[currentIndex],
        ];

        console.log(`📉 Movido gráfico ${graphId} hacia abajo`);
        console.log("📊 Nueva posición:", graphPositions);

        // Re-renderizar los gráficos en el nuevo orden
        renderGraphsInOrder();

        // Guardar configuración
        saveGraphConfiguration();
    }
};

// Función para guardar configuración en localStorage
const saveGraphConfiguration = () => {
    try {
        const config = {
            positions: graphPositions,
            sizes: graphSizes,
            timestamp: new Date().toISOString(),
        };

        localStorage.setItem("graphsConfiguration", JSON.stringify(config));
        console.log("💾 Configuración guardada:", config);
    } catch (error) {
        console.error("❌ Error guardando configuración:", error);
    }
};

// Función para cargar configuración desde localStorage
const loadGraphConfiguration = () => {
    try {
        const saved = localStorage.getItem("graphsConfiguration");
        if (saved) {
            const config = JSON.parse(saved);
            console.log("📁 Configuración cargada:", config);

            // Restaurar posiciones si existen
            if (config.positions && Array.isArray(config.positions)) {
                graphPositions = config.positions;
            }

            // Restaurar tamaños si existen
            if (config.sizes && typeof config.sizes === "object") {
                graphSizes = config.sizes;
            }

            return true;
        }
    } catch (error) {
        console.error("❌ Error cargando configuración:", error);
    }

    return false;
};

/**  Elimina  el gráfico */
window.deleteGraph = async (graphId, confirmFlag = 1) => {
    if (confirmFlag) {
        const result = await Swal.fire({
            title: "¿Eliminar gráfico?",
            text: "Esta acción no se puede deshacer.",
            icon: "warning",
            showCancelButton: true,
            confirmButtonText: "Sí, eliminar",
            cancelButtonText: "Cancelar",
            background: "#1e1e1e",
            color: "#fff",
            confirmButtonColor: "#d33",
            cancelButtonColor: "#3085d6",
        });

        if (!result.isConfirmed) return;
    }

    try {
        const res = await fetch("/api/delete-graph", {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
            },
            body: JSON.stringify({ id: graphId }),
        });

        const data = await res.json();
        console.log("🧹 Respuesta del backend:", data);

        // Eliminar el gráfico del DOM directamente
        const graphCard = document.querySelector(`[data-graph-id="${graphId}"]`);
        if (graphCard) {
            graphCard.classList.add("fade-out-up");
            setTimeout(() => {
                graphCard.remove();
                console.log(`🧽 Gráfico ${graphId} eliminado del DOM`);
            }, 500); // debe coincidir con la duración del CSS (0.3s)
        }

        // Eliminar también del array de posiciones
        const index = graphPositions.indexOf(graphId);
        if (index !== -1) {
            graphPositions.splice(index, 1);
            saveGraphConfiguration();
        }

        // Actualizar contador
        const countElement = document.getElementById("graphs-count");
        if (countElement) {
            countElement.textContent = `${graphPositions.length} gráficos`;
        }
    } catch (error) {
        console.error("❌ Error al eliminar gráfico:", error);
        alert("Hubo un error al intentar eliminar el gráfico.");
    }
};

/**  Cambia el título de gráfico */
window.enableTitleEdit = (h3) => {
    const originalText = h3.textContent;
    const graphId = h3.dataset.graphId;

    // Crear input y reemplazar el h3 por él
    const input = document.createElement("input");
    input.type = "text";
    input.value = originalText;
    input.style = `
        font-size: 18px;
        font-weight: 600;
        color: #6b7280;
        width: 100%;
        background: transparent;
        border: none;
        border-bottom: 1px solid #4b5563;
        outline: none;
    `;

    h3.replaceWith(input);
    input.focus();

    // Al salir del input o presionar Enter, enviar actualización
    const save = async () => {
        const newTitle = input.value.trim() || "Gráfico sin título";

        // Crear nuevo h3
        const newH3 = document.createElement("h3");
        newH3.className = "graph-title";
        newH3.textContent = newTitle;
        newH3.setAttribute("data-graph-id", graphId);
        newH3.setAttribute("style", h3.getAttribute("style"));
        newH3.setAttribute("ondblclick", "enableTitleEdit(this)");
        input.replaceWith(newH3);

        // Llamar al backend
        try {
            const res = await fetch("/api/update-graph", {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                    Accept: "application/json",
                },
                body: JSON.stringify({ id: graphId, title: newTitle }),
            });

            const data = await res.json();

            if (!res.ok) {
                // Mostrar error de validación desde backend
                await Swal.fire({
                    icon: "error",
                    title: "Error al actualizar",
                    text: data.error || "Ocurrió un error inesperado",
                    background: "#1e1e1e",
                    color: "#fff",
                    confirmButtonColor: "#d33",
                });
            } else {
                console.log("📝 Título actualizado:", data.message);
                /*
                await Swal.fire({
                    icon: "success",
                    title: "Título actualizado",
                    text: data.message || "El título fue guardado correctamente",
                    timer: 1200,
                    showConfirmButton: false,
                    background: "#1e1e1e",
                    color: "#fff",
                });
                */
            }
        } catch (error) {
            console.error("❌ Error al actualizar título:", error);

            await Swal.fire({
                icon: "error",
                title: "Error de red",
                text: "No se pudo conectar con el servidor",
                background: "#1e1e1e",
                color: "#fff",
                confirmButtonColor: "#d33",
            });
        }
    };

    input.addEventListener("blur", save);
    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            input.blur();
        }
    });
};

function toggleGraphSelection(el) {
    const graphId = el.getAttribute("data-graph-id");

    if (selectedGraphs.has(graphId)) {
        // Deseleccionado
        selectedGraphs.delete(graphId);
        el.src = "public/clipboard-plus.svg";
        el.title = "Agregar al reporte";
    } else {
        // Seleccionado
        selectedGraphs.add(graphId);
        el.src = "public/clipboard-check.svg";
        el.title = "Quitar del reporte";
    }

    console.log("📋 Gráficos seleccionados:", Array.from(selectedGraphs));
}

async function handleDownloadSelectedGraphs() {
    if (selectedGraphs.size === 0) {
        Swal.fire({
            icon: "warning",
            title: "Ningún gráfico seleccionado",
            text: "Por favor selecciona algún gráfico para crear el reporte",
            confirmButtonText: "OK",
            toast: false,
            position: "center",
            background: "#1f1f1f",
            color: "#e0e0e0",
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
        background: "#1f1f1f",
        color: "#e0e0e0",
    });
    if (confirmed.isConfirmed) {
        // Mostrar loader intermedio
        Swal.fire({
            title: "Generando reporte...",
            background: "#1f1f1f",
            color: "#e0e0e0",
            showConfirmButton: false,
            allowOutsideClick: false,
            allowEscapeKey: false,
            didOpen: () => {
                // Forzar render de loader
                Swal.showLoading();
            },
        });

        try {
            const res = await fetch("/api/create_powerpoint", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ graph_ids: Array.from(selectedGraphs) }),
            });

            const data = await res.json();

            if (res.ok) {
                // Reemplazar el loader por el Swal de éxito
                Swal.fire({
                    icon: "success",
                    title: "Reporte generado",
                    html: `
                    <p>El Power Point fue creado exitosamente.</p><br>
                    <div style="display: flex; justify-content: center; align-items: center; gap: 8px;">
                        <img src="public/download.svg" width="20" height="20" alt="descargar">
                        <a href="${data.url}" download style="color: #60a5fa; text-decoration: none; font-weight: 500;">
                            Descargar ahora
                        </a>
                    </div>
                `,
                    background: "#1f1f1f",
                    color: "#fff",
                    confirmButtonText: "Cerrar",
                });

                selectedGraphs.clear();
                document.querySelectorAll(".clipboard-toggle").forEach((el) => {
                    el.src = "public/clipboard-plus.svg";
                    el.title = "Agregar al reporte";
                });
            } else {
                throw new Error(data.error || "Error desconocido");
            }
        } catch (error) {
            Swal.fire({
                icon: "error",
                title: "Error",
                text: error.message,
                background: "#1f1f1f",
                color: "#e0e0e0",
            });
        }
    }
}
