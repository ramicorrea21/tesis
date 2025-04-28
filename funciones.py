from flask import session
from conexionBD import *
import psycopg2.extras

#creando una funcion y dentro de la misma una data (un diccionario)
#con valores del usuario ya logueado
def dataLoginSesion():
    if 'id' in session:
        inforLogin = {
            "idLogin"             : session['id'],
            "nombre"              : session['nombre'],
            "apellido"            : session['apellido'],
            "emailLogin"          : session['email'],
        }
        return inforLogin
    return {}

def dataPerfilUsuario():
    try:
        conexion_DB = connectionBD()
        if conexion_DB is None:
            return dataLoginSesion()

        cursor = conexion_DB.cursor(cursor_factory=psycopg2.extras.DictCursor)
        idUser = session['id']
        
        # Note: In PostgreSQL, you should use %s for all parameter types
        querySQL = ("SELECT * FROM login_python WHERE id = %s")
        cursor.execute(querySQL, (idUser,))
        datosUsuario = cursor.fetchone()
        
        return dict(datosUsuario) if datosUsuario else dataLoginSesion()
    except Exception as e:
        print(f"Error en dataPerfilUsuario: {str(e)}")
        return dataLoginSesion()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion_DB' in locals() and conexion_DB is not None:
            conexion_DB.close()