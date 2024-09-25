from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)

 # Cambia según tu configuración

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Definición de modelos


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    # Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('list_files'))
        else:
            flash('Nombre de usuario o contraseña incorrectos', 'danger')
    return render_template('login.html')

# Ruta de cierre de sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('login'))

# Ruta de registro de usuario
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Usuario creado exitosamente', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Modelo de la base de datos
class Audio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    control_number = db.Column(db.String(20), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Subir archivos de audio
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        control_number = request.form['control_number']
        file = request.files['file']

        if file and control_number:
            filename = file.filename
            filepath = os.path.join('static/uploads', filename)
            file.save(filepath)

            new_audio = Audio(control_number=control_number, filename=filename)
            db.session.add(new_audio)
            db.session.commit()

            flash('Archivo subido exitosamente')
            return redirect(url_for('list_files'))
        else:
            flash('Faltan datos o archivo')
    
    return render_template('upload.html')

# Listar archivos subidos
@app.route('/files')
def list_files():
    audios = Audio.query.order_by(Audio.upload_date.desc()).all()
    return render_template('files.html', audios=audios)

# Reproducir un archivo de audio
@app.route('/play/<int:audio_id>')
def play(audio_id):
    audio = Audio.query.get_or_404(audio_id)
    return send_from_directory('static/uploads', audio.filename)

# Eliminar un archivo de audio
@app.route('/delete/<int:audio_id>', methods=['POST'])
def delete(audio_id):
    audio = Audio.query.get_or_404(audio_id)
    filepath = os.path.join('static/uploads', audio.filename)

    # Eliminar el archivo del sistema
    if os.path.exists(filepath):
        os.remove(filepath)

    # Eliminar de la base de datos
    db.session.delete(audio)
    db.session.commit()

    flash('Archivo eliminado exitosamente')
    return redirect(url_for('list_files'))

# Actualizar un archivo de audio
@app.route('/update/<int:audio_id>', methods=['GET', 'POST'])
def update(audio_id):
    audio = Audio.query.get_or_404(audio_id)
    if request.method == 'POST':
        control_number = request.form['control_number']
        file = request.files['file']

        if file:
            # Eliminar el archivo antiguo del sistema
            old_filepath = os.path.join('static/uploads', audio.filename)
            if os.path.exists(old_filepath):
                os.remove(old_filepath)
            
            filename = file.filename
            filepath = os.path.join('static/uploads', filename)
            file.save(filepath)

            # Actualizar los detalles en la base de datos
            audio.control_number = control_number
            audio.filename = filename
            db.session.commit()

            flash('Archivo actualizado exitosamente')
            return redirect(url_for('list_files'))
        else:
            flash('Faltan datos o archivo')
    
    return render_template('update.html', audio=audio)

# Inicializa la base de datos directamente
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
