import requests


OLLAMA_URL = "http://190.113.81.253:11434/api/generate"


def consultar_ollama(modelo, prompt):

    datos = {
        "model": modelo,
        "prompt": prompt,
        "stream": False
    }

    respuesta = requests.post(
        OLLAMA_URL,
        json=datos,
        timeout=500
    )

    respuesta.raise_for_status()

    resultado = respuesta.json()

    return resultado.get("response", "")