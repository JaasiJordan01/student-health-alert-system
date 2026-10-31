from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "university_health.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone_number TEXT,
                faculty TEXT,
                year_of_study INTEGER,
                device_id TEXT,
                location_enabled INTEGER DEFAULT 1,
                emergency_access INTEGER DEFAULT 1,
                latitude REAL,
                longitude REAL,
                last_updated TEXT
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                issue_date TEXT NOT NULL,
                expires_at TEXT,
                is_active INTEGER DEFAULT 1
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS location_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                accuracy REAL,
                source TEXT,
                recorded_at TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS emergency_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                relationship TEXT,
                phone_number TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id)
            )
            """
        )


def seed_data():
    conn = get_db_connection()
    student_count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    if student_count == 0:
        students = [
            (
                "Kawuma Mpalanyi",
                "km275497@students.cavebndish.ac.ug",
                "+256772123456",
                "Computer Science",
                3,
                "DEV-CRM-7842",
                1,
                1,
                0.3476,
                32.5825,
                "2026-10-31T08:15:00"
            ),
            (
                "Amina Nakato",
                "an440201@students.cavebndish.ac.ug",
                "+256700445566",
                "Public Health",
                2,
                "DEV-HEA-3104",
                1,
                1,
                0.3333,
                32.5761,
                "2026-10-31T09:20:00"
            ),
            (
                "Daniel Opio",
                "do892101@students.cavebndish.ac.ug",
                "+256788900112",
                "Engineering",
                4,
                "DEV-ENG-9911",
                1,
                1,
                0.3410,
                32.5890,
                "2026-10-31T07:45:00"
            )
        ]
        for std in students:
            conn.execute(
                """
                INSERT INTO students (full_name, email, phone_number, faculty, year_of_study,
                device_id, location_enabled, emergency_access, latitude, longitude, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                std,
            )

        conn.execute(
            """
            INSERT INTO alerts (title, description, category, severity, issue_date, expires_at, is_active)
            VALUES
            (?, ?, ?, ?, ?, ?, 1),
            (?, ?, ?, ?, ?, ?, 1),
            (?, ?, ?, ?, ?, ?, 1),
            (?, ?, ?, ?, ?, ?, 1)
            """,
            (
                "Campus Water Safety Notice",
                "Students are advised to use filtered water points and report any unusual odor or discoloration.",
                "Campus Health",
                "medium",
                "2026-10-30T10:00:00",
                "2026-11-05T23:59:00",
                "Movement and Wellness Update",
                "The university has expanded wellness sessions for stress management and general fitness support.",
                "Mental Health",
                "low",
                "2026-10-31T08:00:00",
                "2026-11-15T23:59:00",
                "Epidemic Awareness",
                "A viral respiratory illness has been reported in the local community. Students should avoid crowded spaces when possible.",
                "Pandemic",
                "high",
                "2026-10-29T12:00:00",
                "2026-11-07T23:59:00",
                "Healthy Living Quote",
                "Take care of your body. It’s the only place you have to live. — Jim Stovall",
                "Wellness",
                "low",
                "2026-10-31T06:00:00",
                "2026-11-30T23:59:00",
            ),
        )

        alert_rows = conn.execute("SELECT id FROM students").fetchall()
        for student_row in alert_rows:
            student_id = student_row[0]
            base_lat = 0.3450 + (student_id * 0.003)
            base_lon = 32.5800 + (student_id * 0.004)
            for idx in range(3):
                conn.execute(
                    """
                    INSERT INTO location_logs (student_id, latitude, longitude, accuracy, source, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        student_id,
                        round(base_lat + (idx * 0.002), 6),
                        round(base_lon + (idx * 0.0015), 6),
                        10 + idx,
                        "GPS",
                        datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
                    )
                )

            conn.execute(
                """
                INSERT INTO emergency_contacts (student_id, name, relationship, phone_number)
                VALUES (?, ?, ?, ?)
                """,
                (
                    student_id,
                    "Guardian Contact" if student_id == 1 else "Emergency Parent",
                    "Parent",
                    "+25670000000" + str(student_id),
                )
            )

    conn.close()


@app.route("/")
def home():
    students = get_students()
    return render_template("home.html", students=students)


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    role = request.form.get("role")

    if role == "admin":
        return redirect(url_for("admin_dashboard"))

    if email:
        return redirect(url_for("student_dashboard", email=email))

    return redirect(url_for("home"))


@app.route("/student/<email>")
def student_dashboard(email):
    student = get_student_by_email(email)
    if not student:
        return "Student not found", 404

    alerts = get_alerts()
    location = get_latest_location(student["id"])
    emergency_contacts = get_emergency_contacts(student["id"])
    return render_template(
        "student_dashboard.html",
        student=student,
        alerts=alerts,
        location=location,
        emergency_contacts=emergency_contacts,
    )


@app.route("/admin")
def admin_dashboard():
    students = get_students()
    alerts = get_alerts()
    summaries = {
        "student_count": len(students),
        "alert_count": len(alerts),
        "high_risk_alerts": sum(1 for a in alerts if a["severity"] == "high"),
    }
    return render_template("admin_dashboard.html", students=students, alerts=alerts, summaries=summaries)


@app.route("/api/students")
def api_students():
    return jsonify(get_students())


@app.route("/api/alerts")
def api_alerts():
    return jsonify(get_alerts())


@app.route("/health")
def health_check():
    return {"status": "ok", "database": str(DB_PATH)}, 200


def get_students():
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT id, full_name, email, phone_number, faculty, year_of_study, device_id,
               location_enabled, emergency_access, latitude, longitude, last_updated
        FROM students
        ORDER BY id ASC
        """
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_student_by_email(email):
    conn = get_db_connection()
    row = conn.execute(
        """
        SELECT id, full_name, email, phone_number, faculty, year_of_study, device_id,
               location_enabled, emergency_access, latitude, longitude, last_updated
        FROM students WHERE email = ?
        """,
        (email,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_alerts():
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT id, title, description, category, severity, issue_date, expires_at, is_active
        FROM alerts ORDER BY id DESC
        """
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_latest_location(student_id):
    conn = get_db_connection()
    row = conn.execute(
        """
        SELECT latitude, longitude, source, accuracy, recorded_at
        FROM location_logs WHERE student_id = ? ORDER BY id DESC LIMIT 1
        """,
        (student_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_emergency_contacts(student_id):
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT name, relationship, phone_number FROM emergency_contacts WHERE student_id = ?
        """,
        (student_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    init_db()
    seed_data()
    app.run(debug=True, host="0.0.0.0", port=5000)

