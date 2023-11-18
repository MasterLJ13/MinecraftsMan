# backend/main.py

from flask import Flask, jsonify
from interact_db import *

app = Flask(__name__)

DB = "/data/check24.db"
PC = "/data/postcode.sql"
QF = "/data/quality_factor_score.sql"
SPP = "/data/service_provider_profile.sql"
# Initialize SQLite database
if not os.path.exists(DB):
    create_db(DB, PC, QF, SPP)

@app.route('/query_radius')
def example():
    profile_list = query_radius(DB, 15, 50, 1)
    return jsonify(postcodes=profile_list)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, debug=True)
