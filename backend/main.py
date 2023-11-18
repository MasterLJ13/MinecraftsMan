# backend/main.py

import os
from flask import Flask, jsonify, request
from interact_db import *

app = Flask(__name__)

DB = "/data/check24.db"
PC = "/data/postcode.sql"
QF = "/data/quality_factor_score.sql"
SPP = "/data/service_provider_profile.sql"
# Initialize SQLite database
if not os.path.exists(DB):
    create_db(DB, PC, QF, SPP)

# make new table with profile scores already calculated
add_new_service_provider_table(DB)
add_profile_score_to_providers(DB)


@app.route('/postcode_infos', methods=['GET'])
def get_postcode_infos():
    try:
        postalcode = request.args.get('postalcode')
        if not postalcode:
            raise ValueError("postal code is required")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    postcode_infos = query_postcode_infos(DB, postalcode)
    return jsonify(postcodes=postcode_infos)


@app.route('/craftsmen', methods=['GET'])
def get_craftsmen():
    try:
        postalcode = request.args.get('postalcode')
        if not postalcode:
            raise ValueError("postal code is required")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    post_lon, post_lat, group = query_postcode_infos(DB, postalcode).values()

    return jsonify({"craftsmen": query_ranking(DB, post_lon, post_lat, group)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, debug=True)
