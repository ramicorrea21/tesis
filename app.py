from flask import Flask
import os
from datetime import timedelta
from routes import registrar_rutas

def crear_app():
    app = Flask(__name__)
    
    # Configuración de la clave secreta para sesiones
    app.secret_key = os.environ.get('SECRET_KEY', 'tu_clave_secreta_aqui')
    
    # Configuración de la duración de la sesión
    app.permanent_session_lifetime = timedelta(minutes=60)
    
    # Registrando todas las rutas
    registrar_rutas(app)
    
    return app

# Crear instancia de la aplicación para Gunicorn
app = crear_app()

if __name__ == "__main__":
    app.run(debug=True, port=8000)