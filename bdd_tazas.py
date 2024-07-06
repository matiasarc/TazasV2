#este archivo hace el acceso de admin a la base de datos desde el back para poder agregar o quitar cosas
import mysql.connector
from mysql.connector import Error

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="Julian",
        password="admin",
        database="tienda_tazas"
    )

# Crear base de datos y tablas
def create_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="Julian",
            password="admin"
        )
        cursor = conn.cursor()
        
        cursor.execute("CREATE DATABASE IF NOT EXISTS tienda_tazas")
        cursor.execute("USE tienda_tazas")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                password VARCHAR(50) NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tazas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                precio DECIMAL(10, 2) NOT NULL
            )
        ''')

        # Usamos INSERT IGNORE para asegurarnos de no duplicar el usuario admin
        cursor.execute('''
            INSERT IGNORE INTO usuarios (username, password) VALUES ('admin', 'admin123')
        ''')
        
        conn.commit()
        print("Base de datos y tablas creadas correctamente.")
    except Error as e:
        print(f"Error al crear la base de datos: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

create_db()

# Función para verificar el login del administrador
def login(username, password):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        # Consume any remaining results
        cursor.fetchall()
        return user is not None
    except Error as e:
        print(f"Error al verificar el login: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Función para agregar una nueva taza
def agregar_taza(nombre, precio):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tazas (nombre, precio) VALUES (%s, %s)', (nombre, precio))
        conn.commit()
        print("Taza agregada con éxito.")
    except Error as e:
        print(f"Error al agregar la taza: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Función para borrar una taza por ID
def borrar_taza(taza_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tazas WHERE id = %s', (taza_id,))
        conn.commit()
        print("Taza borrada con éxito.")
    except Error as e:
        print(f"Error al borrar la taza: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Interfaz de usuario simple
def main():
    print("Bienvenido a la tienda de tazas.")
    
    username = input("Ingrese su nombre de usuario: ")
    password = input("Ingrese su contraseña: ")
    
    if login(username, password):
        print("Login exitoso.")
        while True:
            print("\nOpciones:")
            print("1. Agregar taza")
            print("2. Borrar taza")
            print("3. Salir")
            opcion = input("Seleccione una opción: ")
            
            if opcion == '1':
                nombre = input("Ingrese el nombre de la taza: ")
                precio = float(input("Ingrese el precio de la taza: "))
                agregar_taza(nombre, precio)
            elif opcion == '2':
                taza_id = int(input("Ingrese el ID de la taza a borrar: "))
                borrar_taza(taza_id)
            elif opcion == '3':
                print("Saliendo...")
                break
            else:
                print("Opción no válida.")
    else:
        print("Nombre de usuario o contraseña incorrectos.")

if __name__ == "__main__":
    main()