from flask import render_template, redirect, url_for, session, request
from funciones import *  # Tus funciones personalizadas
from conexionBD import *  # Tu conexión a la base de datos
import re
from werkzeug.security import generate_password_hash, check_password_hash
def registrar_rutas(app):

    # Ruta para página de inicio
    @app.route('/')
    def inicio():
        if 'conectado' in session:
            return render_template('public/dashboard/home.html', dataLogin=dataLoginSesion())
        else:
            return render_template('public/modulo_login/index.html')

    # Ruta para login
    @app.route('/login', methods=['GET', 'POST'])
    def loginUser():
        conexion_MySQLdb = connectionBD()
        msg = ''
        
        if 'conectado' in session:
            return redirect(url_for('inicio'))

        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            cursor = conexion_MySQLdb.cursor(dictionary=True)
            cursor.execute("SELECT * FROM login_python WHERE email = %s", (email,))
            account = cursor.fetchone()
            cursor.close()

            if account and check_password_hash(account['password'], password):
                session['conectado'] = True
                session['id'] = account['id']
                session['nombre'] = account['nombre']
                session['apellido'] = account['apellido']
                session['email'] = account['email']

                msg = "Sesión iniciada correctamente."
                return redirect(url_for('dashboard'))

            else:
                msg = 'Email o contraseña incorrectos.'

        return render_template('public/modulo_login/index.html', msjAlert=msg, typeAlert=0)

    # Ruta para dashboard
    @app.route('/dashboard')
    def dashboard():
        if 'conectado' in session:
            return render_template('public/dashboard/home.html', dataLogin=dataLoginSesion())
        else:
            return redirect(url_for('loginUser'))

    # Ruta para registrar usuario
    @app.route('/registro-usuario', methods=['GET', 'POST'])
    def registerUser():
        msg = ''
        conexion_MySQLdb = connectionBD()
        
        if request.method == 'POST':
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            email = request.form['email']
            password = request.form['password']
            repite_password = request.form['repite_password']

            cursor = conexion_MySQLdb.cursor(dictionary=True)
            cursor.execute('SELECT * FROM login_python WHERE email = %s', (email,))
            account = cursor.fetchone()
            cursor.close()

            if account:
                msg = 'Ya existe un usuario con ese email.'
            elif password != repite_password:
                msg = 'Las contraseñas no coinciden.'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Formato de email inválido.'
            elif not email or not password:
                msg = 'Por favor, completa todos los campos.'
            else:
                password_encriptada = generate_password_hash(password, method='scrypt')
                cursor = conexion_MySQLdb.cursor(dictionary=True)
                cursor.execute('INSERT INTO login_python (nombre, apellido, email, password) VALUES (%s, %s, %s, %s)', 
                               (nombre, apellido, email, password_encriptada))
                conexion_MySQLdb.commit()
                cursor.close()
                msg = 'Cuenta creada exitosamente.'
                return redirect(url_for('loginUser'))

        return render_template('public/modulo_login/register.html', msjAlert=msg, typeAlert=0)

    # Ruta para editar perfil
    @app.route('/edit-profile', methods=['GET', 'POST'])
    def editProfile():
        if 'conectado' in session:
            if request.method == 'POST':
                id = session['id']
                nombre = request.form['nombre']
                apellido = request.form['apellido']
                email = request.form['email']
                password = request.form.get('password')
                repite_password = request.form.get('repite_password')

                conexion_MySQLdb = connectionBD()
                cursor = conexion_MySQLdb.cursor()

                if password:
                    if password == repite_password:
                        nueva_password = generate_password_hash(password, method='pbkdf2:sha256')
                        cursor.execute("""
                            UPDATE login_python SET nombre = %s, apellido = %s, email = %s, password = %s WHERE id = %s
                        """, (nombre, apellido, email, nueva_password, id))
                    else:
                        return render_template('public/dashboard/pages/Profile.html', msjAlert='Las contraseñas no coinciden.', typeAlert=0, dataUser=dataPerfilUsuario(), dataLogin=dataLoginSesion())
                else:
                    cursor.execute("""
                        UPDATE login_python SET nombre = %s, apellido = %s, email = %s WHERE id = %s
                    """, (nombre, apellido, email, id))

                conexion_MySQLdb.commit()
                cursor.close()
                return redirect(url_for('dashboard'))

            return render_template('public/dashboard/pages/Profile.html', dataUser=dataPerfilUsuario(), dataLogin=dataLoginSesion())

        return redirect(url_for('loginUser'))

    # Ruta para cerrar sesión
    @app.route('/logout')
    def logout():
        session.clear()
        msg = "Sesión cerrada correctamente."
        return redirect(url_for('loginUser'))

    # Error 404
    @app.errorhandler(404)
    def not_found(error):
        if 'conectado' in session:
            return redirect(url_for('dashboard'))
        else:
            return render_template('public/modulo_login/index.html')

