from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB = "candidates.db"

def get_conn():
    return sqlite3.connect(DB)
def create_table():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        college_name TEXT,
        round1 FLOAT,
        round2 FLOAT,
        round3 FLOAT,
        technical FLOAT,
        total FLOAT,
        result TEXT,
        rank INTEGER
    )
    """)
    conn.commit()
    conn.close()

def evaluate_candidate(r1, r2, r3, tech):
    #updated code during the machine test as asked
    if (
        r1 < 6.5 or
        r2 < 6.5 or
        r3 < 6.5 or 
        tech < 13
    ) :
        total = r1 + r2 + r3 + tech
        return total, "Rejected"

       
        
    total = r1 + r2 + r3 + tech
    result = "Selected" if total >= 35 else "Rejected"
    return total, result

def calculate_ranks():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, total FROM candidates ORDER BY total DESC")
    rows = cursor.fetchall()

    prev_score = None
    current_rank = 0

    for i, (cid, score) in enumerate(rows):
        if score != prev_score:
            current_rank = i + 1
            prev_score = score
        cursor.execute(
            "UPDATE candidates SET rank = ? WHERE id = ?",
            (current_rank, cid)
        )

    conn.commit()
    conn.close()

@app.route("/", methods=["GET"])
def index():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT student_name, college_name, total, result, rank
        FROM candidates
        ORDER BY rank
    """)
    data = cursor.fetchall()
    conn.close()
    return render_template("index.html", candidates=data)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"].strip()
    college = request.form["college"].strip()
    r1 = float(request.form["r1"])
    r2 = float(request.form["r2"])
    r3 = float(request.form["r3"])
    tech = float(request.form["tech"])

    total, result = evaluate_candidate(r1, r2, r3, tech)

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO candidates
        (student_name, college_name, round1, round2, round3, technical, total, result)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, college, r1, r2, r3, tech, total, result))
    conn.commit()
    conn.close()

    calculate_ranks()
    return redirect(url_for("index"))

# ---------- MAIN ----------
if __name__ == "__main__":
    create_table()
    app.run(debug=True)