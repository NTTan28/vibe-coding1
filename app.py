from flask import Flask, render_template, request, redirect
import sqlite3
import pandas as pd

app = Flask(__name__)

DATABASE = "database.db"


def get_db():
    return sqlite3.connect(DATABASE)


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS student(
        student_id TEXT PRIMARY KEY,
        name TEXT,
        birth_year INTEGER,
        major TEXT,
        gpa REAL
    )
    """)

    conn.commit()
    conn.close()


# import dữ liệu từ file CSV
def import_data():

    conn = get_db()
    df = pd.read_csv("sample_students_data_50.csv")

    for index, row in df.iterrows():

        conn.execute("""
        INSERT OR IGNORE INTO student(student_id,name,birth_year,major,gpa)
        VALUES(?,?,?,?,?)
        """,(row["student_id"],row["name"],row["birth_year"],row["major"],row["gpa"]))

    conn.commit()
    conn.close()


@app.route("/")
def index():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM student")
    students = cur.fetchall()

    conn.close()

    return render_template("index.html", students=students)


@app.route("/add", methods=["GET","POST"])
def add_student():

    if request.method == "POST":

        student_id = request.form["student_id"]
        name = request.form["name"]
        birth_year = request.form["birth_year"]
        major = request.form["major"]
        gpa = request.form["gpa"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO student VALUES(?,?,?,?,?)
        """,(student_id,name,birth_year,major,gpa))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add_student.html")


@app.route("/edit/<student_id>", methods=["GET","POST"])
def edit_student(student_id):

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        birth_year = request.form["birth_year"]
        major = request.form["major"]
        gpa = request.form["gpa"]

        cur.execute("""
        UPDATE student
        SET name=?,birth_year=?,major=?,gpa=?
        WHERE student_id=?
        """,(name,birth_year,major,gpa,student_id))

        conn.commit()
        conn.close()

        return redirect("/")

    cur.execute("SELECT * FROM student WHERE student_id=?",(student_id,))
    student = cur.fetchone()

    conn.close()

    return render_template("edit_student.html", student=student)


@app.route("/delete/<student_id>")
def delete_student(student_id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM student WHERE student_id=?",(student_id,))
    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    init_db()
    import_data()
    app.run(debug=True)