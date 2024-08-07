from datetime import datetime
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '123456'

# Configuración de PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost:5432/sistema_evaluacion'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Definición de modelos
class Usuarios(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    contraseña = db.Column(db.String(256), nullable=False)  # Cambiado a 256

class Temas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_creacion = db.Column(db.Date, nullable=False)
    usuario = db.relationship('Usuarios', backref=db.backref('temas', lazy=True))

class Respuestas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_tema = db.Column(db.Integer, db.ForeignKey('temas.id'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    calificacion = db.Column(db.Integer, default=0, nullable=False)
    moderado = db.Column(db.Boolean, default=False)
    fecha_respuesta = db.Column(db.Date, nullable=False)
    tema = db.relationship('Temas', backref=db.backref('respuestas', lazy=True))
    usuario = db.relationship('Usuarios', backref=db.backref('respuestas', lazy=True))

class Asignaturas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class Evaluaciones(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.Date, nullable=False)

class Calificaciones(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    id_evaluacion = db.Column(db.Integer, db.ForeignKey('evaluaciones.id'), nullable=False)
    calificacion = db.Column(db.Integer, nullable=False)

class Asistencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    presente = db.Column(db.Boolean, nullable=False)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id))

# Rutas y vistas para registro e inicio de sesión
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        if Usuarios.query.filter_by(nombre_usuario=username).first():
            flash('El nombre de usuario ya está en uso', 'error')
            return redirect(url_for('registro'))

        nuevo_usuario = Usuarios(nombre_usuario=username, email=email, contraseña=password)
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash('¡Registro exitoso! Por favor inicia sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        usuario = Usuarios.query.filter_by(nombre_usuario=username).first()
        if usuario and check_password_hash(usuario.contraseña, password):
            login_user(usuario)
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Credenciales incorrectas. Por favor intenta de nuevo.', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('¡Has cerrado sesión exitosamente!', 'success')
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    temas = Temas.query.all()
    for tema in temas:
        tema.promedio_calificaciones = db.session.query(db.func.avg(Respuestas.calificacion)).filter(Respuestas.id_tema == tema.id).scalar()
    return render_template('home.html', temas=temas)

@app.route('/agregar_tema', methods=['GET', 'POST'])
@login_required
def agregar_tema():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        id_usuario = current_user.id

        nuevo_tema = Temas(
            titulo=titulo,
            descripcion=descripcion,
            id_usuario=id_usuario,
            fecha_creacion=datetime.now()
        )

        db.session.add(nuevo_tema)
        db.session.commit()

        return redirect(url_for('ver_tema', id_tema=nuevo_tema.id))
    
    return render_template('agregar_tema.html')

@app.route('/temas/<int:id_tema>')
@login_required
def ver_tema(id_tema):
    tema = Temas.query.get_or_404(id_tema)
    respuestas = Respuestas.query.filter_by(id_tema=id_tema).all()
    promedio_calificaciones = db.session.query(db.func.avg(Respuestas.calificacion)).filter(Respuestas.id_tema == id_tema).scalar()
    if promedio_calificaciones is None:
        promedio_calificaciones = 0
    return render_template('ver_tema.html', tema=tema, respuestas=respuestas, promedio_calificaciones=promedio_calificaciones)

@app.route('/temas/<int:id_tema>/agregar_respuesta', methods=['POST'])
@login_required
def agregar_respuesta(id_tema):
    contenido = request.form['contenido']
    calificacion = int(request.form['calificacion'])
    id_usuario = current_user.id

    if Respuestas.query.filter_by(id_tema=id_tema, id_usuario=id_usuario).first():
        flash('Ya has calificado este tema', 'error')
        return redirect(url_for('ver_tema', id_tema=id_tema))

    nueva_respuesta = Respuestas(
        id_tema=id_tema,
        id_usuario=id_usuario,
        contenido=contenido,
        calificacion=calificacion,
        fecha_respuesta=datetime.now()
    )

    db.session.add(nueva_respuesta)
    db.session.commit()

    flash('Respuesta y calificación agregadas satisfactoriamente', 'success')
    return redirect(url_for('ver_tema', id_tema=id_tema))

# Rutas para gestión de usuarios
@app.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    usuario = Usuarios.query.get_or_404(id)
    if request.method == 'POST':
        usuario.nombre_usuario = request.form['nombre_usuario']
        usuario.email = request.form['email']
        if request.form['password']:
            usuario.contraseña = generate_password_hash(request.form['password'])
        db.session.commit()
        flash('Usuario actualizado correctamente', 'success')
        return redirect(url_for('lista_usuarios'))
    return render_template('editar_usuario.html', usuario=usuario)

@app.route('/eliminar_usuario/<int:id>', methods=['POST'])
@login_required
def eliminar_usuario(id):
    usuario = Usuarios.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado correctamente', 'success')
    return redirect(url_for('lista_usuarios'))

@app.route('/lista_usuarios')
@login_required
def lista_usuarios():
    usuarios = Usuarios.query.all()
    return render_template('lista_usuarios.html', usuarios=usuarios)

# Rutas para gestión de asignaturas
@app.route('/asignaturas', methods=['GET', 'POST'])
@login_required
def gestion_asignaturas():
    if request.method == 'POST':
        nombre = request.form['nombre']
        nueva_asignatura = Asignaturas(nombre=nombre)
        db.session.add(nueva_asignatura)
        db.session.commit()
        flash('Asignatura añadida', 'success')
    asignaturas = Asignaturas.query.all()
    return render_template('gestion_asignaturas.html', asignaturas=asignaturas)

# Rutas para evaluaciones y calificaciones
@app.route('/evaluaciones', methods=['GET', 'POST'])
@login_required
def gestion_evaluaciones():
    if request.method == 'POST':
        nombre = request.form['nombre']
        fecha = request.form['fecha']
        nueva_evaluacion = Evaluaciones(nombre=nombre, fecha=fecha)
        db.session.add(nueva_evaluacion)
        db.session.commit()
        flash('Evaluación añadida', 'success')
    evaluaciones = Evaluaciones.query.all()
    return render_template('gestion_evaluaciones.html', evaluaciones=evaluaciones)

@app.route('/calificaciones', methods=['GET', 'POST'])
@login_required
def gestion_calificaciones():
    if request.method == 'POST':
        id_usuario = request.form['id_usuario']
        id_evaluacion = request.form['id_evaluacion']
        calificacion = request.form['calificacion']
        nueva_calificacion = Calificaciones(id_usuario=id_usuario, id_evaluacion=id_evaluacion, calificacion=calificacion)
        db.session.add(nueva_calificacion)
        db.session.commit()
        flash('Calificación añadida', 'success')
    calificaciones = Calificaciones.query.all()
    return render_template('gestion_calificaciones.html', calificaciones=calificaciones)

# Rutas para asistencia
@app.route('/asistencia', methods=['GET', 'POST'])
@login_required
def gestion_asistencia():
    if request.method == 'POST':
        id_usuario = request.form['id_usuario']
        fecha = request.form['fecha']
        presente = request.form['presente']
        nueva_asistencia = Asistencia(id_usuario=id_usuario, fecha=fecha, presente=presente)
        db.session.add(nueva_asistencia)
        db.session.commit()
        flash('Asistencia registrada', 'success')
    asistencias = Asistencia.query.all()
    return render_template('gestion_asistencia.html', asistencias=asistencias)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
