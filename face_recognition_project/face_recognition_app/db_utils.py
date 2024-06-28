# db_utils.py

import mysql.connector

def get_database_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="attendance"
        )
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None
