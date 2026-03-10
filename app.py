from flask import Flask, render_template, request, redirect, send_file
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
    CREATE TABLE IF NOT EXISTS class(
        class_id TEXT PRIMARY KEY,
        class_name TEXT,
        advisor TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS student(
        student_id TEXT PRIMARY KEY,
        name TEXT,
        birth_year INTEGER,
        major TEXT,
        gpa REAL,
        class_id TEXT,
        FOREIGN KEY(class_id) REFERENCES class(class_id)
    )
    """)

    conn.commit()
    conn.close()


def insert_classes():

    conn = get_db()

    conn.execute("INSERT OR IGNORE INTO class VALUES ('C01','Computer Science','Nguyen Van A')")
    conn.execute("INSERT OR IGNORE INTO class VALUES ('C02','Data Science','Tran Thi B')")
    conn.execute("INSERT OR IGNORE INTO class VALUES ('C03','Artificial Intelligence','Le Van C')")

    conn.commit()
    conn.close()


def import_data():

    conn = get_db()

    df = pd.read_csv("sample_students_data_50.csv")

    for index,row in df.iterrows():

        conn.execute("""
        INSERT OR IGNORE INTO student
        VALUES(?,?,?,?,?,?)
        """,(row["student_id"],row["name"],row["birth_year"],row["major"],row["gpa"],"C01"))

    conn.commit()
    conn.close()


@app.route("/")
def index():

    search = request.args.get("search","")

    conn = get_db()
    cur = conn.cursor()

    if search:

        cur.execute("""
        SELECT student.student_id,student.name,student.birth_year,
        student.major,student.gpa,class.class_name
        FROM student
        LEFT JOIN class ON student.class_id = class.class_id
        WHERE student.name LIKE ?
        """,('%'+search+'%',))

    else:

        cur.execute("""
        SELECT student.student_id,student.name,student.birth_year,
        student.major,student.gpa,class.class_name
        FROM student
        LEFT JOIN class ON student.class_id = class.class_id
        """)

    students = cur.fetchall()

    # lấy danh sách lớp
    cur.execute("SELECT * FROM class")
    classes = cur.fetchall()

    # statistics
    cur.execute("SELECT COUNT(*) FROM student")
    total = cur.fetchone()[0]

    cur.execute("SELECT AVG(gpa) FROM student")
    avg_gpa = cur.fetchone()[0]

    cur.execute("SELECT major, COUNT(*) FROM student GROUP BY major")
    major_stats = cur.fetchall()

    conn.close()

    return render_template(
        "index.html",
        students=students,
        classes=classes,
        total=total,
        avg_gpa=avg_gpa,
        major_stats=major_stats,
        search=search
    )


@app.route("/add", methods=["GET","POST"])
def add_student():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM class")
    classes = cur.fetchall()

    if request.method == "POST":

        student_id = request.form["student_id"]
        name = request.form["name"]
        birth_year = request.form["birth_year"]
        major = request.form["major"]
        gpa = request.form["gpa"]
        class_id = request.form["class_id"]

        cur.execute("""
        INSERT INTO student VALUES(?,?,?,?,?,?)
        """,(student_id,name,birth_year,major,gpa,class_id))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add_student.html", classes=classes)


@app.route("/edit/<student_id>", methods=["GET","POST"])
def edit_student(student_id):

    conn = get_db()
    cur = conn.cursor()

    # lấy danh sách lớp
    cur.execute("SELECT * FROM class")
    classes = cur.fetchall()

    if request.method == "POST":

        name = request.form["name"]
        birth_year = request.form["birth_year"]
        major = request.form["major"]
        gpa = request.form["gpa"]
        class_id = request.form["class_id"]

        cur.execute("""
        UPDATE student
        SET name=?,birth_year=?,major=?,gpa=?,class_id=?
        WHERE student_id=?
        """,(name,birth_year,major,gpa,class_id,student_id))

        conn.commit()
        conn.close()

        return redirect("/")

    cur.execute("SELECT * FROM student WHERE student_id=?",(student_id,))
    student = cur.fetchone()

    conn.close()

    return render_template(
        "edit_student.html",
        student=student,
        classes=classes
    )


@app.route("/delete/<student_id>")
def delete_student(student_id):

    conn = get_db()

    conn.execute("DELETE FROM student WHERE student_id=?",(student_id,))
    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/export")
def export():

    conn = get_db()

    df = pd.read_sql_query("SELECT * FROM student",conn)

    file = "students.csv"
    df.to_csv(file,index=False)

    return send_file(file,as_attachment=True)


if __name__ == "__main__":

    init_db()
    insert_classes()
    import_data()

    app.run(debug=True)