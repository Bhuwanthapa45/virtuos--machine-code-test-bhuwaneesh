import sqlite3

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

def get_candidate_input():
    name = input("Enter student name: ").strip()
    if not name or len(name) > 30:

        print("Invalid student name")
        return None
    
    college = input("Enter college name: ").strip()
    if not college or len(college) > 50:
        print("Invalid college name")
        return None

    def valid_marks(label, max_val):
       val = float(input(label))
       if val < 0 or val > max_val:
        raise ValueError
       return val
 
    try:

       
        r1 = valid_marks("Round 1 (0-10): ", 10)
        r2 = valid_marks("Round 2 (0-10): ", 10)
        r3 = valid_marks("Round 3 (0-10): ", 10)
        tech = valid_marks("Technical (0-20): ", 20)
    except:
        

        print("Invalid marks entered")
        return None
    return name, college, r1,r2, r3, tech

def evaluate_candidate(r1, r2, r3, tech):
    total = r1 + r2 + r3 + tech
    result = "Selected" if total >= 35 else "Rejected"
    return total, result

def save_candidate(data):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO candidates
                   (student_name, college_name, round1, round2, round3, technical, total, result)
                   VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                   """, data)
    conn.commit()
    conn.close()

def calculate_ranks():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, total FROM candidates
                   ORDER BY total DESC
                   """)
    
    rows = cursor.fetchall()
    rank = 0
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

def display_all():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT student_name, college_name, total, result, rank
                   FROM candidates
                   ORDER BY rank
                   """)
    print("\nFinal Result:")
    for row in cursor.fetchall():
        print(row)

    conn.close()

def main():
    create_table()

    data = get_candidate_input()
    if not data:
        return
    name, college, r1, r2, r3, tech = data
    total, result = evaluate_candidate(r1, r2, r3, tech)

    save_candidate((name, college, r1, r2, r3, tech, total ,result))
    calculate_ranks()
    display_all()

if __name__ == "__main__":
    main()

