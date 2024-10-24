from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('extinguisher.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home route to display the list of sections
@app.route('/')
def index():
    sections = ['MOB A', 'MOB B', 'MOB C', 'MOB D', 'Employee Parking Deck', 
                'Visitor Parking Deck', 'Women\'s Medical Center', 
                'Main Hospital/North Tower/Psych', 'FED']
    return render_template('index.html', sections=sections)

# Route to display extinguishers in a specific section
@app.route('/section/<section>')
def section(section):
    conn = get_db_connection()
    extinguishers = conn.execute('SELECT * FROM extinguishers WHERE section = ?', (section,)).fetchall()
    conn.close()
    return render_template('section.html', section=section, extinguishers=extinguishers)

# Route to add new extinguisher
@app.route('/add_extinguisher', methods=['POST'])
def add_extinguisher():
    data = request.form
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO extinguishers (section, location_number, type, size, location, barcode, serial_number, pass_fail, date_inspected, initials)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Unchecked', ?, ?)
    ''', (data['section'], data['location_number'], data['type'], data['size'], data['location'], data['barcode'], data['serial_number'], None, None))
    conn.commit()
    conn.close()
    return redirect(url_for('section', section=data['section']))

# Route to capture and save location
@app.route('/capture_location/<int:id>', methods=['POST'])
def capture_location(id):
    data = request.json
    coordinates = f"{data['latitude']}, {data['longitude']}"
    conn = get_db_connection()
    conn.execute('UPDATE extinguishers SET location_coordinates = ? WHERE id = ?', (coordinates, id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'coordinates': coordinates})

# Route to mark pass/fail for an extinguisher
@app.route('/mark_pass_fail/<int:id>', methods=['POST'])
def mark_pass_fail(id):
    status = request.form['status']
    conn = get_db_connection()
    conn.execute('UPDATE extinguishers SET pass_fail = ?, date_inspected = ?, initials = ? WHERE id = ?', 
                 (status, datetime.now().strftime("%Y-%m-%d"), request.form['initials'], id))
    conn.commit()
    conn.close()
    return redirect(url_for('section', section=request.form['section']))

# Barcode scanning endpoint
@app.route('/scan', methods=['POST'])
def scan():
    barcode = request.form['barcode']
    conn = get_db_connection()
    extinguisher = conn.execute('SELECT * FROM extinguishers WHERE barcode = ?', (barcode,)).fetchone()
    conn.close()
    if extinguisher:
        return render_template('extinguisher_details.html', extinguisher=extinguisher)
    else:
        return "Extinguisher not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
