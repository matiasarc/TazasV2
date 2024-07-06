from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="Julian",
        password="admin",
        database="tienda_tazas"
    )

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if verify_login(username, password):
        session['logged_in'] = True
        return redirect(url_for('admin'))
    else:
        return "Nombre de usuario o contraseña incorrectos"

def verify_login(username, password):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        cursor.fetchall()
        return user is not None
    except Error as e:
        print(f"Error al verificar el login: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    tazas = get_all_tazas()
    taza_to_delete = session.pop('taza_to_delete', None)
    taza_to_delete_name = session.pop('taza_to_delete_name', None)
    return render_template('admin.html', tazas=tazas, taza_to_delete=taza_to_delete, taza_to_delete_name=taza_to_delete_name)

def get_all_tazas():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tazas')
        tazas = cursor.fetchall()
        return tazas
    except Error as e:
        print(f"Error al obtener las tazas: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/add_taza', methods=['POST'])
def add_taza():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    nombre = request.form['nombre']
    precio = request.form['precio']
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tazas (nombre, precio) VALUES (%s, %s)', (nombre, precio))
        conn.commit()
        return redirect(url_for('admin'))
    except Error as e:
        print(f"Error al agregar la taza: {e}")
        return "Hubo un error al agregar la taza"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/delete_taza', methods=['POST'])
def delete_taza():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    taza_id = request.form['id']
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT nombre FROM tazas WHERE id = %s', (taza_id,))
        taza_name = cursor.fetchone()
        if taza_name:
            taza_name = taza_name[0]
            session['taza_to_delete'] = taza_id
            session['taza_to_delete_name'] = taza_name
        else:
            session['taza_to_delete'] = None
            session['taza_to_delete_name'] = None
    except Error as e:
        print(f"Error al obtener el nombre de la taza: {e}")
        session['taza_to_delete_name'] = ""
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
    return redirect(url_for('admin'))

@app.route('/confirm_delete_taza', methods=['POST'])
def confirm_delete_taza():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    taza_id = request.form['id']
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tazas WHERE id = %s', (taza_id,))
        conn.commit()
        return redirect(url_for('admin'))
    except Error as e:
        print(f"Error al eliminar la taza: {e}")
        return "Hubo un error al eliminar la taza"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
