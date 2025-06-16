from flask import Flask, session,redirect, url_for, jsonify, render_template,request, send_file
import bcrypt
import mysql.connector
import mysql.connector.errors
from flask_wtf.csrf import CSRFProtect
import random
import string
import io
from news_scripts import get_news
from io import BytesIO
from urllib.parse import urlparse
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os
import pandas as pd

app = Flask(__name__)

app.secret_key = '@\xf6\xdd\x16.\x9b?\xbbHx\xc0\x95fr\x1b\xb7\xf5l\tF\xfe\xf4\xa4\x1a'

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'xls', 'xlsx'}

# Función para verificar la extensión del archivo
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_db_connection():
    try:
        conexion = mysql.connector.connect(
            host='192.168.88.214',      
            user='callmyway',     
            password='call$9222',  
            database='Script_Teams',
        )
        return conexion
    except ConnectionError as e:
        print(f"Error al conectar a MySQL: {e}")
        return None
    
def log_script_creation(user_name, script_name, description):
    conn = get_db_connection()
    if conn is None:
        print("Error: No se pudo conectar a la base de datos")
        return
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO script_creation_log (user_name, script_name, description) 
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (user_name, script_name, description))
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error al registrar la creación del script: {err}")

def get_script_creation_logs():
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT log_id, user_name, script_name, creation_time, description FROM script_creation_log")
        logs = cursor.fetchall()
        cursor.close()
        conn.close()
        return logs
    except mysql.connector.Error as err:
        print(f"Error en la consulta de base de datos: {err}")
        return []

def get_accounts():
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_cuenta, cuenta_id, nombre_cuenta FROM cuenta")
        cuentas = cursor.fetchall()
        cursor.close()
        conn.close()
        return cuentas
    except mysql.connector.Error as err:
        print(f"Error en la consulta de base de datos: {err}")
        return []
    
def get_account(id):
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre_cuenta FROM cuenta WHERE id_cuenta = %s", (id,))
        cuentas = cursor.fetchall()
        cursor.close()
        conn.close()
        return cuentas
    except mysql.connector.Error as err:
        print(f"Error en la consulta de base de datos: {err}")
        return []
    
def get_account_newAccount(id):
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT cuenta_id, nombre_cuenta FROM cuenta WHERE id_cuenta = %s", (id,))
        cuentas = cursor.fetchall()
        cursor.close()
        conn.close()
        return cuentas
    except mysql.connector.Error as err:
        print(f"Error en la consulta de base de datos: {err}")
        return []
    
def get_policy(id):
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT  p.id, cp.id_cuenta, p.nombre
            FROM cuenta_politicas cp
            JOIN politicas p ON cp.id_politica = p.id
            WHERE cp.id_cuenta = %s
        """, (id,))
        descriptions = cursor.fetchall()
        cursor.close()
        conn.close()
        return descriptions
    except mysql.connector.Error as err:
        print(f"Error en la consulta de base de datos: {err}")
        return []
    

def get_policy_account():
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT DISTINCT c.id_cuenta, c.nombre_cuenta
                       FROM cuenta c
                       JOIN cuenta_politicas cp ON c.id_cuenta = cp.id_cuenta;
                       """)
        accounts = cursor.fetchall()
        cursor.close()
        conn.close()
        return accounts
    except mysql.connector.Error as err:
        print(f"Error en la consulta de base de datos: {err}")
        return []


def get_policy_descriptions_accounts(account_id):
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.nombre, p.descripcion
            FROM politicas p
            JOIN cuenta_politicas cp ON p.id = cp.id_politica
            WHERE cp.id_cuenta = %s ORDER BY CASE WHEN prioridad IS NULL THEN 1 ELSE 0 END, prioridad ASC;
        """, (account_id,))
        policies = cursor.fetchall()
        cursor.close()
        conn.close()
        return policies
    except mysql.connector.Error as err:
        print(f"Error en la consulta de base de datos: {err}")
        return []

def get_policy_descriptions():
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id ,nombre, descripcion, prioridad, active FROM politicas ORDER BY CASE WHEN prioridad IS NULL THEN 1 ELSE 0 END, prioridad ASC")
        descriptions = cursor.fetchall()
        cursor.close()
        conn.close()
        return descriptions
    except mysql.connector.Error as err:
        print(f"Error en la consulta de base de datos: {err}")
        return []

def get_policy_descriptions_Baja():
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id,nombre, descripcion, prioridad, active FROM politicas_Baja ORDER BY CASE WHEN prioridad IS NULL THEN 1 ELSE 0 END, prioridad ASC")
        descriptions = cursor.fetchall()
        cursor.close()
        conn.close()
        return descriptions
    except mysql.connector.Error as err:
        print(f"Error en la consulta de base de datos: {err}")
        return []
    

def get_policy_descriptions_NewAccount():
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre_politica, descripcion FROM politicas_nuevo_Cliente ORDER BY CASE WHEN prioridad IS NULL THEN 1 ELSE 0 END, prioridad ASC")
        descriptions = cursor.fetchall()
        cursor.close()
        conn.close()
        return descriptions
    except mysql.connector.Error as err:
        print(f"Error en la consulta de base de datos: {err}")
        return []
    

@app.route('/log')
def log():
    logs = get_script_creation_logs()
    return render_template('log.html', user=session.get('user'), logs=logs)


@app.route('/get-account-E/<int:account_id>')
def get_account_E(account_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM politicas_nuevo_Cliente WHERE id = %s", (account_id,))
        account_info = cursor.fetchone()
        if account_info:
            return jsonify({'nombre_politica': account_info[2], 'descripcion': account_info[2]})
        else:
            return jsonify({'error': 'Usuario no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


    

def get_policy_scripts_E(id):
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre_politica, descripcion FROM politicas_nuevo_Cliente WHERE id = %s", (id,))
        descriptions = cursor.fetchall()
        cursor.close()
        conn.close()
        return descriptions
    except mysql.connector.Error as err:
        print(f"Error en la consulta de base de datos: {err}")
        return []
    


@app.route('/get-account-info/<int:account_id>')
def get_account_info(account_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cuenta WHERE id_cuenta = %s", (account_id,))
        account_info = cursor.fetchone()
        if account_info:
            return jsonify({'nombre_cuenta': account_info[2], 'cuenta_id': account_info[1]})
        else:
            return jsonify({'error': 'Usuario no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/get-user-info/<int:user_id>')
def get_user_info(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre_usuario FROM usuarios WHERE id_usuario = %s", (user_id,))
        user_info = cursor.fetchone()
        if user_info:
            return jsonify({'nombre_usuario': user_info[0]})
        else:
            return jsonify({'error': 'Usuario no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_users():
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id_usuario, u.nombre_usuario, r.nombre_rol
            FROM usuarios u
            JOIN usuario_roles ur ON u.id_usuario = ur.id_usuario
            JOIN roles r ON ur.id_rol = r.id_rol
        """)
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return users
    except mysql.connector.Error as err:
        print(f"Error en la consulta de base de datos: {err}")
        return []

@app.route('/docs')
def docs():
    if 'role' in session and session['role'] == 'Administrador':
        return render_template('docs.html', user=session.get('user'))
    else:
        return render_template('soporte.html')

@app.route('/admin')
def admin_dashboard():
    if 'role' in session and session['role'] == 'Administrador':
        descriptions = get_policy_descriptions()
        return render_template('PoliticasTeams.html', user=session.get('user'), descriptions=descriptions)
    else:
        return render_template('soporte.html')

@app.route('/soporte')
def user_dashboard():
    if 'role' in session and session['role'] == 'Usuario':
        return render_template('index.html',user=session.get('user'))
    else:
        return render_template('soporte.html')

@app.route('/inicio', methods=['GET', 'POST'])
def soporte():
   if request.method == 'POST':
        usuario = request.form['text']
        contraseña_ingresada = request.form['password'].encode('utf-8')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.hash_contraseña, r.nombre_rol
            FROM usuarios u
            INNER JOIN usuario_roles ur ON u.id_usuario = ur.id_usuario
            INNER JOIN roles r ON ur.id_rol = r.id_rol
            WHERE u.nombre_usuario = %s
        """, (usuario,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.checkpw(contraseña_ingresada, user[0].encode('utf-8')): # type: ignore
            session['user'] = usuario
            session['role'] = user[1] 
            print(session['role'])
            if user[1] == 'Administrador':
                return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('soporte'))
        
   return render_template('soporte.html')

@app.route('/logout')
def logout():
    session.clear()  
    return render_template('soporte.html')

@app.route('/get-politicas')
def get_politicas():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, active FROM politicas")
    politicas = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([{'id': pol[0], 'nombre': pol[1], 'active': pol[2]} for pol in politicas])

@app.route('/get-politicas-baja')
def get_politicas_baja():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, active FROM politicas_Baja")
    politicas = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([{'id': pol[0], 'nombre': pol[1], 'active': pol[2]} for pol in politicas])


@app.route('/update-users', methods=['POST'])
def update_users():
    user_id = request.form['UserSelect']
    nombre_usuario = request.form['UserName']
    nueva_contraseña = request.form['UserPassword']
    rol_id = request.form['roles']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if nueva_contraseña or rol_id:
            if nueva_contraseña:
                hashed_password = bcrypt.hashpw(nueva_contraseña.encode('utf-8'), bcrypt.gensalt())
                cursor.execute("UPDATE usuarios SET nombre_usuario = %s, hash_contraseña = %s WHERE id_usuario = %s", (nombre_usuario, hashed_password, user_id))
            if rol_id:
                cursor.execute("UPDATE usuario_roles SET id_rol = %s WHERE id_usuario = %s", (rol_id, user_id))
        else:
            cursor.execute("UPDATE usuarios SET nombre_usuario = %s WHERE id_usuario = %s", (nombre_usuario, user_id))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error SQL: {err}")
        conn.rollback()
        return "Error al actualizar el usuario", 500
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('usuarios'))


@app.route('/usuarios')
def usuarios():
    if 'role' in session and session['role'] == 'Administrador':
        users = get_users()
        return render_template('Usuarios.html', user=session['user'], users = users)
    return redirect(url_for('soporte'))

@app.route('/cuentas')
def cuentas():
    if 'role' in session and session['role'] == 'Administrador':
        accounts = get_accounts()
        descriptions = get_policy_descriptions()
        return render_template('cuentas.html', user=session['user'], accounts = accounts, descriptions = descriptions)
    return redirect(url_for('soporte'))
               
@app.route('/cuentas_detalles')
def cuentas_detalles():
    if 'role' in session and session['role'] == 'Administrador':
        id_cuenta = request.args.get('id')
        print(id_cuenta)
        account = get_account(id_cuenta)
        print(account)
        policies = get_policy(id_cuenta)
        print(policies)
        return render_template('cuentas_detalles.html', user=session['user'], account = account, policies = policies)
    return redirect(url_for('soporte'))
       
@app.route('/scripts')
def scripts():
    if 'role' in session and session['role'] == 'Administrador':
        return render_template('scripts.html', user=session.get('user'))
    elif 'role' in session and session['role'] == 'Usuario':
        return render_template('index.html', user=session.get('user'))
    return redirect(url_for('soporte'))


@app.route('/scriptsAccount')
def scriptsAccount():
    if 'role' in session and session['role'] == 'Administrador':
        accounts = get_policy_account()
        return render_template('scriptsAccount.html', user=session.get('user'), accounts=accounts)
    elif 'role' in session and session['role'] == 'Usuario':
        return render_template('index.html', user=session.get('user'))
    return redirect(url_for('soporte'))


@app.route('/scriptsAccountUser')
def scriptsAccountUser():
    if 'role' in session and session['role'] == 'Usuario':
        accounts = get_policy_account()
        return render_template('scriptsAccountUser.html', user=session.get('user'), accounts=accounts)
    elif 'role' in session and session['role'] == 'Usuario':
        return render_template('index.html', user=session.get('user'))
    return redirect(url_for('soporte'))

@app.route('/news')
def news():
    if 'user' in session and session['role'] == 'Usuario':
        bitcoin_articles, tech_articles = get_news()
        return render_template('news.html', user=session['user'], bitcoin_articles=bitcoin_articles, tech_articles=tech_articles)
    return redirect(url_for('soporte'))

@app.route('/genPass')
def genPass():
    if 'user' in session and session['role'] == 'Usuario':
        users = get_users()
        return render_template('generadorPass.html', user=session['user'], users = users)
    return redirect(url_for('soporte'))


@app.route('/politicasTeams')
def politicasTeams():
    if 'role' in session and session['role'] == 'Administrador':
        descriptions = get_policy_descriptions()
        return render_template('PoliticasTeams.html', user=session.get('user'), descriptions=descriptions)
    return redirect(url_for('soporte'))

@app.route('/PoliticasTeamsBaja')
def PoliticasTeamsBaja():
    if 'role' in session and session['role'] == 'Administrador':
        descriptions = get_policy_descriptions_Baja()
        return render_template('PoliticasTeamsBaja.html', user=session.get('user'), descriptions=descriptions)
    return redirect(url_for('soporte'))

#Scripts Cliente Nuevo
@app.route('/PoliticasClienteNuevo')
def PoliticasClienteNuevo():
    if 'role' in session and session['role'] == 'Administrador':
        descriptions = get_policy_descriptions_NewAccount()
        return render_template('PoliticasNuevoCliente.html', user=session.get('user'), descriptions=descriptions)
    return redirect(url_for('soporte'))

# Politicas Cliente Nuevo
@app.route('/ScriptsClienteNuevo')
def ScriptsClienteNuevo():
    if 'role' in session and session['role'] == 'Administrador':
        accounts = get_policy_account()
        descriptions = get_policy_descriptions_NewAccount()
        return render_template('ScriptsNuevoCliente.html', user=session.get('user'), accounts=accounts,descriptions=descriptions)
    return redirect(url_for('soporte'))

@app.route('/add-user', methods=['POST'])
def add_user():
    nombre_usuario = request.form['nombreUsuario']
    contraseña = request.form['password']
    rol_id = request.form['roles']

    # Encriptar la contraseña
    hashed_password = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())
    conn = get_db_connection()
    if conn is None:
        return "Error de conexión a la base de datos", 500

    try:
        cursor = conn.cursor()
        # Insertar el usuario
        cursor.execute("""
            INSERT INTO usuarios (nombre_usuario, hash_contraseña) VALUES (%s, %s)
        """, (nombre_usuario, hashed_password))

        # Obtener el ID del usuario insertado
        user_id = cursor.lastrowid

        # Asignar rol al usuario
        cursor.execute("""
            INSERT INTO usuario_roles (id_usuario, id_rol) VALUES (%s, %s)
        """, (user_id, int(rol_id)))

        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Error SQL: {err}")
        return "Error al crear el usuario", 500
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_dashboard'))



@app.route('/update_policy', methods=['POST'])
def update_policy():
    data = request.get_json()
    policy_id = data.get('id')
    description = data.get('description')

    if not policy_id or not description:
        return jsonify({'success': False, 'error': 'Faltan datos'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'success': False, 'error': 'No se pudo conectar a la base de datos'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE politicas_nuevo_Cliente
            SET descripcion = %s
            WHERE id = %s
        """, (description, policy_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except mysql.connector.Error as err:
        print(f"Error en la actualización de la base de datos: {err}")
        return jsonify({'success': False, 'error': str(err)}), 500




@app.route('/add-policy', methods=['POST'])
def add_policy():
    policy_name = request.form['namePolicy'] 
    commandExecutable = request.form['commandExecutableAdd'] 
    priorityModify = request.form['priorityAdd'] 
    activeModify = request.form.get('active') == 'on'
    commandText = f'echo "{commandExecutable}"'
    new_policy = commandText + "\n" + commandExecutable
    if policy_name and new_policy:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO politicas(nombre, descripcion,prioridad, active) values (%s,%s,%s,%s)"
        cursor.execute(sql, (policy_name, new_policy, priorityModify,activeModify))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    else:
        return "Error: Falta información necesaria."


@app.route('/update-policy-description', methods=['POST'])
def update_policy_description():
    policy_name = request.form['policyName'] 
    commandExecutable = request.form['commandExecutable'] 
    priorityModify = request.form['priorityA'] 
    activeModify = request.form.get('activeA') == 'on'
    commandText = f'echo "{commandExecutable}"'
    new_description = commandText + "\n" + commandExecutable
    if policy_name and new_description:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "UPDATE politicas SET descripcion = %s, prioridad = %s, active = %s WHERE nombre = %s"
        cursor.execute(sql, (new_description, priorityModify, activeModify, policy_name))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    else:
        return "Error: Falta información necesaria."


## Politica Baja

@app.route('/add-policy-baja', methods=['POST'])
def add_policy_baja():
    policy_name = request.form['namePolicy'] 
    commandExecutable = request.form['commandExecutableAdd'] 
    priorityAdd = request.form['priorityAdd'] 
    activeModify = request.form.get('active') == 'on'
    commandText = f'echo "{commandExecutable}"'
    new_policy = commandText + "\n" + commandExecutable
    if policy_name and new_policy:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO politicas_Baja(nombre, descripcion,prioridad,active) values (%s,%s,%s,%s)"
        cursor.execute(sql, (policy_name, new_policy,priorityAdd,activeModify))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    else:
        return "Error: Falta información necesaria."


@app.route('/update-policy-description-baja', methods=['POST'])
def update_policy_description_baja():
    policy_name = request.form['policyName'] 
    commandExecutable = request.form['commandExecutable'] 
    priorityModify = request.form['priority'] 
    activeModify = request.form.get('activeA') == 'on'
    commandText = f'echo "{commandExecutable}"'
    new_description = commandText + "\n" + commandExecutable
    if policy_name and new_description:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "UPDATE politicas_Baja SET descripcion = %s, prioridad = %s, active = %s WHERE nombre = %s"
        cursor.execute(sql, (new_description, priorityModify, activeModify, policy_name))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    else:
        return "Error: Falta información necesaria."


@app.route('/delete-policy-baja/<int:policy_id>', methods=['POST'])
def delete_policy_baja(policy_id):
    if 'role' in session and session['role'] == 'Administrador':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM politicas_Baja WHERE id = %s", (policy_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    else:
        return "No tiene permiso para realizar esta acción", 403

@app.route('/delete-policy-account/<int:policy_id>/<int:account_id>', methods=['POST'])
def delete_policy_account(policy_id, account_id):
    if 'role' in session and session['role'] == 'Administrador':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cuenta_politicas WHERE id_cuenta = %s AND id_politica = %s", (account_id, policy_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    else:
        return "No tiene permiso para realizar esta acción", 403

@app.route('/delete-policy/<int:policy_id>', methods=['POST'])
def delete_policy(policy_id):
    if 'role' in session and session['role'] == 'Administrador':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM politicas WHERE id = %s", (policy_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    else:
        return "No tiene permiso para realizar esta acción", 403

@app.route('/delete-user/<int:userId>', methods=['POST'])
def delete_user(userId):
    if 'role' in session and session['role'] == 'Administrador':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (userId,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    else:
        return "No tiene permiso para realizar esta acción", 403

@app.route('/generate_password', methods=['POST'])
def generate_password():
    length = int(request.form['length'])
    include_uppercase = 'includeUppercase' in request.form
    include_lowercase = 'includeLowercase' in request.form
    include_symbols = 'includeSymbols' in request.form
    keyword = request.form.get('keyword', '')

    characters = ''
    if include_uppercase:
        characters += string.ascii_uppercase
    if include_lowercase:
        characters += string.ascii_lowercase
    if include_symbols:
        characters += string.punctuation

    if len(characters) == 0:
        characters = string.ascii_letters

    random_part = ''.join(random.choice(characters) for _ in range(length - len(keyword)))

    sustituciones = {
            'a': '@', 'A': '4',
            'b': '8', 'B': '8',
            'c': '<', 'C': '(',
            'e': '3', 'E': '3',
            'g': '9', 'G': '6',
            'i': '!', 'I': '1',
            'l': '1', 'L': '|',
            'o': '0', 'O': '0',
            's': '5', 'S': '$',
            't': '7', 'T': '+',
            'z': '2', 'Z': '2',
            'h': '#', 'H': '#',
            'r': '2', 'R': '2',
            'u': 'μ', 'U': 'μ',
            'v': '√', 'V': '√',
            'x': '%', 'X': '%',
            'd': '<|', 'D': '<|',
            'm': 'M', 'M': '^^',
            'n': '^', 'N': '^',
            'q': '9', 'Q': '9',
            'y': '¥', 'Y': '¥',
            'w': 'ω', 'W': 'ω',
            'k': 'κ', 'K': 'κ',
            'p': 'ρ', 'P': 'ρ',
            'f': '=', 'F': '=',
        }

    modified_keyword = []
    for i, char in enumerate(keyword):
        if i % 2 == 0:
            char = char.upper()
        else:
            char = char.lower()

        modified_char = sustituciones.get(char, char)
        modified_keyword.append(modified_char)

    password = ''.join(modified_keyword) + random_part

    return jsonify({'password': password})



# -----------   Cuentas  ---------------

@app.route('/add-policy-account', methods=['POST'])
def add_policy_account():
    accountSelect = request.form.getlist('AccountSelect[]')
    accountID = request.form['IDAccountSelect']
    conn = get_db_connection()
    cursor = conn.cursor()
    try:      
        for policy in accountSelect:
            cursor.execute("INSERT INTO cuenta_politicas (id_cuenta, id_politica) VALUES (%s, %s)", (accountID, policy))

        conn.commit()
        return redirect(url_for('admin_dashboard'))
    except mysql.connector.Error as error:
        print(f"Failed to insert record into MySQL table: {error}")
        return "Error al agregar la cuenta"
    finally:
        cursor.close()
        conn.close()


@app.route('/add-account', methods=['POST'])
def add_account():
    account_id = request.form['idAccountAdd']
    account_name = request.form['nameAccountAdd']
    conn = get_db_connection()
    cursor = conn.cursor()
    try:      
        cursor.execute("INSERT INTO cuenta (cuenta_id, nombre_cuenta) VALUES (%s, %s)", (account_id, account_name,))
        conn.commit()
        return redirect(url_for('admin_dashboard'))
    except mysql.connector.Error as error:
        print(f"Failed to insert record into MySQL table: {error}")
        return "Error al agregar la cuenta"
    finally:
        cursor.close()
        conn.close()

@app.route('/update-accounts', methods=['POST'])
def update_accounts():
    IDaccount = request.form['accountSelect']
    account_id = request.form['newAccountID']
    account_name = request.form['newAccountName']
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE cuenta SET nombre_cuenta = %s, cuenta_id = %s WHERE id_cuenta = %s", (account_name, account_id , IDaccount))
        conn.commit()
        return redirect(url_for('cuentas'))
    except mysql.connector.Error as error:
        print(f"Failed to update record: {error}")
        return "Error al actualizar la cuenta"
    finally:
        cursor.close()
        conn.close()

@app.route('/delete-account/<int:account_id>', methods=['POST'])
def delete_account(account_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cuenta WHERE id_cuenta = %s", (account_id,))
        conn.commit()
        return redirect(url_for('cuentas'))
    except mysql.connector.Error as error:
        print(f"Failed to delete record: {error}")
        return "Error al eliminar la cuenta"
    finally:
        cursor.close()
        conn.close()

##################################################### SCRIPTS ######################################################################

FirstCode = """
Start-Transcript -Path $env:USERPROFILE\\Desktop\\Config_IMC_nombre.txt
        
Import-Module -Name MicrosoftTeams
Connect-MicrosoftTeams 

"""

@app.route('/altaUser', methods=['POST'])
def alta_user():
    POLICIES = get_policy_descriptions()
    data = request.form
    emails = request.form.getlist('correo[]')
    extensions = request.form.getlist('extension[]')
    numbers = request.form.get('numero')
    names = request.form.get('nombre')
    selected_policies = request.form.getlist('opciones[]')
    processed_policies = []
    processed_policies.append(FirstCode.replace('nombre', names))

    for policy in POLICIES:
        if policy[1] in selected_policies:
            for email, extension in zip(emails, extensions):
                processed_policy = policy[2]
                processed_policy = processed_policy.replace('email', email)
                if 'extension' in processed_policy:
                    processed_policy = processed_policy.replace('extension', extension)
                if 'numero' in processed_policy:
                    processed_policy = processed_policy.replace('numero', numbers)
                processed_policies.append(processed_policy)
                processed_policies.append("\n")
            processed_policies.append("\n")

    script_content = ''.join(processed_policies)
    user=session.get('user')
    log_script_creation(user, names, "Creación Script de Alta")
    return script_content 


@app.route('/bajaUser', methods=['POST'])
def baja_user():
    POLICIES = get_policy_descriptions_Baja()
    data = request.form
    emails = request.form.getlist('correoB[]')
    extensions = request.form.getlist('extensionB[]')
    selected_policies = request.form.getlist('opcionesB[]')
    names = request.form.get('nombre')
    processed_policies = []
    processed_policies.append(FirstCode.replace('nombre', names))

    for policy in POLICIES:
        if policy[1] in selected_policies:
            for email, extension in zip(emails, extensions):
                processed_policy = policy[2]
                processed_policy = processed_policy.replace('email', email)
                if 'extension' in processed_policy:
                    processed_policy = processed_policy.replace('extension', extension)
                processed_policies.append(processed_policy)
                processed_policies.append("\n")
            processed_policies.append("\n")

    script_contentB = ''.join(processed_policies)
    user=session.get('user')
    log_script_creation(user, names, "Creación Script Baja")
    return script_contentB
### END ####

## Alta y baja
@app.route('/altabajaUser', methods=['POST'])
def alta_baja_user():
    POLICIES = get_policy_descriptions()
    POLICIES_BAJA = get_policy_descriptions_Baja()
    data = request.form
    emails = request.form.getlist('correoA[]')
    extensions = request.form.getlist('extensionA[]')
    emailsB = request.form.getlist('correoAB[]')
    extensionsB = request.form.getlist('extensionAB[]')
    selected_policies = request.form.getlist('opciones[]')
    selected_policiesB = request.form.getlist('opcionesB[]')
    names = request.form.get('nombre')
    numbers = request.form.get('numero')
    processed_policies = []
    processed_policies.append(FirstCode.replace('nombre', names))
    i = 0

    # Procesar políticas de baja

    for policyB in POLICIES_BAJA:
        if policyB[1] in selected_policiesB:
            for email, extension in zip(emailsB, extensionsB):
                processed_policy = policyB[2]
                processed_policy = processed_policy.replace('email', email)
                if 'extension' in processed_policy:
                    processed_policy = processed_policy.replace('extension', extension)
                processed_policies.append(processed_policy)
                processed_policies.append("\n")
            processed_policies.append("\n")

    # Procesar políticas de alta

    for policy in POLICIES:
        if policy[1] in selected_policies:
            for email, extension in zip(emails, extensions):
                processed_policy = policy[2]
                processed_policy = processed_policy.replace('email', email)
                if 'extension' in processed_policy:
                    processed_policy = processed_policy.replace('extension', extension)
                if 'numero' in processed_policy:
                    processed_policy = processed_policy.replace('numero', numbers)
                processed_policies.append(processed_policy)
                processed_policies.append("\n")
            processed_policies.append("\n")

    script_content = ''.join(processed_policies)
    user=session.get('user')
    log_script_creation(user, names, "Creación Script Alta y Baja")
    return script_content



##Scripts x Cuenta
@app.route('/accountScripts', methods=['POST'])
def accountScripts():
    data = request.form
    emails = request.form.getlist('correo[]')
    extensions = request.form.getlist('extension[]')
    account_id = request.form.get('policyName')
    numbers = request.form.get('numero')
    POLICIES = get_policy_descriptions_accounts(account_id)
    names = request.form.get('nombre')
    processed_policies = []
    processed_policies.append(FirstCode.replace('nombre', names))

    for policy in POLICIES:
            for email, extension in zip(emails, extensions):
                processed_policy = policy[2]
                processed_policy = processed_policy.replace('email', email)
                if 'extension' in processed_policy:
                    processed_policy = processed_policy.replace('extension', extension)
                if 'numero' in processed_policy:
                    processed_policy = processed_policy.replace('numero', numbers)
                processed_policies.append(processed_policy)
                processed_policies.append("\n")
            processed_policies.append("\n")

    script_contentB = ''.join(processed_policies)
    user=session.get('user')
    log_script_creation(user, names, "Creación Script por Cuenta")
    return script_contentB



##Cliente Nuevo##
@app.route('/newAccountScripts', methods=['POST'])
def newAccountScripts():
    data = request.form
    emails = request.form.getlist('correo[]')
    extensions = request.form.getlist('extension[]')
    account_id = request.form.get('policyName')
    numbers = request.form.get('numero')
    script = request.form.get('scriptESelect')
    POLICIES = get_policy_descriptions_accounts(account_id)
    names = request.form.get('nombre')
    policyNewAccount = get_policy_scripts_E(script)
    accounts = get_account_newAccount(account_id)
    processed_policies = []
 
    for account in accounts:
        account_id = account[0]
        account_name = account[1]
        for newAccount in policyNewAccount:
            policyAccount = newAccount[2]
            if 'nombre' in policyAccount:
                policyAccount = policyAccount.replace('nombre', names)

            if 'name_account' in policyAccount:
                policyAccount = policyAccount.replace('name_account', account_name)

            if 'id_account' in policyAccount:
                policyAccount = policyAccount.replace('id_account', str(account_id))
            processed_policies.append("\n")

        processed_policies.append("\n")

    processed_policies.append(policyAccount)

    for policy in POLICIES:
            for email, extension in zip(emails, extensions):
                processed_policy = policy[2]
                processed_policies.append("\n")
                processed_policies.append("\n")
                processed_policy = processed_policy.replace('email', email)
                if 'extension' in processed_policy:
                    processed_policy = processed_policy.replace('extension', extension)
                if 'numero' in processed_policy:
                    processed_policy = processed_policy.replace('numero', numbers)
                processed_policies.append(processed_policy)
                processed_policies.append("\n")
            processed_policies.append("\n")

    script_contentNewAccount = ''.join(processed_policies)
    user=session.get('user')
    log_script_creation(user, names, "Creación Script Cuenta Nueva")
    return script_contentNewAccount



##################################################### SCRIPTS  Manfred ######################################################################

politicas = []

# Función para obtener políticas
def obtener_politicas_por_dominio_y_extension(correo, tipo_extension):
    global politicas # Indica que estás usando la variable global 
    dominio = correo.split('@')[-1]

    #cursor = mysql.connection.cursor()

    #if tipo_extension == 'altaybaja':
    #    consulta = "SELECT descripcion FROM politicas WHERE dominio = %s AND tipo_politica = %s"
    #    cursor.execute(consulta, (dominio, "baja", "alta"))
    #else:
    #    consulta = "SELECT politica FROM politicas WHERE dominio = %s AND tipo_politica = %s"
    #    cursor.execute(consulta, (dominio, tipo_extension))

    #politicas = cursor.fetchall()
    #cursor.close()

    politicas = "¡¡¡No se han registrado políticas asociadas a este dominio!!!"

    #politicas_formateadas = "<br><br>".join(politica[0] for politica in politicas)

    politicas_formateadas = politicas

    return politicas_formateadas

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route('/script_alta', methods=['GET', 'POST'])
def script_alta():
    if request.method == 'POST':
        correo = request.form.get('correo')
        politicas = obtener_politicas_por_dominio_y_extension(correo, 'alta')
        return render_template('script_alta_busqueda.html', politicas=politicas)
    return render_template('script_alta.html')

@app.route('/script_alta_busqueda', methods=['POST'])
def obtener_politicas():
    correo = request.json.get('correo')
    tipo_extension = request.json.get('tipo_extension')

    politicas = obtener_politicas_por_dominio_y_extension(correo, tipo_extension)
    return jsonify({'politicas': politicas})

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
                    if not correos or not extensiones:
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
    # Ejemplo de carga de políticas

        for correo, extension in zip(correos, extensiones):
            for politica in politicas:
                politica_texto = politica[0]  # Extrae el texto de la política

                # Asegúrate de que el correo no esté vacío
                if correo:
                # Reemplaza el correo en la política
                    politica_texto_reemplazada = politica_texto.replace("{correo}", correo)
                else:
                    print("No se encontró un correo para reemplazar, saltando a la siguiente.")
                    continue  # Si el correo es vacío, continuar con la siguiente iteración

                # Reemplaza la extensión si existe
                if extension:
                    politica_texto_reemplazada = politica_texto_reemplazada.replace("{extension}", extension)
                else:
                    print("No se encontró una extensión para reemplazar, saltando a la siguiente.")
                    continue  # Si la extensión es vacía, continuar con la siguiente iteración

                # Añade la política al archivo PS1
                contenido_ps1 += f'echo "{politica_texto_reemplazada}"\n'
                contenido_ps1 += f'{politica_texto_reemplazada}\n\n'


    elif politicas_seleccionadas == 'dominio' and accion == "baja":

        contenido_ps1 += "#Dar_de_baja\n\n"

        for correo, extension in zip(correos, extensiones):
            for politica in politicas:
                politica_texto = politica[0]  # Extrae el texto de la política

                # Asegúrate de que el correo no esté vacío
                if correo:
                # Reemplaza el correo en la política
                    politica_texto_reemplazada = politica_texto.replace("{correo}", correo)
                else:
                    print("No se encontró un correo para reemplazar, saltando a la siguiente.")
                    continue  # Si el correo es vacío, continuar con la siguiente iteración

                # Reemplaza la extensión si existe
                if extension:
                    politica_texto_reemplazada = politica_texto_reemplazada.replace("{extension}", extension)
                else:
                    print("No se encontró una extensión para reemplazar, saltando a la siguiente.")
                    continue  # Si la extensión es vacía, continuar con la siguiente iteración

                # Añade la política al archivo PS1
                contenido_ps1 += f'echo "{politica_texto_reemplazada}"\n'
                contenido_ps1 += f'{politica_texto_reemplazada}\n\n'


    elif politicas_seleccionadas == 'dominio' and accion == "altaybaja":

        contenido_ps1 += "#Dar_de_baja\n\n"

        for correo_baja, extension_baja in zip(correos_baja, extensiones_baja):
            print("El correo por dominio es: ", correo_dominio)
            obtener_politicas_por_dominio_y_extension(correo_dominio, "baja")
            print("Las politicas de baja son: ",politicas)
            for politica in politicas:
                politica_texto = politica[0]  # Extrae el texto de la política

                # Asegúrate de que el correo no esté vacío
                if correo_baja:
                # Reemplaza el correo en la política
                    politica_texto_reemplazada = politica_texto.replace("{correo}", correo_baja)
                else:
                    print("No se encontró un correo para reemplazar, saltando a la siguiente.")
                    continue  # Si el correo es vacío, continuar con la siguiente iteración

                # Reemplaza la extensión si existe
                if extension_baja:
                    politica_texto_reemplazada = politica_texto_reemplazada.replace("{extension}", extension_baja)
                else:
                    print("No se encontró una extensión para reemplazar, saltando a la siguiente.")
                    continue  # Si la extensión es vacía, continuar con la siguiente iteración

                # Añade la política al archivo PS1
                contenido_ps1 += f'echo "{politica_texto_reemplazada}"\n'
                contenido_ps1 += f'{politica_texto_reemplazada}\n\n'
        
        contenido_ps1 += "#Dar_de_alta\n\n"
            
        for correo_alta, extension_alta in zip(correos_alta, extensiones_alta):
            obtener_politicas_por_dominio_y_extension(correo_dominio, "alta")
            print("Las politicas de alta son: ",politicas)
            for politica in politicas:
                politica_texto = politica[0]  # Extrae el texto de la política

                # Asegúrate de que el correo no esté vacío
                if correo_alta:
                # Reemplaza el correo en la política
                    politica_texto_reemplazada = politica_texto.replace("{correo}", correo_alta)
                else:
                    print("No se encontró un correo para reemplazar, saltando a la siguiente.")
                    continue  # Si el correo es vacío, continuar con la siguiente iteración

                # Reemplaza la extensión si existe
                if extension_alta:
                    politica_texto_reemplazada = politica_texto_reemplazada.replace("{extension}", extension_alta)
                else:
                    print("No se encontró una extensión para reemplazar, saltando a la siguiente.")
                    continue  # Si la extensión es vacía, continuar con la siguiente iteración

                # Añade la política al archivo PS1
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

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
