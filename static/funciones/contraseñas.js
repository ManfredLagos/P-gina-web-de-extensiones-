const lengthEl = document.getElementById("length");
const quantityEl = document.getElementById("quantity");

const upperEl = document.getElementById("upper");
const lowerEl = document.getElementById("lower");
const numbersEl = document.getElementById("numbers");
const symbolsEl = document.getElementById("symbols");

const outputEl = document.getElementById("output");
const strengthBar = document.getElementById("strengthBar");
const strengthText = document.getElementById("strengthText");

lengthEl.addEventListener("input", () => {
    document.getElementById("lengthValue").innerText = lengthEl.value;
    checkStrengthConfig();
});

quantityEl.addEventListener("input", () => {
    document.getElementById("quantityValue").innerText = quantityEl.value;
});

[upperEl, lowerEl, numbersEl, symbolsEl].forEach(el => {
    el.addEventListener("change", checkStrengthConfig);
});

function generatePassword() {
    const seccionPass = document.querySelector(".result");
    const length = parseInt(lengthEl.value);
    const quantity = parseInt(quantityEl.value);

    const upper = upperEl.checked;
    const lower = lowerEl.checked;
    const numbers = numbersEl.checked;
    const symbols = symbolsEl.checked;

    let chars = "";

    if (upper) chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    if (lower) chars += "abcdefghijklmnopqrstuvwxyz";
    if (numbers) chars += "0123456789";
    if (symbols) chars += "!@#$%&_";

    if (chars.length === 0) {
        document.getElementById('error_caracteres').style.display = 'block';
        document.getElementById('shadow').style.display = 'block';
        return;
    }

    let results = [];

    for (let q = 0; q < quantity; q++) {
        let password = [];

        if (upper) password.push(randomChar("ABCDEFGHIJKLMNOPQRSTUVWXYZ"));
        if (lower) password.push(randomChar("abcdefghijklmnopqrstuvwxyz"));
        if (numbers) password.push(randomChar("0123456789"));
        if (symbols) password.push(randomChar("!@#$%&*()_+"));

        // Completar el resto
        while (password.length < length) {
            password.push(randomChar(chars));
        }

        // Mezclar
        password = shuffleArray(password);

        results.push(password.join(""));
    }

    agregarDivsPass(results);
}

function reGeneratePassword() {

    const length = parseInt(lengthEl.value);

    let chars = "";
    let password = [];

    if (upperEl.checked) {
        chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        password.push(randomChar("ABCDEFGHIJKLMNOPQRSTUVWXYZ"));
    }

    if (lowerEl.checked) {
        chars += "abcdefghijklmnopqrstuvwxyz";
        password.push(randomChar("abcdefghijklmnopqrstuvwxyz"));
    }

    if (numbersEl.checked) {
        chars += "0123456789";
        password.push(randomChar("0123456789"));
    }

    if (symbolsEl.checked) {
        chars += "!@#$%&*()_+";
        password.push(randomChar("!@#$%&*()_+"));
    }

    if (chars.length === 0) {
        strengthText.innerText = "Seleccione al menos un tipo de carácter";
        strengthBar.style.width = "0%";
        return "";
    }

    while (password.length < length) {
        password.push(randomChar(chars));
    }

    password = shuffleArray(password);

    return password.join("");
}

function checkStrengthConfig() {
    const length = parseInt(lengthEl.value);

    const upper = upperEl.checked;
    const lower = lowerEl.checked;
    const numbers = numbersEl.checked;
    const symbols = symbolsEl.checked;

    let charsetSize = 0;

    if (lower) charsetSize += 15;
    if (upper) charsetSize += 20;
    if (numbers) charsetSize += 10;
    if (symbols) charsetSize += 25;

    let bonus = 0;
    if (length >= 16) bonus = 30;
    else if (length >= 12) bonus = 25;
    else if (length >= 8) bonus = 20;
    else if (length >= 6) bonus = 15;

    charsetSize += bonus;

    if (charsetSize === 0) {
        updateUI(0);
        return;
    }

    let score = charsetSize;

    updateUI(score);
}

function updateUI(score) {
    console.log("Score:", score);

    if (score < 25) {
        strengthBar.style.width = "20%";
        strengthBar.style.background = "#dc2626"; // rojo fuerte
        strengthText.innerText = "Muy débil";
    } 
    else if (score < 50) {
        strengthBar.style.width = "35%";
        strengthBar.style.background = "#f97316"; // naranja
        strengthText.innerText = "Débil";
    } 
    else if (score < 65) {
        strengthBar.style.width = "50%";
        strengthBar.style.background = "#eab308"; // amarillo
        strengthText.innerText = "Media";
    } 
    else if (score < 80) {
        strengthBar.style.width = "70%";
        strengthBar.style.background = "#84cc16"; // verde lima
        strengthText.innerText = "Fuerte";
    } 
    else if (score < 96) {
        strengthBar.style.width = "90%";
        strengthBar.style.background = "#22c55e"; // verde
        strengthText.innerText = "Muy fuerte";
    }
    else {
        strengthBar.style.width = "100%";
        strengthBar.style.background = "#06b6d4"; // azul (nivel máximo)
        strengthText.innerText = "Super fuerte";
    }
}

function randomChar(str) {
    return str[Math.floor(Math.random() * str.length)];
}

function shuffleArray(array) {
    return array.sort(() => Math.random() - 0.5);
}

function regenerarPassword(button){

    const upper = upperEl.checked;
    const lower = lowerEl.checked;
    const numbers = numbersEl.checked;
    const symbols = symbolsEl.checked;

    let chars = "";

    if (upper) chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    if (lower) chars += "abcdefghijklmnopqrstuvwxyz";
    if (numbers) chars += "0123456789";
    if (symbols) chars += "!@#$%&_";

    if (chars.length === 0) {
        document.getElementById('error_caracter').style.display = 'block';
        document.getElementById('shadow').style.display = 'block';
        return;
    }

    const input =
        button.parentElement.querySelector("input");
    input.value = reGeneratePassword();
}

function copy() {

    const copiar = querySelector("img");
    const check = querySelector(".icon-check");

    /*const fila = button.closest(".resultados_contraseñas");
    const input = fila.querySelector("input");

    navigator.clipboard.writeText(input.value);*/

    copiar.style.visibility = "hidden";
    check.style.visibility = "visible";

    setTimeout(() => {
        copiar.style.visibility = "visible";
        check.style.visibility = "hidden";
    }, 1500);
}

function agregarDivsPass(results) {

    const result = document.querySelector(".result");

    result.innerHTML = "";

    for (let i = 0; i < results.length; i++) {
        const div = document.createElement('div');
        div.classList.add('resultados_contraseñas');
        div.innerHTML = `
            <input type="text" id="output${i + 1}" value="${results[i]}" readonly>
            <button class="icon-btn" onclick="copy()"><img class="icon-img" src="/static/imagenes/copiar_blanco.png" alt="Copiar"></button>
            <img class="icon-check" src="/static/imagenes/check_blanco.png" alt="Confirmación">
            <button class="icon-btn" onclick="regenerarPassword(this)"><img class="icon-img" src="/static/imagenes/recargar.png" alt="Actualizar"></button>
        `;
        result.appendChild(div);
    }
}

checkStrengthConfig();

function ocultar_alerta(){
    document.getElementById('error_caracteres').style.display = 'none';
    document.getElementById('shadow').style.display = 'none';
}