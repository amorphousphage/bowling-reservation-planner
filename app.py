from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import numpy as np
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='templates')  # Set the template folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:4493abcd@localhost/bowlingreservation'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    date = db.Column(db.DateTime)
    start_time = db.Column(db.Time)
    duration = db.Column(db.Float)
    players = db.Column(db.Integer)
    kids = db.Column(db.Boolean)
    lanes = db.Column(db.String(100))
    specialevent = db.Column(db.String(200))

class DefectiveLane(db.Model):
    lane_number = db.Column(db.Integer, primary_key=True, unique=True)
    is_defective = db.Column(db.Boolean, default=False)
#Translation dictionary (german)
translations_de = {
    "Add Bowling Data":"Reservierung aktualisieren",
    "Name":"Name",
    "Date":"Datum",
    "Start Time":"Start Zeit",
    "duration (hours)":"Dauer (Stunden)",
    "Number of Players": "Anzahl Spieler",
    "Kids Playing?":"Mit Kind?",
    "Select Lane Number(s)":"Bahn(en) auswählen",
    "Lane":"Bahn",
    "Special Event":"Spezialevent",
    "No":"Nein",
    "Kid Birthday Variant 1": "Geburtstag Variante 1",
    "Kid Birthday Variant 2": "Geburtstag Variante 2",
    "Add Reservation": "Neue Reservation",
    "Save New Reservation": "Reservation abschliessen",
    "Back":"Zurück",
    "Bowling Lane Schedule":"Bowling Reservationen",
    "Bowling Lane Schedule for ":"Bowling Reservationen für ",
    "Today":"Heute",
    "Show Reservations":"Reservationen anzeigen",
    "OK":"OK",
    "Defective":"Defekt",
    "players":"Spieler",
    "with kids":" mit Kind",
    "Update Bowling Data":"Reservation aktualisieren",
    "Update Reservation":"Reservation aktualisieren",
    "Delete Reservation":"Reservation löschen"
}
days_de = {
    'Monday': 'Montag',
    'Tuesday': 'Dienstag',
    'Wednesday': 'Mittwoch',
    'Thursday': 'Donnerstag',
    'Friday': 'Freitag',
    'Saturday': 'Samstag',
    'Sunday': 'Sonntag'
}

months_de = {
    'January': 'Januar',
    'February': 'Februar',
    'March': 'März',
    'April': 'April',
    'May': 'Mai',
    'June': 'Juni',
    'July': 'Juli',
    'August': 'August',
    'September': 'September',
    'October': 'Oktober',
    'November': 'November',
    'December': 'Dezember'
}

# Define the number of lanes and time range
num_lanes = 12
start_time = 12 * 60  # Start time in minutes (12:00)
end_time = 26 * 60  # End time in minutes (02:00 on the next day)

# Generate time slots
time_slots = np.arange(start_time, end_time, 30)  # 30-minute intervals
time_slots_str = '[' + ', '.join(map(str, time_slots)) + ']'

def convert_to_date(date_string):
    try:
        return datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        return datetime.now().date()

@app.route('/', methods=['GET'])
@app.route('/<date>', methods=['GET'])
def display_schedule(date=None): 
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
        
    requested_date = convert_to_date(date)
    selected_date = request.args.get('selected_date')  # Get selected date from the form
    
    if selected_date:
        requested_date = convert_to_date(selected_date)
        date = requested_date.strftime('%Y-%m-%d')  # Get the formatted date to pass to the URL
    #translate day name and month to german
    translated_day = days_de[requested_date.strftime('%A')]
    translated_month = months_de[requested_date.strftime('%B')]
    
    # Calculate previous and next dates
    prev_date = (requested_date - timedelta(days=1)).strftime('%Y-%m-%d')
    next_date = (requested_date + timedelta(days=1)).strftime('%Y-%m-%d')

    # Get defective states for all lanes
    defective_states = {lane.lane_number: lane.is_defective for lane in DefectiveLane.query.all()}

    
    reservations = Reservation.query.filter_by(date=requested_date).all()
    lane_reservations = {lane: {time_slot: None for time_slot in time_slots} for lane in range(num_lanes)}

    for reservation in reservations:
        lanes = reservation.lanes.split(',')  # Split the stored lane string into individual lanes
        start_time = reservation.start_time.strftime('%H:%M')
        duration_slots = int(reservation.duration * 60 / 30)
        for lane in lanes:  # Iterate through each lane in the reservation
            lane = int(lane) - 1 # Convert lane to integer and adjust index
            for i, time_slot in enumerate(time_slots):
                time_slot_formatted = "%02d:%02d" % ((time_slot // 60) % 24, time_slot % 60)
                if time_slot_formatted == start_time:
                    lane_reservations[lane][time_slot] = {
                        'id': reservation.id,
                        'name': reservation.name,
                        'players': reservation.players,
                        'duration_slots': duration_slots,
                        'kids': reservation.kids,
                        'specialevent': reservation.specialevent
                    }
                    for j in range(1, duration_slots):
                        lane_reservations[lane][time_slots[i + j]] = 'occupied'
    
    lane_defective_states = {}
    for lane in range(num_lanes):
        defective_lane = DefectiveLane.query.filter_by(lane_number=lane + 1).first()
        lane_defective_states[lane] = defective_lane.is_defective if defective_lane else False
    
    
    return render_template('schedule.html', num_lanes=num_lanes, time_slots=time_slots, time_slots_str=time_slots_str, lane_reservations=lane_reservations, requested_date=requested_date, prev_date=prev_date, next_date=next_date, lane_defective_states=lane_defective_states, translations_de=translations_de, translated_day=translated_day, translated_month=translated_month)

def home():
    return 'This is a protected page!'

@app.before_request
def check_auth():
    auth = request.authorization
    if not auth or not (auth.username == 'GoEasy Bowling' and auth.password == 'goebrp'):
        return authenticate()
        
def authenticate():
    return Response('Please authenticate.', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

@app.route('/add_data')
def add_data():
    today = datetime.today().strftime('%d-%b-%Y')
    return render_template('add_data.html', num_lanes=num_lanes, lanes=range(1, num_lanes + 1), today=today, translations_de=translations_de)
@app.route('/submit_data', methods=['POST'])
def submit_data():
    name = request.form.get('name')
    date = datetime.strptime(request.form.get('date'), '%d-%b-%Y').date()
    start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
    duration = float(request.form.get('duration'))
    
    if request.form.get('players') != '':    
        players = int(request.form.get('players'))
    else:
        players = None
        
    selected_lanes = request.form.getlist('lanes[]')

    lanes_string = ','.join(selected_lanes)
    kids_playing = 1 if 'kids' in request.form else 0
    special_event = request.form.get('special_event')

    # Save the reservation to the database
    new_reservation = Reservation(
        name=name,
        date=date,
        start_time=start_time,
        duration=duration,
        players=players,
        kids=kids_playing,
        lanes=lanes_string,
        specialevent=special_event
    )
    db.session.add(new_reservation)
    db.session.commit()

    return redirect(url_for('display_schedule'))
    

@app.route('/update_data', methods=['GET'])
def update_data():
    reservation_id = request.args.get('id')
    reservation = Reservation.query.filter_by(id=reservation_id).first()
    
    if reservation:
        return render_template('update_data.html', reservation=reservation, lanes=range(1, num_lanes + 1), translations_de=translations_de)
    else:
        return "Reservation not found", 404

    
@app.route('/update_reservation', methods=['POST'])
def update_reservation():
    action = request.form.get('action')
    reservation_id = request.form.get('reservation_id')
    # Query the database to get the reservation entry
    reservation = Reservation.query.filter_by(id=reservation_id).first()
   
    if action == 'Update':
        # Extract updated reservation data from the form
        kids_playing = 1 if 'kids' in request.form else 0
    
        name = request.form.get('name')
        date = datetime.strptime(request.form.get('date'), '%d-%b-%Y').date()
        start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
        duration = float(request.form.get('duration'))
        
        if request.form.get('players') != '':    
            players = int(request.form.get('players'))
        else:
            players = None
            
        selected_lanes = request.form.getlist('lanes[]')
    
        lanes_string = ','.join(selected_lanes)
        kids_playing = 1 if 'kids' in request.form else 0
        special_event = request.form.get('special_event')
        
        # Update the reservation entry with the new data
        reservation.name = name
        reservation.date = date
        reservation.start_time = start_time
        reservation.duration = duration
        reservation.players = players
        reservation.kids = kids_playing
        reservation.lanes = lanes_string
        reservation.specialevent = special_event

        # Commit the changes to the database
        db.session.commit()

        # Redirect to the schedule page or any other page after successful update
        return redirect(url_for('display_schedule'))
    
    elif action == 'Delete':

        print(reservation)
        if reservation:
            db.session.delete(reservation)
            db.session.commit()
            return redirect(url_for('display_schedule'))
        else:
            return "Reservation not found", 404
            
    return "Invalid action or reservation not found", 404

@app.route('/update_defective_state', methods=['POST'])
def update_defective_state():
    lane_number = request.form.get('laneNumber')
    is_defective_str = request.form.get('isDefective')

    # Convert the string to a boolean
    is_defective = is_defective_str.lower() == 'true'

    # Update the defective state in the database
    defective_lane = DefectiveLane.query.filter_by(lane_number=lane_number).first()
    if defective_lane:
        defective_lane.is_defective = is_defective
    else:
        new_defective_lane = DefectiveLane(lane_number=lane_number, is_defective=is_defective)
        db.session.add(new_defective_lane)

    db.session.commit()
    
    return ('', 204)

if __name__ == '__main__':
    app.run(debug=True)
