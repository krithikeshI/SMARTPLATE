# smartplate/db.py
import oracledb
import bcrypt
from contextlib import contextmanager
import os
import re 


ORACLE_USER = "system"
ORACLE_PASSWORD = "sanjay" 
ORACLE_DSN = "localhost:1521/XE" 


ORACLE_CLIENT_LIB_DIR = r"C:\oracle\instantclient-basic-windows\instantclient_23_8" 

@contextmanager
def get_conn():
    """Provides an Oracle database connection that is safely closed."""
    conn = None
    try:
        conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)
        yield conn
    except oracledb.DatabaseError as e:
        print(f"Database connection error: {e}"); raise
    finally:
        if conn:
            try: conn.close()
            except oracledb.DatabaseError as e: print(f"Error closing DB connection: {e}")

def init_oracle_driver():
    """Initializes the Oracle client driver."""
    try:
        print(f"Initializing Oracle client from: {ORACLE_CLIENT_LIB_DIR}...")
        oracledb.init_oracle_client(lib_dir=ORACLE_CLIENT_LIB_DIR)
        print("Oracle client initialized."); return True
    except Exception as e:
        print(f"CRITICAL: Failed to initialize Oracle client: {e}"); return False

def init_db_schema():
    """Initializes the database schema only if objects don't exist (11g compatible)."""
    print("Checking database schema (11g compatible)...")
    created_objects = False
    try:
        with get_conn() as conn:
            c = conn.cursor()

            # --- Check and Create Users Table, Sequence, Trigger ---
            c.execute("SELECT table_name FROM user_tables WHERE table_name = 'USERS'")
            if c.fetchone() is None:
                print("Creating table: USERS")
                c.execute("CREATE TABLE users (id NUMBER PRIMARY KEY, email VARCHAR2(255) UNIQUE NOT NULL, password_hash RAW(60) NOT NULL, name VARCHAR2(255))")
                created_objects = True # Mark that we created something

                # Only create sequence/trigger if table was just created
                print("Creating sequence: USERS_SEQ")
                c.execute("CREATE SEQUENCE users_seq START WITH 1 INCREMENT BY 1 NOCACHE")
                print("Creating trigger: USERS_BI")
                c.execute("""CREATE OR REPLACE TRIGGER users_bi BEFORE INSERT ON users FOR EACH ROW
                           BEGIN IF :new.id IS NULL THEN SELECT users_seq.NEXTVAL INTO :new.id FROM dual; END IF; END;""")
                c.execute("ALTER TRIGGER users_bi ENABLE")
            else:
                print("Table 'USERS' already exists.")

            # --- Check and Create Meal Logs Table, Sequence, Trigger ---
            c.execute("SELECT table_name FROM user_tables WHERE table_name = 'MEAL_LOGS'")
            if c.fetchone() is None:
                print("Creating table: MEAL_LOGS")
                c.execute("""CREATE TABLE meal_logs (id NUMBER PRIMARY KEY, user_id NUMBER, date_log DATE, meal VARCHAR2(500), calories NUMBER,
                           protein VARCHAR2(50), carbs VARCHAR2(50), fat VARCHAR2(50), fiber VARCHAR2(50), sugar VARCHAR2(50), sodium VARCHAR2(50),
                           FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)""")
                created_objects = True

                print("Creating sequence: MEAL_LOGS_SEQ")
                c.execute("CREATE SEQUENCE meal_logs_seq START WITH 1 INCREMENT BY 1 NOCACHE")
                print("Creating trigger: MEAL_LOGS_BI")
                c.execute("""CREATE OR REPLACE TRIGGER meal_logs_bi BEFORE INSERT ON meal_logs FOR EACH ROW
                           BEGIN IF :new.id IS NULL THEN SELECT meal_logs_seq.NEXTVAL INTO :new.id FROM dual; END IF; END;""")
                c.execute("ALTER TRIGGER meal_logs_bi ENABLE")
            else:
                print("Table 'MEAL_LOGS' already exists.")


            # --- Check and Create Profiles Table ---
            c.execute("SELECT table_name FROM user_tables WHERE table_name = 'PROFILES'")
            if c.fetchone() is None:
                print("Creating table: PROFILES")
                c.execute("""CREATE TABLE profiles (user_id NUMBER PRIMARY KEY, name VARCHAR2(255), dob VARCHAR2(20), height_cm NUMBER,
                           weight_kg NUMBER, activity_level VARCHAR2(100), FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)""")
                created_objects = True
            else:
                print("Table 'PROFILES' already exists.")

            if created_objects:
                conn.commit() # Commit only if we actually created something
                print("Database schema creation complete.")
            else:
                print("Database schema check complete (already exists).")

    except oracledb.DatabaseError as e:
        print(f"Error checking/initializing database schema: {e}")
        error_obj, = e.args
        print(f"Oracle Error Code: {error_obj.code}, Message: {error_obj.message}")
        raise # Re-raise after logging


def _row_to_dict(cursor, row):
    """Converts an Oracle row (tuple) to a dictionary using cursor description."""
    if row is None: return None
    cols = [d[0].lower() for d in cursor.description]
    return dict(zip(cols, row))

# --- User Functions ---
def create_user(email, password, name=""):
    """Creates a new user with a hashed password."""
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    with get_conn() as conn:
        c = conn.cursor();
        try: c.execute("INSERT INTO users (email, password_hash, name) VALUES (:1, :2, :3)", (email, password_hash, name)); conn.commit(); return True
        except oracledb.IntegrityError: print(f"Email exists: {email}"); return False
        except oracledb.DatabaseError as e: print(f"DB error creating user: {e}"); conn.rollback(); return False

def authenticate(email, password):
    """Authenticates a user by email and password."""
    with get_conn() as conn:
        c = conn.cursor(); c.execute("SELECT * FROM users WHERE email = :1", (email,)); user_row = c.fetchone()
        if user_row:
            user_dict = _row_to_dict(c, user_row); stored_hash = user_dict["password_hash"]
            if isinstance(stored_hash, memoryview): stored_hash = bytes(stored_hash)
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash): return user_dict
    return None

# --- Profile Functions ---
def update_profile(user_id, name, dob, height, weight, activity):
    """Updates or inserts a user's profile."""
    with get_conn() as conn:
        c = conn.cursor(); c.execute("""MERGE INTO profiles p USING (SELECT :user_id AS user_id FROM dual) d ON (p.user_id = d.user_id) WHEN MATCHED THEN UPDATE SET p.name = :name, p.dob = :dob, p.height_cm = :height, p.weight_kg = :weight, p.activity_level = :activity WHEN NOT MATCHED THEN INSERT (user_id, name, dob, height_cm, weight_kg, activity_level) VALUES (:user_id, :name, :dob, :height, :weight, :activity)""", {"user_id": user_id, "name": name, "dob": dob, "height": height, "weight": weight, "activity": activity}); conn.commit()

def get_profile(user_id):
    """Retrieves a user's profile."""
    with get_conn() as conn:
        c = conn.cursor(); c.execute("SELECT * FROM profiles WHERE user_id = :1", (user_id,)); row = c.fetchone()
        return _row_to_dict(c, row) if row else None

# --- Meal Log Functions ---
def add_meal(user_id, date, meal, calories, protein, carbs, fat, fiber, sugar, sodium):
    """Adds a meal entry using direct string values from the UI."""
    try: calories_f = float(calories) if calories else 0.0
    except (ValueError, TypeError): calories_f = 0.0
    with get_conn() as conn:
        c = conn.cursor(); c.execute("""INSERT INTO meal_logs (user_id, date_log, meal, calories, protein, carbs, fat, fiber, sugar, sodium) VALUES (:1, TO_DATE(:2, 'YYYY-MM-DD'), :3, :4, :5, :6, :7, :8, :9, :10)""", (user_id, date, meal, calories_f, protein, carbs, fat, fiber, sugar, sodium)); conn.commit()

def get_meals(user_id, limit=200):
    """Retrieves meal log entries for a user, using ROWNUM for Oracle 11g compatibility."""
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""SELECT * FROM (SELECT id, TO_CHAR(date_log, 'YYYY-MM-DD') AS date_log, meal, calories, protein, carbs, fat, fiber, sugar, sodium FROM meal_logs WHERE user_id = :1 ORDER BY date_log DESC, id DESC) WHERE ROWNUM <= :2""", (user_id, limit)); rows = c.fetchall()
        return [_row_to_dict(c, row) for row in rows]

def delete_meal(meal_id):
    """Deletes a specific meal log entry by its ID."""
    with get_conn() as conn: c = conn.cursor(); c.execute("DELETE FROM meal_logs WHERE id = :1", (int(meal_id),)); conn.commit()

def update_meal(meal_id, date_str, meal, calories_str, protein_str, carbs_str, fat_str, fiber_str, sugar_str, sodium_str):
    """Updates an existing meal log entry in the database."""
    print(f"DB: Updating meal {meal_id}...");
    try: calories = float(calories_str) if calories_str else 0.0
    except ValueError: print(f"Warning: Invalid calorie value '{calories_str}'. Setting to 0."); calories = 0.0
    with get_conn() as conn:
        c = conn.cursor(); c.execute("""UPDATE meal_logs SET date_log = TO_DATE(:1, 'YYYY-MM-DD'), meal = :2, calories = :3, protein = :4, carbs = :5, fat = :6, fiber = :7, sugar = :8, sodium = :9 WHERE id = :10""", (date_str, meal, calories, protein_str, carbs_str, fat_str, fiber_str, sugar_str, sodium_str, int(meal_id))); conn.commit()
        print(f"DB: Meal {meal_id} updated.")

# --- Analytics Functions ---
def get_all_nutrition_for_today(user_id):
    """Calculates ALL key nutrient totals for today's chart."""
    with get_conn() as conn:
        c = conn.cursor()
        # Use REGEXP_SUBSTR robustly
        c.execute("""
            SELECT
                NVL(SUM(calories), 0) as total_calories,
                NVL(SUM(TO_NUMBER(REGEXP_SUBSTR(protein, '^[0-9]+(\.[0-9]+)?'))), 0) as total_protein,
                NVL(SUM(TO_NUMBER(REGEXP_SUBSTR(carbs, '^[0-9]+(\.[0-9]+)?'))), 0) as total_carbs,
                NVL(SUM(TO_NUMBER(REGEXP_SUBSTR(fat, '^[0-9]+(\.[0-9]+)?'))), 0) as total_fat,
                NVL(SUM(TO_NUMBER(REGEXP_SUBSTR(fiber, '^[0-9]+(\.[0-9]+)?'))), 0) as total_fiber,
                NVL(SUM(TO_NUMBER(REGEXP_SUBSTR(sugar, '^[0-9]+(\.[0-9]+)?'))), 0) as total_sugar,
                NVL(SUM(TO_NUMBER(REGEXP_SUBSTR(sodium, '^[0-9]+(\.[0-9]+)?'))), 0) as total_sodium
            FROM meal_logs
            WHERE user_id = :1 AND date_log = TRUNC(SYSDATE)
        """, (user_id,))
        row = c.fetchone(); return _row_to_dict(c, row)