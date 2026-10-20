from flask import Flask, session,redirect, url_for, jsonify, render_template,request, send_file
import mysql.connector
import mysql.connector.errors
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import pandas as pd
import time
import os
from datetime import timedelta
from detector_pdf import analizar_pdf
from ollama_client import consultar_ollama
from werkzeug.utils import secure_filename
from codigo import generar_codigo_verificacion, enviar_correo_verificacion

app = Flask(__name__)

app.secret_key = '@\xf6\xdd\x16.\x9b?\xbbHx\xc0\x95fr\x1b\xb7\xf5l\tF\xfe\xf4\xa4\x1a'

app.permanent_session_lifetime = timedelta(days=30)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'xls', 'xlsx'}

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

inicio_ollama = time.perf_counter()

politicas = []

def get_db_connection():
    return mysql.connector.connect(
        host="190.113.81.253",
        user="manfred",
        password="CwsrOPiEn3Dh%bcd",
        database="postits_db",
        auth_plugin='mysql_native_password'
    )

@app.route('/Generador_Script', methods=['GET', 'POST'])
def Generador_Script():
    if 'email' in session:
        return render_template('generador_script.html')
        
    else:
        return redirect(url_for('login'))

@app.route('/script_alta', methods=['GET', 'POST'])
def script_alta():
    if request.method == 'POST':
        correo = request.form.get('correo')
        politicas = obtener_politicas_por_dominio_y_extension(correo, 'alta')
        return render_template('script_alta_busqueda.html', politicas=politicas)
    return render_template('script_alta.html')

@app.route('/script_baja', methods=['GET', 'POST'])
def script_baja():
    if request.method == 'POST':
        correo = request.form.get('correo')
        politicas = obtener_politicas_por_dominio_y_extension(correo, 'baja')
        return render_template('script_baja_busqueda.html', politicas=politicas)
    return render_template('script_baja.html')

@app.route('/script_altaybaja', methods=['GET', 'POST'])
def script_altaybaja():
    if request.method == 'POST':
        correo = request.form.get('correo')
        politicas = obtener_politicas_por_dominio_y_extension(correo, 'altaybaja')
        return render_template('script_altaybaja_busqueda.html', politicas=politicas)
    return render_template('script_altaybaja.html')

@app.route('/script_alta_busqueda', methods=['POST'])
def obtener_politicas():
    correo = request.json.get('correo')
    tipo_extension = request.json.get('tipo_extension')

    politicas = obtener_politicas_por_dominio_y_extension(correo, tipo_extension)
    return jsonify({'politicas': politicas})

def obtener_politicas_por_dominio_y_extension(correo, tipo_extension):
    global politicas # Indica que estás usando la variable global 
    dominio = correo.split('@')[-1]

    cursor = mysql.connection.cursor()

    if tipo_extension == 'altaybaja':
        consulta = "SELECT descripcion FROM politicas WHERE dominio = %s AND tipo_politica = %s"
        cursor.execute(consulta, (dominio, "baja", "alta"))
    else:
        consulta = "SELECT politica FROM politicas WHERE dominio = %s AND tipo_politica = %s"
        cursor.execute(consulta, (dominio, tipo_extension))

    politicas = cursor.fetchall()
    cursor.close()

    politicas = "¡¡¡No se han registrado políticas asociadas a este dominio!!!"

    politicas_formateadas = "<br><br>".join(politica[0] for politica in politicas)

    politicas_formateadas = politicas

    return politicas_formateadas

@app.route('/descargar_script', methods=['POST'])
def descargar_script():

    # Recoger los correos y extensiones dinámicos
    correos = []
    extensiones = []
    numeros = []
    correos_alta = []
    extensiones_alta = []
    numeros_alta = []
    correos_baja = []
    extensiones_baja = []
    numero = request.form.get('numero')
    nombre_archivo = request.form.get('nombre_documento')
    correo_dominio = request.form.get('correo_dominio')
    archivo = request.files['archivo']
    filename = secure_filename(archivo.filename)  # Usa secure_filename para asegurar el nombre
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    dato = request.form.get('dato')
    numero_general = dato == 'True'

    print("Este es el valor de numero_general", numero_general)


    if 'archivo' in request.files and archivo.filename != '':

        print("Se ingresaron los datos desde el archivo exel")

        numero_general = False
        archivo = request.files['archivo']
        
        # Verificar que el archivo es de tipo Excel
        if archivo and allowed_file(archivo.filename):
            filename = secure_filename(archivo.filename)  # Usa secure_filename para asegurar el nombre
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            print(f"Archivo recibido: {filename}")

            try:
                # Guardar el archivo en el servidor
                archivo.save(filepath)

                # Leer la primera hoja 'alta o baja' asegurándonos de que todas las columnas sean tratadas como string
                df = pd.read_excel(filepath, sheet_name="alta o baja", engine='openpyxl', dtype=str)

                # Normalizar los nombres de las columnas (eliminar espacios y poner en minúsculas)
                df.columns = df.columns.str.strip().str.lower()

                # Imprimir las columnas después de la normalización para ver si hay espacios extra
                print(f"Columnas después de normalización en la hoja 'alta o baja': {df.columns.tolist()}")

                # Verificar que las columnas necesarias existen en la primera hoja
                if 'correo' in df.columns and 'extensión' in df.columns and 'código de país + número' in df.columns:
                    # Extraer los correos, extensiones y números, eliminando valores nulos
                    correos = df['correo'].dropna().tolist()
                    extensiones = df['extensión'].dropna().tolist()
                    numeros = df['código de país + número'].dropna().tolist()

                    # Imprimir los correos, extensiones y números encontrados
                    print(f"Correos encontrados: {correos}")
                    print(f"Extensiones encontradas: {extensiones}")
                    print(f"Números encontrados: {numeros}")

                    # Si no se encontraron correos o extensiones, devolver un error
                    if not correos:
                        print(f"No se encontraron correos o extensiones válidos en el archivo.")
                        return jsonify({"error": "El archivo Excel no contiene correos o extensiones válidos."}), 400
                else:
                    print(f"Error: Las columnas necesarias ('Correo', 'Extensión', 'Número') no están presentes en la hoja 'alta o baja'.")
                    return jsonify({"error": "El archivo Excel debe contener las columnas 'Correo', 'Extensión', y 'Número' en la hoja 'alta o baja'."}), 400

                # Ahora leeremos la segunda hoja llamada 'alta y baja'
                xl = pd.ExcelFile(filepath, engine='openpyxl')
                if 'alta y baja' in xl.sheet_names:  # Nombre correcto de la segunda hoja
                    df_nuevas_hojas = xl.parse('alta y baja', dtype=str)  # Aseguramos que las columnas también sean tratadas como str

                    # Verificar que las columnas necesarias estén presentes en la nueva hoja
                    required_columns = ['correo_alta', 'extensión_alta', 'código de país + número_alta', 'correo_baja']
                    if all(col in df_nuevas_hojas.columns for col in required_columns):
                        # Extraer los datos de la nueva hoja
                        correos_alta = df_nuevas_hojas['correo_alta'].dropna().tolist()
                        extensiones_alta = df_nuevas_hojas['extensión_alta'].dropna().tolist()
                        numeros_alta = df_nuevas_hojas['código de país + número_alta'].dropna().tolist()
                        correos_baja = df_nuevas_hojas['correo_baja'].dropna().tolist()

                        # Imprimir los datos extraídos de la nueva hoja
                        print(f"Correos Alta: {correos_alta}")
                        print(f"Extensiones Alta: {extensiones_alta}")
                        print(f"Números Alta: {numeros_alta}")
                        print(f"Correos Baja: {correos_baja}")

                    else:
                        print(f"Error: Las columnas requeridas no están presentes en la hoja 'alta y baja'.")
                        return jsonify({"error": "La hoja 'alta y baja' debe contener las columnas 'correo_alta', 'extensión_alta', 'número_alta', 'correo_baja'."}), 400
                else:
                    print(f"Error: La hoja 'alta y baja' no está presente en el archivo Excel.")
                    return jsonify({"error": "El archivo Excel debe contener una hoja llamada 'alta y baja'."}), 400

    

            except Exception as e:
                print(f"Error al procesar el archivo Excel: {str(e)}")
                return jsonify({"error": f"Error al procesar el archivo Excel: {str(e)}"}), 500

    else:

        print("Se ingresaron los datos desde el formulario")

        for key in request.form:
            if 'correo' in key:
                correos.append(request.form.get(key))
            if 'extension' in key:
                extensiones.append(request.form.get(key))
            if 'numero' in key:
                numeros.append(request.form.get(key))

        for key in request.form:
            if 'correo_alta' in key:
                correos_alta.append(request.form.get(key))
            if 'extension_alta' in key:
                extensiones_alta.append(request.form.get(key))
            if 'numero_alta' in key:
                numeros_alta.append(request.form.get(key))

        for key in request.form:
            if 'correo_baja' in key:
                correos_baja.append(request.form.get(key))
            if 'extension_baja' in key:
                extensiones_baja.append(request.form.get(key))

    # Imprime los valores de correos y extensiones para debug
    print(f"Correos: {correos}")
    print(f"Extensiones: {extensiones}")
    print(f"Numeros: {numeros}")
    
    # Obtener la ruta anterior desde donde se envía el formulario
    ruta_anterior = request.referrer  # Esto obtiene la URL de la página anterior

    # Usar urlparse para extraer solo la ruta
    parsed_url = urlparse(ruta_anterior)
    ruta_final = parsed_url.path  # Esto te dará solo la parte del path

    print(f'Ruta anterior: {ruta_final}')  # Ahora solo tendrás la parte de la ruta

    if ruta_final == "/script_altaybaja":
        print(f"Correos de alta: {correos_alta}")
        print(f"Extensiones de alta: {extensiones_alta}")
        print(f"Numero de alta: {numeros_alta}")
        print(f"Correos de numeros_alta: {numeros_alta}")
        print(f"Correos de baja: {correos_baja}")


    if ruta_final == "/script_alta":
        accion = "alta"
    elif ruta_final == "/script_baja":
        accion = "baja"
    elif ruta_final == "/script_altaybaja":
        accion = "altaybaja"

    print("La accion selecionada es: ", accion)

    politicas_seleccionadas = request.form.get('politica')
    print(f"Tipo de politica: {politicas_seleccionadas}")

        # Obtener las políticas individuales seleccionadas
    politicas_individuales = request.form.getlist('politicas_individuales[]')
    print(f"Politicas selecionadas: {politicas_individuales}")

    print(request.form)

    contenido_ps1 = f"Start-Transcript -Path $env:USERPROFILE\\Desktop\\Config_IMC_{nombre_archivo}.txt\n\n"
    contenido_ps1 += "Start-Service WinRM\n"
    contenido_ps1 += "Install-Module MicrosoftTeams\n\n"
    contenido_ps1 += "Import-Module -Name MicrosoftTeams\n"
    contenido_ps1 += "Connect-MicrosoftTeams\n\n"

    if politicas_seleccionadas == 'generales' and accion == "alta":
        contenido_ps1 += "#Dar_de_alta\n\n"
        for correo, extension in zip(correos, extensiones):
            contenido_ps1 += f'echo "Set-CsPhoneNumberAssignment -Identity {correo} -EnterpriseVoiceEnabled $true"\n'
            contenido_ps1 += f'Set-CsPhoneNumberAssignment -Identity {correo} -EnterpriseVoiceEnabled $true\n'
        contenido_ps1 += f'\n'

        for correo, extension in zip(correos, extensiones):
            contenido_ps1 += f'echo "Set-CsPhoneNumberAssignment -Identity {correo} -PhoneNumber +{extension} -PhoneNumberType DirectRouting"\n'
            contenido_ps1 += f'Set-CsPhoneNumberAssignment -Identity {correo} -PhoneNumber +{extension} -PhoneNumberType DirectRouting\n'
        contenido_ps1 += f'\n'

        for correo, extension in zip(correos, extensiones):
            contenido_ps1 += f'echo "Grant-CsOnlineVoiceRoutingPolicy -Identity {correo} -PolicyName ISMYCONNECT"\n'
            contenido_ps1 += f'Grant-CsOnlineVoiceRoutingPolicy -Identity {correo} -PolicyName "ISMYCONNECT"\n'
        contenido_ps1 += f'\n'

        for correo, extension in zip(correos, extensiones):
            contenido_ps1 += f'echo "Grant-CsTeamsCallingPolicy -Identity {correo} -PolicyName AllowCalling"\n'
            contenido_ps1 += f'Grant-CsTeamsCallingPolicy -Identity {correo} -PolicyName AllowCalling\n'
        contenido_ps1 += f'\n'

        for correo, extension in zip(correos, extensiones):
            contenido_ps1 += f'echo "Grant-CsTenantDialPlan -Identity {correo} -PolicyName ISMYCONNECT"\n'
            contenido_ps1 += f'Grant-CsTenantDialPlan -Identity {correo} -PolicyName ISMYCONNECT\n'
        contenido_ps1 += f'\n'

    elif politicas_seleccionadas == 'generales' and accion == "baja":
        contenido_ps1 += "#Dar_de_baja\n\n"
        for correo in correos:
            contenido_ps1 += f'echo "Remove-CsPhoneNumberAssignment -Identity {correo} -PhoneNumberType -RemoveAll"\n'
            contenido_ps1 += f'Remove-CsPhoneNumberAssignment -Identity {correo} -RemoveAll\n'
        contenido_ps1 += f'\n'

        for correo in correos:
            contenido_ps1 += f'echo "Grant-CsOnlineVoiceRoutingPolicy -Identity {correo} -PolicyName $null"\n'
            contenido_ps1 += f'Grant-CsOnlineVoiceRoutingPolicy -Identity {correo} -PolicyName $null\n'
        contenido_ps1 += f'\n'

        for correo in correos:
            contenido_ps1 += f'echo "Grant-CsTeamsCallingPolicy -Identity {correo} -PolicyName $null"\n'
            contenido_ps1 += f'Grant-CsTeamsCallingPolicy -Identity {correo} -PolicyName $null\n'
        contenido_ps1 += f'\n'

    elif politicas_seleccionadas == 'generales' and accion == "altaybaja":
        contenido_ps1 += "#Dar_de_baja\n\n"
        for correo_baja in correos_baja:
            contenido_ps1 += f'echo "Remove-CsPhoneNumberAssignment -Identity {correo_baja} -PhoneNumberType -RemoveAll"\n'
            contenido_ps1 += f'Remove-CsPhoneNumberAssignment -Identity {correo_baja} -RemoveAll\n'
        contenido_ps1 += f'\n'
        for correo_baja in correos_baja:
            contenido_ps1 += f'echo "Grant-CsOnlineVoiceRoutingPolicy -Identity {correo_baja} -PolicyName $null"\n'
            contenido_ps1 += f'Grant-CsOnlineVoiceRoutingPolicy -Identity {correo_baja} -PolicyName $null\n'
        contenido_ps1 += f'\n'
        for correo_baja in correos_baja:
            contenido_ps1 += f'echo "Grant-CsTeamsCallingPolicy -Identity {correo_baja} -PolicyName $null"\n'
            contenido_ps1 += f'Grant-CsTeamsCallingPolicy -Identity {correo_baja} -PolicyName $null\n'
        contenido_ps1 += f'\n'
        
        contenido_ps1 += "#Dar_de_alta\n\n"
        for correo_alta, extension_alta in zip(correos_alta, extensiones_alta):
            contenido_ps1 += f'echo "Set-CsPhoneNumberAssignment -Identity {correo_alta} -EnterpriseVoiceEnabled $true"\n'
            contenido_ps1 += f'Set-CsPhoneNumberAssignment -Identity {correo_alta} -EnterpriseVoiceEnabled $true\n'
        contenido_ps1 += f'\n'
        for correo_alta, extension_alta in zip(correos_alta, extensiones_alta):
            contenido_ps1 += f'echo "Set-CsPhoneNumberAssignment -Identity {correo_alta} -PhoneNumber +{extension_alta} -PhoneNumberType DirectRouting"\n'
            contenido_ps1 += f'Set-CsPhoneNumberAssignment -Identity {correo_alta} -PhoneNumber +{extension_alta} -PhoneNumberType DirectRouting\n'
        contenido_ps1 += f'\n'
        for correo_alta, extension_alta in zip(correos_alta, extensiones_alta):
            contenido_ps1 += f'echo "Grant-CsOnlineVoiceRoutingPolicy -Identity {correo_alta} -PolicyName ISMYCONNECT"\n'
            contenido_ps1 += f'Grant-CsOnlineVoiceRoutingPolicy -Identity {correo_alta} -PolicyName "ISMYCONNECT"\n'
        contenido_ps1 += f'\n'
        for correo_alta, extension_alta in zip(correos_alta, extensiones_alta):
            contenido_ps1 += f'echo "Grant-CsTeamsCallingPolicy -Identity {correo_alta} -PolicyName AllowCalling"\n'
            contenido_ps1 += f'Grant-CsTeamsCallingPolicy -Identity {correo_alta} -PolicyName AllowCalling\n'
        contenido_ps1 += f'\n'
        for correo_alta, extension_alta in zip(correos_alta, extensiones_alta):
            contenido_ps1 += f'echo "Grant-CsTenantDialPlan -Identity {correo_alta} -PolicyName ISMYCONNECT"\n'
            contenido_ps1 += f'Grant-CsTenantDialPlan -Identity {correo_alta} -PolicyName ISMYCONNECT\n'
        contenido_ps1 += f'\n'
    
    elif politicas_seleccionadas == 'individuales' and accion == "alta":
        contenido_ps1 += "#Dar_de_alta\n\n"
        if numero_general == True:
            for correo, extension in zip(correos, extensiones):
                if 'set1' in politicas_individuales:
                    contenido_ps1 += f'echo "Set-CsPhoneNumberAssignment -Identity {correo} -EnterpriseVoiceEnabled $true"\n'
                    contenido_ps1 += f'Set-CsPhoneNumberAssignment -Identity {correo} -EnterpriseVoiceEnabled $true\n'
            if 'set1' in politicas_individuales:
                contenido_ps1 += f'\n'

            for correo, extension in zip(correos, extensiones):
                if 'set2' in politicas_individuales:
                    contenido_ps1 += f'echo "Set-CsPhoneNumberAssignment -Identity {correo} -PhoneNumber +{extension} -PhoneNumberType DirectRouting"\n'
                    contenido_ps1 += f'Set-CsPhoneNumberAssignment -Identity {correo} -PhoneNumber +{extension} -PhoneNumberType DirectRouting\n'
            if 'set2' in politicas_individuales:
                contenido_ps1 += f'\n'

            for correo, extension in zip(correos, extensiones):
                if 'set3' in politicas_individuales:
                    contenido_ps1 += f'echo "Set-CsPhoneNumberAssignment -Identity {correo} -PhoneNumber +{numero};ext={extension} -PhoneNumberType DirectRouting"\n'
                    contenido_ps1 += f'Set-CsPhoneNumberAssignment -Identity {correo} -PhoneNumber "+{numero};ext={extension}" -PhoneNumberType DirectRouting\n'
            if 'set3' in politicas_individuales:
                contenido_ps1 += f'\n'

            for correo, extension in zip(correos, extensiones):
                if 'set4' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsOnlineVoiceRoutingPolicy -Identity {correo} -PolicyName ISMYCONNECT"\n'
                    contenido_ps1 += f'Grant-CsOnlineVoiceRoutingPolicy -Identity {correo} -PolicyName "ISMYCONNECT"\n'
            if 'set4' in politicas_individuales:
                contenido_ps1 += f'\n'

            for correo, extension in zip(correos, extensiones):
                if 'set5' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsTeamsCallingPolicy -Identity {correo} -PolicyName AllowCalling"\n'
                    contenido_ps1 += f'Grant-CsTeamsCallingPolicy -Identity {correo} -PolicyName AllowCalling\n'
            if 'set5' in politicas_individuales:
                contenido_ps1 += f'\n'   

            for correo, extension in zip(correos, extensiones):
                if 'set12' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsTeamsCallingPolicy -Identity {correo} -PolicyName CMW-All-Enabled"\n'
                    contenido_ps1 += f'Grant-CsTeamsCallingPolicy -Identity {correo} -PolicyName CMW-All-Enabled\n'  
            if 'set12' in politicas_individuales:
                contenido_ps1 += f'\n'

            for correo, extension in zip(correos, extensiones):
                if 'set13' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsTeamsCallingPolicy -Identity {correo} -PolicyName CMW-VM-Disabled"\n'
                    contenido_ps1 += f'Grant-CsTeamsCallingPolicy -Identity {correo} -PolicyName CMW-VM-Disabled\n' 
            if 'set13' in politicas_individuales:
                contenido_ps1 += f'\n'                        

            for correo, extension in zip(correos, extensiones):
                if 'set6' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsTenantDialPlan -Identity {correo} -PolicyName ISMYCONNECT"\n'
                    contenido_ps1 += f'Grant-CsTenantDialPlan -Identity {correo} -PolicyName ISMYCONNECT\n'
            if 'set6' in politicas_individuales:
                contenido_ps1 += f'\n'
 
            for correo, extension in zip(correos, extensiones):
                if 'set7' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsOnlineAudioConferencingRoutingPolicy  -Identity {correo} -PolicyName ISMYCONNECT"\n'
                    contenido_ps1 += f'Grant-CsOnlineAudioConferencingRoutingPolicy -Identity {correo} -PolicyName ISMYCONNECT\n'   
            if 'set7' in politicas_individuales:
                contenido_ps1 += f'\n'

        else:
            for correo, extension in zip(correos, extensiones):
                if 'set1' in politicas_individuales:
                    contenido_ps1 += f'echo "Set-CsPhoneNumberAssignment -Identity {correo} -EnterpriseVoiceEnabled $true"\n'
                    contenido_ps1 += f'Set-CsPhoneNumberAssignment -Identity {correo} -EnterpriseVoiceEnabled $true\n'
            if 'set1' in politicas_individuales:
                contenido_ps1 += f'\n'

            for correo, extension in zip(correos, extensiones): 
                if 'set2' in politicas_individuales:
                    contenido_ps1 += f'echo "Set-CsPhoneNumberAssignment -Identity {correo} -PhoneNumber +{extension} -PhoneNumberType DirectRouting"\n'
                    contenido_ps1 += f'Set-CsPhoneNumberAssignment -Identity {correo} -PhoneNumber +{extension} -PhoneNumberType DirectRouting\n'
            if 'set2' in politicas_individuales:
                contenido_ps1 += f'\n'
            
            for correo, extension, numero in zip(correos, extensiones, numeros):
                if 'set3' in politicas_individuales:
                    contenido_ps1 += f'echo "Set-CsPhoneNumberAssignment -Identity {correo} -PhoneNumber +{numero};ext={extension} -PhoneNumberType DirectRouting"\n'
                    contenido_ps1 += f'Set-CsPhoneNumberAssignment -Identity {correo} -PhoneNumber "+{numero};ext={extension}" -PhoneNumberType DirectRouting\n'
            if 'set3' in politicas_individuales:
                contenido_ps1 += f'\n'

            for correo, extension in zip(correos, extensiones):
                if 'set4' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsOnlineVoiceRoutingPolicy -Identity {correo} -PolicyName ISMYCONNECT"\n'
                    contenido_ps1 += f'Grant-CsOnlineVoiceRoutingPolicy -Identity {correo} -PolicyName "ISMYCONNECT"\n'
            if 'set4' in politicas_individuales:
                contenido_ps1 += f'\n'

            for correo, extension in zip(correos, extensiones):
                if 'set5' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsTeamsCallingPolicy -Identity {correo} -PolicyName AllowCalling"\n'
                    contenido_ps1 += f'Grant-CsTeamsCallingPolicy -Identity {correo} -PolicyName AllowCalling\n' 
            if 'set5' in politicas_individuales:
                contenido_ps1 += f'\n' 

            for correo, extension in zip(correos, extensiones):
                if 'set12' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsTeamsCallingPolicy -Identity {correo} -PolicyName CMW-All-Enabled"\n'
                    contenido_ps1 += f'Grant-CsTeamsCallingPolicy -Identity {correo} -PolicyName CMW-All-Enabled\n'  
            if 'set12' in politicas_individuales:
                contenido_ps1 += f'\n'

            for correo, extension in zip(correos, extensiones):
                if 'set13' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsTeamsCallingPolicy -Identity {correo} -PolicyName CMW-VM-Disabled"\n'
                    contenido_ps1 += f'Grant-CsTeamsCallingPolicy -Identity {correo} -PolicyName CMW-VM-Disabled\n' 
            if 'set13' in politicas_individuales:
                contenido_ps1 += f'\n'                         

            for correo, extension in zip(correos, extensiones):
                if 'set6' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsTenantDialPlan -Identity {correo} -PolicyName ISMYCONNECT"\n'
                    contenido_ps1 += f'Grant-CsTenantDialPlan -Identity {correo} -PolicyName ISMYCONNECT\n'
            if 'set6' in politicas_individuales:
                contenido_ps1 += f'\n'
                    
            for correo, extension in zip(correos, extensiones):
                if 'set7' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsOnlineAudioConferencingRoutingPolicy  -Identity {correo} -PolicyName ISMYCONNECT"\n'
                    contenido_ps1 += f'Grant-CsOnlineAudioConferencingRoutingPolicy -Identity {correo} -PolicyName ISMYCONNECT\n'   
            if 'set7' in politicas_individuales:
                contenido_ps1 += f'\n'

    elif politicas_seleccionadas == 'individuales' and accion == "baja":
        contenido_ps1 += "#Dar_de_baja\n\n"
        for correo in correos:
            if 'set8' in politicas_individuales:
                contenido_ps1 += f'echo "Remove-CsPhoneNumberAssignment -Identity {correo} -PhoneNumberType -RemoveAll"\n'
                contenido_ps1 += f'Remove-CsPhoneNumberAssignment -Identity {correo} -RemoveAll\n'
        if 'set8' in politicas_individuales:
                contenido_ps1 += f'\n'

        for correo in correos:
            if 'set9' in politicas_individuales:
                contenido_ps1 += f'echo "Grant-CsOnlineVoiceRoutingPolicy -Identity {correo} -PolicyName $null"\n'
                contenido_ps1 += f'Grant-CsOnlineVoiceRoutingPolicy -Identity {correo} -PolicyName $null\n'
        if 'set9' in politicas_individuales:
                contenido_ps1 += f'\n'

        for correo in correos:
            if 'set10' in politicas_individuales:
                contenido_ps1 += f'echo "Grant-CsTeamsCallingPolicy -Identity {correo} -PolicyName $null"\n'
                contenido_ps1 += f'Grant-CsTeamsCallingPolicy -Identity {correo} -PolicyName $null\n'
        if 'set10' in politicas_individuales:
                contenido_ps1 += f'\n'

        for correo in correos:
            if 'set11' in politicas_individuales:
                contenido_ps1 += f'echo "Grant-CsOnlineAudioConferencingRoutingPolicy -Identity {correo} -PolicyName $null"\n'
                contenido_ps1 += f'Grant-CsOnlineAudioConferencingRoutingPolicy -Identity {correo} -PolicyName $null\n'
        if 'set11' in politicas_individuales:
                contenido_ps1 += f'\n'


    elif politicas_seleccionadas == 'individuales' and accion == "altaybaja":
        contenido_ps1 += "#Dar_de_baja\n\n"
        for correo_baja in correos_baja:
            if 'set8' in politicas_individuales:
                contenido_ps1 += f'echo "Remove-CsPhoneNumberAssignment -Identity {correo_baja} -PhoneNumberType -RemoveAll"\n'
                contenido_ps1 += f'Remove-CsPhoneNumberAssignment -Identity {correo_baja} -RemoveAll\n'
        if 'set8' in politicas_individuales:
                contenido_ps1 += f'\n'

        for correo_baja in correos_baja:
            if 'set9' in politicas_individuales:
                contenido_ps1 += f'echo "Grant-CsOnlineVoiceRoutingPolicy -Identity {correo_baja} -PolicyName $null"\n'
                contenido_ps1 += f'Grant-CsOnlineVoiceRoutingPolicy -Identity {correo_baja} -PolicyName $null\n'
        if 'set9' in politicas_individuales:
                contenido_ps1 += f'\n'

        for correo_baja in correos_baja:
            if 'set10' in politicas_individuales:
                contenido_ps1 += f'echo "Grant-CsTeamsCallingPolicy -Identity {correo_baja} -PolicyName $null"\n'
                contenido_ps1 += f'Grant-CsTeamsCallingPolicy -Identity {correo_baja} -PolicyName $null\n'
        if 'set10' in politicas_individuales:
                contenido_ps1 += f'\n'

        for correo_baja in correos_baja:
            if 'set11' in politicas_individuales:
                contenido_ps1 += f'echo "Grant-CsOnlineAudioConferencingRoutingPolicy -Identity {correo_baja} -PolicyName $null"\n'
                contenido_ps1 += f'Grant-CsOnlineAudioConferencingRoutingPolicy -Identity {correo_baja} -PolicyName $null\n'
        if 'set11' in politicas_individuales:
                contenido_ps1 += f'\n'                             
        
        contenido_ps1 += "#Dar_de_alta\n\n"
        if numero_general == True:
            for correo_alta, extension_alta in zip(correos_alta, extensiones_alta):
                if 'set1' in politicas_individuales:
                    contenido_ps1 += f'echo "Set-CsPhoneNumberAssignment -Identity {correo_alta} -EnterpriseVoiceEnabled $true"\n'
                    contenido_ps1 += f'Set-CsPhoneNumberAssignment -Identity {correo_alta} -EnterpriseVoiceEnabled $true\n'
            if 'set1' in politicas_individuales:
                contenido_ps1 += f'\n'

            for correo_alta, extension_alta in zip(correos_alta, extensiones_alta):
                if 'set2' in politicas_individuales:
                    contenido_ps1 += f'echo "Set-CsPhoneNumberAssignment -Identity {correo_alta} -PhoneNumber +{extension_alta} -PhoneNumberType DirectRouting"\n'
                    contenido_ps1 += f'Set-CsPhoneNumberAssignment -Identity {correo_alta} -PhoneNumber +{extension_alta} -PhoneNumberType DirectRouting\n'
            if 'set2' in politicas_individuales:
                contenido_ps1 += f'\n'

            for correo_alta, extension_alta in zip(correos_alta, extensiones_alta):
                if 'set3' in politicas_individuales:
                    contenido_ps1 += f'echo "Set-CsPhoneNumberAssignment -Identity {correo_alta} -PhoneNumber +{numero};ext={extension_alta} -PhoneNumberType DirectRouting"\n'
                    contenido_ps1 += f'Set-CsPhoneNumberAssignment -Identity {correo_alta} -PhoneNumber "+{numero};ext={extension_alta}" -PhoneNumberType DirectRouting\n'
            if 'set3' in politicas_individuales:
                contenido_ps1 += f'\n'
 
            for correo_alta, extension_alta in zip(correos_alta, extensiones_alta):
                if 'set4' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsOnlineVoiceRoutingPolicy -Identity {correo_alta} -PolicyName ISMYCONNECT"\n'
                    contenido_ps1 += f'Grant-CsOnlineVoiceRoutingPolicy -Identity {correo_alta} -PolicyName "ISMYCONNECT"\n'
            if 'set4' in politicas_individuales:
                contenido_ps1 += f'\n'

            for correo_alta, extension_alta in zip(correos_alta, extensiones_alta):
                if 'set5' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsTeamsCallingPolicy -Identity {correo_alta} -PolicyName AllowCalling"\n'
                    contenido_ps1 += f'Grant-CsTeamsCallingPolicy -Identity {correo_alta} -PolicyName AllowCalling\n' 
            if 'set5' in politicas_individuales:
                contenido_ps1 += f'\n'   

            for correo_alta, extension_alta in zip(correos_alta, extensiones_alta):
                if 'set12' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsTeamsCallingPolicy -Identity {correo_alta} -PolicyName CMW-All-Enabled"\n'
                    contenido_ps1 += f'Grant-CsTeamsCallingPolicy -Identity {correo_alta} -PolicyName CMW-All-Enabled\n'  
            if 'set12' in politicas_individuales:
                contenido_ps1 += f'\n'

            for correo_alta, extension_alta in zip(correos_alta, extensiones_alta):
                if 'set13' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsTeamsCallingPolicy -Identity {correo_alta} -PolicyName CMW-VM-Disabled"\n'
                    contenido_ps1 += f'Grant-CsTeamsCallingPolicy -Identity {correo_alta} -PolicyName CMW-VM-Disabled\n' 
            if 'set13' in politicas_individuales:
                contenido_ps1 += f'\n'                       

            for correo_alta, extension_alta in zip(correos_alta, extensiones_alta):
                if 'set6' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsTenantDialPlan -Identity {correo_alta} -PolicyName ISMYCONNECT"\n'
                    contenido_ps1 += f'Grant-CsTenantDialPlan -Identity {correo_alta} -PolicyName ISMYCONNECT\n'
            if 'set6' in politicas_individuales:
                contenido_ps1 += f'\n'

            for correo_alta, extension_alta in zip(correos_alta, extensiones_alta):
                if 'set7' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsOnlineAudioConferencingRoutingPolicy  -Identity {correo_alta} -PolicyName ISMYCONNECT"\n'
                    contenido_ps1 += f'Grant-CsOnlineAudioConferencingRoutingPolicy -Identity {correo_alta} -PolicyName ISMYCONNECT\n'   
            if 'set7' in politicas_individuales:
                contenido_ps1 += f'\n'

        else:
            for correo_alta, extension_alta, numero_alta in zip(correos_alta, extensiones_alta, numeros_alta):
                if 'set1' in politicas_individuales:
                    contenido_ps1 += f'echo "Set-CsPhoneNumberAssignment -Identity {correo_alta} -EnterpriseVoiceEnabled $true"\n'
                    contenido_ps1 += f'Set-CsPhoneNumberAssignment -Identity {correo_alta} -EnterpriseVoiceEnabled $true\n'
            if 'set1' in politicas_individuales:
                contenido_ps1 += f'\n'

            for correo_alta, extension_alta, numero_alta in zip(correos_alta, extensiones_alta, numeros_alta):
                if 'set2' in politicas_individuales:
                    contenido_ps1 += f'echo "Set-CsPhoneNumberAssignment -Identity {correo_alta} -PhoneNumber +{extension_alta} -PhoneNumberType DirectRouting"\n'
                    contenido_ps1 += f'Set-CsPhoneNumberAssignment -Identity {correo_alta} -PhoneNumber +{extension_alta} -PhoneNumberType DirectRouting\n'
            if 'set2' in politicas_individuales:
                contenido_ps1 += f'\n'

            for correo_alta, extension_alta, numero_alta in zip(correos_alta, extensiones_alta, numeros_alta):
                if 'set3' in politicas_individuales:
                    contenido_ps1 += f'echo "Set-CsPhoneNumberAssignment -Identity {correo_alta} -PhoneNumber +{numero_alta};ext={extension_alta} -PhoneNumberType DirectRouting"\n'
                    contenido_ps1 += f'Set-CsPhoneNumberAssignment -Identity {correo_alta} -PhoneNumber "+{numero_alta};ext={extension_alta}" -PhoneNumberType DirectRouting\n'
            if 'set3' in politicas_individuales:
                contenido_ps1 += f'\n'

            for correo_alta, extension_alta, numero_alta in zip(correos_alta, extensiones_alta, numeros_alta):
                if 'set4' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsOnlineVoiceRoutingPolicy -Identity {correo_alta} -PolicyName ISMYCONNECT"\n'
                    contenido_ps1 += f'Grant-CsOnlineVoiceRoutingPolicy -Identity {correo_alta} -PolicyName "ISMYCONNECT"\n'
            if 'set4' in politicas_individuales:
                contenido_ps1 += f'\n'

            for correo_alta, extension_alta, numero_alta in zip(correos_alta, extensiones_alta, numeros_alta):
                if 'set5' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsTeamsCallingPolicy -Identity {correo_alta} -PolicyName AllowCalling"\n'
                    contenido_ps1 += f'Grant-CsTeamsCallingPolicy -Identity {correo_alta} -PolicyName AllowCalling\n'
            if 'set5' in politicas_individuales:
                contenido_ps1 += f'\n'   

            for correo_alta, extension_alta, numero_alta in zip(correos_alta, extensiones_alta, numeros_alta):
                if 'set12' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsTeamsCallingPolicy -Identity {correo_alta} -PolicyName CMW-All-Enabled"\n'
                    contenido_ps1 += f'Grant-CsTeamsCallingPolicy -Identity {correo_alta} -PolicyName CMW-All-Enabled\n'  
            if 'set12' in politicas_individuales:
                contenido_ps1 += f'\n'

            for correo_alta, extension_alta, numero_alta in zip(correos_alta, extensiones_alta, numeros_alta):
                if 'set13' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsTeamsCallingPolicy -Identity {correo_alta} -PolicyName CMW-VM-Disabled"\n'
                    contenido_ps1 += f'Grant-CsTeamsCallingPolicy -Identity {correo_alta} -PolicyName CMW-VM-Disabled\n' 
            if 'set13' in politicas_individuales:
                contenido_ps1 += f'\n'                        

            for correo_alta, extension_alta, numero_alta in zip(correos_alta, extensiones_alta, numeros_alta):
                if 'set6' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsTenantDialPlan -Identity {correo_alta} -PolicyName ISMYCONNECT"\n'
                    contenido_ps1 += f'Grant-CsTenantDialPlan -Identity {correo_alta} -PolicyName ISMYCONNECT\n'
            if 'set6' in politicas_individuales:
                contenido_ps1 += f'\n'

            for correo_alta, extension_alta, numero_alta in zip(correos_alta, extensiones_alta, numeros_alta):
                if 'set7' in politicas_individuales:
                    contenido_ps1 += f'echo "Grant-CsOnlineAudioConferencingRoutingPolicy  -Identity {correo_alta} -PolicyName ISMYCONNECT"\n'
                    contenido_ps1 += f'Grant-CsOnlineAudioConferencingRoutingPolicy -Identity {correo_alta} -PolicyName ISMYCONNECT\n'   
            if 'set7' in politicas_individuales:
                contenido_ps1 += f'\n'

    elif politicas_seleccionadas == 'dominio' and accion == "alta":
        contenido_ps1 += "#Dar_de_alta\n\n"

        for correo, extension in zip(correos, extensiones):
            for politica in politicas:
                politica_texto = politica[0]

                if correo:
                    politica_texto_reemplazada = politica_texto.replace("{correo}", correo)
                else:
                    print("No se encontró un correo para reemplazar, saltando a la siguiente.")
                    continue

                # Reemplaza la extensión si existe
                if extension:
                    politica_texto_reemplazada = politica_texto_reemplazada.replace("{extension}", extension)
                else:
                    print("No se encontró una extensión para reemplazar, saltando a la siguiente.")
                    continue 

                contenido_ps1 += f'echo "{politica_texto_reemplazada}"\n'
                contenido_ps1 += f'{politica_texto_reemplazada}\n\n'


    elif politicas_seleccionadas == 'dominio' and accion == "baja":

        contenido_ps1 += "#Dar_de_baja\n\n"

        for correo, extension in zip(correos, extensiones):
            for politica in politicas:
                politica_texto = politica[0]


                if correo:
                    politica_texto_reemplazada = politica_texto.replace("{correo}", correo)
                else:
                    print("No se encontró un correo para reemplazar, saltando a la siguiente.")
                    continue

                if extension:
                    politica_texto_reemplazada = politica_texto_reemplazada.replace("{extension}", extension)
                else:
                    print("No se encontró una extensión para reemplazar, saltando a la siguiente.")
                    continue

                contenido_ps1 += f'echo "{politica_texto_reemplazada}"\n'
                contenido_ps1 += f'{politica_texto_reemplazada}\n\n'


    elif politicas_seleccionadas == 'dominio' and accion == "altaybaja":

        contenido_ps1 += "#Dar_de_baja\n\n"

        for correo_baja, extension_baja in zip(correos_baja, extensiones_baja):
            print("El correo por dominio es: ", correo_dominio)
            obtener_politicas_por_dominio_y_extension(correo_dominio, "baja")
            print("Las politicas de baja son: ",politicas)
            for politica in politicas:
                politica_texto = politica[0]

                if correo_baja:
                    politica_texto_reemplazada = politica_texto.replace("{correo}", correo_baja)
                else:
                    print("No se encontró un correo para reemplazar, saltando a la siguiente.")
                    continue

                if extension_baja:
                    politica_texto_reemplazada = politica_texto_reemplazada.replace("{extension}", extension_baja)
                else:
                    print("No se encontró una extensión para reemplazar, saltando a la siguiente.")
                    continue

                contenido_ps1 += f'echo "{politica_texto_reemplazada}"\n'
                contenido_ps1 += f'{politica_texto_reemplazada}\n\n'
        
        contenido_ps1 += "#Dar_de_alta\n\n"
            
        for correo_alta, extension_alta in zip(correos_alta, extensiones_alta):
            obtener_politicas_por_dominio_y_extension(correo_dominio, "alta")
            print("Las politicas de alta son: ",politicas)
            for politica in politicas:
                politica_texto = politica[0]

                if correo_alta:
                    politica_texto_reemplazada = politica_texto.replace("{correo}", correo_alta)
                else:
                    print("No se encontró un correo para reemplazar, saltando a la siguiente.")
                    continue

                if extension_alta:
                    politica_texto_reemplazada = politica_texto_reemplazada.replace("{extension}", extension_alta)
                else:
                    print("No se encontró una extensión para reemplazar, saltando a la siguiente.")
                    continue

                contenido_ps1 += f'echo "{politica_texto_reemplazada}"\n'
                contenido_ps1 += f'{politica_texto_reemplazada}\n\n'
        

    contenido_ps1 += "Stop-Transcript\n"

    archivo = BytesIO(contenido_ps1.encode('utf-8'))
    archivo.name = f"{nombre_archivo}.ps1"

    return send_file(archivo, as_attachment=True, download_name=f"{nombre_archivo}.ps1", mimetype='text/plain')

@app.route('/texto')
def texto():
    return render_template('texto.html')

@app.route('/respuestas')
def respuestas():
    return render_template('respuestas.html')

@app.route('/prueba')
def prueba():
    return render_template('prueba.html')

@app.route('/Genedador_contraseña')
def Genedador_contraseña():
    return render_template('contraseña.html')

#-------------------------------------  Post It  ----------------------------------------

@app.route("/check_session", methods=["POST"])
def check_session():
    data = request.get_json()
    fingerprint = data.get("fingerprint")
    ip = request.remote_addr
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT
            u.id,
            u.nombre
        FROM dispositivos d
        INNER JOIN usuarios u
            ON u.id = d.user_id
        WHERE
            d.ip=%s
            AND d.fingerprint=%s
    """, (ip, fingerprint))
    usuario = cur.fetchone()#

    if usuario:
        session["user_id"] = usuario["id"]
        session["nombre"] = usuario["nombre"]
        cur.execute("""
            UPDATE dispositivos
            SET
                ultimo_uso = NOW()
            WHERE
                ip=%s
                AND fingerprint=%s
        """, (ip, fingerprint))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({
            "authenticated": True
        })

    cur.close()
    conn.close()

    return jsonify({
        "authenticated": False
    })

@app.route('/get_notes')
def get_notes():
    #if "user_id" not in session:
    #    return jsonify({"error": "No autorizado"}), 401
    user_id = 1 #session["user_id"]
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT id,title,content,color,position FROM notes WHERE user_id=%s ORDER BY position
    """,
    (user_id,))
    notes = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify({"notes":notes})

@app.route('/add_note', methods=['POST'])
def add_note():

    if "user_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    data = request.get_json()
    user_id = session["user_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO notes (user_id, title, content, color) VALUES (%s, %s, %s, %s)
    """, (
        user_id,
        data["title"],
        data["content"],
        data["color"]

    ))

    conn.commit()
    note_id = cur.lastrowid
    cur.close()
    conn.close()

    return jsonify({
        "status": "ok",
        "id": note_id
    })


@app.route('/edit_note/<int:note_id>', methods=['PUT'])
def edit_note(note_id):
    if "user_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    data = request.get_json()
    user_id = session["user_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE notes SET title=%s, content=%s, color=%s WHERE id=%s AND user_id=%s
    """, (

        data["title"],
        data["content"],
        data["color"],
        note_id,
        user_id

    ))

    conn.commit()
    actualizado = cur.rowcount
    cur.close()
    conn.close()

    if actualizado == 0:
        return jsonify({
            "error": "La respuesta no existe."
        }),404
    return jsonify({
        "status":"ok"
    })

@app.route('/delete_note/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    if "user_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    user_id = session["user_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM notes WHERE id=%s AND user_id=%s
    """,(note_id,user_id))

    conn.commit()
    eliminado = cur.rowcount
    cur.close()
    conn.close()

    if eliminado == 0:
        return jsonify({
            "error":"La respuesta no existe."
        }),404

    return jsonify({
        "status":"ok"
    })

@app.route('/update_positions', methods=['PATCH'])
def update_positions():
    if "user_id" not in session:
        return jsonify({"error":"No autorizado"}),401

    data = request.get_json()
    user_id = session["user_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    for posicion in data["positions"]:

        cur.execute("""
            UPDATE notes SET position=%s WHERE id=%s AND user_id=%s
        """,(
            posicion["position"],
            posicion["id"],
            user_id
        ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "status":"ok"
    })

#-------------------------------------  chat ia  ----------------------------------------

@app.route('/Chat_IA')
def chat_ia():
    return render_template('chat_ia.html')

@app.route("/api/chat", methods=["POST"])
def api_chat():

    try:
        texto = request.form.get("message", "").strip()
        archivo = request.files.get("file")

        if not texto and not archivo:
            return jsonify({
                "success": False,
                "error": "Debe ingresar una consulta o adjuntar un documento."
            }), 400

        tipo_documento = None
        informacion_pdf = None

        if archivo and archivo.filename:

            if not archivo.filename.lower().endswith(".pdf"):
                return jsonify({
                    "success": False,
                    "error": "Solo se permiten archivos PDF."
                }), 400

            nombre_archivo = secure_filename(
                archivo.filename
            )

            ruta_pdf = os.path.join(
                app.config["UPLOAD_FOLDER"],
                nombre_archivo
            )

            archivo.save(ruta_pdf)

            informacion_pdf = analizar_pdf(
                ruta_pdf
            )

            tipo_documento = informacion_pdf["tipo"]

        modelo = "llama3.2"

        contexto = ""

        if informacion_pdf:

            contexto = f"""
Se ha adjuntado un documento PDF.

Información del documento:

- Tipo: {tipo_documento}
- Páginas: {informacion_pdf['paginas']}
- Páginas con texto: {informacion_pdf['paginas_con_texto']}
- Páginas con imágenes: {informacion_pdf['paginas_con_imagenes']}
- Cantidad de imágenes: {informacion_pdf['cantidad_imagenes']}
- Caracteres de texto: {informacion_pdf['caracteres_texto']}

El documento será procesado posteriormente para extraer
su contenido completo.
"""
        prompt = f"""

Responde siempre en español.

Consulta del usuario:

{texto}

{contexto}
"""
        inicio_ollama = time.perf_counter()

        respuesta_ia = consultar_ollama(
            modelo,
            prompt
        )

        fin_ollama = time.perf_counter()

        tiempo_ollama = fin_ollama - inicio_ollama

        return jsonify({

            "success": True,
            "response": respuesta_ia,
            "model": modelo,
            "ollama_time": round(tiempo_ollama, 2),
            "document_type": tipo_documento,
            "document_info": informacion_pdf

        })

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

#-------------------------------------  inicio de sesión  ----------------------------------------

@app.route('/')
def index():
    error_message = session.pop('error_message', None)
    email = session.get('email', None)
    return render_template('index.html', error_message=error_message, email=email)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pin = request.form['pin']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if user:
            if user[2] == pin:
                session['email'] = user[1]
                return redirect('/Generador_Script')
            else:
                error_message = "Las credenciales ingresadas son incorrectas. Por favor, verifica tu correo electrónico y contraseña e inténtalo nuevamente."
                session['error_message'] = {'text': error_message}
                session['email'] = email  # Mantener el correo ingresado en la sesión
                return redirect(url_for('index'))

        else:
            error_message = "La cuenta ingresada no está registrada. Por favor, asegúrate de haber ingresado correctamente tus credenciales o crea una cuenta nueva."
            session['error_message'] = {'text': error_message, 'text_color': text_color,
                                        'font_weight': font_weight}
            return redirect(url_for('index'))

    return render_template('index.html')


@app.route('/Registrar', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        pin = request.form.get('pin')
        confirm_pin = request.form.get('confirm_pin')

        if pin != confirm_pin:
            error_message = "Las contraseñas no coinciden. Por favor, inténtalo de nuevo."
            return render_template('/Registrar', error_message=error_message, pin=pin)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (email, pin) VALUES (%s, %s)",
            (email, pin))
        conn.commit()
        cur.close()
        conn.close()

        return redirect('/')

    return render_template('register.html')


@app.route('/Olvidé_mi_contraseña', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        code = generar_codigo_verificacion()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO new_pin (email, code) VALUES (%s, %s)", (email, code))
        conn.commit()
        cur.close()
        conn.close()

        enviar_correo_verificacion(email, code)

        session['email'] = email
        session['code'] = code

        return redirect(url_for('reset_password'))

    return render_template('forgot_password.html')

@app.route('/Regenerar_Contraseña', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        code = request.form.get('code')
        new_pin = request.form.get('new_pin')
        confirm_pin = request.form.get('confirm_pin')

        if new_pin != confirm_pin:
            error_message = "Las contraseñas no coinciden. Por favor, inténtalo de nuevo."
            return render_template('reset_password.html', error_message=error_message, code=code)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM new_pin WHERE code = %s", (code,))
        password_data = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if password_data:
            email = password_data[0]
            new_pin = request.form.get('new_pin')

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE users SET pin = %s WHERE email= %s", (new_pin, email))
            cur.execute("DELETE FROM new_pin WHERE code = %s", (code,))
            conn.commit()
            cur.close()
            conn.close()

            return redirect(url_for('index'))

        elif 'resend_pin' in request.form:
            code = session.get('code')
            email = session.get('email')
            enviar_correo_verificacion(email, code)
            session.pop('email', None)
            session.pop('code', None)

            return render_template('reset_password.html', email=email, pin=code)

        else:
            error_message = "El código es incorrecto. Por favor, verifica el código e inténtalo de nuevo."
            return render_template('reset_password.html', error_message=error_message, pin_error=True)

    return render_template('reset_password.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
