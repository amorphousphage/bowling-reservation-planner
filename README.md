# bowling lane reservation planner

A flask application for displaying and recording bowling lane reservations for any bowling center.

## current features
- Display a bowling lane reservation plan for today for 12 bowling lanes (number of lanes can be modified in the code). The default timeframe is 12pm - 2 am (can be modified in the code).
- Date picker functionality to show the reservation plan for any given day.
- Display bowling reservations with the following data:
    - Date of the reservation
    - Name of the person who reserved a lane
    - Start Time (in 30 minute intervals)
    - Duration
    - Number of Players
    - Indicator if kids are playing (who would like to use the side bumpers)
    - Lane Number(s)
    - If the reservation is a special event (per default there are two variants for a Kid's Birthday. This can be modified in the code)
- While adding a new reservation, one can press a button to autopopulate and unknown name or someone arriving spontaneously, which sets name and the current time.
- Update or Delete an existing reservation
- Mark each lane as "OK" or "Defective"
- The current timeslot is indicated in red for the reservation planner of the current day
- To each day a free-text comment can be added. (e.g. "clean lanes today!", "John Doe out of office today.")
- Translations for the following languages: English, German, French, Italian, Spanish (can be selected in the code)
- Validation Check (Error Message) if a new/update reservation is overlapping with an existing one
- Validation Check (Warning Message) if a reservation is booked on a defective lane
- Validation Check (Warning Message) if kids are indicated for a lane, but one of the selected lanes does not have side bumpers installed)
- HTML integrated validations for required data and start time only starting :00 or :30
- Reservation plan is secured with a User login (password should be saved in the browser if desired)

## status
The first production version was deployed in Fall of 2023 and is running smooth.

## features to be added in the future
- Reservation planner for Billards

## technical specifications
This application uses a MySQL database for data storage of reservations and lane status (OK vs. Defective)

