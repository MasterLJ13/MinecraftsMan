# backend/main.py

from flask import Flask, jsonify
import sqlite3
import os
from initDb import *

app = Flask(__name__)

DB = "check24.db"
PC = "./data/postcode.sql"
QF = "./data/quality_factor_score.sql"
SPP = "./data/service_provider_profile.sql"

# Initialize SQLite database
if(not os.path.exists(DB)):
    createDB(DB, PC, QF, SPP)

@app.route('/')
def example():
    # Connect to the SQLite database
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # Query data from the users table
    cursor.execute("SELECT * FROM postcode LIMITS 10")
    rows = cursor.fetchall()

    # Close the connection
    conn.close()

    # Convert rows to a list of dictionaries
    postcodeList = [{'postcode': row[0], 'lon': row[1], 'lat': row[2]} for row in rows]

    return jsonify(postcodes=postcodeList)

#########################################################
################# EXAMPLE DATABASE CODE #################
#########################################################

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, debug=True)
