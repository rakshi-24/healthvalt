from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medic.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '1234'


# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    patients = db.relationship('Patient', backref='user', lazy=True)


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    children = db.Column(db.Integer, nullable=False)
    charges = db.Column(db.Float, nullable=False)
    region = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Ensure 'is_active' column exists
def ensure_is_active_column():
    with sqlite3.connect('medic.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(user)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'is_active' not in columns:
                cursor.execute("ALTER TABLE user ADD COLUMN is_active BOOLEAN DEFAULT 1")
                conn.commit()


# Authentication Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    hashed_password = generate_password_hash(data['password'])
    user = User(username=data['username'], password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        login_user(user)
        return jsonify({'message': 'Login successful'})
    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})


# Patient CRUD Routes
@app.route('/patients', methods=['GET', 'POST'])
@login_required
def manage_patients():
    if request.method == 'POST':
        data = request.json
        patient = Patient(
            name=data['name'], age=data['age'], sex=data['sex'], bmi=data['bmi'],
            children=data['children'], charges=data['charges'], region=data['region'],
            user_id=current_user.id
        )
        db.session.add(patient)
        db.session.commit()
        return jsonify({'message': 'Patient added successfully'})

    patients = Patient.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': p.id, 'name': p.name, 'age': p.age, 'sex': p.sex, 'bmi': p.bmi,
        'children': p.children, 'charges': p.charges, 'region': p.region
    } for p in patients])


@app.route('/patients/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def patient_detail(id):
    patient = Patient.query.get_or_404(id)
    if patient.user_id != current_user.id and current_user.username != ADMIN_USERNAME:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'PUT':
        data = request.json
        patient.name = data['name']
        patient.age = data['age']
        patient.sex = data['sex']
        patient.bmi = data['bmi']
        patient.children = data['children']
        patient.charges = data['charges']
        patient.region = data['region']
        db.session.commit()
        return jsonify({'message': 'Patient updated successfully'})

    if request.method == 'DELETE':
        db.session.delete(patient)
        db.session.commit()
        return jsonify({'message': 'Patient deleted successfully'})

    return jsonify({
        'id': patient.id, 'name': patient.name, 'age': patient.age, 'sex': patient.sex, 'bmi': patient.bmi,
        'children': patient.children, 'charges': patient.charges, 'region': patient.region
    })


# Admin Dashboard
@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if current_user.username == ADMIN_USERNAME:
        patients = Patient.query.all()
    else:
        patients = Patient.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': p.id, 'name': p.name, 'age': p.age, 'sex': p.sex, 'bmi': p.bmi,
        'children': p.children, 'charges': p.charges, 'region': p.region
    } for p in patients])


# Search Patients
@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query', '')
    if current_user.username == ADMIN_USERNAME:
        patients = Patient.query.filter(Patient.name.ilike(f"%{query}%")).all()
    else:
        patients = Patient.query.filter(Patient.user_id == current_user.id, Patient.name.ilike(f"%{query}%")).all()
    return jsonify([{'id': p.id, 'name': p.name} for p in patients])


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_is_active_column()
    app.run(debug=True)
