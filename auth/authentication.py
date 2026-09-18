import sqlite3
import hashlib
import secrets
from pathlib import Path


# ==========================================================
# BASE DIRECTORY
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

DATABASE_PATH = DATA_DIR / "careersense.db"


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def get_connection():

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    return sqlite3.connect(
        DATABASE_PATH
    )


# ==========================================================
# INITIALIZE DATABASE
# ==========================================================

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
        """
    )

    connection.commit()

    connection.close()


# ==========================================================
# HASH PASSWORD
# ==========================================================

def hash_password(password):

    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000
    ).hex()

    return password_hash, salt


# ==========================================================
# VERIFY PASSWORD
# ==========================================================

def verify_password(
    password,
    stored_hash,
    salt
):

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000
    ).hex()

    return password_hash == stored_hash


# ==========================================================
# REGISTER USER
# ==========================================================

def register_user(
    name,
    email,
    password
):

    name = name.strip()

    email = email.strip().lower()


    # ------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------

    if not name:

        return False, "Please enter your full name."


    if not email:

        return False, "Please enter your email address."


    if not password:

        return False, "Please enter a password."


    if len(password) < 6:

        return False, (
            "Password must contain at least 6 characters."
        )


    # ------------------------------------------------------
    # HASH PASSWORD
    # ------------------------------------------------------

    password_hash, salt = hash_password(
        password
    )


    # ------------------------------------------------------
    # INSERT USER
    # ------------------------------------------------------

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password_hash,
                salt
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                email,
                password_hash,
                salt
            )
        )

        connection.commit()

        return True, "Account created successfully."


    except sqlite3.IntegrityError:

        return False, (
            "An account with this email already exists."
        )


    finally:

        connection.close()


# ==========================================================
# AUTHENTICATE USER
# ==========================================================

def authenticate_user(
    email,
    password
):

    email = email.strip().lower()


    # ------------------------------------------------------
    # NEVER ALLOW EMPTY PASSWORD
    # ------------------------------------------------------

    if not email:

        return None


    if not password:

        return None


    # ------------------------------------------------------
    # FIND USER BY EMAIL
    # ------------------------------------------------------

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            email,
            password_hash,
            salt
        FROM users
        WHERE email = ?
        """,
        (email,)
    )

    user = cursor.fetchone()

    connection.close()


    # ------------------------------------------------------
    # USER NOT FOUND
    # ------------------------------------------------------

    if user is None:

        return None


    # ------------------------------------------------------
    # GET USER DATA
    # ------------------------------------------------------

    user_id = user[0]

    name = user[1]

    user_email = user[2]

    stored_hash = user[3]

    salt = user[4]


    # ------------------------------------------------------
    # VERIFY PASSWORD
    # ------------------------------------------------------

    if not verify_password(
        password,
        stored_hash,
        salt
    ):

        return None


    # ------------------------------------------------------
    # RETURN AUTHENTICATED USER
    # ------------------------------------------------------

    return {
        "id": user_id,
        "name": name,
        "email": user_email
    }


# ==========================================================
# CHECK IF USER EXISTS
# ==========================================================

def user_exists(email):

    email = email.strip().lower()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE email = ?
        """,
        (email,)
    )

    result = cursor.fetchone()

    connection.close()

    return result is not None


# ==========================================================
# INITIALIZE DATABASE
# ==========================================================

initialize_database()