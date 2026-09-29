import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("MYSQL_PASSWORD"),
            database="fingerprint_exam"
        )

        return connection

    except mysql.connector.Error as error:
        print("Database connection failed:", error)
        return None


connection = create_connection()

if connection:
    print("MySQL connection successful!")

    connection.close()
else:
    print("Could not connect to MySQL.")