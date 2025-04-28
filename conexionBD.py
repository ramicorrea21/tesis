# conexionBD.py
import psycopg2
import psycopg2.extras
import os

def connectionBD():
    """
    Create a connection to PostgreSQL database
    Returns connection object or None if connection fails
    """
    try:
        # Using direct connection parameters
        connection = psycopg2.connect(
            host="dpg-d07f1gili9vc73f7ufl0-a",
            database="tesis_login",
            user="tesis_login_user",
            password="glgwEdMrdPKQkkq5mPDXPtaemBHfWUeV",
            port="5432"
        )
            
        return connection
    except Exception as e:
        print(f"Database Error: {str(e)}")
        return None