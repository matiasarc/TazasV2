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
    def agregar_producto(self, nombre, edad, dineroTotal, imagen, nroDeCompras):
               
        sql = "INSERT INTO usuarios (nombre, edad, dineroTotal, imagen_url, nroDeCompras) VALUES (%s, %s, %s, %s, %s)"
        valores = (nombre, edad, dineroTotal, imagen, nroDeCompras)

        self.cursor.execute(sql, valores)        
        self.conn.commit()
        return self.cursor.lastrowid

    #----------------------------------------------------------------
    def consultar_producto(self, idUsuario):
        # Consultamos un producto a partir de su código
        self.cursor.execute(f"SELECT * FROM usuarios WHERE idUsuario = {idUsuario}")
        return self.cursor.fetchone()

    #----------------------------------------------------------------
    def modificar_producto(self, idUsuario, nueva_descripcion, nueva_cantidad, nuevo_precio, nueva_imagen, nuevo_proveedor):
        sql = "UPDATE usuarios SET nombre = %s, edad = %s, dineroTotal = %s, imagen_url = %s, nroDeCompras = %s WHERE idUsuario = %s"
        valores = (nueva_descripcion, nueva_cantidad, nuevo_precio, nueva_imagen, nuevo_proveedor, idUsuario)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

    #----------------------------------------------------------------
    def listar_productos(self):
        self.cursor.execute("SELECT * FROM usuarios")
        usuarios = self.cursor.fetchall()
        return usuarios

    #----------------------------------------------------------------
    def eliminar_producto(self, idUsuario):
        # Eliminamos un producto de la tabla a partir de su código
        self.cursor.execute(f"DELETE FROM usuarios WHERE idUsuario = {idUsuario}")
        self.conn.commit()
        return self.cursor.rowcount > 0

    #----------------------------------------------------------------
    def mostrar_producto(self, idUsuario):
        # Mostramos los datos de un producto a partir de su código
        producto = self.consultar_producto(idUsuario)
        if producto:
            print("-" * 40)
            print(f"ID Usuario.: {producto['idUsuario']}")
            print(f"Nombre.....: {producto['nombre']}")
            print(f"Edad.......: {producto['edad']}")
            print(f"Dinero.....: {producto['dineroTotal']}")
            print(f"Imagen.....: {producto['imagen_url']}")
            print(f"Proveedor..: {producto['nroDeCompras']}")
            print("-" * 40)
        else:
            print("Producto no encontrado.")


#--------------------------------------------------------------------
# Cuerpo del programa
#--------------------------------------------------------------------
# Crear una instancia de la clase Catalogo
catalogo = Catalogo(host='sql10.freemysqlhosting.net', user='sql10717353', password='nIZtbnw9yy', database='sql10717353')
#catalogo = Catalogo(host='7qv.h.filess.io', user='cac_broaddawn', password='dd8f805bf4a8c0e20a14c957109a81645a243e55', database='cac_broaddawn')
#catalogo = Catalogo(host='USUARIO.mysql.pythonanywhere-services.com', user='USUARIO', password='CLAVE', database='USUARIO$miapp')


# Carpeta para guardar las imagenes.
RUTA_DESTINO = 'static/imagenes/'

#Al subir al servidor, deberá utilizarse la siguiente ruta. USUARIO debe ser reemplazado por el nombre de usuario de Pythonanywhere
#RUTA_DESTINO = '/home/USUARIO/mysite/static/imagenes'


#--------------------------------------------------------------------
# Listar todos los usuarios
#--------------------------------------------------------------------
#La ruta Flask /usuarios con el método HTTP GET está diseñada para proporcionar los detalles de todos los usuarios almacenados en la base de datos.
#El método devuelve una lista con todos los usuarios en formato JSON.
@app.route("/usuarios", methods=["GET"])
def listar_productos():
    usuarios = catalogo.listar_productos()
    return jsonify(usuarios)


#--------------------------------------------------------------------
# Mostrar un sólo producto según su código
#--------------------------------------------------------------------
#La ruta Flask /usuarios/<int:idUsuario> con el método HTTP GET está diseñada para proporcionar los detalles de un producto específico basado en su código.
#El método busca en la base de datos el producto con el código especificado y devuelve un JSON con los detalles del producto si lo encuentra, o None si no lo encuentra.
@app.route("/usuarios/<int:idUsuario>", methods=["GET"])
def mostrar_producto(idUsuario):
    producto = catalogo.consultar_producto(idUsuario)
    if producto:
        return jsonify(producto), 201
    else:
        return "Producto no encontrado", 404


#--------------------------------------------------------------------
# Agregar un producto
#--------------------------------------------------------------------
@app.route("/usuarios", methods=["POST"])
#La ruta Flask `/usuarios` con el método HTTP POST está diseñada para permitir la adición de un nuevo producto a la base de datos.
#La función agregar_producto se asocia con esta URL y es llamada cuando se hace una solicitud POST a /usuarios.
def agregar_producto():
    #Recojo los datos del form
    nombre = request.form['nombre']
    edad = request.form['edad']
    dineroTotal = request.form['dineroTotal']
    imagen = request.files['imagen']
    nroDeCompras = request.form['nroDeCompras']  
    nombre_imagen=""

    
    # Genero el nombre de la imagen.
    nombre_imagen = secure_filename(imagen.filename) #Chequea el nombre del archivo de la imagen, asegurándose de que sea seguro para guardar en el sistema de archivos
    #nombre_base, extension = os.path.splitext(nombre_imagen) #Separa el nombre del archivo de su extensión.
    #nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" #Genera un nuevo nombre para la imagen usando un timestamp, para evitar sobreescrituras y conflictos de nombres.

    nuevo_codigo = catalogo.agregar_producto(nombre, edad, dineroTotal, nombre_imagen, nroDeCompras)
    if nuevo_codigo:    
        imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))
        print("Se guardo!")
        #Si el producto se agrega con éxito, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 201 (Creado).
        return jsonify({"mensaje": "Producto agregado correctamente.", "idUsuario": nuevo_codigo, "imagen": nombre_imagen}), 201
    else:
        #Si el producto no se puede agregar, se devuelve una respuesta JSON con un mensaje de error y un código de estado HTTP 500 (Internal Server Error).
        return jsonify({"mensaje": "Error al agregar el producto pyth."}), 500
    

#--------------------------------------------------------------------
# Modificar un producto según su código
#--------------------------------------------------------------------
@app.route("/usuarios/<int:idUsuario>", methods=["PUT"])
#La ruta Flask /usuarios/<int:idUsuario> con el método HTTP PUT está diseñada para actualizar la información de un producto existente en la base de datos, identificado por su código.
#La función modificar_producto se asocia con esta URL y es invocada cuando se realiza una solicitud PUT a /usuarios/ seguido de un número (el código del producto).
def modificar_producto(idUsuario):
    #Se recuperan los nuevos datos del formulario
    nueva_descripcion = request.form.get("nombre")
    nueva_cantidad = request.form.get("edad")
    nuevo_precio = request.form.get("dineroTotal")
    nuevo_proveedor = request.form.get("nroDeCompras")
    
    
    # Verifica si se proporcionó una nueva imagen
    if 'imagen' in request.files:
        imagen = request.files['imagen']
        # Procesamiento de la imagen
        nombre_imagen = secure_filename(imagen.filename) #Chequea el nombre del archivo de la imagen, asegurándose de que sea seguro para guardar en el sistema de archivos
        nombre_base, extension = os.path.splitext(nombre_imagen) #Separa el nombre del archivo de su extensión.
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" #Genera un nuevo nombre para la imagen usando un timestamp, para evitar sobreescrituras y conflictos de nombres.

        # Guardar la imagen en el servidor
        imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))
        
        # Busco el producto guardado
        producto = catalogo.consultar_producto(idUsuario)
        if producto: # Si existe el producto...
            imagen_vieja = producto["imagen_url"]
            # Armo la ruta a la imagen
            ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

            # Y si existe la borro.
            if os.path.exists(ruta_imagen):
                os.remove(ruta_imagen)
    
    else:
        # Si no se proporciona una nueva imagen, simplemente usa la imagen existente del producto
        producto = catalogo.consultar_producto(idUsuario)
        if producto:
            nombre_imagen = producto["imagen_url"]


    # Se llama al método modificar_producto pasando el idUsuario del producto y los nuevos datos.
    if catalogo.modificar_producto(idUsuario, nueva_descripcion, nueva_cantidad, nuevo_precio, nombre_imagen, nuevo_proveedor):
        
        #Si la actualización es exitosa, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
        return jsonify({"mensaje": "Producto modificado"}), 200
    else:
        #Si el producto no se encuentra (por ejemplo, si no hay ningún producto con el código dado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado).
        return jsonify({"mensaje": "Producto no encontrado"}), 404



#--------------------------------------------------------------------
# Eliminar un producto según su código
#--------------------------------------------------------------------
@app.route("/usuarios/<int:idUsuario>", methods=["DELETE"])
#La ruta Flask /usuarios/<int:idUsuario> con el método HTTP DELETE está diseñada para eliminar un producto específico de la base de datos, utilizando su código como identificador.
#La función eliminar_producto se asocia con esta URL y es llamada cuando se realiza una solicitud DELETE a /usuarios/ seguido de un número (el código del producto).
def eliminar_producto(idUsuario):
    # Busco el producto en la base de datos
    producto = catalogo.consultar_producto(idUsuario)
    if producto: # Si el producto existe, verifica si hay una imagen asociada en el servidor.
        imagen_vieja = producto["imagen_url"]
        # Armo la ruta a la imagen
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

        # Y si existe, la elimina del sistema de archivos.
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

        # Luego, elimina el producto del catálogo
        if catalogo.eliminar_producto(idUsuario):
            #Si el producto se elimina correctamente, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
            return jsonify({"mensaje": "Producto eliminado"}), 200
        else:
            #Si ocurre un error durante la eliminación (por ejemplo, si el producto no se puede eliminar de la base de datos por alguna razón), se devuelve un mensaje de error con un código de estado HTTP 500 (Error Interno del Servidor).
            return jsonify({"mensaje": "Error al eliminar el producto"}), 500
    else:
        #Si el producto no se encuentra (por ejemplo, si no existe un producto con el idUsuario proporcionado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado). 
        return jsonify({"mensaje": "Producto no encontrado"}), 404

#--------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)