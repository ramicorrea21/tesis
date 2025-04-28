# routes.py
from flask import render_template, redirect, url_for, session, request, flash
from funciones import dataLoginSesion, dataPerfilUsuario
from conexionBD import connectionBD
import re
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import psycopg2.extras

def registrar_rutas(app):
    
    # Ruta para página de inicio
    @app.route('/')
    def inicio():
        if 'conectado' in session:
            return redirect(url_for('dashboard'))
        return redirect(url_for('loginUser'))

    # Ruta para login
    @app.route('/login', methods=['GET', 'POST'])
    def loginUser():
        if 'conectado' in session:
            return redirect(url_for('dashboard'))
        
        msg = ''
        typeAlert = 0
        
        if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']
            
            try:
                conexion_DB = connectionBD()
                if conexion_DB is None:
                    msg = 'Error de conexión a la base de datos. Por favor contacte al administrador.'
                    typeAlert = 0
                    return render_template('public/modulo_login/index.html', msjAlert=msg, typeAlert=typeAlert)
                    
                cursor = conexion_DB.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cursor.execute("SELECT * FROM login_python WHERE email = %s", (email,))
                account = cursor.fetchone()
                
                if account and check_password_hash(account['password'], password):
                    session['conectado'] = True
                    session['id'] = account['id']
                    session['nombre'] = account['nombre']
                    session['apellido'] = account['apellido']
                    session['email'] = account['email']
                    
                    return render_template('public/dashboard/home.html', 
                                          msjAlert='Ha iniciado sesión correctamente.', 
                                          typeAlert=1, 
                                          dataLogin=dataLoginSesion())
                else:
                    msg = 'Email o contraseña incorrectos.'
                    typeAlert = 0
            except Exception as e:
                msg = f'Error: {str(e)}'
                typeAlert = 0
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conexion_DB' in locals() and conexion_DB is not None:
                    conexion_DB.close()
        
        return render_template('public/modulo_login/index.html', msjAlert=msg, typeAlert=typeAlert)

    # Ruta para dashboard
    @app.route('/dashboard')
    def dashboard():
        if 'conectado' not in session:
            return redirect(url_for('loginUser'))
        return render_template('public/dashboard/home.html', dataLogin=dataLoginSesion())

    # Ruta para registrar usuario
    @app.route('/registro-usuario', methods=['GET', 'POST'])
    def registerUser():
        msg = ''
        typeAlert = 0
        
        if request.method == 'POST':
            nombre = request.form.get('nombre', '')
            apellido = request.form.get('apellido', '')
            email = request.form.get('email', '')
            password = request.form.get('password', '')
            repite_password = request.form.get('repite_password', '')
            
            # Validaciones
            if not all([nombre, apellido, email, password, repite_password]):
                msg = 'Por favor, completa todos los campos.'
                typeAlert = 0
            elif password != repite_password:
                msg = 'Las contraseñas no coinciden.'
                typeAlert = 0
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Formato de email inválido.'
                typeAlert = 0
            else:
                try:
                    conexion_DB = connectionBD()
                    if conexion_DB is None:
                        msg = 'Error de conexión a la base de datos. Por favor contacte al administrador.'
                        typeAlert = 0
                        return render_template('public/modulo_login/index.html', msjAlert=msg, typeAlert=typeAlert)
                        
                    cursor = conexion_DB.cursor(cursor_factory=psycopg2.extras.DictCursor)
                    cursor.execute('SELECT * FROM login_python WHERE email = %s', (email,))
                    account = cursor.fetchone()
                    
                    if account:
                        msg = 'Ya existe un usuario con ese email.'
                        typeAlert = 0
                    else:
                        password_encriptada = generate_password_hash(password, method='scrypt')
                        cursor.execute('INSERT INTO login_python (nombre, apellido, email, password) VALUES (%s, %s, %s, %s)', 
                                     (nombre, apellido, email, password_encriptada))
                        conexion_DB.commit()
                        msg = 'Cuenta creada exitosamente.'
                        typeAlert = 1
                        return render_template('public/modulo_login/index.html', msjAlert=msg, typeAlert=typeAlert)
                except Exception as e:
                    msg = f'Error: {str(e)}'
                    typeAlert = 0
                finally:
                    if 'cursor' in locals():
                        cursor.close()
                    if 'conexion_DB' in locals() and conexion_DB is not None:
                        conexion_DB.close()
        
        return render_template('public/modulo_login/register.html', msjAlert=msg, typeAlert=typeAlert)

    # Ruta para actualizar perfil
# Ruta para actualizar perfil
@app.route('/actualizar-mi-perfil/<int:id>', methods=['GET', 'POST'])
def actualizarMiPerfil(id):
    if 'conectado' not in session:
        return redirect(url_for('loginUser'))
    
    if int(session['id']) != id:
        return render_template('public/dashboard/home.html', 
                              msjAlert='No tiene permiso para editar este perfil.', 
                              typeAlert=0,
                              dataLogin=dataLoginSesion())
    
    msg = ''
    typeAlert = 0
    
    # For both GET and POST requests, get the user data
    try:
        conexion_DB = connectionBD()
        if conexion_DB is None:
            return render_template('public/dashboard/home.html', 
                                  msjAlert='Error de conexión a la base de datos.', 
                                  typeAlert=0,
                                  dataLogin=dataLoginSesion())
        
        cursor = conexion_DB.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM login_python WHERE id = %s", (id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            return render_template('public/dashboard/home.html', 
                                  msjAlert='No existe el usuario!', 
                                  typeAlert=0,
                                  dataLogin=dataLoginSesion())
                                  
        # If this is a GET request, show the profile edit form
        if request.method == 'GET':
            return render_template('public/dashboard/pages/Profile.html',
                                  dataUser=dict(user_data),
                                  dataLogin=dataLoginSesion())
        
        # Process form submission for POST requests
        if request.method == 'POST':
            nombre = request.form.get('nombre', '')
            apellido = request.form.get('apellido', '')
            email = request.form.get('email', '')
            password = request.form.get('password', '')
            repite_password = request.form.get('repite_password', '')
            
            if password:
                if password != repite_password:
                    msg = 'Las contraseñas no coinciden.'
                    typeAlert = 0
                else:
                    nueva_password = generate_password_hash(password, method='pbkdf2:sha256')
                    cursor.execute("""
                        UPDATE login_python 
                        SET nombre = %s, apellido = %s, email = %s, password = %s 
                        WHERE id = %s
                    """, (nombre, apellido, email, nueva_password, id))
                    msg = 'Perfil actualizado correctamente.'
                    typeAlert = 1
            else:
                cursor.execute("""
                    UPDATE login_python 
                    SET nombre = %s, apellido = %s, email = %s 
                    WHERE id = %s
                """, (nombre, apellido, email, id))
                msg = 'Perfil actualizado correctamente.'
                typeAlert = 1
            
            conexion_DB.commit()
            
            # Actualizar datos de sesión
            session['nombre'] = nombre
            session['apellido'] = apellido
            session['email'] = email
            
            return render_template('public/dashboard/home.html', 
                                  msjAlert=msg, 
                                  typeAlert=typeAlert, 
                                  dataLogin=dataLoginSesion())
            
    except Exception as e:
        msg = f'Error: {str(e)}'
        typeAlert = 0
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion_DB' in locals() and conexion_DB is not None:
            conexion_DB.close()
    
    return render_template('public/dashboard/home.html', 
                          msjAlert=msg, 
                          typeAlert=typeAlert, 
                          dataLogin=dataLoginSesion())

    # Ruta para cerrar sesión
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('loginUser'))

    # Error 404
    @app.errorhandler(404)
    def not_found(error):
        if 'conectado' in session:
            return render_template('public/dashboard/error.html', dataLogin=dataLoginSesion(), error=404)
        return redirect(url_for('loginUser'))
    
    # Error 500
    @app.errorhandler(500)
    def internal_error(error):
        if 'conectado' in session:
            return render_template('public/dashboard/error.html', dataLogin=dataLoginSesion(), error=500)
        return redirect(url_for('loginUser'))