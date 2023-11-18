import sqlite3
import sys
from sqlite3 import Error
import os


def create_db(db_file, f1, f2, f3):
    try:
        print("Connecting to database")
        conn = sqlite3.connect(db_file)

        with open(f1) as f:
            print("Read first file")
            conn.executescript(f.read())
        with open(f2) as f:
            print("Read second file")
            conn.executescript(f.read())
        with open(f3) as f:
            print("Read third file")
            conn.executescript(f.read())
        conn.close()
        print("Importing sql files finished")
        return True
    except Error as e:
        print(e)
        return False


def query_radius(db_file, lon, lat, rad):
    try:
        print("Connecting to database", file=sys.stderr)
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Query data from the users table
        query = (f"SELECT * FROM service_provider_profile WHERE lon >= {lon - 1} AND lon <= {lon + 1} AND lat >= {lat - rad} AND lat <= {lat + rad} LIMIT 20;")

        # Execute the query
        cursor.execute(query)

        # Get the column names
        columns = [col[0] for col in cursor.description]

        # Fetch all rows
        rows = cursor.fetchall()

        # Create a list of dictionaries
        profile_list = [dict(zip(columns, row)) for row in rows]

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return profile_list
    except Error as e:
        print("Error while connecting:", e)
        return []
