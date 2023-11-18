# backend/main.py

from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

# Initialize SQLite database
conn = sqlite3.connect('/data/test.db')
cursor = conn.cursor()

#########################################################
################# EXAMPLE DATABASE CODE #################
#########################################################

# Create a users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL
    )
''')

# Sample data
sample_data = [
    ('Maler', 'maler@tum.de'),
    ('Handwerker', 'handwerker@tum.de')
]

# Insert sample data
cursor.executemany("INSERT INTO users (username, email) VALUES (?, ?)", sample_data)

# Commit changes and close the connection
conn.commit()
conn.close()


@app.route('/')
def example():
    # Connect to the SQLite database
    conn = sqlite3.connect('/data/test.db')
    cursor = conn.cursor()

    # Query data from the users table
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    # Close the connection
    conn.close()

    # Convert rows to a list of dictionaries
    user_list = [{'id': row[0], 'username': row[1], 'email': row[2]} for row in rows]

    return jsonify(users=user_list)


#########################################################
################# EXAMPLE DATABASE CODE #################
#########################################################

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, debug=True)
