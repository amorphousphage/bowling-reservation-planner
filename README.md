# bowling lane reservation planner

A flask application for displaying and recording bowling lane reservations for any bowling center.

## current features
- Display a bowling lane reservation plan for today for 12 bowling lanes (number of lanes can be adapted in the code). The default timeframe is 12pm - 2 am (can be adapted in the code).
- Date picker functionality to show the reservation plan for any given day.
- Display bowling reservations with the following data:
    - Date of the reservation
    - Name of the person who reserved a lane
    - Start Time
    - Duration
    - Number of Players
    - Indicator if kids are playing (who would like to use the side bumpers)
    - Lane Number(s)
    - If the reservation is a special event (per default there are two variants for a Kid's Birthday. This can be adopted in the code)
- Update or Delete an existing reservation
- Mark each lane as "OK" or "Defective"
- The current timeslot is indicated in red for the reservation planner of the current day
- Translation into German
- Reservation plan is secured with a User login

## status
This application is still in early development and not ready for use.

## features to be added in the future
- Edit Check (Error Message) if a new/update reservation is overlapping with an existing one
- Edit Check (Warning Message) if kids are indicated for a lane, but one of the selected lanes does not have side bumpers installed)
- Edit Check (Warning Message) if a reservation is booked on a defective lane
- GUI to change the amount of lanes and the timeframe displayed
- Translations for the following languages with a GUI indicator to switch: English, French, Italian, Spanish
- Reservation planner for Billards

## technical specifications
This application uses a MySQL database for data storage of reservations and lane status (OK vs. Defective)

