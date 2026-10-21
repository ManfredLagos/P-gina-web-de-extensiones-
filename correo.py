import secrets
import smtplib
from email.utils import make_msgid
import mimetypes
import os


from email.message import EmailMessage

logo_cid = make_msgid(domain="callmyway.net")

EMAIL_EMISOR = "connecting.conectandopersonas@gmail.com"
EMAIL_PASSWORD = "tewzfmaeieppwahl"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465


def generar_contrasena():
    return ''.join(str(secrets.randbelow(10)) for _ in range(6))

def enviar_contrasena(nombre, correo_destino, contrasena):

    mensaje = EmailMessage()

    mensaje["From"] = EMAIL_EMISOR
    mensaje["To"] = correo_destino
    mensaje["Subject"] = "Acceso al sistema de Mesa de Ayuda"

    mensaje.set_content(f"""
Hola {nombre},

Su contraseña para ingresar al sistema Respuestas Rápidas es:

{contrasena}

Esta contraseña será utilizada para iniciar sesión cuando el sistema detecte un nuevo dispositivo.

Si usted no solicitó este acceso, puede ignorar este correo.

Mesa de Ayuda
Call My Way
""")

# -------- HTML --------

    html = f"""
<!DOCTYPE html>

<html lang="es">

<head>

<meta charset="UTF-8">

</head>

<body style="margin:0;padding:0;background:#f4f6f9;font-family:Arial,Helvetica,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0">

<tr>

<td align="center">

<table width="700" cellpadding="0" cellspacing="0"
style="background:white;border-collapse:collapse;">

<tr>

<td align="center" style="padding:30px;">

<img src="cid:{logo_cid[1:-1]}">

</td>

</tr>

<tr>

<td style="height:8px;background:#8BC400;"></td>

</tr>

<tr>

<td style="height:34px;background:#1E73BE;"></td>

</tr>

<tr>

<td style="padding:40px;color:#333;font-size:15px;line-height:28px;">

<p>

Estimado(a)
<strong>{nombre}</strong>,

</p>

<p>

Su contraseña para acceder al sistema de
<strong>Mesa de Ayuda</strong>
ha sido generada correctamente.

</p>

<table align="center"
style="margin-top:35px;margin-bottom:35px;">

<tr>

<td
style="
background:#eaf3ff;
border:2px solid #1E73BE;
padding:20px 50px;
font-size:38px;
font-weight:bold;
letter-spacing:10px;
color:#1E73BE;
border-radius:10px;
">

{contrasena}

</td>

</tr>

</table>

<p>

Esta contraseña será utilizada para iniciar sesión cuando el sistema detecte un dispositivo nuevo.

</p>

<p>

Por seguridad, no comparta esta contraseña con otras personas.

</p>

<p>

Si usted no solicitó este acceso, puede ignorar este mensaje.

</p>

</td>

</tr>

<tr>

<td
align="center"
style="
background:#8BC400;
padding:25px;
color:white;
font-size:13px;
font-weight:bold;
">

CallMyWay, IsMyConnect y su logo son marca registrada propiedad de CallMyWay NY S.A. Empresa Habilitada por la SUTEL bajo el título habilitante SUTEL-TH-003 Todos los derechos reservados. Copyright ©2001 - 2020

</td>

</tr>

</table>

</td>

</tr>

</table>

</body>

</html>
"""


    # Ruta del logo
    ruta_logo = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "static", "img", "CMW_correo.png"
    )

    # Crear primero el contenido del mensaje
    em.set_content(cuerpo)
    em.add_alternative(html, subtype="html")

    # Obtener la parte HTML
    parte_html = em.get_body(preferencelist=("html",))

    # Incorporar el logo al HTML
    with open(ruta_logo, "rb") as img:
        imagen = img.read()

    tipo, _ = mimetypes.guess_type(ruta_logo)
    tipo = tipo or "image/png"
    maintype, subtype = tipo.split("/", 1)

    parte_html.add_related(
        imagen,
        maintype=maintype,
        subtype=subtype,
        cid=logo_cid
    )

    try:

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:

            smtp.login(EMAIL_EMISOR, EMAIL_PASSWORD)

            smtp.send_message(mensaje)

        return True

    except Exception as e:

        print("Error enviando correo:", e)

        return False
    
enviar_contrasena("Manfred Lagos", "manfred.lagos@callmyway.net", "123456")