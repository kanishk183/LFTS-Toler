import mysql.connector
from mysql.connector import Error

from config.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


def create_connection():
    

    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        if connection.is_connected():
            print("Successfully connected to LFTS-Toler database.")
            return connection

    except Error as error:
        print(f"Database connection failed: {error}")

    return None