function renderVariacion(actual, anterior) {
    if (anterior === undefined || anterior === null || anterior === 0) return ""; // sin comparación
    const delta = actual - anterior;
    const pct = (delta / Math.abs(anterior)) * 100;
    let icono, color, txt;

    if (delta > 0) {
        icono = "↑";
        color = "#22c55e";
    } else if (delta < 0) {
        icono = "↓";
        color = "#ef4444";
    } else {
        icono = "●";
        color = "#6b7280";
    }
    txt = `${delta > 0 ? "+" : ""}${pct.toFixed(1)}% ${icono}`;
    return `<span style="font-size: 0.88em; margin-left:6px; color:${color}; font-weight: 600; vertical-align: middle;">${txt}</span>`;
}

function renderVariacionTiker(actual, anterior) {
    if (anterior === undefined || anterior === null || anterior === 0) return ""; // sin comparación
    const delta = actual - anterior;
    const pct = (delta / Math.abs(anterior)) * 100;
    let icono, color, txt;

    if (delta > 0) {
        icono = "↑";
        color = "#22c55e";
    } else if (delta < 0) {
        icono = "↓";
        color = "#ef4444";
    } else {
        icono = "●";
        color = "#6b7280";
    }
    txt = `${delta > 0 ? "+" : ""}${pct.toFixed(1)}% ${icono}`;
    return `<span style="font-size: 0.88em; margin-left:6px; color:${color};">${txt}</span>`;
}

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

            <h1 style="margin: 0; font-size: 24px; font-weight: 600; color: #fff;">Métricas y Análisis</h1>
      </div>
      
      <div style="display: flex; align-items: center; gap: 12px;">
           
            <img 
            src="public/settings.svg" 
            width="22" 
            height="22" 
            style="cursor: pointer; margin-left: 12px;" 
            title="Generar reporte PowerPoint"
            onclick="handleMetricsReport()" 
            />
      </div>


      </div>
      </header>


      <!-- Contenido principal -->
      <main style="max-width: 1900px; margin: 0 auto; padding: 32px 24px;">
        <div id="graphs-container-new">
          <!-- Loading state elegante -->
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
        border-radius: 0px;
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

      .metrica-grande{
            font-size: 26px;
      }
      .verde{
            color: #3d9970
      }
      .sky{
            color:    #1d7088
      }
      .rojo{
            color:#ff4136
      }  

      #analisis_ia {
            max-height: 400px; 
            overflow-y: auto; 
            overflow-x: hidden; 
      }

      /* Scrollbar para Chrome, Safari, Edge */
      #analisis_ia::-webkit-scrollbar {
      width: 8px;
      }
      #analisis_ia::-webkit-scrollbar-track {
            background: #2a2a2a;
            border-radius: 4px;
      }

      #analisis_ia::-webkit-scrollbar-thumb {
            background-color: #555;
            border-radius: 4px;
            border: 2px solid #2a2a2a;
      }

      #analisis_ia::-webkit-scrollbar-thumb:hover {
            background-color: #777;
      }

      /* Scrollbar para Firefox */
      #analisis_ia {
            scrollbar-width: thin;
            scrollbar-color: #555 #2a2a2a;
      }

      /* Estilos solo dentro de #analisis_ia */
      #analisis_ia h2 {
      color: #e5e7eb;
      font-size: 1.6em;
      margin-bottom: 0.5em;
      }

      #analisis_ia h3 {
      color: #9ca3af; 
      font-size: 1.3em;
      margin-top: 1em;
      margin-bottom: 0.4em;
      }

      #analisis_ia ul {
      list-style: disc inside;
      padding-left: 1em;
      margin-bottom: 1em;
      }

      #analisis_ia ul li {
      color: #d1d5db; 
      margin-bottom: 0.3em;
      line-height: 1.4;
      }

      /* Tablas dentro de #analisis_ia */
      #analisis_ia table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 40px;
      }

      #analisis_ia table th,
      #analisis_ia table td {
            padding: 8px;
            border: 1px solid rgba(255,255,255,0.1);
            color: #ddd;
      }

      #analisis_ia table th {
            background-color: rgba(255,255,255,0.05);
      }

      #analisis_ia b,
      #analisis_ia strong {
            color:rgb(170, 173, 173);   
            font-weight: 500; 
      }

      #analisis_ia ul {
            margin-bottom: 40px;
            padding-left: 1.2em;
      }

      #analisis_ia ul li {
            line-height: 1.6;
            margin-bottom: 0.4em;
      }
     .kpi-ticker-band {
      width: 100%;
      overflow: hidden;
      background: #23272c;
      /* border-radius: 12px; */
      box-shadow: 0 2px 8px #0002;
      /* margin: 16px 0 24px 0; */
      /* border: 1px solid #3c3c3c; */
      position: relative;
      height: 40px;
      }

      .kpi-ticker-track {
            display: inline-block;
            white-space: nowrap;
            animation: ticker-scroll 30s linear infinite;
            font-size: 1.08em;
            height: 40px;
            line-height: 40px;
      }

      .kpi-item {
            display: inline-block;
            margin-right: 36px;
            font-weight: 500;
            color: #e6e6e6;
      }

      .kpi-item.verde, .pct.verde { color: #22c55e !important; }
      .kpi-item.rojo, .pct.rojo   { color: #ef4444 !important; }
      .kpi-item.azul  { color: #60a5fa !important; }
      .kpi-item.gris  { color: #6b7280 !important; }

      .pct {
            font-size: 0.93em;
            font-weight: 700;
            margin-left: 5px;
      }

      @keyframes ticker-scroll {
            0%   { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
      }


            
      </style>
  `;

    try {
        console.log("🔄 Cargando reporte...");

        const response = await fetch("/api/get_last_and_previous_report", {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json", Accept: "application/json" },
            body: JSON.stringify({}),
        });

        if (!response.ok) {
            const respData = await response.json();

            if (response.status === 401) {
                window.location.href = "/login";
                return;
            }

            showErrorNew("Error: " + (respData.error || "Error desconocido"));
            return;
        }

        const respData = await response.json();

        // Aquí el truco: asigna el último reporte como data
        const data = respData.ultimo || respData.data || {}; // fallback si hay un cambio de backend
        const anterior = respData.anterior || null;

        const container = document.getElementById("graphs-container-new");
        console.log("✅ Reporte Cargado.");
        console.log("📊 Datos ultimo mes:", data);

        //renderGraphsInOrder(data);
        renderGraphsInOrder(data, anterior);

        // Si quieres hacer la comparativa con el anterior:
        if (anterior) {
            console.log("📊 Datos anteriores", anterior);
            //renderComparativa(data, anterior); // implementa esta función si quieres
        } else {
            // Mensaje opcional para el usuario
            document.getElementById("comparativa-label").textContent = "Primer mes: sin comparativo.";
        }
    } catch (error) {
        console.error("💥 Error:", error);
        showErrorNew("Error: " + error.message);
    }
};

// Función para renderizar gráficos en el orden correcto
const renderGraphsInOrder = (data, anterior = null) => {
    const container = document.getElementById("graphs-container-new");

    const tarjetaMetricas = `
      <div class="graph-card">
        <div style="padding: 20px 24px 16px; border-bottom: 1px solid #3c3c3c; display: flex; justify-content: space-between; align-items: flex-start;">
          <div style="flex: 1;">
            <h3 class="graph-title" style="margin: 0 0 4px; font-size: 18px; font-weight: 600; color: #6b7280; display: flex; align-items: center; gap: 8px;">
            <img src="public/chart-no-axes-combined.svg" width="14" height="14" alt="Icono"> 
            Métricas globales
            </h3>
          </div>
          <div class="drag-handle" title="Arrastrar para cambiar de lugar">
            <img src="public/grip.svg" width="20" height="20" />
          </div>
        </div>
       <div style="padding: 20px;">
        <p class="" style="color:#ccc; display: flex; justify-content: space-between; align-items: center;">
            <span>Conversaciones:</span> 
            <span>
             <span class="" style="font-variant-numeric: tabular-nums;">${data.conversaciones}</span>
          ${anterior ? renderVariacion(data.conversaciones, anterior.conversaciones) : ""}
        </span>
             
            </span>
        </p>
        <p class="" style="color:#ccc; display: flex; justify-content: space-between; align-items: center;">
            <span>Interacciones Totales:</span>
            <span>
              <span class="">${data.interacciones}</span>
              ${anterior ? renderVariacion(data.interacciones, anterior.interacciones) : ""}
            </span>
        </p>
        <!-- Continúa igual para las demás métricas... -->
        <br>
        <p>Desagregación de interacciones:</p>
        <p style="color:#ccc; display: flex; justify-content: space-between; align-items: center;">
            <span>Consultas de usuario:</span>
            <span>
              ${data.consultas_usuario}
              ${anterior ? renderVariacion(data.consultas_usuario, anterior.consultas_usuario) : ""}
            </span>
        </p>
        <p style="color:#ccc; display: flex; justify-content: space-between; align-items: center;">
            <span>Respuestas del asistente:</span>
            <span>
              ${data.respuestas_asistente}
              ${anterior ? renderVariacion(data.respuestas_asistente, anterior.respuestas_asistente) : ""}
            </span>
        </p>
        <p style="color:#ccc; display: flex; justify-content: space-between; align-items: center;">
            <span>Consultas a fuentes de datos:</span>
            <span>
              ${data.consultas_fuentes}
              ${anterior ? renderVariacion(data.consultas_fuentes, anterior.consultas_fuentes) : ""}
            </span>
        </p>
        <p style="color:#ccc; display: flex; justify-content: space-between; align-items: center;">
            <span>Otras interacciones:</span>
            <span>
              ${data.otras}
              ${anterior ? renderVariacion(data.otras, anterior.otras) : ""}
            </span>
        </p>
        </div>
      </div>
    `;
    const tarjetaGraficoTorta = `
      <div class="graph-card">
            <div style="padding: 20px 24px 16px; border-bottom: 1px solid #3c3c3c; display: flex; justify-content: space-between; align-items: flex-start;">
                  <div style="flex: 1;">
                  <h3 class="graph-title" style="margin: 0 0 4px; font-size: 18px; font-weight: 600; color: #6b7280; display: flex; align-items: center; gap: 8px;">
                  <img src="public/message-square-more.svg" width="14" height="14" alt="Icono"> 
                  Distribución de interacciones
                  </h3>
                  </div>
                  <div class="drag-handle" title="Arrastrar para cambiar de lugar">
                  <img src="public/grip.svg" width="20" height="20" />
                  </div>
            </div>
            <div style="padding: 20px;">
                  <div id="grafico-torta" style="width: 100%; height: 300px;"></div>
            </div>
      </div>
      `;

    const toolsHTML = Object.entries(data.tools || {})
        .map(
            ([tool, count]) => `
      <p style="color:#ccc; display: flex; justify-content: space-between;">
        <span>${tool}</span><span>${count}</span>
      </p>
    `
        )
        .join("");

    const tarjetaTools = `
      <div class="graph-card">
        <div style="padding: 20px 24px 16px; border-bottom: 1px solid #3c3c3c; display: flex; justify-content: space-between; align-items: flex-start;">
          <div style="flex: 1;">
            <h3 class="graph-title" style="margin: 0 0 4px; font-size: 18px; font-weight: 600; color: #6b7280; display: flex; align-items: center; gap: 8px;">
                  <img src="public/pocket-knife.svg" width="14" height="14" alt="Icono"> 
                  Frecuencia uso de Herramientas
            </h3>
          
           </div>
          <div class="drag-handle" title="Arrastrar para cambiar de lugar">
            <img src="public/grip.svg" width="20" height="20" />
          </div>
        </div>

        <div style="padding: 20px;">
        <p>El agente utilizó las siguientes herramientas en sus ${data.consultas_fuentes} consultas a fuentes de datos:</p><br>
          ${toolsHTML}
        </div>
      </div>
    `;

    const elementosHTML = Object.entries(data.elementos || {})
        .map(
            ([element, count]) => `
      <p style="color:#ccc; display: flex; justify-content: space-between;">
        <span>${element}</span><span>${count}</span>
      </p>
    `
        )
        .join("");
    const tarjetaElementos = `
            <div class="graph-card">
            <div style="padding: 20px 24px 16px; border-bottom: 1px solid #3c3c3c; display: flex; justify-content: space-between; align-items: flex-start;">
            <div style="flex: 1;">
                 
            <h3 class="graph-title" style="margin: 0 0 4px; font-size: 18px; font-weight: 600; color: #6b7280; display: flex; align-items: center; gap: 8px;">
                  <img src="public/component.svg" width="14" height="14" alt="Icono"> 
                  Frecuencia entrega de elementos
            </h3>
            
            </div>
            <div class="drag-handle" title="Arrastrar para cambiar de lugar">
                  <img src="public/grip.svg" width="20" height="20" />
            </div>
            </div>
            <div style="padding: 20px;">
            ${elementosHTML}
            </div>
            </div>
      `;

    const tarjetaFeedback = `
      <div class="graph-card">
        <div style="padding: 20px 24px 16px; border-bottom: 1px solid #3c3c3c; display: flex; justify-content: space-between; align-items: flex-start;">
          <div style="flex: 1;">
           
            <h3 class="graph-title" style="margin: 0 0 4px; font-size: 18px; font-weight: 600; color: #6b7280; display: flex; align-items: center; gap: 8px;">
                  <img src="public/heart.svg" width="14" height="14" alt="Icono"> 
                  Feedback
            </h3>
          
            </div>
          <div class="drag-handle" title="Arrastrar para cambiar de lugar">
            <img src="public/grip.svg" width="20" height="20" />
          </div>
        </div>
       <div style="padding: 20px;">
        <p class="metrica-grande" style="color:#ccc; display: flex; justify-content: space-between;">
            <span>Feedback Positivo:</span> <span class="verde" >${data.feedback_positivo}</span>
        </p>
        <p class="metrica-grande" style="color:#ccc; display: flex; justify-content: space-between;">
            <span>Feedback Negativos :</span> <span class="rojo">${data.feedback_negativo}</span>
        </p>
        <br>
        
        </div>

      </div>
    `;

    const tarjetaTiempos = `
      <div class="graph-card">
        <div style="padding: 20px 24px 16px; border-bottom: 1px solid #3c3c3c; display: flex; justify-content: space-between; align-items: flex-start;">
          <div style="flex: 1;">
           
            <h3 class="graph-title" style="margin: 0 0 4px; font-size: 18px; font-weight: 600; color: #6b7280; display: flex; align-items: center; gap: 8px;">
                  <img src="public/timer.svg" width="14" height="14" alt="Icono"> 
                  Duración de las conversaciones
            </h3>
          
            </div>
          <div class="drag-handle" title="Arrastrar para cambiar de lugar">
            <img src="public/grip.svg" width="20" height="20" />
          </div>
        </div>
       <div style="padding: 20px;">

        <p  style="color:#ccc; display: flex; justify-content: space-between;">
            <span>Duración total del periodo:</span> <span class="" >${data.tiempo_total}</span>
        </p>
        <p  style="color:#ccc; display: flex; justify-content: space-between;">
            <span>Duración promedio:</span> <span class="" >${data.duracion_promedio}</span>
        </p>
        <p  style="color:#ccc; display: flex; justify-content: space-between;">
            <span>Mayor duración:</span> <span class="verde">${data.duracion_mas_alta}</span>
        </p>
         <p  style="color:#ccc; display: flex; justify-content: space-between;">
            <span>Menor duración:</span> <span class="rojo">${data.duracion_mas_baja}</span>
        </p>
        <br>
        
        </div>

      </div>
    `;

    const tarjetaGraficoTemporal = `
      <div class="graph-card graph-item-3">
            <div style="padding: 20px 24px 16px; border-bottom: 1px solid #3c3c3c; display: flex; justify-content: space-between; align-items: flex-start;">
                  <div style="flex: 1;">
                  
                  <h3 class="graph-title" style="margin: 0 0 4px; font-size: 18px; font-weight: 600; color: #6b7280; display: flex; align-items: center; gap: 8px;">
                        <img src="public/calendar-days.svg" width="14" height="14" alt="Icono"> 
                        Tendencia diarias de uso
                  </h3>
                  
                  </div>
                  <div class="drag-handle" title="Arrastrar para cambiar de lugar">
                  <img src="public/grip.svg" width="20" height="20" />
                  </div>
            </div>
            <div style="padding: 20px;">
                  <div id="grafico-temporal" style="width: 100%; height: 300px;"></div>
            </div>
      </div>
      `;

    const tarjetaAnalisis = `
      <div class="graph-card graph-item-3">
            <div style="padding: 20px 24px 16px; border-bottom: 1px solid #3c3c3c; display: flex; justify-content: space-between; align-items: flex-start;">
                  <div style="flex: 1;">
                  
                  <h3 class="graph-title" style="margin: 0 0 4px; font-size: 18px; font-weight: 600; color: #6b7280; display: flex; align-items: center; gap: 8px;">
                        <img src="public/bot.svg" width="14" height="14" alt="Icono"> 
                        Análisis IA
                  </h3>
                  
                  </div>
                   <div onclick="analisis()" class="" title="Crear análisis" style="cursor: pointer; margin-right:10px" >
                        <img src="public/settings.svg" width="20" height="20" />
                  </div>
                  
                  <div  class="drag-handle" title="Arrastrar para cambiar de lugar">
                        <img src="public/grip.svg" width="20" height="20" />
                  </div>
            </div>
            <div style="padding: 20px;">
                  <div id="analisis_ia" style="padding: 10px;">
                  
                  <h2>Análisis de Interacciones y Conversaciones con el Asistente AI - Chat Comercial/Operativo</h2>

                  <h3>1. Tenor y Preguntas Más Frecuentes</h3>
                  <ul>
                  <li><b>Consultas sobre ventas y productos:</b> Las preguntas más repetidas giran en torno a ventas por periodo, productos más vendidos, ranking de vendedores, mix de productos por unidad de medida, y evolución de ventas de categorías como fitosanitarios, semillas y fertilizantes.</li>   
                  <li><b>Consultas técnicas y regulatorias:</b> Hay reiteradas solicitudes de fichas técnicas SAG, ingredientes activos, productos para plagas específicas (ej. mosquita blanca, benomilo), y cumplimiento normativo.</li>
                  <li><b>Análisis de clientes y vendedores:</b> Se repiten preguntas sobre segmentación de clientes por volumen de compra, productos preferidos por cliente, top vendedores por sucursal y participación de mercado.</li>
                  <li><b>Solicitudes de visualización:</b> Es frecuente la petición de gráficos de torta, barras, líneas, burbujas y gauges para visualizar KPIs 
                  comerciales, evolución de ventas y comparaciones contra presupuesto.</li>
                  </ul>
                  <p><b>Ejemplos de preguntas frecuentes:</b> “¿Cuáles son los 3 mejores vendedores?”, “¿Qué productos existen para la mosquita blanca?”, “Hazme un gráfico de evolución de ventas mensuales de fitosanitarios”, “¿Cuántos litros de BIOAMINO-L se vendieron en San Felipe en 2024?”, “¿Quién es el 
                  mejor vendedor de San Felipe para productos Bayer?”.</p>

                  <h3>2. Tipos de Análisis Solicitados y Objetivos de Información</h3>
                  <ul>
                  <li><b>Análisis comerciales:</b> Evolución de ventas por producto, categoría, sucursal o vendedor; ranking de productos/clientes/vendedores; comparativos año contra año; análisis de mix por unidad de medida; participación de vendedores en ventas totales.</li>
                  <li><b>Análisis técnicos y normativos:</b> Consulta de fichas técnicas, ingredientes activos, productos autorizados por SAG, uso de plaguicidas/fertilizantes, cumplimiento de normativas.</li>
                  <li><b>Soporte a la gestión y toma de decisiones:</b> Visualización de KPIs, avance contra presupuesto, identificación de productos de nicho vs. masivos, segmentación de clientes y oportunidades de venta cruzada.</li>
                  <li><b>Visualización y exploración de datos:</b> Solicitud de ejemplos de gráficos avanzados (burbujas, scatter, gauge, mapas), pruebas de colores y formatos para dashboards y reportes ejecutivos.</li>
                  <li><b>Soporte operativo:</b> Estado de pedidos, consultas de facturas, búsqueda de clientes y productos específicos por SKU o razón social.</li>
                  </ul>

                  <h3>3. Análisis General de Sentimiento</h3>
                  <ul>
                  <li><b>Sentimiento global:</b> Predominantemente positivo y constructivo. El usuario explora capacidades, desafía el sistema y agradece respuestas útiles (“Muy buen dato!”, “Muy bien!!”, “Excelente”, “super”, “Perfecto!”).</li>
                  <li><b>Feedback negativo:</b> Ocasionalmente hay comentarios críticos cuando la respuesta es incompleta o no cumple la expectativa (“Le pregunté por uno me entregó 3”, “No se pudo procesar la solicitud”, “Lo siento, ha ocurrido un error…”). Sin embargo, estos son escasos y suelen acompañarse de nueva instrucción o reintento.</li>
                  <li><b>Actitud colaborativa:</b> El usuario frecuentemente da feedback constructivo, pide “intenta nuevamente”, explica el objetivo de la consulta y sugiere mejoras (“hazlo por año”, “muéstrame solo el top 5 y el resto como ‘Resto’”).</li>
                  </ul>

                  <h3>4. Conteo y Calificación de Conversaciones</h3>
                  <table>
                  <thead>
                  <tr>
                        <th>Calificación</th>
                        <th>Ejemplo / Justificación</th>
                        <th>Cantidad (aprox.)</th>
                  </tr>
                  </thead>
                  <tbody>
                  <tr>
                        <td><b>Perfecta</b></td>
                        <td>Respuestas rápidas, precisas, con ejecución y visualización de consultas (ej. ranking vendedores, gráficos por categoría, fichas técnicas SAG, segmentación clientes).</td>
                        <td>~60%</td>
                  </tr>
                  <tr>
                        <td><b>Aceptable</b></td>
                        <td>Respuestas correctas pero con algún paso intermedio erróneo, consulta SQL inicial sin resultado pero corregida en el siguiente intento, o consultas sin registros (ej. “No se encontraron ventas para NPK 12-3-37 en San Felipe”).</td>
                        <td>~20%</td>
                  </tr>
                  <tr>
                        <td><b>Necesita mejorar</b></td>
                        <td>Respuestas incompletas, errores temporales de sistema, respuestas en blanco o con error técnico, pero con reintentos exitosos posteriores.</td>
                        <td>~15%</td>
                  </tr>
                  <tr>
                        <td><b>Fallida</b></td>
                        <td>Errores sistemáticos, respuestas incoherentes o sin ejecución de consulta, caídas de sistema, respuestas en inglés aisladas (“This message has a Dataframe”).</td>
                        <td>~5%</td>
                  </tr>
                  </tbody>
                  </table>
                  <p><b>Nota:</b> La gran mayoría de las conversaciones tienen resolución exitosa, aunque en algunos casos requieren reiteración o ajuste de la consulta.</p>

                  <h3>5. Observaciones, Insights y Recomendaciones</h3>
                  <ul>
                  <li><b>Alta interacción exploratoria:</b> El usuario utiliza el sistema para pruebas, exploración de tipos de gráficos y validación de capacidades, lo que evidencia confianza y curiosidad en las funcionalidades del asistente.</li>
                  <li><b>Valor en la visualización:</b> Los gráficos (torta, barras, líneas, burbujas, gauge) son altamente valorados y solicitados, especialmente para comparaciones interanuales, seguimiento de KPIs y análisis de mix de ventas.</li>
                  <li><b>Soporte técnico y comercial:</b> El asistente cumple un rol dual: entrega soporte técnico (fichas, ingredientes, normativas) y comercial (ventas, clientes, vendedores, KPIs), lo que enriquece la experiencia del usuario.</li>
                  <li><b>Oportunidad de mejora:</b> Mejorar la robustez frente a consultas sin resultados, manejo de errores técnicos y mensajes de retroalimentación más claros cuando una consulta no puede ejecutarse.</li>
                  <li><b>Potencial para dashboards ejecutivos:</b> El usuario explora activamente ejemplos de indicadores visuales (gauge) y gráficos avanzados, 
                  lo que sugiere que la integración de dashboards ejecutivos sería de alto valor para la toma de decisiones.</li>
                  <li><b>Feedback como motor de mejora:</b> El usuario entrega feedback explícito en el chat, lo que permite ajustar respuestas y mejorar la experiencia iterativamente.</li>
                  </ul>

                  <h3>Conclusión</h3>
                  <p>
                  El análisis de las conversaciones muestra un uso intensivo y avanzado del asistente AI para consultas comerciales, técnicas y de visualización. El sistema responde satisfactoriamente en la mayoría de los casos, con alto grado de precisión y utilidad para el usuario. La experiencia es positiva, con oportunidades puntuales de mejora en robustez y manejo de errores. El nivel de interacción y la diversidad de consultas evidencian que el asistente es una herramienta clave para la gestión comercial, operativa y técnica, y que la visualización de indicadores y datos es altamente valorada por los usuarios.

                                    
                  </div>
            </div>
      </div>
      `;

    const mesReporte = getMesTexto(data.fecha_inicio);
    const fechaCreacion = formatoCorto(data.fecha_reporte);
    const tarjetaInicial = `
       <div class="graph-card graph-item-3">
            <div style="padding: 20px 24px 16px; border-bottom: 1px solid #3c3c3c; display: flex; justify-content: space-between; align-items: flex-start;">
                  <div style="flex: 1;">
                  
                  <h3 class="graph-title" style="margin: 0 0 4px; font-size: 18px; font-weight: 600; color: #6b7280; display: flex; align-items: center; gap: 8px;">
                        <img src="public/calendar-days.svg" width="14" height="14" alt="Icono"> 
                        Reporte QAgent
                  </h3>
                  
                  </div>
                  <div class="drag-handle" title="Arrastrar para cambiar de lugar">
                  <img src="public/grip.svg" width="20" height="20" />
                  </div>
            </div>
            <div style="padding: 20px;">
                 <p>Mes del reporte:</b> ${mesReporte}</p>
                 <span style="color:#6b7280; font-size: 0.96em;">Creado el ${fechaCreacion}</span>
            </div>
           
            <div id="kpi-ticker" class="kpi-ticker-band">
                  <div class="kpi-ticker-track" id="kpi-ticker-track">
                      
                  </div>
            </div>
            
      </div>
      `;

    container.innerHTML = `
      <div class="graph-grid" id="graph-grid">
            ${tarjetaInicial}
            ${tarjetaMetricas}
            ${tarjetaGraficoTorta}
            ${tarjetaTools}
            ${tarjetaElementos}
            ${tarjetaFeedback}
            ${tarjetaTiempos}
            ${tarjetaGraficoTemporal}
            ${tarjetaAnalisis}        
      </div>
    `;

    cargarTickerKPI();

    Plotly.newPlot(
        "grafico-torta",
        [
            {
                type: "pie",
                hole: 0.4,
                values: [data.consultas_usuario, data.respuestas_asistente, data.consultas_fuentes, data.otras],
                labels: ["Consultas Usuario", "Respuestas Asistente.", "Consulta a datos", "Otras"],
                textinfo: "percent",
                hoverinfo: "label+percent",
                textinfo: "percent",
                showlegend: true,
                textposition: "inside",
                marker: {
                    colors: ["#1d7088", "#3d9970", "#ccc", "#ff4136"],
                },
                grid: { rows: 1, columns: 1 },
            },
        ],
        {
            height: 300,
            margin: { t: 0, b: 0, l: 0, r: 0 },
            showlegend: false,
        },
        { locale: "es" }
    );
    renderTimeSeries(data, anterior);
};

const handleMetricsReport = async () => {
    const { value: formValues } = await Swal.fire({
        title: "Generar reporte",
        html: `
          <div style="display: flex; flex-direction: column; gap: 12px;">
        
        <div style="display: flex; flex-direction: column; gap: 4px;">
          Fecha de inicio
          <input id="fecha-inicio" type="date" class="swal2-input" style="background: #111; color: #fff; border: 1px solid #333;">
        </div>
        
        <div style="display: flex; flex-direction: column; gap: 4px;">
          Fecha de fin
          <input id="fecha-fin" type="date" class="swal2-input" style="background: #111; color: #fff; border: 1px solid #333;">
        </div>
      </div>
    `,
        focusConfirm: false,
        confirmButtonText: "Generar",
        cancelButtonText: "Cancelar",
        showCancelButton: true,
        background: "#1f1f1f",
        color: "#e0e0e0",
        preConfirm: () => {
            const startDate = document.getElementById("fecha-inicio").value;
            const endDate = document.getElementById("fecha-fin").value;
            if (!startDate || !endDate) {
                Swal.showValidationMessage("Debes seleccionar ambas fechas.");
                return;
            }
            return { startDate, endDate };
        },
    });

    if (!formValues) return;

    try {
        Swal.fire({
            title: "Generando reporte...",
            html: `<div style="display:flex; justify-content:center; align-items:center; flex-direction:column;">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="none"
            viewBox="0 0 24 24" stroke="#60a5fa" stroke-width="2"
            class="lucide lucide-loader-circle animate-spin">
            <path d="M12 2a10 10 0 1 1-7.75 3.75" />
        </svg>
        <p style="margin-top: 12px; color: #ccc;">Procesando datos...</p>
      </div>`,
            background: "#1f1f1f",
            color: "#e0e0e0",
            showConfirmButton: false,
            allowOutsideClick: false,
            allowEscapeKey: false,
        });

        const response = await fetch("/api/metrics_summary", {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json", Accept: "application/json" },
            body: JSON.stringify({
                fecha_inicio: formValues.startDate,
                fecha_fin: formValues.endDate,
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = "/login";
                return;
            }
            showErrorNew("Error: " + (data.error || "Error desconocido"));
            return;
        }

        // Mostrar los gráficos con los datos
        console.log("📊 Datos recibidos:", data);
        renderGraphsInOrder(data);

        Swal.close(); // Cerrar el loader
    } catch (error) {
        console.error("💥 Error:", error);
        showErrorNew("Error: " + error.message);
    }
};

async function analisis() {
    console.log("🔄 Cargando reporte...");
    let startDate = "2025-06-01";
    let endDate = "2025-06-30";

    const response = await fetch("/api/analisis", {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
        },
        body: JSON.stringify({ fecha_inicio: startDate, fecha_fin: endDate }),
    });

    if (!response.ok) {
        console.error("Error al obtener análisis:", response.statusText);
        return;
    }

    const data = await response.json();
    const container = document.getElementById("analisis_ia");

    // Suponiendo que data.texto trae HTML o texto plano
    container.innerHTML = data.texto;
    console.log("👌 Reporte Cargado...");
}

function renderTimeSeries(data, anterior = null) {
    // Serie principal (último reporte)
    const traceActual = {
        type: "scatter",
        mode: "lines+markers",
        name: "Mes actual",
        x: data.time_series_dates,
        y: data.time_series_conversaciones,
        line: { color: "#1f77b4", width: 3 },
        marker: { color: "#1f77b4" },
    };

    // Serie anterior (si existe)
    let traces = [traceActual];
    if (anterior && anterior.time_series_dates && anterior.time_series_conversaciones) {
        traces.push({
            type: "scatter",
            mode: "lines+markers",
            name: "Mes anterior",
            x: anterior.time_series_dates,
            y: anterior.time_series_conversaciones,
            line: { color: "#f23636", dash: "dash", width: 2 },
            marker: { color: "#f23636", symbol: "circle-open" },
        });
    }

    Plotly.newPlot(
        "grafico-temporal",
        traces,
        {
            title: { text: "Conversaciones únicas por día", font: { size: 16 } },
            xaxis: { title: "Fecha", type: "date", tickformat: "%Y-%m-%d" },
            yaxis: { title: "Número de conversaciones", rangemode: "tozero" },
            margin: { t: 30, b: 40 },
            legend: { orientation: "h", x: 0.1, y: 1.15 },
            hovermode: "x unified",
        },
        { locale: "es", responsive: true }
    );
}

function getMesTexto(fecha) {
    // Recibe un string "2025-06-01"
    const meses = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
    ];
    const d = new Date(fecha);
    const mes = meses[d.getMonth()];
    const anio = d.getFullYear();
    return `${mes.charAt(0).toUpperCase() + mes.slice(1)} ${anio}`;
}

function formatoCorto(fechaStr) {
    const d = new Date(fechaStr);
    const dia = String(d.getDate()).padStart(2, "0");
    const mes = String(d.getMonth() + 1).padStart(2, "0");
    const anio = d.getFullYear();
    return `${dia}-${mes}-${anio}`;
}

async function cargarTickerKPI() {
    try {
        const kpiData = await fetch("/api/metrics_today", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({}), // <-- ¡esto lo arregla!
        }).then((r) => r.json());

        console.log("kpiData", kpiData);

        // Usa renderVariacion si quieres flechas SVG:
        const kpis = [
            `Hoy ${kpiData.hoy}`,
            `Conversaciones Hoy: ${kpiData.conversaciones_hoy} ${renderVariacionTiker(
                kpiData.conversaciones_hoy,
                kpiData.conversaciones_ayer
            )}`,
            `Acumulado: ${kpiData.conversaciones_mes} ${renderVariacionTiker(
                kpiData.conversaciones_mes,
                kpiData.conversaciones_mes_ayer
            )}`,
            `Interacciones Hoy: ${kpiData.interacciones_hoy} ${renderVariacionTiker(
                kpiData.interacciones_hoy,
                kpiData.interacciones_ayer
            )}`,
            `Acumulado: ${kpiData.interacciones_mes} ${renderVariacionTiker(
                kpiData.interacciones_mes,
                kpiData.interacciones_mes_ayer
            )}`,
        ];

        // Arma los spans
        document.getElementById("kpi-ticker-track").innerHTML = kpis
            .map((k, i) => `<span class="kpi-item">${k}</span>`)
            .join("");
    } catch (err) {
        document.getElementById("kpi-ticker-track").innerHTML = `<span class="kpi-item">Error cargando KPIs</span>`;
        console.error("Error cargando KPIs:", err);
    }
}

/*
  <!-- Aquí van los KPIs en span, por JS o directo para prueba -->
  <span class="kpi-item">Hoy 19-06-2025</span>
  <span class="kpi-item verde">Conversaciones Hoy: 35 <span class="pct verde">+3% ↑</span></span>
  <span class="kpi-item azul">Acumulado: 89 <span class="pct verde">+2% ↑</span></span>
  <span class="kpi-item">Interacciones Hoy: 5 <span class="pct rojo">-1% ↓</span></span>
  <span class="kpi-item azul">Acumulado: 56 <span class="pct verde">+2% ↑</span></span>
  <span class="kpi-item gris">Errores: 0</span>
  */

document.addEventListener("DOMContentLoaded", () => {
    renderGraphsNew();
});
