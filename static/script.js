/*
SmartPlannerX - Script Principal

Equipo 3:
- Cristian E. Sánchez R. (25-0688)
- Hansel Augusto Pérez (25-0461)
- Lia De Oleo (25-0673)
- Juan José Cruz Romero (25-0888)
- Samir Gonzalez (25-0808)
- Alejandro Bruno (25-0947)
- Daniel Osvaldo Lopez (25-0655)
*/

let currentSolutionIndex = 0;
let solutionsCache = [];

document.addEventListener("DOMContentLoaded", () => {
  console.log("SmartSchedule JS Loaded - v2.0 (Multi-Materia)");
  loadMaterias();

  // --- CHAT LOGIC ---
  const chatInput = document.getElementById("chat-input");
  const chatSend = document.getElementById("chat-send");
  const chatBox = document.getElementById("chat-box");

  function addMessage(text, isUser) {
    const div = document.createElement("div");
    div.className = `chat-msg ${isUser ? "user" : "bot"}`;
    div.textContent = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  async function sendChat() {
    const text = chatInput.value.trim();
    if (!text) return;

    addMessage(text, true);
    chatInput.value = "";

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensaje: text }),
      });
      const data = await response.json();

      if (data.success) {
        addMessage(data.message, false);
        loadMaterias(); // Refresh list
      } else {
        addMessage(data.message || "No entendí eso.", false);
      }
    } catch (e) {
      addMessage("Error de conexión.", false);
    }
  }

  chatSend.addEventListener("click", sendChat);
  chatInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendChat();
  });



  // --- MANUAL ADD LOGIC ---
  document.getElementById("add-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    // (Same logic as before)
    const materia = document.getElementById("materia").value;
    const seccion = document.getElementById("seccion").value;
    const inicio = document.getElementById("inicio").value;
    const fin = document.getElementById("fin").value;
    const dias = Array.from(
      document.querySelectorAll('input[type="checkbox"]:checked')
    ).map((cb) => cb.value);

    if (dias.length === 0) {
      Swal.fire("Error", "Selecciona un día", "error");
      return;
    }

    const data = { materia, seccion, dias, inicio, fin };
    await fetch("/api/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    loadMaterias();
    document.getElementById("materia").value = "";
    document.getElementById("seccion").value = "";
  });

  // --- GENERATE LOGIC ---

    document.getElementById("generate-btn").addEventListener("click", generateSchedule);

    // ... (rest of the file)



  // Add navigation controls if not exists
  const resultsSection = document.querySelector(".results-section");
  if (!document.getElementById("sol-nav")) {
    const nav = document.createElement("div");
    nav.id = "sol-nav";
    nav.className = "nav-controls";
    nav.innerHTML = `
            <button class="nav-btn" id="prev-sol"><i class="fas fa-chevron-left"></i> Anterior</button>
            <span id="sol-counter">Opción 1</span>
            <button class="nav-btn" id="next-sol">Siguiente <i class="fas fa-chevron-right"></i></button>
        `;
    resultsSection.insertBefore(
      nav,
      document.getElementById("horarios-container")
    );

    document.getElementById("prev-sol").addEventListener("click", () => {
      if (currentSolutionIndex > 0) {
        currentSolutionIndex--;
        renderCalendar(solutionsCache[currentSolutionIndex]);
      }
    });
    document.getElementById("next-sol").addEventListener("click", () => {
      if (currentSolutionIndex < solutionsCache.length - 1) {
        currentSolutionIndex++;
        renderCalendar(solutionsCache[currentSolutionIndex]);
      }
    });
  }
});

async function loadMaterias() {
    const response = await fetch('/api/list');
    const materias = await response.json();
    const list = document.getElementById('lista-items');
    list.innerHTML = '';
    
    materias.forEach(m => {
        const li = document.createElement('li');
        li.className = 'materia-item-container';
        
        // Header de la materia
        const header = document.createElement('div');
        header.className = 'materia-header';
        header.innerHTML = `
            <span><strong>${m.nombre}</strong> <small>(${m.secciones.length} secciones)</small></span>
            <button class="btn-delete" onclick="deleteMateria('${m.nombre}')"><i class="fas fa-trash"></i></button>
        `;
        li.appendChild(header);

        // Lista de secciones
        const ulSec = document.createElement('ul');
        ulSec.className = 'secciones-list';
        
        m.secciones.forEach(s => {
            const liSec = document.createElement('li');
            liSec.className = 'seccion-item';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = s.enabled;
            checkbox.onchange = () => toggleSection(m.nombre, s.uuid, checkbox.checked);
            
            const label = document.createElement('label');
            label.textContent = ` Sec ${s.id} - ${s.dias.join(', ')} (${formatTime(s.inicio)} - ${formatTime(s.fin)})`;
            label.prepend(checkbox);
            
            const btnDelSec = document.createElement('button');
            btnDelSec.className = 'btn-delete-sec';
            btnDelSec.innerHTML = '<i class="fas fa-times"></i>';
            btnDelSec.onclick = () => deleteSection(m.nombre, s.uuid);

            liSec.appendChild(label);
            liSec.appendChild(btnDelSec);
            ulSec.appendChild(liSec);
        });
        
        li.appendChild(ulSec);
        list.appendChild(li);
    });
}

async function toggleSection(materia, uuid, enabled) {
    await fetch('/api/toggle_section', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ materia, uuid: uuid, enabled })
    });
}

async function deleteSection(materia, uuid) {
    const result = await Swal.fire({
        title: '¿Eliminar sección?',
        text: "No podrás revertir esto",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ef4444',
        cancelButtonColor: '#3b82f6',
        confirmButtonText: 'Sí, eliminar'
    });

    if (result.isConfirmed) {
        await fetch('/api/delete_section', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ materia, uuid: uuid })
        });
        await loadMaterias();
        generateSchedule(); // Auto-regenerate
    }
}

function formatTime(h) {
    const hours = Math.floor(h);
    const minutes = Math.round((h - hours) * 60);
    const ampm = hours >= 12 ? 'pm' : 'am';
    let hours12 = hours % 12;
    hours12 = hours12 ? hours12 : 12;
    const minStr = minutes === 0 ? '' : `:${minutes.toString().padStart(2, '0')}`;
    return `${hours12}${minStr}${ampm}`;
}

async function deleteMateria(nombre) {
  await fetch("/api/delete", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ materia: nombre }),
  });
  await loadMaterias();
  generateSchedule(); // Auto-regenerate
}

async function generateSchedule() {
    const response = await fetch("/api/generate");
    const data = await response.json();
    document.getElementById("stats-teoricas").textContent = data.teoricas;
    document.getElementById("stats-validas").textContent = data.validas;

    solutionsCache = data.soluciones;
    currentSolutionIndex = 0;

    if (data.validas === 0) {
    Swal.fire("Sin Resultados", "Conflictos detectados.", "warning");
    document.getElementById("horarios-container").innerHTML =
        '<p class="placeholder-text">No hay horarios válidos.</p>';
    } else {
    renderCalendar(solutionsCache[0]);
    }
}

function renderCalendar(solucion) {
  const container = document.getElementById("horarios-container");
  const counter = document.getElementById("sol-counter");
  if (counter)
    counter.textContent = `Opción ${currentSolutionIndex + 1} de ${
      solutionsCache.length
    }`;

  container.innerHTML = "";



  // Events
  const dayMap = {
    Lunes: 2,
    Martes: 3,
    Miercoles: 4,
    Jueves: 5,
    Viernes: 6,
    Sabado: 7,
  };
  const colors = [
    "#3b82f6",
    "#10b981",
    "#8b5cf6",
    "#f59e0b",
    "#ef4444",
    "#ec4899",
  ];

  try {
    if (!solucion || !Array.isArray(solucion)) {
      console.error("Solución inválida:", solucion);
      Swal.fire("Error Interno", "Datos de solución inválidos", "error");
      return;
    }

    // Crear Tabla
    const table = document.createElement("table");
    table.className = "schedule-table";

    // Header
    const thead = document.createElement("thead");
    thead.innerHTML = `
            <tr>
                <th>Materia</th>
                <th>Sección</th>
                <th>Lunes</th>
                <th>Martes</th>
                <th>Miércoles</th>
                <th>Jueves</th>
                <th>Viernes</th>
                <th>Sábado</th>
            </tr>
        `;
    table.appendChild(thead);

    // Body
    const tbody = document.createElement("tbody");

    solucion.forEach((clase) => {
      const tr = document.createElement("tr");

      // Datos básicos
      tr.innerHTML = `
                <td class="fw-bold">${clase.materia}</td>
                <td>${clase.seccion}</td>
            `;

      // Días
      const diasSemana = [
        "Lunes",
        "Martes",
        "Miercoles",
        "Jueves",
        "Viernes",
        "Sabado",
      ];

      diasSemana.forEach((diaNombre) => {
        const td = document.createElement("td");
        // Verificar si esta clase se da en este día
        // La API devuelve 'dias': ['Lunes', 'Miercoles'] y 'hora': '14:00 - 16:00'
        if (clase.dias.includes(diaNombre)) {
          td.className = "active-day";
          td.innerHTML = `<span class="time-badge">${clase.hora}</span>`;
        }
        tr.appendChild(td);
      });

      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    container.appendChild(table);
  } catch (e) {
    console.error("Error renderizando tabla:", e);
    Swal.fire("Error de Visualización", `Detalle: ${e.message}`, "error");
  }
}


