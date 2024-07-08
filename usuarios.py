from flask import Flask, request, jsonify, render_template
from flask import request
from flask_cors import CORS
import mysql.connector
from werkzeug.utils import secure_filename
import os
import time


usuariosFlask = Flask(__name__)
CORS(usuariosFlask)  # Esto habilitará CORS para todas las rutas


class UsuariosServer:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=3306
        )
        self.cursor = self.conn.cursor()

        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            idUsuario INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            edad INT NOT NULL,
            dineroTotal DECIMAL(10, 2) NOT NULL,
            imagen_url VARCHAR(255),
            nroDeCompras INT(4))''')
        self.conn.commit()

        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)
        
    def agregar_usuario(self, nombre, edad, dineroTotal, imagen, nroDeCompras):
               
        sql = "INSERT INTO usuarios (nombre, edad, dineroTotal, imagen_url, nroDeCompras) VALUES (%s, %s, %s, %s, %s)"
        valores = (nombre, edad, dineroTotal, imagen, nroDeCompras)
        self.cursor.execute(sql, valores)        
        self.conn.commit()
        return self.cursor.lastrowid

    def consultar_usuario(self, idUsuario):
        self.cursor.execute(f"SELECT * FROM usuarios WHERE idUsuario = {idUsuario}")
        return self.cursor.fetchone()

    def modificar_usuario(self, idUsuario, nuevo_nombre, nueva_edad, nuevo_dineroTotal, nueva_imagen, nuevo_cantidadCompras):
        sql = "UPDATE usuarios SET nombre = %s, edad = %s, dineroTotal = %s, imagen_url = %s, nroDeCompras = %s WHERE idUsuario = %s"
        valores = (nuevo_nombre, nueva_edad, nuevo_dineroTotal, nueva_imagen, nuevo_cantidadCompras, idUsuario)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def listar_usuarios(self):
        self.cursor.execute("SELECT * FROM usuarios")
        usuarios = self.cursor.fetchall()
        return usuarios

    def eliminar_usuarios(self, idUsuario):
        self.cursor.execute(f"DELETE FROM usuarios WHERE idUsuario = {idUsuario}")
        self.conn.commit()
        return self.cursor.rowcount > 0

    def mostrar_usuarios(self, idUsuario):
        usuario = self.consultar_usuario(idUsuario)
        if usuario:
            print("-" * 40)
            print(f"ID Usuario.: {usuario['idUsuario']}")
            print(f"Nombre.....: {usuario['nombre']}")
            print(f"Edad.......: {usuario['edad']}")
            print(f"Dinero.....: {usuario['dineroTotal']}")
            print(f"Imagen.....: {usuario['imagen_url']}")
            print(f"Proveedor..: {usuario['nroDeCompras']}")
            print("-" * 40)
        else:
            print("Usuario no encontrado.")


#====================================================================================================

objUsuarios = UsuariosServer(host='sql10.freemysqlhosting.net', user='sql10717353', password='nIZtbnw9yy', database='sql10717353')
#objUsuarios = UsuariosServer(host='7qv.h.filess.io', user='cac_broaddawn', password='dd8f805bf4a8c0e20a14c957109a81645a243e55', database='cac_broaddawn')
#objUsuarios = UsuariosServer(host='USUARIO.mysql.pythonanywhere-services.com', user='USUARIO', password='CLAVE', database='USUARIO$miapp')

RUTA_DESTINO = 'imagenesUsr/'

@usuariosFlask.route("/usuarios", methods=["GET"])
def listar_usuarios():
    usuarios = objUsuarios.listar_usuarios()
    return jsonify(usuarios)

@usuariosFlask.route("/usuarios/<int:idUsuario>", methods=["GET"])
def mostrar_usuarios(idUsuario):
    usuario = objUsuarios.consultar_usuario(idUsuario)
    if usuario:
        return jsonify(usuario), 201
    else:
        return "Usuario no encontrado", 404


@usuariosFlask.route("/usuarios", methods=["POST"])
def agregar_usuario():
    nombre = request.form['nombre']
    edad = request.form['edad']
    dineroTotal = request.form['dineroTotal']
    imagen = request.files['imagen']
    nroDeCompras = request.form['nroDeCompras']  
    nombre_imagen=""

    nombre_imagen = secure_filename(imagen.filename) 
    nombre_base, extension = os.path.splitext(nombre_imagen)
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"

    nuevo_codigo = objUsuarios.agregar_usuario(nombre, edad, dineroTotal, nombre_imagen, nroDeCompras)
    if nuevo_codigo:    
        imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))
        print("Se guardo!")
        return jsonify({"mensaje": "Usuario agregado correctamente.", "idUsuario": nuevo_codigo, "imagen": nombre_imagen}), 201
    else:
        return jsonify({"mensaje": "Error al agregar el usuario pyth."}), 500
    

@usuariosFlask.route("/usuarios/<int:idUsuario>", methods=["PUT"])
def modificar_usuario(idUsuario):
    nuevo_nombre = request.form.get("nombre")
    nueva_edad = request.form.get("edad")
    nuevo_dineroTotal = request.form.get("dineroTotal")
    nuevo_cantidadCompras = request.form.get("nroDeCompras")
    
    if 'imagen' in request.files:
        imagen = request.files['imagen']
        nombre_imagen = secure_filename(imagen.filename)
        nombre_base, extension = os.path.splitext(nombre_imagen)
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"
        imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))
        
        usuario = objUsuarios.consultar_usuario(idUsuario)
        if usuario:
            imagen_vieja = usuario["imagen_url"]
            ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)
            if os.path.exists(ruta_imagen):
                os.remove(ruta_imagen)
    
    else:
        usuario = objUsuarios.consultar_usuario(idUsuario)
        if usuario:
            nombre_imagen = usuario["imagen_url"]

    if objUsuarios.modificar_usuario(idUsuario, nuevo_nombre, nueva_edad, nuevo_dineroTotal, nombre_imagen, nuevo_cantidadCompras):
        return jsonify({"mensaje": "Usuario modificado"}), 200
    else:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404


@usuariosFlask.route("/usuarios/<int:idUsuario>", methods=["DELETE"])
def eliminar_usuarios(idUsuario):
    usuario = objUsuarios.consultar_usuario(idUsuario)
    if usuario:
        imagen_vieja = usuario["imagen_url"]
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)
        if objUsuarios.eliminar_usuarios(idUsuario):
            return jsonify({"mensaje": "Usuario eliminado"}), 200
        else:
            return jsonify({"mensaje": "Error al eliminar el usuario"}), 500
    else:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404



if __name__ == "__main__":
    usuariosFlask.run(debug=True)