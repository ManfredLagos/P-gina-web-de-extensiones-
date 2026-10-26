const board = document.getElementById('board');
const form = document.getElementById('noteForm');
let notes = [];

function obtenerSaludo() {
  const h = new Date().getHours();
  if (h < 12) return "Buenos días";
  if (h < 18) return "Buenas tardes";
  return "Buenas noches";
}

async function copiarTexto(texto) {
    try {
        await navigator.clipboard.writeText(texto);
    } catch (error) {
        console.error("Error al copiar el texto:", error);
        alert("No se pudo copiar el texto al portapapeles.");
    }
}

function eliminarNota(id) {
    fetch(`/delete_note/${id}`, { method: 'DELETE' })
        .then(response => {
            if (!response.ok) {
                throw new Error('No se pudo eliminar la nota');
            }

            notes = notes.filter(note => note.id !== id);

            renderNotes();
        })
        .catch(error => {
            console.error('Error al eliminar la nota:', error);
        });
}


function renderNotes() {
    // Limpiar únicamente las notas guardadas
    board.querySelectorAll('.note:not(.note-create)').forEach(nota => {
        nota.remove();
    });

    notes.forEach(note => {
        const div = document.createElement('div');
        div.className = `note ${note.color}`;
        div.dataset.id = note.id;

        // Construir el texto según la configuración de la nota
        let textoCopiar = note.content;

        console.log("Nota completa:", note);

        if (Number(note.cuerpo) === 1) {
            const respuesta_inicio =
                `${obtenerSaludo()},\n\n` +
                `Espero se encuentre muy bien.\n\n`;

            const respuesta_fin =
                `\n\nQuedamos a su disposición para cualquier información adicional o consulta que pueda surgir.\n\n` +
                `Saludos cordiales,`;

            textoCopiar = `${respuesta_inicio}${note.content}${respuesta_fin}`;
        }

        // Crear encabezado
        const header = document.createElement('div');
        header.className = 'note-header';

        const titulo = document.createElement('h3');
        titulo.textContent = note.title;

        const imgCopiar = document.createElement('img');
        imgCopiar.src = ICON_COPY;
        imgCopiar.alt = 'Copiar';
        imgCopiar.title = 'Copiar';
        imgCopiar.style.marginRight = '5px';
        imgCopiar.style.cursor = 'pointer';

        imgCopiar.addEventListener('click', () => {
            copiarTexto(textoCopiar);
        });

        const imgEliminar = document.createElement('img');
        imgEliminar.src = ICON_DELETE;
        imgEliminar.alt = 'Eliminar';
        imgEliminar.title = 'Eliminar';
        imgEliminar.style.cursor = 'pointer';

        imgEliminar.addEventListener('click', () => {
            eliminarNota(note.id);
        });

        header.append(titulo, imgCopiar, imgEliminar);

        // Crear contenido de la nota
        const contenido = document.createElement('p');
        contenido.className = 'note-content';
        contenido.textContent = textoCopiar;

        const footer = document.createElement('div');
        footer.className = 'note-footer';

        div.append(header, contenido, footer);
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

  const selectedColor = document.querySelector('.color-picker .selected');

  const newNote = {
    title: document.getElementById('title').value,
    content: document.getElementById('content').value,
    color: selectedColor.dataset.color,
    cuerpo: document.getElementById('respuesta_cuerpo').checked ? 1 : 0
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

new Sortable(board, {
    animation: 150,

    // Permitir arrastrar únicamente las notas guardadas
    draggable: '.note:not(.note-create)',

    onEnd: evt => {
        const positions = Array.from(
            board.querySelectorAll('.note:not(.note-create)')
        ).map((note, index) => ({
            id: Number(note.dataset.id),
            position: index + 1
        }));

        fetch('/update_positions', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ positions })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('No se pudieron actualizar las posiciones');
            }
            return response.json();
        })
        .catch(error => {
            console.error('Error al actualizar posiciones:', error);
        });
    }
});




fetchNotes();