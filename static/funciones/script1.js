//*************************función para ocultar y mostrar los input type radio*****************************************//
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
    var numeros_individuales = document.getElementsByClassName('input numero');
    var numeros_generales = document.getElementById("div_numero_general");

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

    if (clickedRadio.checked){
        if (clickedRadio.value === 'True'){
            numeros_generales.style.display = "block";
            // Recorrer todos los elementos 'input numero' y ocultarlos
            for (var i = 0; i < numeros_individuales.length; i++) {
                numeros_individuales[i].style.display = "none";
            }
    } else if (clickedRadio.value === 'False'){
        numeros_generales.style.display = "none";
        // Recorrer todos los elementos 'input numero' y mostrarlos
        for (var i = 0; i < numeros_individuales.length; i++) {
            numeros_individuales[i].style.display = "block";
        }
    }}
}
//************************************************** Fin de la función *************************************************//

function ocultarYLimpiar(section) {
    // Limpiar los valores de los inputs dentro de la sección
    var inputs = section.getElementsByTagName("input");
    for (var i = 0; i < inputs.length; i++) {
        // Limpiar el valor de cada input
        inputs[i].value = ""; 
    }
}
//************************************************** Fin de la función *************************************************//

// Función para desmarcar checkboxes en la sección de individuales
function desmarcarCheckboxes() {
    var checkboxes = document.querySelectorAll('#individuales input[type="checkbox"]');
    for (var i = 0; i < checkboxes.length; i++) {
        checkboxes[i].checked = false; // Desmarcar cada checkbox
    }
}
//************************************************** Fin de la función *************************************************//


// Función para guardar el nombre del documento
function generar() {

    const archivo = document.querySelector('input[name="nombre_documento"]').value;

    // Verifica que el valor no esté vacío antes de almacenarlo
    if (archivo) {
        localStorage.setItem('nombre_documento', archivo);
        console.log('Archivo guardado en localStorage:', archivo); // Log para depurar
    } else {
        console.log('El archivo está vacío o no se pudo obtener.');
    }
}
//************************************************** Fin de la función *************************************************//


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
//************************************************** Fin de la función *************************************************//

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
//************************************************** Fin de la función *************************************************//

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
//************************************************** Fin de la función *************************************************//

function toggleNumero() {
    // Get the specific checkbox and div by their IDs
    const checkbox = document.getElementById('checkbox-set3');
    const numeroDiv = document.getElementById('numero-set3');
    
    // Toggle the display of the 'numero' div based on the checkbox status
    numeroDiv.style.display = checkbox.checked ? 'block' : 'none';
}
//************************************************** Fin de la función *************************************************//

document.addEventListener('keydown', function(event) {
    const url = window.location.pathname;

    // Si el mensaje de error está visible y se presiona Enter
    if (event.key === 'Enter' && document.getElementById('mensaje').style.display === 'block') {
        event.preventDefault(); // Prevenir el comportamiento predeterminado
        document.querySelector('.volver').click(); // Simula clic en "Volver"
        return; // Salir para evitar otros manejos de "Enter"
    }

    // Si estamos en la página "/texto" y se presiona Enter
    if (event.key === 'Enter' && url === "/texto") {
        event.preventDefault(); // Prevenir submit
        document.querySelector('.button_nuevo_script').click(); // Simula clic en "Nuevo Script"
        return;
    }

    // Si estamos en alguna de las páginas de script y se presiona Enter
    if (event.key === 'Enter' && (url === "/script_alta" || url === "/script_baja" || url === "/script_altaybaja")) {
        event.preventDefault(); // Prevenir el comportamiento predeterminado

        // Ejecutar handleSubmit, que contiene la lógica de generación y redirección
        handleSubmit(event);
        return;
    }

    // Si estamos en otro contexto, controlar la validación antes de redirigir
    if (event.key === 'Enter' && url === "/") {
        event.preventDefault(); // Prevenir submit por Enter
        continuar(); // Redirige o realiza la acción
    }
});
//************************************************** Fin de la función *************************************************//

//***************************** Función para manejar el submit y redirección con retraso *******************************//
function handleSubmit(event) {
    event.preventDefault(); // Evitar el envío del formulario predeterminado
    document.getElementById('altaForm').submit(); // Enviar el formulario

    // Muestra el GIF de carga y la sombra
    document.getElementById('loading').style.display = 'block';
    document.getElementById('shadow').style.display = 'block';

    generar();

    // Esperar 2.5 segundos antes de redirigir a "texto.html"
    setTimeout(function() {
        // Redirige a la página de texto
        window.location.href = "/texto";  

        // Ocultar el GIF de carga y la sombra después de la redirección
        document.getElementById('loading').style.display = 'none';
        document.getElementById('shadow').style.display = 'none';
    }, 2500); // Espera 2.5 segundos
}
//************************************************** Fin de la función *************************************************//





function descargarExcel(url, nombreArchivo) {
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al descargar el archivo');
            }
            return response.blob();
        })
        .then(blob => {
            // Crear un enlace para descargar el archivo
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = nombreArchivo || 'extensiones_teams.xlsx';
            link.click();
        })
        .catch(error => console.error('Error:', error));
}

// Usar la función
const urlDelArchivo = 'C:\Users\Soporte\Documents\carpeta de prueba\Sandbox Teams\extensiones_teams.xlsx'; // URL del archivo Excel
const nombreArchivo = 'extensiones_teams.xlsx'; // Nombre con el que quieres guardar el archivo

descargarExcel(urlDelArchivo, nombreArchivo);



