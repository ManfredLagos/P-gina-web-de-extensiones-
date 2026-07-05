const board = document.getElementById('board');
const form = document.getElementById('noteForm');
let notes = [];

function obtenerSaludo() {
  const h = new Date().getHours();
  if (h < 12) return "Buenos días";
  if (h < 18) return "Buenas tardes";
  return "Buenas noches";
}

function copiarTexto(texto) {
  navigator.clipboard.writeText(texto);
  alert("Texto copiado al portapapeles");
}

function eliminarNota(id) {
  fetch(`/delete_note/${id}`, { method: 'DELETE' })
    .then(() => fetchNotes());
}

function renderNotes() {
    /*board.innerHTML = '';*/
    notes.forEach(note => {

        const saludoTexto = note.saludo ? obtenerSaludo() + ',\n\n' : obtenerSaludo() + ',\n\n';

        const div = document.createElement('div');
        div.className = `note ${note.color}`;
        div.innerHTML = `
        <div class="note-header">
            <h3>${note.title}</h3>
            <img style = "margin-right: 5px;"
                src="${ICON_COPY}"
                alt="Copiar"
                title="Copiar"
                onclick="copiarTexto('${saludoTexto}${note.content}')">
            <img src="${ICON_DELETE}"
                alt="Eliminar"
                title="Eliminar"
                onclick="eliminarNota(${note.id})">
        </div>

        <p class="note-content">
            ${saludoTexto}${note.content}
        </p>

        <div class="note-footer">
            
        </div>
        `;
        board.appendChild(div);
    });
    }


function fetchNotes() {
  fetch('/get_notes')
    .then(res => res.json())
    .then(data => {
      notes = data.notes;
      renderNotes();
    });
}

form.addEventListener('submit', e => {
  e.preventDefault();
  const newNote = {
    title: document.getElementById('title').value,
    content: document.getElementById('content').value,
    color: document.getElementById('color').value,
    saludo: document.getElementById('addSaludo').checked
  };
  fetch('/add_note', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(newNote)
  }).then(() => {
    form.reset();
    fetchNotes();
  });
});

// Inicializar SortableJS para arrastrar
new Sortable(board, {
  animation: 150,
  onEnd: evt => {
    const positions = Array.from(board.children).map((child, index) => ({ id: child.querySelector('img[alt="Eliminar"]').onclick.toString().match(/\d+/)[0], position: index }));
    fetch('/update_positions', {
      method: 'PATCH',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({positions})
    });
  }
});
fetchNotes();