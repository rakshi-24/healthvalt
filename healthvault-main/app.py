
from flask import Flask, render_template, request, redirect, jsonify, session, url_for

from utils.db import db
from models.medic import *


app =  Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medic.db'

@app.route('/')
def home():
    return render_template('home.html')  # Ensure home.html has a link to /login


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Replace this with your actual authentication logic
        if username == "admin" and password == "1234":
            return redirect('/index')  # Redirect to index page on successful login
        else:
            return render_template('login.html', error="Invalid username or password")
    else:
        return render_template('login.html')  # Render login.html for GET requests


@app.route('/logout')
def logout():
      # Remove the logged_in session variable
    return redirect(url_for('home'))


@app.route('/index')
def index():
    patient = Patients.query.all()
    return render_template('index.html',  content=patient)

@app.route('/queries')
def queries():
    return render_template('queries.html')

@app.route('/patients')
def patients():
    return render_template('patient.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    patient = Patients.query.all()  # ORM query to fetch data
    patient = [{
        'id': patient.id,
        'name': patient.name,
        'age': patient.age,
        'sex': patient.sex,
        'bmi': patient.bmi,
        'children': patient.children,
        'charges': patient.charges,
        'region': patient.region
    } for patient in patient]
    return render_template('dashboard.html', content=patient)



@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/help')
def help():
    return render_template('help.html')


db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/submit", methods=['POST'])
def submit():
    form_data = request.form.to_dict()
    print(f"form_data: {form_data}")

    name = form_data.get('name')
    age = form_data.get('age')
    sex = form_data.get('sex')
    bmi = form_data.get('bmi')
    children = form_data.get('children')
    charges = form_data.get('charges')
    region = form_data.get('region')


    patient = Patients.query.filter_by(age=age).first()
    if not patient:
        patient = Patients(name=name,age=age,sex=sex, bmi=bmi, children=children, charges=charges, region=region)
        db.session.add(patient)
        db.session.commit()
    print("sumitted successfully")
    return redirect('/')



@app.route('/delete/<int:id>', methods=['GET', 'DELETE'])
def delete(id):
    patient = Patients.query.get(id)
    print("task: {}".format(patient))

    if not patient:
        return jsonify({'message': 'patient not found'}), 404
    try:
        db.session.delete(patient)
        db.session.commit()
        return redirect('/')
        return jsonify({'message': 'patient deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return redirect('/')
        return jsonify({'message': 'An error occurred while deleting the data {}'.format(e)}), 500


@app.route('/add', methods=['POST'])
def add_patient():
    try:
        # Get the data from the request
        data = request.get_json()

        # Create a new patient instance
        patient = Patients(
            name=data.get('name'),
            age=data.get('age'),
            sex=data.get('sex'),
            bmi=data.get('bmi'),
            children=data.get('children'),
            charges=data.get('charges'),
            region=data.get('region')
        )

        # Add to the database
        db.session.add(patient)
        db.session.commit()

        # Respond with a success message
        return jsonify({'message': 'Patient added successfully'}), 201

    except Exception as e:
        # Handle errors
        db.session.rollback()  # Rollback in case of error
        return jsonify({'message': str(e)}), 400


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    patient = Patients.query.get_or_404(id)
    print(patient.id)
    if not patient:
        return jsonify({'message': 'patient not found'}), 404

    if request.method == 'POST':
        patient.name = request.form['name']
        patient.age = request.form['age']
        patient.sex = request.form['sex']
        patient.bmi = request.form['bmi']
        patient.children = request.form['children']
        patient.charges = request.form['charges']
        patient.region = request.form['region']

        try:
            db.session.commit()
            return redirect('/')

        except Exception as e:
            db.session.rollback()
            return "there is an issue while updating the record"
    return render_template('update.html', patient=patient)


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    patient = Patients.query.filter(Patients.name.ilike(f"%{query}%")).all() if query else []
    return render_template('search.html', patient=patient, query=query)




if __name__ =='__main__':
    app.run(host='127.0.0.1',port=5003,debug=True)
