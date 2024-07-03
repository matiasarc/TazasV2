#--------------------------------------------------------------------
# Instalar con pip install Flask
from flask import Flask, request, jsonify, render_template
from flask import request

# Instalar con pip install flask-cors
from flask_cors import CORS

# Instalar con pip install mysql-connector-python
import mysql.connector

# Si es necesario, pip install Werkzeug
from werkzeug.utils import secure_filename

# No es necesario instalar, es parte del sistema standard de Python
import os
import time
#--------------------------------------------------------------------



app = Flask(__name__)
CORS(app)  # Esto habilitará CORS para todas las rutas

#--------------------------------------------------------------------
class Catalogo:
    #----------------------------------------------------------------
    # Constructor de la clase
    def __init__(self, host, user, password, database):
        # Primero, establecemos una conexión sin especificar la base de datos
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=3306
        )
        self.cursor = self.conn.cursor()

        # Intentamos seleccionar la base de datos
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            # Si la base de datos no existe, la creamos
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err

        # Una vez que la base de datos está establecida, creamos la tabla si no existe
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            idUsuario INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            edad INT NOT NULL,
            dineroTotal DECIMAL(10, 2) NOT NULL,
            imagen_url VARCHAR(255),
            nroDeCompras INT(4))''')
        self.conn.commit()

        # Cerrar el cursor inicial y abrir uno nuevo con el parámetro dictionary=True
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)
        
    #----------------------------------------------------------------
    def agregar_usuario(self, nombre, edad, dineroTotal, imagen, nroDeCompras):
               
        sql = "INSERT INTO usuarios (nombre, edad, dineroTotal, imagen_url, nroDeCompras) VALUES (%s, %s, %s, %s, %s)"
        valores = (nombre, edad, dineroTotal, imagen, nroDeCompras)

        self.cursor.execute(sql, valores)        
        self.conn.commit()
        return self.cursor.lastrowid

    #----------------------------------------------------------------
    def consultar_usuario(self, idUsuario):
        # Consultamos un usuario a partir de su código
        self.cursor.execute(f"SELECT * FROM usuarios WHERE idUsuario = {idUsuario}")
        return self.cursor.fetchone()

    #----------------------------------------------------------------
    def modificar_usuario(self, idUsuario, nuevo_nombre, nueva_edad, nuevo_dineroTotal, nueva_imagen, nuevo_cantidadCompras):
        sql = "UPDATE usuarios SET nombre = %s, edad = %s, dineroTotal = %s, imagen_url = %s, nroDeCompras = %s WHERE idUsuario = %s"
        valores = (nuevo_nombre, nueva_edad, nuevo_dineroTotal, nueva_imagen, nuevo_cantidadCompras, idUsuario)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

    #----------------------------------------------------------------
    def listar_usuarios(self):
        self.cursor.execute("SELECT * FROM usuarios")
        usuarios = self.cursor.fetchall()
        return usuarios

    #----------------------------------------------------------------
    def eliminar_usuarios(self, idUsuario):
        # Eliminamos un usuario de la tabla a partir de su código
        self.cursor.execute(f"DELETE FROM usuarios WHERE idUsuario = {idUsuario}")
        self.conn.commit()
        return self.cursor.rowcount > 0

    #----------------------------------------------------------------
    def mostrar_usuarios(self, idUsuario):
        # Mostramos los datos de un usuario a partir de su código
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


#--------------------------------------------------------------------
# Cuerpo del programa
#--------------------------------------------------------------------
# Crear una instancia de la clase Catalogo
catalogo = Catalogo(host='sql10.freemysqlhosting.net', user='sql10717353', password='nIZtbnw9yy', database='sql10717353')
#catalogo = Catalogo(host='7qv.h.filess.io', user='cac_broaddawn', password='dd8f805bf4a8c0e20a14c957109a81645a243e55', database='cac_broaddawn')
#catalogo = Catalogo(host='USUARIO.mysql.pythonanywhere-services.com', user='USUARIO', password='CLAVE', database='USUARIO$miapp')


# Carpeta para guardar las imagenes.
RUTA_DESTINO = 'imagenesUsr/'

#Al subir al servidor, deberá utilizarse la siguiente ruta. USUARIO debe ser reemplazado por el nombre de usuario de Pythonanywhere
#RUTA_DESTINO = '/home/USUARIO/mysite/static/imagenes'


#--------------------------------------------------------------------
# Listar todos los usuarios
#--------------------------------------------------------------------
#La ruta Flask /usuarios con el método HTTP GET está diseñada para proporcionar los detalles de todos los usuarios almacenados en la base de datos.
#El método devuelve una lista con todos los usuarios en formato JSON.
@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    usuarios = catalogo.listar_usuarios()
    return jsonify(usuarios)


#--------------------------------------------------------------------
# Mostrar un sólo usuario según su código
#--------------------------------------------------------------------
#La ruta Flask /usuarios/<int:idUsuario> con el método HTTP GET está diseñada para proporcionar los detalles de un usuario específico basado en su código.
#El método busca en la base de datos el usuario con el código especificado y devuelve un JSON con los detalles del usuario si lo encuentra, o None si no lo encuentra.
@app.route("/usuarios/<int:idUsuario>", methods=["GET"])
def mostrar_usuarios(idUsuario):
    usuario = catalogo.consultar_usuario(idUsuario)
    if usuario:
        return jsonify(usuario), 201
    else:
        return "Usuario no encontrado", 404


#--------------------------------------------------------------------
# Agregar un usuario
#--------------------------------------------------------------------
@app.route("/usuarios", methods=["POST"])
#La ruta Flask `/usuarios` con el método HTTP POST está diseñada para permitir la adición de un nuevo usuario a la base de datos.
#La función agregar_usuario se asocia con esta URL y es llamada cuando se hace una solicitud POST a /usuarios.
def agregar_usuario():
    #Recojo los datos del form
    nombre = request.form['nombre']
    edad = request.form['edad']
    dineroTotal = request.form['dineroTotal']
    imagen = request.files['imagen']
    nroDeCompras = request.form['nroDeCompras']  
    nombre_imagen=""

    
    # Genero el nombre de la imagen.
    nombre_imagen = secure_filename(imagen.filename) #Chequea el nombre del archivo de la imagen, asegurándose de que sea seguro para guardar en el sistema de archivos
    nombre_base, extension = os.path.splitext(nombre_imagen) #Separa el nombre del archivo de su extensión.
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" #Genera un nuevo nombre para la imagen usando un timestamp, para evitar sobreescrituras y conflictos de nombres.

    nuevo_codigo = catalogo.agregar_usuario(nombre, edad, dineroTotal, nombre_imagen, nroDeCompras)
    if nuevo_codigo:    
        imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))
        print("Se guardo!")
        #Si el usuario se agrega con éxito, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 201 (Creado).
        return jsonify({"mensaje": "Usuario agregado correctamente.", "idUsuario": nuevo_codigo, "imagen": nombre_imagen}), 201
    else:
        #Si el usuario no se puede agregar, se devuelve una respuesta JSON con un mensaje de error y un código de estado HTTP 500 (Internal Server Error).
        return jsonify({"mensaje": "Error al agregar el usuario pyth."}), 500
    

#--------------------------------------------------------------------
# Modificar un usuario según su código
#--------------------------------------------------------------------
@app.route("/usuarios/<int:idUsuario>", methods=["PUT"])
#La ruta Flask /usuarios/<int:idUsuario> con el método HTTP PUT está diseñada para actualizar la información de un usuario existente en la base de datos, identificado por su código.
#La función modificar_usuario se asocia con esta URL y es invocada cuando se realiza una solicitud PUT a /usuarios/ seguido de un número (el código del usuario).
def modificar_usuario(idUsuario):
    #Se recuperan los nuevos datos del formulario
    nuevo_nombre = request.form.get("nombre")
    nueva_edad = request.form.get("edad")
    nuevo_dineroTotal = request.form.get("dineroTotal")
    nuevo_cantidadCompras = request.form.get("nroDeCompras")
    
    
    # Verifica si se proporcionó una nueva imagen
    if 'imagen' in request.files:
        imagen = request.files['imagen']
        # Procesamiento de la imagen
        nombre_imagen = secure_filename(imagen.filename) #Chequea el nombre del archivo de la imagen, asegurándose de que sea seguro para guardar en el sistema de archivos
        nombre_base, extension = os.path.splitext(nombre_imagen) #Separa el nombre del archivo de su extensión.
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" #Genera un nuevo nombre para la imagen usando un timestamp, para evitar sobreescrituras y conflictos de nombres.

        # Guardar la imagen en el servidor
        imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))
        
        # Busco el usuario guardado
        usuario = catalogo.consultar_usuario(idUsuario)
        if usuario: # Si existe el usuario...
            imagen_vieja = usuario["imagen_url"]
            # Armo la ruta a la imagen
            ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

            # Y si existe la borro.
            if os.path.exists(ruta_imagen):
                os.remove(ruta_imagen)
    
    else:
        # Si no se proporciona una nueva imagen, simplemente usa la imagen existente del usuario
        usuario = catalogo.consultar_usuario(idUsuario)
        if usuario:
            nombre_imagen = usuario["imagen_url"]


    # Se llama al método modificar_usuario pasando el idUsuario del usuario y los nuevos datos.
    if catalogo.modificar_usuario(idUsuario, nuevo_nombre, nueva_edad, nuevo_dineroTotal, nombre_imagen, nuevo_cantidadCompras):
        
        #Si la actualización es exitosa, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
        return jsonify({"mensaje": "Usuario modificado"}), 200
    else:
        #Si el usuario no se encuentra (por ejemplo, si no hay ningún usuario con el código dado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado).
        return jsonify({"mensaje": "Usuario no encontrado"}), 404



#--------------------------------------------------------------------
# Eliminar un usuario según su código
#--------------------------------------------------------------------
@app.route("/usuarios/<int:idUsuario>", methods=["DELETE"])
#La ruta Flask /usuarios/<int:idUsuario> con el método HTTP DELETE está diseñada para eliminar un usuario específico de la base de datos, utilizando su código como identificador.
#La función eliminar_usuarios se asocia con esta URL y es llamada cuando se realiza una solicitud DELETE a /usuarios/ seguido de un número (el código del usuario).
def eliminar_usuarios(idUsuario):
    # Busco el usuario en la base de datos
    usuario = catalogo.consultar_usuario(idUsuario)
    if usuario: # Si el usuario existe, verifica si hay una imagen asociada en el servidor.
        imagen_vieja = usuario["imagen_url"]
        # Armo la ruta a la imagen
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

        # Y si existe, la elimina del sistema de archivos.
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

        # Luego, elimina el usuario del catálogo
        if catalogo.eliminar_usuarios(idUsuario):
            #Si el usuario se elimina correctamente, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
            return jsonify({"mensaje": "Usuario eliminado"}), 200
        else:
            #Si ocurre un error durante la eliminación (por ejemplo, si el usuario no se puede eliminar de la base de datos por alguna razón), se devuelve un mensaje de error con un código de estado HTTP 500 (Error Interno del Servidor).
            return jsonify({"mensaje": "Error al eliminar el usuario"}), 500
    else:
        #Si el usuario no se encuentra (por ejemplo, si no existe un usuario con el idUsuario proporcionado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado). 
        return jsonify({"mensaje": "Usuario no encontrado"}), 404

#--------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)