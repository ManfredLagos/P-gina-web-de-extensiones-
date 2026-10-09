import fitz
import os


def analizar_pdf(ruta_pdf):

    documento = fitz.open(ruta_pdf)

    paginas = len(documento)
    paginas_con_texto = 0
    paginas_con_imagenes = 0

    caracteres_texto = 0
    cantidad_imagenes = 0

    for pagina in documento:

        texto = pagina.get_text("text").strip()

        if texto:
            paginas_con_texto += 1
            caracteres_texto += len(texto)

        imagenes = pagina.get_images(full=True)

        if imagenes:
            paginas_con_imagenes += 1
            cantidad_imagenes += len(imagenes)

    documento.close()

    if paginas_con_texto > 0 and paginas_con_imagenes > 0:
        tipo = "texto_imagenes"

    elif paginas_con_texto > 0:
        tipo = "solo_texto"

    elif paginas_con_imagenes > 0:
        tipo = "solo_imagenes"

    else:
        tipo = "sin_contenido"

    return {
        "tipo": tipo,
        "paginas": paginas,
        "paginas_con_texto": paginas_con_texto,
        "paginas_con_imagenes": paginas_con_imagenes,
        "caracteres_texto": caracteres_texto,
        "cantidad_imagenes": cantidad_imagenes
    }