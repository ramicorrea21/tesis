from flask import session
from conexionBD import *

#https://pynative.com/python-mysql-database-connection/
#https://pynative.com/python-mysql-select-query-to-fetch-data/

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
        conexion_MySQLdb = connectionBD()
        if conexion_MySQLdb is None:
            return dataLoginSesion()

        mycursor = conexion_MySQLdb.cursor(dictionary=True)
        idUser = session['id']
        
        querySQL = ("SELECT * FROM login_python WHERE id='%s'" % (idUser,))
        mycursor.execute(querySQL)
        datosUsuario = mycursor.fetchone()
        
        return datosUsuario
    except Exception as e:
        print(f"Error en dataPerfilUsuario: {str(e)}")
        return dataLoginSesion()
    finally:
        if 'mycursor' in locals():
            mycursor.close()
        if 'conexion_MySQLdb' in locals() and conexion_MySQLdb is not None:
            conexion_MySQLdb.close()