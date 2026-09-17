import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "careersense.db")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def register_user(fullname, email, password):
    init_db()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        hashed_pw = hash_password(password)
        cursor.execute("INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)", (fullname, email, hashed_pw))
        conn.commit()
        conn.close()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, "This email is already registered!"
    except Exception as e:
        return False, str(e)

def verify_user(email, password):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    cursor.execute("SELECT fullname, email FROM users WHERE email = ? AND password = ?", (email, hashed_pw))
    user = cursor.fetchone()
    conn.close()
    if user:
        return True, user[0]  # Returns user's full name
    return False, None

# Alias function to support imports looking for authenticate_user
def authenticate_user(email, password):
    return verify_user(email, password)