import sqlite3
import os
import config
import logging
import time
import json
import secrets

logger = logging.getLogger(__name__)


def _generate_short_id():
    """Generates a 16-character hex string ID."""
    return secrets.token_hex(8)


def init_db():
    """Initializes the database and creates tables if they don't exist."""
    logger.info("Initializing database...")
    os.makedirs(config.DB_DIRECTORY, exist_ok=True)
    with sqlite3.connect(config.DB_PATH) as conn:
        cursor = conn.cursor()

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                created_at INTEGER,
                last_active INTEGER,
                metadata TEXT
            )
        """)

        # Create sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                created_at INTEGER,
                last_active INTEGER,
                expires_at INTEGER,
                turn INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Create messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                session_id TEXT,
                role TEXT,
                content TEXT,
                tokens TEXT,
                model TEXT,
                timestamp INTEGER,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        # Create indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id)")

        conn.commit()
        logger.info("Database initialized.")

def create_user(user_id, metadata=None):
    """Adds a user if they don't exist."""
    with sqlite3.connect(config.DB_PATH) as conn:
        cursor = conn.cursor()
        now = int(time.time())
        meta_str = json.dumps(metadata) if metadata else "{}"

        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if user:
            logger.debug(f"User '{user_id}' already exists.")
        else:
            logger.info(f"Creating new user '{user_id}'.")
            cursor.execute(
                "INSERT INTO users (user_id, created_at, last_active, metadata) VALUES (?, ?, ?, ?)",
                (user_id, now, now, meta_str)
            )
            conn.commit()
            logger.info(f"User '{user_id}' created.")

def create_session(user_id, session_id=None, session_duration_days=7):
    """Creates a new session, generating an ID if not provided, and returns the session_id."""
    if not session_id:
        session_id = _generate_short_id()
    with sqlite3.connect(config.DB_PATH) as conn:
        cursor = conn.cursor()
        now = int(time.time())
        expires_at = now + (session_duration_days * 24 * 60 * 60)
        logger.info(f"Creating new session '{session_id}' for user '{user_id}'.")
        cursor.execute(
            "INSERT INTO sessions (session_id, user_id, created_at, last_active, expires_at, turn) VALUES (?, ?, ?, ?, ?, 0)",
            (session_id, user_id, now, now, expires_at)
        )
        conn.commit()
        logger.info(f"Session '{session_id}' created.")
    return session_id

def add_message(session_id, role, content, model_name=None, scenario_name=None, tokens=None):
    """Adds a message to the database and updates activity timestamps."""
    with sqlite3.connect(config.DB_PATH) as conn:
        cursor = conn.cursor()
        now = int(time.time())

        # Get user_id from session
        cursor.execute("SELECT user_id FROM sessions WHERE session_id = ?", (session_id,))
        result = cursor.fetchone()
        if not result:
            logger.error(f"Cannot add message, session '{session_id}' not found.")
            return
        user_id = result[0]

        logger.debug(f"Adding message for session ID {session_id}. Role: {role}, Content: {content[:50]}...")

        # Update last_active timestamps
        cursor.execute("UPDATE sessions SET last_active = ? WHERE session_id = ?", (now, session_id))
        cursor.execute("UPDATE users SET last_active = ? WHERE user_id = ?", (now, user_id))

        # Add message
        message_id = _generate_short_id()
        tokens_str = json.dumps(tokens) if tokens else None
        # The Go code adds 7 days to the timestamp, let's replicate that for consistency
        timestamp = now + (7 * 24 * 60 * 60)

        cursor.execute(
            "INSERT INTO messages (message_id, session_id, role, content, tokens, model, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (message_id, session_id, role, content, tokens_str, model_name, timestamp)
        )

        # Increment turn counter for the session
        if role == 'assistant':
            cursor.execute("UPDATE sessions SET turn = turn + 1 WHERE session_id = ?", (session_id,))

        conn.commit()
        logger.info(f"Message added for session ID {session_id}.")

def get_session_context_and_turn(session_id: str, max_messages: int = 100):
    """
    Returns formatted context for LLM inference and the current session turn.
    """
    with sqlite3.connect(config.DB_PATH) as conn:
        cursor = conn.cursor()

        # Get turn
        cursor.execute("SELECT turn FROM sessions WHERE session_id = ?", (session_id,))
        result = cursor.fetchone()
        if not result:
            logger.error(f"Session with id {session_id} not found.")
            return "", 0
        turn = result[0]

        # Get messages
        cursor.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp ASC LIMIT ?",
            (session_id, max_messages)
        )
        messages = cursor.fetchall()

        # Format context
        formatted_context = ""
        for role, content in messages:
            formatted_context += f"<|im_start|>{role}\n{content}<|im_end|>\n"

        return formatted_context, turn
