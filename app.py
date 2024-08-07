from datetime import datetime
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = '123456'

# Configuración de PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost:5432/sistema_evaluacion'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definición de modelos
class Usuarios(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    contraseña = db.Column(db.String(100), nullable=False)

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
        password = request.form['password']

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
        if usuario and usuario.contraseña == password:
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
        promedio_calificaciones = 0  # O cualquier valor por defecto que consideres apropiado
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
