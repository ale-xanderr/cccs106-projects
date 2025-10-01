import sqlite3

def init_db():
    """Initializes the database and creates the contacts table if it doesn't exist."""
    conn = sqlite3.connect('contacts.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT
        )
    ''')
    conn.commit()
    return conn


def add_contact_db(conn, name, phone, email):
    """Adds a new contact to the database."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)",
        (name, phone, email)
    )
    conn.commit()


def get_all_contacts_db(conn, search=""):
    """Retrieves all contacts from the database."""
    cursor = conn.cursor()
    if search:
        query = "SELECT id, name, phone, email FROM contacts WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?"
        wildcard = f"%{search}%"
        cursor.execute(query,(wildcard, wildcard, wildcard))
    else:
        cursor.execute("SELECT id, name, phone, email FROM contacts")

    rows = cursor.fetchall()
    conn.close()
    return rows

def update_contact_db(conn, contact_id, name, phone, email):
    """Updates an existing contact in the database."""
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE contacts SET name = ?, phone = ?, email = ? WHERE id = ?",
        (name, phone, email, contact_id)
    )
    conn.commit()


def delete_contact_db(conn, contact_id):
    """Deletes a contact from the database."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    conn.commit()