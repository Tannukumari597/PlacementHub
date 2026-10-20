from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

# Session ke liye secret key
app.secret_key = "placementhub_secret_key"


# ================= DATABASE =================

def create_database():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            course TEXT NOT NULL,
            skills TEXT,
            passing_year INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            company TEXT NOT NULL,
            job_role TEXT NOT NULL,
            status TEXT DEFAULT 'Applied'
        )
    """)

    conn.commit()
    conn.close()


# ================= HOME =================

@app.route("/")
def home():
    return render_template("index.html")


# ================= STUDENT REGISTER =================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        course = request.form["course"]
        skills = request.form["skills"]
        passing_year = request.form["passing_year"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO students
            (name, email, phone, course, skills, passing_year)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            email,
            phone,
            course,
            skills,
            passing_year
        ))

        conn.commit()
        conn.close()

        return "Registration Successful!"

    return render_template("register.html")


# ================= STUDENT LOGIN =================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE email = ?",
            (email,)
        )

        student = cursor.fetchone()

        conn.close()

        if student:

            return render_template(
                "dashboard.html",
                student=student
            )

        return "Student not found!"

    return render_template("login.html")


# ================= COMPANIES =================

@app.route("/companies")
def companies():

    return render_template("companies.html")


# ================= JOBS =================

@app.route("/jobs/<int:student_id>")
def jobs(student_id):

    return render_template(
        "jobs.html",
        student_id=student_id
    )


# ================= APPLY FOR JOB =================

@app.route("/apply", methods=["POST"])
def apply():

    student_id = request.form["student_id"]
    company = request.form["company"]
    job_role = request.form["job_role"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO applications
        (student_id, company, job_role, status)
        VALUES (?, ?, ?, ?)
    """, (
        student_id,
        company,
        job_role,
        "Applied"
    ))

    conn.commit()
    conn.close()

    return "Application Submitted Successfully!"


# ================= MY APPLICATIONS =================

@app.route("/applications/<int:student_id>")
def applications(student_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, company, job_role, status
        FROM applications
        WHERE student_id = ?
    """, (student_id,))

    applications = cursor.fetchall()

    conn.close()

    return render_template(
        "applications.html",
        applications=applications
    )


# ================= ADMIN LOGIN =================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            session["admin_logged_in"] = True

            return redirect("/admin")

        return "Invalid Admin Username or Password!"

    return render_template("admin_login.html")


# ================= ADMIN DASHBOARD =================

@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):

        return redirect("/admin-login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Registered students
    cursor.execute("""
        SELECT * FROM students
    """)

    students = cursor.fetchall()

    # Placement applications
    cursor.execute("""
        SELECT
            applications.id,
            students.name,
            applications.company,
            applications.job_role,
            applications.status
        FROM applications
        JOIN students
        ON applications.student_id = students.id
    """)

    applications = cursor.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        students=students,
        applications=applications
    )


# ================= UPDATE APPLICATION STATUS =================

@app.route("/update_status/<int:application_id>", methods=["POST"])
def update_status(application_id):

    if not session.get("admin_logged_in"):

        return redirect("/admin-login")

    status = request.form["status"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE applications
        SET status = ?
        WHERE id = ?
    """, (
        status,
        application_id
    ))

    conn.commit()
    conn.close()

    return redirect("/admin")


# ================= ADMIN LOGOUT =================

@app.route("/admin-logout")
def admin_logout():

    session.pop("admin_logged_in", None)

    return redirect("/admin-login")


# ================= RUN APPLICATION =================

if __name__ == "__main__":

    create_database()

    app.run(debug=True)