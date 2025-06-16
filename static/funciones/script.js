// funcion para ocultar y mostrar los los input de alta, baja o alta y baja

function mostrarinput(input) {
    // Obtiene los elementos por su ID
    var alta = document.getElementById("alta");
    var baja = document.getElementById("baja");
    var altaybaja = document.getElementById("altaybaja");

    // Oculta todas las secciones
    alta.style.visibility = "hidden";
    baja.style.visibility = "hidden";
    altaybaja.style.visibility = "hidden";

    // Muestra la sección seleccionada
    if (input === 'alta') {
        alta.style.visibility = "visible";
    } else if (input === 'baja') {
        baja.style.visibility = "visible";
    } else if (input === 'altaybaja') {
        altaybaja.style.visibility = "visible";
    }

    // Limpiar los inputs de todas las secciones
    if (input !== 'alta') {
        limpiarInputs(alta);
    }
    if (input !== 'baja') {
        limpiarInputs(baja);
    }
    if (input !== 'altaybaja') {
        limpiarInputs(altaybaja);
    }

}

function limpiarInputs(section) {
    var inputs = section.getElementsByTagName("input");
    for (var i = 0; i < inputs.length; i++) {
        inputs[i].value = ""; // Limpia el valor de cada input
    }
}

//                   fin de la función


//                   función para ocultar y mostrar los input[type="radio"]

// Función para ocultar y mostrar los input[type="radio"]
document.addEventListener('DOMContentLoaded', function() {
    // Seleccionamos todos los checkboxes
    var radios = document.querySelectorAll('input[type="radio"]');

    // Añadimos el evento 'change' a cada checkbox
    radios.forEach(function(radio) {
        radio.addEventListener('change', function() {
            mostrarradio(this); // Pasamos el radio clicado
        });
    });
});

function mostrarradio(clickedRadio) {
    // Selección de las secciones de políticas
    var generales = document.getElementById("generales");
    var individuales = document.getElementById("individuales");
    var dominio = document.getElementById("dominio");

    // Ocultar y limpiar todas las secciones
    ocultarYLimpiar(dominio);

    // Mostrar y ocultar secciones según la opción seleccionada
    if (clickedRadio.checked) {
        if (clickedRadio.value === 'generales') {
            generales.style.display = "block";
            individuales.style.display = "none";
            dominio.style.display = "none";
            desmarcarCheckboxes(); // Llamar a la función para desmarcar checkboxes
        } else if (clickedRadio.value === 'individuales') {
            individuales.style.display = "block";
            dominio.style.display = "none";
            generales.style.display = "none";
        } else if (clickedRadio.value === 'dominio') {
            dominio.style.display = "block";
            generales.style.display = "none";
            individuales.style.display = "none";
            desmarcarCheckboxes(); // Llamar a la función para desmarcar checkboxes
        }
    }
}

function ocultarYLimpiar(section) {
    // Limpiar los valores de los inputs dentro de la sección
    var inputs = section.getElementsByTagName("input");
    for (var i = 0; i < inputs.length; i++) {
        // Limpiar el valor de cada input
        inputs[i].value = ""; 
    }
}

// Función para desmarcar checkboxes en la sección de individuales
function desmarcarCheckboxes() {
    var checkboxes = document.querySelectorAll('#individuales input[type="checkbox"]');
    for (var i = 0; i < checkboxes.length; i++) {
        checkboxes[i].checked = false; // Desmarcar cada checkbox
    }
}


//                              fin de la función


//                              Función para guardar el nombre del documento

function generar() {
    // Obtener el nombre del archivo
    const archivo = document.querySelector('input[name="nombre_documento"]').value;

    // Verifica que el valor no esté vacío antes de almacenarlo
    if (archivo) {
        localStorage.setItem('nombre_documento', archivo);
        console.log('Archivo guardado en localStorage:', archivo); // Log para depurar
    } else {
        console.log('El archivo está vacío o no se pudo obtener.');
    }
}

//                              fin de la función


//                               funcion para copiar el texto 

// Función para determinar el saludo según la hora
function obtenerSaludo() {
    const fecha = new Date();
    const horas = fecha.getHours();

    if (horas >= 0 && horas < 12) {
        return "Buenos días,";
    } else if (horas >= 12 && horas < 18) {
        return "Buenas tardes,";
    } else {
        return "Buenas noches,";
    }
}

function copiarTexto() {

    const texto = document.getElementById("copiar_texto").innerText;

    // Texto formateado a copiar
    var textoCompleto = `${texto}`;

    // Crear un elemento temporal para copiar al portapapeles
    var elementoTemporal = document.createElement('textarea');
    elementoTemporal.value = textoCompleto;
    document.body.appendChild(elementoTemporal);
    elementoTemporal.select();
    document.execCommand('copy');
    document.body.removeChild(elementoTemporal);

    // Confirmación de copiado
    var imagen = document.getElementById("imagen");
    var check = document.getElementById("check");

    imagen.style.visibility = "hidden";
    check.style.visibility = "visible";

    // Después de 3 segundos, volver a la imagen original
    setTimeout(function() {
        // Esconde el check
        check.style.visibility = "hidden";

        // Muestra de nuevo la imagen original
        imagen.style.visibility = "visible"; // Si usas 'display: none' aquí sería 'block'
    }, 3000);
}

    // Redirige a la página 'texto.html' después de la descarga
    function handleSubmit() {
        // Muestra el GIF de carga
        document.getElementById('loading').style.display = 'block';
        document.getElementById('shadow').style.display = 'block';
    
        // Espera 1.5 segundos antes de redirigir y ocultar el GIF
        setTimeout(function() {
            // Redirigir a texto.html
            window.location.href = "/texto";  
    
            // Ocultar el GIF de carga y el shadow después de la redirección
            document.getElementById('loading').style.display = 'none';
            document.getElementById('shadow').style.display = 'none';
        }, 2500);  // Espera 2.5 segundos
    }

//                        fin de la función






function enviarCorreo() {
    const correo = document.getElementById('correo').value;
    const tipo_extension = 'alta'; // Puedes cambiar esto según lo que necesites
    var buscar = document.getElementById("buscar");

    // Enviar los datos con fetch a la ruta /obtener_politicas
    fetch('/script_alta_busqueda', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ correo: correo, tipo_extension: tipo_extension })
    })
    .then(response => response.json())
    .then(data => {
        // Mostrar las políticas recibidas
        document.getElementById('politicas').innerHTML = data.politicas;
    })
    .catch(error => console.error('Error:', error));

    // ocultar la seccion de buscar
    buscar.style.display = "none";
}