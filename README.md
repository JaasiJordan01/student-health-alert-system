# University Health Alert & Student Tracking System

A prototype application for university health alerts, wellness updates, and emergency location support.

## Features
- Student login using university email
- Health alert feed for epidemics, pandemic issues, wellness, and mental health
- Student profile and emergency contacts
- Location tracking simulation with GPS-style coordinates
- Admin dashboard overview
- Sample data for prototype testing

## Tech stack
- Python 3
- Flask
- SQLite
- HTML/CSS/JS

## Run locally
1. Clone the repository
2. Create a virtual environment
3. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open:
- http://localhost:5000/
- http://localhost:5000/admin

Sample student email for testing:
- km275497@students.cavebndish.ac.ug

## Prototype testing notes
- The app uses SQLite and generates sample data automatically on first launch.
- Location data is simulated for testing purposes.
- This is a prototype and should be expanded before production deployment.
