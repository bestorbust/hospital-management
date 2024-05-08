from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('hospital.db')
    conn.row_factory = sqlite3.Row
    return conn

# Routes for managing patients
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/enter_details', methods=['GET', 'POST'])
def enter_details():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        condition = request.form.get('condition')
        admitted = True if request.form.get('admitted') else False
        date = request.form.get('date')

        if name and age and gender and condition and date:
            conn = get_db_connection()
            conn.execute('INSERT INTO patients (name, age, gender, condition, admitted, date) VALUES (?, ?, ?, ?, ?, ?)',
                         (name, age, gender, condition, admitted, date))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        else:
            return "Missing required information. Please fill in all fields.", 400
    else:
        return render_template('add_patient.html')

@app.route('/patients')
def patients_list():
    conn = get_db_connection()
    patients = conn.execute('SELECT * FROM patients').fetchall()
    conn.close()
    return render_template('patients_list.html', patients=patients)

@app.route('/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('patients_list'))

@app.route('/update_patient/<int:patient_id>', methods=['GET', 'POST'])
def update_patient(patient_id):
    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()

    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        condition = request.form.get('condition')
        admitted = True if request.form.get('admitted') else False
        date = request.form.get('date')

        if name and age and gender and condition and date:
            conn.execute('UPDATE patients SET name=?, age=?, gender=?, condition=?, admitted=?, date=? WHERE id=?',
                         (name, age, gender, condition, admitted, date, patient_id))
            conn.commit()
            conn.close()
            return redirect(url_for('patients_list'))
        else:
            return "Missing required information. Please fill in all fields.", 400

    conn.close()
    return render_template('update_patient.html', patient=patient)
@app.route('/doctors')
def doctors_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM doctors')
    doctors = []
    for doctor_row in cursor.fetchall():
        doctor = dict(doctor_row)
        doctor['appointments'] = conn.execute('SELECT * FROM appointments WHERE doctor_id = ?', (doctor['id'],)).fetchall()
        doctors.append(doctor)
    conn.close()
    return render_template('doctors_list.html', doctors=doctors)

@app.route('/enter_doctor_details', methods=['GET', 'POST'])
def enter_doctor_details():
    if request.method == 'POST':
        # Extract doctor information from the form
        name = request.form.get('name')
        specialization = request.form.get('specialization')
        consultancy_fee = request.form.get('consultancy_fee')

        if name and specialization and consultancy_fee:
            conn = get_db_connection()
            conn.execute('INSERT INTO doctors (name, specialization, consultancy_fee) VALUES (?, ?, ?)',
                         (name, specialization, consultancy_fee))
            conn.commit()
            conn.close()
            return redirect(url_for('doctors_list'))
        else:
            return "Missing required information. Please fill in all fields.", 400
    else:
        return render_template('add_doctor.html')

@app.route('/delete_doctor/<int:doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM appointments WHERE doctor_id = ?', (doctor_id,))
    conn.execute('DELETE FROM doctors WHERE id = ?', (doctor_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('doctors_list'))

@app.route('/update_doctor/<int:doctor_id>', methods=['GET', 'POST'])
def update_doctor(doctor_id):
    conn = get_db_connection()
    doctor = conn.execute('SELECT * FROM doctors WHERE id = ?', (doctor_id,)).fetchone()

    if request.method == 'POST':
        name = request.form.get('name')
        specialization = request.form.get('specialization')
        consultancy_fee = request.form.get('consultancy_fee')

        if name and specialization and consultancy_fee:
            conn.execute('UPDATE doctors SET name=?, specialization=?, consultancy_fee=? WHERE id=?',
                         (name, specialization, consultancy_fee, doctor_id))
            conn.commit()
            conn.close()
            return redirect(url_for('doctors_list'))
        else:
            return "Missing required information. Please fill in all fields.", 400

    conn.close()
    return render_template('update_doctor.html', doctor=doctor)


@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if request.method == 'POST':
        # Extract appointment information from the form
        patient_id = request.form.get('patient_id')
        doctor_id = request.form.get('doctor_id')
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')

        # Check if all required fields are filled
        if patient_id and doctor_id and appointment_date and appointment_time:
            conn = get_db_connection()
            conn.execute('INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time) VALUES (?, ?, ?, ?)',
                         (patient_id, doctor_id, appointment_date, appointment_time))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))  # Redirect to home page for now
        else:
            return "Missing required information. Please fill in all fields.", 400
    else:
        conn = get_db_connection()
        patients = conn.execute('SELECT * FROM patients').fetchall()
        doctors = conn.execute('SELECT * FROM doctors').fetchall()
        conn.close()
        return render_template('book_appointment.html', patients=patients, doctors=doctors)
with app.app_context():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS patients
                    (id INTEGER PRIMARY KEY,
                     name TEXT NOT NULL,
                     age INTEGER NOT NULL,
                     gender TEXT NOT NULL,
                     condition TEXT NOT NULL,
                     admitted BOOLEAN NOT NULL,
                     date TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS doctors
                    (id INTEGER PRIMARY KEY,
                     name TEXT NOT NULL,
                     specialization TEXT NOT NULL,
                     consultancy_fee REAL NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS appointments
                    (id INTEGER PRIMARY KEY,
                     patient_id INTEGER NOT NULL,
                     doctor_id INTEGER NOT NULL,
                     appointment_date TEXT NOT NULL,
                     appointment_time TEXT NOT NULL,
                     FOREIGN KEY(patient_id) REFERENCES patients(id),
                     FOREIGN KEY(doctor_id) REFERENCES doctors(id))''')
    conn.commit()
    conn.close()
# if __name__ == '__main__':
    # app.run(debug=True)
