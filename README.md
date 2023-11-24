# bowling lane reservation planner

A flask application for displaying and recording bowling lane reservations for any bowling center.

## current features
- Display a bowling lane reservation plan for today for 12 bowling lanes (number of lanes can be modified in the code). The default timeframe is 12pm - 2 am (can be modified in the code).
- Date picker functionality to show the reservation plan for any given day.
- Display bowling reservations with the following data:
    - Date of the reservation
    - Name of the person who reserved a lane
    - Start Time
    - Duration
    - Number of Players
    - Indicator if kids are playing (who would like to use the side bumpers)
    - Lane Number(s)
    - If the reservation is a special event (per default there are two variants for a Kid's Birthday. This can be modified in the code)
- Update or Delete an existing reservation
- Mark each lane as "OK" or "Defective"
- The current timeslot is indicated in red for the reservation planner of the current day
- Translations for the following languages: English, German, French, Italian, Spanish (can be selected in the code)
- Reservation plan is secured with a User login

## status
The first testing version was hosted on PythonAnywhere, but has not been tested/validated yet.

## features to be added in the future
- Validation Check (Error Message) if a new/update reservation is overlapping with an existing one
- Validation Check (Warning Message) if kids are indicated for a lane, but one of the selected lanes does not have side bumpers installed)
- Validation Check (Warning Message) if a reservation is booked on a defective lane
- Reservation planner for Billards

## technical specifications
This application uses a MySQL database for data storage of reservations and lane status (OK vs. Defective)

