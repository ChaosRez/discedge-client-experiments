import sqlite3
import os
import config
import logging

logger = logging.getLogger(__name__)


def init_db():
    """Initializes the database and creates tables if they don't exist."""
    logger.info("Initializing database...")
    os.makedirs(config.DB_DIRECTORY, exist_ok=True)
    with sqlite3.connect(config.DB_PATH) as conn:
        cursor = conn.cursor()

        # Create users table
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS users (
                                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                            user_id TEXT UNIQUE NOT NULL,
                                                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                       )
                       """)

        # Create sessions table
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS sessions (
                                                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                               session_id TEXT UNIQUE NOT NULL,
                                                               user_db_id INTEGER NOT NULL,
                                                               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                               FOREIGN KEY(user_db_id) REFERENCES users(id)
                           )
                       """)

        # Create messages table
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS messages (
                                                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                               session_db_id INTEGER NOT NULL,
                                                               role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                           content TEXT NOT NULL,
                           model_name TEXT,
                           scenario_name TEXT,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY(session_db_id) REFERENCES sessions(id)
                           )
                       """)
        conn.commit()
        logger.info("Database initialized.")

def add_user_if_not_exists(user_id):
    """Adds a user if they don't exist and returns their database ID."""
    with sqlite3.connect(config.DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if user:
            logger.debug(f"User '{user_id}' already exists with DB ID {user[0]}.")
            return user[0]
        else:
            logger.info(f"Creating new user '{user_id}'.")
            cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
            conn.commit()
            new_user_id = cursor.lastrowid
            logger.info(f"User '{user_id}' created with DB ID {new_user_id}.")
            return new_user_id

def create_session(session_id, user_db_id):
    """Creates a new session and returns its database ID."""
    with sqlite3.connect(config.DB_PATH) as conn:
        cursor = conn.cursor()
        logger.info(f"Creating new session '{session_id}' for user DB ID {user_db_id}.")
        cursor.execute("INSERT INTO sessions (session_id, user_db_id) VALUES (?, ?)", (session_id, user_db_id))
        conn.commit()
        new_session_id = cursor.lastrowid
        logger.info(f"Session '{session_id}' created with DB ID {new_session_id}.")
        return new_session_id

def add_message(session_db_id, role, content, model_name=None, scenario_name=None):
    """Adds a message to the database."""
    with sqlite3.connect(config.DB_PATH) as conn:
        cursor = conn.cursor()
        logger.debug(f"Adding message for session DB ID {session_db_id}. Role: {role}, Content: {content[:50]}...")
        cursor.execute(
            "INSERT INTO messages (session_db_id, role, content, model_name, scenario_name) VALUES (?, ?, ?, ?, ?)",
            (session_db_id, role, content, model_name, scenario_name)
        )
        conn.commit()
        logger.info(f"Message added for session DB ID {session_db_id}.")
