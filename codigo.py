import random
import smtplib
from email.message import EmailMessage
import os
from email.utils import make_msgid
import mimetypes

logo_cid = make_msgid(domain="callmyway.net")

def generar_codigo_verificacion():
    codigo = random.randint(100000, 999999)
    return str(codigo)

def enviar_correo_verificacion(email_receptor, verification_code):
    email_emisor = "connecting.conectandopersonas@gmail.com"
    email_contrasena = "tewzfmaeieppwahl"

    asunto = "Código de verificación"
    cuerpo = f"Tu código de verificación es: {verification_code}"

    em = EmailMessage()
    em["From"] = email_emisor
    em["To"] = email_receptor
    em["Subject"] = "Acceso al sistema de Mesa de Ayuda"

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
<strong>{email_receptor}</strong>,

</p>

<p> Su código ha sido generada correctamente.</p>

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

{verification_code}

</td>
</tr>
</table>


<p>Por seguridad, no comparta este código con otras personas.</p>

<p>Si usted no solicitó este acceso, puede ignorar este mensaje.</p>

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

CallMyWay, IsMyConnect y su logo son marca registrada propiedad de CallMyWay NY S.A. Empresa Habilitada por la SUTEL bajo el título habilitante SUTEL-TH-003 Todos los derechos reservados. Copyright ©2001 - 2026

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

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email_emisor, email_contrasena)
            smtp.send_message(em)

        return True

    except Exception as e:

        print("Error enviando correo:", e)

        return False
