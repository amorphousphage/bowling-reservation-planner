#Import necessary modules and translations.py
from flask import Flask, render_template, request, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import numpy as np
from datetime import datetime, timedelta
from translations import *

#Setup app name and database connection
app = Flask(__name__, template_folder='templates')  # Set the template folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@hostadress/databasename'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Define reservation table design
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

#Define defective lane table design
class DefectiveLane(db.Model):
    lane_number = db.Column(db.Integer, primary_key=True, unique=True)
    is_defective = db.Column(db.Boolean, default=False)

#Define daily comment table design
class DailyComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    dailycomment = db.Column(db.String(4000))


#Select appropriate translation for the webpage
def select_language(language):
    if language == "en":
        return translations_en, days_en, months_en
    elif language == "de":
        return translations_de, days_de, months_de
    elif language == "it":
        return translations_it, days_it, months_it
    elif language == "fr":
        return translations_fr, days_fr, months_fr
    elif language == "es":
        return translations_es, days_es, months_es
    else:
        return translations_en, days_en, months_en

#Set the appriopriate language for the webpage
preferred_language = "en"
translations_selected, days_selected, months_selected = select_language(preferred_language)

#Define the date converter to convert short format of months to English for storage
def parse_date_custom(date_str, lang):
    # Get the month dictionary based on the language
    lang_months = month_dict.get(lang, {})

    # Replace month names with English abbreviations
    for locallanguage_month, english_month in lang_months.items():

        date_str = date_str.replace(locallanguage_month, english_month)

    try:
        parsed_date = datetime.strptime(date_str, '%d-%b-%Y').date()
        return parsed_date
    except ValueError:
        # Handle the case where the date format doesn't match
        return None

#Define the date converter to convert short format of months from English to preferred_language for display
def convert_to_local_date(date_string, language):

    # Get the language-specific month dictionary	
    language_months = month_dict.get(language, {})

    # Reverse the month dictionary for lookup by English month abbreviation
    reversed_month_dict = {v: k for k, v in language_months.items()}

    # Split the date string into day, month abbreviation, and year
    day, month_abbr, year = date_string.split('-')

    # Translate the month abbreviation to the local language
    translated_month = reversed_month_dict.get(month_abbr, month_abbr)

    # Return the date in the local format
    return f"{day}-{translated_month}-{year}"

#
# SET UP YOUR CENTER SETTINGS BELOW
#

# Define the number of lanes, if they have bumpers and time range to be displayed
num_lanes = 12
non_bumper_lanes = [7,8,9,10,11,12]
start_time = 12 * 60  # Start time in minutes (e.g. 12 for 12:00)
end_time = 26 * 60  # End time in minutes (if the End Time is past midnight, write 24 + hour (e.g. 26 for 2 am, as it is 24+2))
list_of_events = ["Kid Birthday Variant 1","Kid Birthday Variant 2","Company Event","Club Event","Bowling Club"] #Make sure that all events are entered here in English and that for all events translations exist in translations.py (even for translations to English)

# --------------------------------------------------------------------------

# Generate time slots
time_slots = np.arange(start_time, end_time, 30)  # 30-minute intervals
time_slots_str = '[' + ', '.join(map(str, time_slots)) + ']'

#Convert the date string for a given day as indicated in the URL to a date, otherwise select today
def convert_to_date(date_string):
    try:
        return datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        return datetime.now().date()

#Define message for reaching a password-protected page
def home():
    return 'This is a protected page!'

#Setup the simple password protection for the website
@app.before_request
def check_auth():
    auth = request.authorization
    if not auth or not (auth.username == 'username' and auth.password == 'password'):
        return authenticate()
        
def authenticate():
    return Response('Please authenticate.', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

#Route for the index homepage (Show the reservation planner)
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
    
    #translate day name and month to the language selected (for the title)
    translated_day = days_selected[requested_date.strftime('%A')]
    translated_month = months_selected[requested_date.strftime('%B')]
    
    # Calculate previous and next dates (for the <<< and >>> buttons)
    prev_date = (requested_date - timedelta(days=1)).strftime('%Y-%m-%d')
    next_date = (requested_date + timedelta(days=1)).strftime('%Y-%m-%d')

    #Get the reservations for the selected date from the database
    reservations = Reservation.query.filter_by(date=requested_date).all()
    lane_reservations = {lane: {time_slot: None for time_slot in time_slots} for lane in range(num_lanes)}
    
    #Store the reservation data in a variable
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
                    #Mark the succeeding slots after the start time for a reservation as "occupied"
                    for j in range(1, duration_slots):
                        lane_reservations[lane][time_slots[i + j]] = 'occupied'
    
    #Get the lane status for each lane
    lane_defective_states = {}
    for lane in range(num_lanes):
        defective_lane = DefectiveLane.query.filter_by(lane_number=lane + 1).first()
        lane_defective_states[lane] = defective_lane.is_defective if defective_lane else False
        
    #Get the daily comment if it exists
    daily_comment_from_database = DailyComment.query.filter_by(date=requested_date).first()
    dailycomment= daily_comment_from_database.dailycomment
    #Display the schedule.html with the indicated variables passed to it
    return render_template('schedule.html', num_lanes=num_lanes, time_slots=time_slots, time_slots_str=time_slots_str, lane_reservations=lane_reservations, requested_date=requested_date, prev_date=prev_date, next_date=next_date, lane_defective_states=lane_defective_states, translations_selected=translations_selected, translated_day=translated_day, translated_month=translated_month, preferred_language=preferred_language, dailycomment=dailycomment)

#Route for the page of adding a reservation
@app.route('/add_data')
def add_data():
	#Format the date to auto-populate in the new reservation in the selected language
    today = convert_to_local_date(datetime.today().strftime('%d-%b-%Y'), preferred_language)
    
    #Display the add_data.html with the indicated variables passed to it
    return render_template('add_data.html', num_lanes=num_lanes, lanes=range(1, num_lanes + 1), today=today, translations_selected=translations_selected, preferred_language=preferred_language, list_of_events=list_of_events)

#Route for the page of submitting reservation data into the database
@app.route('/submit_data', methods=['POST'])
def submit_data():
	#obtain and derive the values to be stored in the database

    name = request.form.get('name')
    date = parse_date_custom(request.form.get('date'),preferred_language)
    start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
    duration = float(request.form.get('duration'))
    duration_slots = int(duration * 60 / 30)
    
    if request.form.get('players') != '':    
        players = int(request.form.get('players'))
    else:
        players = None
        
    selected_lanes = request.form.getlist('lanes[]')

    lanes_string = ','.join(selected_lanes)
    kids_playing = 1 if 'kids' in request.form else 0
    special_event = request.form.get('special_event')
    
    #Setup the dictionary for the new_reservation
    new_reservation = {lane: {time_slot: None for time_slot in time_slots} for lane in range(num_lanes)}
    #Get the reservations for the selected date from the database
    reservations = Reservation.query.filter_by(date=date).all()
    lane_reservations = {lane: {time_slot: None for time_slot in time_slots} for lane in range(num_lanes)}
    
    #Store the reservation data from the database in a dictionary for comparison
    for reservation in reservations:
        res_lanes = reservation.lanes.split(',')  # Split the stored lane string into individual lanes
        res_start_time = reservation.start_time.strftime('%H:%M')
        res_duration_slots = int(reservation.duration * 60 / 30)
        for lane in res_lanes:  # Iterate through each lane in the reservation
            lane = int(lane) - 1 # Convert lane to integer and adjust index
            for i, time_slot in enumerate(time_slots):
                time_slot_formatted = "%02d:%02d" % ((time_slot // 60) % 24, time_slot % 60)
                if time_slot_formatted == res_start_time:
                    lane_reservations[lane][time_slot] = {
                        'id': reservation.id,
                    }
                    #Mark the succeeding slots after the start time for a reservation as "occupied"
                    for j in range(1, res_duration_slots):
                        lane_reservations[lane][time_slots[i + j]] = 'occupied'
 
    # Store reservation data of the new reservation in a dictionary for comparison with the one from the database
    for lane in selected_lanes:
        lane = int(lane) - 1  # Adjust lane index
        for i, time_slot in enumerate(time_slots):
            time_slot_formatted = "%02d:%02d" % ((time_slot // 60) % 24, time_slot % 60)
            if time_slot_formatted == start_time.strftime('%H:%M'):
                new_reservation[lane][time_slot] = {
                    'name': name,
                }
                
                #Mark the succeeding slots after the start time for a reservation as "occupied"
                for j in range(1, duration_slots):
                    new_reservation[lane][time_slots[i + j]] = 'occupied'
	
    # Function to check if a new reservation overlaps with existing reservations
    overlapping_reservation= False
    for lane, slots in new_reservation.items():
        for time_slot, reservation_data in slots.items():
            # Check if the time_slot is not None in both dictionaries
            if reservation_data is not None and lane_reservations[lane][time_slot] is not None:
                overlapping_reservation = True
                break  # Exit the loop if an overlap is found

    # Check if any overlapping reservation was found
    if overlapping_reservation:
        return render_template('recheck_add_data.html', overlapping_reservation=overlapping_reservation, lanes=range(1, num_lanes + 1), translations_selected=translations_selected, name=name, date=convert_to_local_date(date,preferred_language),start_time=start_time,duration=duration,players=players,lanes_selected=lanes_string,kids=kids_playing,specialevent=special_event,preferred_language=preferred_language,list_of_events=list_of_events)
    
    # Check for defective lanes
    defective_lanes = DefectiveLane.query.filter_by(is_defective=True).all()
    defective_lane_numbers = [defective_lane.lane_number for defective_lane in defective_lanes]
    selected_lanes = request.form.getlist('lanes[]')   

    is_defective_lane = any(int(lane) in defective_lane_numbers for lane in selected_lanes)
    
    #Check for kids booked on a lane without bumpers
    is_non_bumper_lane_with_kids = any(int(lane) in non_bumper_lanes for lane in selected_lanes) and kids_playing == 1
    
    #Display the reservation again for changes or confirmation if a discrepancy is found.
    if is_defective_lane or is_non_bumper_lane_with_kids:
        return render_template('recheck_add_data.html', is_defective_lane=is_defective_lane, no_bumper_lane=is_non_bumper_lane_with_kids, lanes=range(1, num_lanes + 1), translations_selected=translations_selected, name=name, date=request.form.get('date'),start_time=start_time,duration=duration,players=players,lanes_selected=lanes_string,kids=kids_playing,specialevent=special_event, preferred_language=preferred_language,list_of_events=list_of_events)
    
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
	
	# Re-route to show the schedule after submitting a reservation
    return redirect(url_for('display_schedule'))
	
@app.route('/confirm_adding_reservation', methods=['POST'])
def confirm_adding_reservation():
	#obtain and derive the values to be stored in the database
    name = request.form.get('name')
    date = parse_date_custom(request.form.get('date'),preferred_language)
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
	
	# Re-route to show the schedule after submitting a reservation
    return redirect(url_for('display_schedule'))
    
#Route for the page of updating a reservation
@app.route('/update_data', methods=['GET'])
def update_data():
	#Obtain the reservation from the database indicated by its unique ID
    reservation_id = request.args.get('id')
    reservation = Reservation.query.filter_by(id=reservation_id).first()
    
    #Populate update_data.html with the data from the database
    if reservation:
        date = convert_to_local_date(reservation.date.strftime('%d-%b-%Y'), preferred_language)
        return render_template('update_data.html', reservation=reservation, lanes=range(1, num_lanes + 1), translations_selected=translations_selected, date=date, preferred_language=preferred_language,list_of_events=list_of_events)
    else:
        return "Reservation not found", 404

#Route for updating or deleting reservation data in the database
@app.route('/update_reservation', methods=['POST'])
def update_reservation():
    action = request.form.get('action')
    reservation_id = request.form.get('reservation_id')

   
    #Action if Update button is pressed
    if action == 'Update':
        # Extract updated reservation data from the form
        kids_playing = 1 if 'kids' in request.form else 0
    
        name = request.form.get('name')
        date = parse_date_custom(request.form.get('date'),preferred_language)
        start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
        duration = float(request.form.get('duration'))
        duration_slots = int(duration * 60 / 30)
        
        if request.form.get('players') != '':    
            players = int(request.form.get('players'))
        else:
            players = None
            
        selected_lanes = request.form.getlist('lanes[]')
    
        lanes_string = ','.join(selected_lanes)
        kids_playing = 1 if 'kids' in request.form else 0
        special_event = request.form.get('special_event')
        
        #Setup the dictionary for the new_reservation
        updated_reservation = {lane: {time_slot: None for time_slot in time_slots} for lane in range(num_lanes)}
        #Get the reservations for the selected date from the database
        reservations = Reservation.query.filter_by(date=date).all()
        lane_reservations = {lane: {time_slot: None for time_slot in time_slots} for lane in range(num_lanes)}
    
        #Store the reservation data from the database in a dictionary for comparison
        for reservation in reservations:
            res_lanes = reservation.lanes.split(',')  # Split the stored lane string into individual lanes
            res_start_time = reservation.start_time.strftime('%H:%M')
            res_duration_slots = int(reservation.duration * 60 / 30)
            for lane in res_lanes:  # Iterate through each lane in the reservation
                lane = int(lane) - 1 # Convert lane to integer and adjust index
                for i, time_slot in enumerate(time_slots):
                    time_slot_formatted = "%02d:%02d" % ((time_slot // 60) % 24, time_slot % 60)
                    if time_slot_formatted == res_start_time:
                        lane_reservations[lane][time_slot] = {
                            'id': reservation.id,
                        }
                        #Mark the succeeding slots after the start time for a reservation as "occupied"
                        for j in range(1, res_duration_slots):
                            lane_reservations[lane][time_slots[i + j]] = 'occupied'
 
        # Store reservation data of the new reservation in a dictionary for comparison with the one from the database
        for lane in selected_lanes:
            lane = int(lane) - 1  # Adjust lane index
            for i, time_slot in enumerate(time_slots):
                time_slot_formatted = "%02d:%02d" % ((time_slot // 60) % 24, time_slot % 60)
                if time_slot_formatted == start_time.strftime('%H:%M'):
                    updated_reservation[lane][time_slot] = {
                        'id': int(reservation_id),
                    }
                
                    #Mark the succeeding slots after the start time for a reservation as "occupied"
                    for j in range(1, duration_slots):
                        updated_reservation[lane][time_slots[i + j]] = 'occupied'
	
        # Function to check if a new reservation overlaps with existing reservations
        overlapping_reservation= False
        for lane, slots in updated_reservation.items():
            for time_slot, reservation_data in slots.items():
                # Check if the time_slot is not None in both dictionaries
                if reservation_data is not None and lane_reservations[lane][time_slot] is not None:
                    if reservation_data != lane_reservations[lane][time_slot]:
                    #if the IDs match, it is fine since the updated reservation is overlapping with itself
                        overlapping_reservation = True
                        break  # Exit the loop if an overlap is found

        # Check if any overlapping reservation was found
        if overlapping_reservation:
            return render_template('recheck_update_data.html', overlapping_reservation=overlapping_reservation, lanes=range(1, num_lanes + 1), translations_selected=translations_selected, id=reservation_id,name=name, date=request.form.get('date'),start_time=start_time,duration=duration,players=players,lanes_selected=lanes_string,kids=kids_playing,specialevent=special_event, preferred_language=preferred_language, list_of_events=list_of_events)
        
        # Check for defective lanes
        defective_lanes = DefectiveLane.query.filter_by(is_defective=True).all()
        defective_lane_numbers = [defective_lane.lane_number for defective_lane in defective_lanes]
        selected_lanes = request.form.getlist('lanes[]')

        is_defective_lane = any(int(lane) in defective_lane_numbers for lane in selected_lanes)
        
        #Check for kids booked on a lane without bumpers
        is_non_bumper_lane_with_kids = any(int(lane) in non_bumper_lanes for lane in selected_lanes) and kids_playing == 1
     
		#Display the reservation again for changes or confirmation if a discrepancy is found.
        if is_defective_lane or is_non_bumper_lane_with_kids:
            return render_template('recheck_update_data.html', is_defective_lane=is_defective_lane, no_bumper_lane=is_non_bumper_lane_with_kids, lanes=range(1, num_lanes + 1), translations_selected=translations_selected, id=reservation_id,name=name, date=request.form.get('date'),start_time=start_time,duration=duration,players=players,lanes_selected=lanes_string,kids=kids_playing,specialevent=special_event, preferred_language=preferred_language, list_of_events=list_of_events)
 
        # Query the database to get the reservation entry
        reservation = Reservation.query.filter_by(id=reservation_id).first()
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
    
    #Action if Delete button is pressed
    elif action == 'Delete':
		
        # Query the database to get the reservation entry
        reservation = Reservation.query.filter_by(id=reservation_id).first()
        if reservation:
            db.session.delete(reservation)
            db.session.commit()
            return redirect(url_for('display_schedule'))
        else:
            return "Reservation not found", 404
            
    return "Invalid action or reservation not found", 404

#Route for updating or deleting reservation data in the database
@app.route('/confirm_updating_reservation', methods=['POST'])
def confirm_updating_reservation():
    reservation_id = request.form.get('reservation_id')
    # Query the database to get the reservation entry
    reservation = Reservation.query.filter_by(id=reservation_id).first()
   

    # Extract updated reservation data from the form
    kids_playing = 1 if 'kids' in request.form else 0

    name = request.form.get('name')
    date = parse_date_custom(request.form.get('date'),preferred_language)
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


#Route for updating the daily comment
@app.route('/update_dailycomment/<date>', methods=['POST'])
def update_dailycomment(date=None):
    #Obtain date and comment
    requested_date=convert_to_date(date)
    daily_comment_from_form=request.form.get('dailycomment')
	
	# Query the database to get the daily comment entry
    daily_comment_from_database = DailyComment.query.filter_by(date=requested_date).first()
	
    if daily_comment_from_database:
        #Update date and comment in the database
        daily_comment_from_database.date = date
        daily_comment_from_database.dailycomment = daily_comment_from_form
    else:
        new_comment = DailyComment(
        date=date,
        dailycomment=daily_comment_from_form
        )
        db.session.add(new_comment)
    
    # Commit the changes to the database
    db.session.commit()
 
    # Redirect to the schedule page or any other page after successful update
    return redirect(url_for('display_schedule'))
    
#Route for updating an "OK" or "Defective" Lane status in the database
@app.route('/update_defective_state', methods=['POST'])
def update_defective_state():
	
	#Obtain lane number and state
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
