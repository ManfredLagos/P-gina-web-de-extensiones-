    const messageInput =
        document.getElementById("messageInput");

    const sendButton =
        document.getElementById("sendButton");

    const attachButton =
        document.getElementById("attachButton");

    const fileInput =
        document.getElementById("fileInput");

    const selectedFile =
        document.getElementById("selectedFile");

    const selectedFileName =
        document.getElementById("selectedFileName");

    const removeFile =
        document.getElementById("removeFile");

    const chatMessages =
        document.getElementById("chatMessages");

    const messagesWrapper =
        document.getElementById("messagesWrapper");


    console.log("Elementos encontrados:", {
        messageInput: !!messageInput,
        sendButton: !!sendButton,
        attachButton: !!attachButton,
        fileInput: !!fileInput,
        selectedFile: !!selectedFile,
        chatMessages: !!chatMessages
    });


    let currentFile = null;
    let chatHistory = [];

    try {

        chatHistory =
            JSON.parse(
                localStorage.getItem("chatHistory")
            ) || [];

    } catch (error) {

        console.error(
            "Error leyendo historial:",
            error
        );

        chatHistory = [];
    }

    function loadHistory() {

        messagesWrapper.innerHTML = "";
        chatHistory.forEach(message => {
            createMessage(
                message.role,
                message.text,
                message.fileName || null
            );
        });

        scrollToBottom();
    }

    function saveMessage(
        role,
        text,
        fileName = null
    ) {

        chatHistory.push({
            role: role,
            text: text,
            fileName: fileName,
            date: new Date().toISOString()
        });

        localStorage.setItem(
            "chatHistory",
            JSON.stringify(chatHistory)
        );
    }

    function createMessage(
        role,
        text,
        fileName = null
    ) {

        const message =
            document.createElement("div");

        message.classList.add(
            "message",
            role
        );

        const content =
            document.createElement("div");

        content.classList.add(
            "message-content"
        );

        content.textContent = text;

        if (fileName) {

            const fileElement =
                document.createElement("div");

            fileElement.classList.add(
                "attached-file"
            );

            const icon =
                document.createElement("span");

            icon.classList.add(
                "attached-file-icon"
            );

            icon.textContent = "📄";

            const name =
                document.createElement("span");

            name.textContent = fileName;
            fileElement.appendChild(icon);
            fileElement.appendChild(name);
            content.appendChild(fileElement);
        }

        message.appendChild(content);
        messagesWrapper.appendChild(message);
    }

    function scrollToBottom() {
        setTimeout(() => {
            chatMessages.scrollTop =
                chatMessages.scrollHeight;
        }, 50);
    }

    function resizeTextarea() {
        messageInput.style.height = "auto";
        const maxHeight = 112;
        const newHeight =
            Math.min(
                messageInput.scrollHeight,
                maxHeight
            );

        messageInput.style.height =
            newHeight + "px";

        messageInput.style.overflowY =
            messageInput.scrollHeight > maxHeight
                ? "auto"
                : "hidden";
    }

    messageInput.addEventListener(
        "input",
        resizeTextarea
    );

    messageInput.addEventListener(
        "keydown",
        function(event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {
                event.preventDefault();
                sendMessage();
            }
        }
    );

    attachButton.addEventListener(
        "click",
        function() {
            console.log(
                "Botón de adjuntar presionado"
            );
            fileInput.click();
        }
    );

    fileInput.addEventListener(
        "change",
        function() {

            if (this.files.length === 0) {
                return;
            }
            handleFile(
                this.files[0]
            );
        }
    );

    function handleFile(file) {

        console.log(
            "Archivo seleccionado:",
            file.name
        );

        if (
            file.type !== "application/pdf" &&
            !file.name
                .toLowerCase()
                .endsWith(".pdf")
        ) {
            alert(
                "Solo se permiten documentos PDF."
            );

            return;
        }

        currentFile = file;
        selectedFileName.textContent =
            file.name;
        selectedFile.classList.add(
            "show"
        );
    }

    removeFile.addEventListener(
        "click",
        function() {

            console.log(
                "Archivo eliminado"
            );
            currentFile = null;
            fileInput.value = "";
            selectedFile.classList.remove(
                "show"
            );
        }
    );

    chatMessages.addEventListener(
        "dragover",
        function(event) {
            event.preventDefault();
            chatMessages.classList.add(
                "dragging"
            );
        }
    );


    chatMessages.addEventListener(
        "dragleave",
        function(event) {
            event.preventDefault();
            chatMessages.classList.remove(
                "dragging"
            );
        }
    );


    chatMessages.addEventListener(
        "drop",
        function(event) {

            event.preventDefault();
            chatMessages.classList.remove(
                "dragging"
            );
            const files =
                event.dataTransfer.files;
            if (files.length === 0) {
                return;
            }
            handleFile(
                files[0]
            );
        }
    );

    sendButton.addEventListener(
        "click",
        function() {
            console.log(
                "BOTÓN ENVIAR PRESIONADO"
            );
            sendMessage();
        }
    );

    async function sendMessage() {

        console.log(
            "SEND MESSAGE EJECUTADO"
        );

        const text =
            messageInput.value.trim();

        console.log(
            "Mensaje:",
            text
        );

        console.log(
            "Archivo:",
            currentFile
        );

        if (!text && !currentFile) {

            console.log(
                "No hay mensaje ni archivo."
            );
            return;
        }

        const fileName =
            currentFile
                ? currentFile.name
                : null;

        createMessage(
            "user",
            text || "Analizar documento",
            fileName
        );

        saveMessage(
            "user",
            text || "Analizar documento",
            fileName
        );

        messageInput.value = "";

        resizeTextarea();

        scrollToBottom();

        const typingMessage =
            document.createElement("div");


        typingMessage.classList.add(
            "message",
            "ai"
        );

        typingMessage.innerHTML = `
            <div class="message-content">
                <div class="typing">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;

        messagesWrapper.appendChild(
            typingMessage
        );

        scrollToBottom();

        const formData =
            new FormData();

        formData.append(
            "message",
            text
        );

        if (currentFile) {

            formData.append(
                "file",
                currentFile
            );
        }

        console.log(
            "FormData preparado."
        );

        console.log(
            "Enviando POST a /api/chat..."
        );

        try {
            const inicioTotal = performance.now();

            const response =
                
                await fetch(
                    "/api/chat",
                    {
                        method: "POST",
                        body: formData
                    }
                );

            console.log(
                "Respuesta recibida."
            );

            const finTotal = performance.now();

            const tiempoTotal =
                (finTotal - inicioTotal) / 1000;

            console.log(
                "HTTP Status:",
                response.status
            );

            console.log(
                "Content-Type:",
                response.headers.get(
                    "content-type"
                )
            );

            const responseText =
                await response.text();


            console.log(
                "Respuesta del servidor:"
            );

            console.log(
                responseText
            );

            let data;

            try {

                data =
                    JSON.parse(
                        responseText
                    );

            } catch (jsonError) {

                console.error(
                    "LA RESPUESTA DE FLASK NO ES JSON"
                );


                console.error(
                    "Respuesta recibida:",
                    responseText
                );

                typingMessage.remove();

                createMessage(
                    "ai",
                    "El servidor devolvió una respuesta no válida. Revise la consola de Flask."
                );

                scrollToBottom();

                return;
            }

            if (!response.ok) {

                console.error(
                    "Error HTTP:",
                    response.status
                );


                console.error(
                    "Detalle:",
                    data
                );


                typingMessage.remove();

                createMessage(
                    "ai",
                    "Error del servidor: " +
                    (
                        data.error ||
                        "Error HTTP " +
                        response.status
                    )
                );

                scrollToBottom();

                return;
            }

            if (!data.success) {

                console.error(
                    "La API devolvió success=false:",
                    data
                );

                typingMessage.remove();

                createMessage(
                    "ai",
                    "Error: " +
                    (
                        data.error ||
                        "No fue posible obtener una respuesta."
                    )
                );

                scrollToBottom();

                return;
            }

            typingMessage.remove();

            createMessage(
                "ai",
                data.response
            );

            saveMessage(
                "ai",
                data.response
            );

            console.log(
                "Respuesta IA:",
                data.response
            );

            console.log(
                "Modelo utilizado:",
                data.model
            );

            console.log(
                "Tipo de documento:",
                data.document_type
            );

            console.log(
                "Información PDF:",
                data.document_info
            );

            scrollToBottom();

        } catch (error) {

            console.error(
                "ERROR EN FETCH:"
            );

            console.error(
                error
            );

            typingMessage.remove();

            createMessage(
                "ai",
                "No fue posible comunicarse con el servidor."
            );

            scrollToBottom();

        }

        currentFile = null;

        fileInput.value = "";

        selectedFile.classList.remove(
            "show"
        );
    }

    loadHistory();

    resizeTextarea();

    console.log(
        "ASISTENTE IA INICIALIZADO CORRECTAMENTE"
    );