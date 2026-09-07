import sqlite3

DB_PATH = "db/weather.db"
SQL_PATH = "sql/build_analytical_tables.sql"

def run_transformations():
    with open(SQL_PATH, "r") as f:
        script = f.read()

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(script)
    conn.commit()
    conn.close()
    print("Analytical base tables refreshed successfully.")

if __name__ == "__main__":
    run_transformations()
