import sqlite3

DB_NAME = "clashforces.db"

def init_db():
    """Initializes the database and creates the necessary tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Table to link Discord IDs to Codeforces handles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            discord_id INTEGER PRIMARY KEY,
            cf_handle TEXT NOT NULL
        )
    ''')
    
    # Table to track active match teams
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            discord_id INTEGER PRIMARY KEY,
            team_name TEXT NOT NULL,
            FOREIGN KEY (discord_id) REFERENCES users (discord_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def link_user(discord_id, cf_handle):
    """Links or updates a Discord user's Codeforces handle."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (discord_id, cf_handle)
        VALUES (?, ?)
        ON CONFLICT(discord_id) DO UPDATE SET cf_handle = excluded.cf_handle
    ''', (discord_id, cf_handle.lower()))
    conn.commit()
    conn.close()

def get_cf_handle(discord_id):
    """Retrieves the Codeforces handle for a given Discord ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT cf_handle FROM users WHERE discord_id = ?', (discord_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None