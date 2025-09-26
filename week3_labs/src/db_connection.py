# src/db_connection.py
import mysql.connector 

def connect_db():
    # return None ## for testing the database error dialog
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="fletapp"
    )