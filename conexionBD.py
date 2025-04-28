import mysql.connector
import os

def connectionBD():

    host = os.environ.get('DB_HOST', 'localhost')
    user = os.environ.get('DB_USER', 'AdminAvedano')
    password = os.environ.get('DB_PASSWORD', 'juancho16')
    database = os.environ.get('DB_NAME', 'ejemplo_youtubee')
    port = os.environ.get('DB_PORT', '3306')
    
    try:
        mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=int(port)
        )
        return mydb
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        # Return None if connection fails, handle this in the routes
        return None