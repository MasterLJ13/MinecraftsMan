# backend/main.py

import os
from flask import Flask, jsonify, request
from interact_db import *
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB = "/data/check24.db"
PC = "/data/postcode.sql"
QF = "/data/quality_factor_score.sql"
SPP = "/data/service_provider_profile.sql"
# Initialize SQLite database
if not os.path.exists(DB):
    create_db(DB, PC, QF, SPP)


@app.route('/craftsmen', methods=['GET'])
def get_craftsmen():
    try:
        postalcode = request.args.get('postalcode')
        if not postalcode:
            raise ValueError("postal code is required")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        index = request.args.get("index", type=int)
        if index is None:
            index = 0
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    result = query_postcode_infos(DB, postalcode)
    if not result:
        return jsonify({"error": "postal code not found"}), 400

    return jsonify({"craftsmen": query_ranking(DB, result[0], result[1], result[2], index)})


@app.route('/craftman/<int:craftman_id>', methods=['PATCH'])
def patch_craftman(craftman_id):
    # Parse the request JSON
    patch_data = request.json
    if not patch_data:
        return jsonify({'error': 'No data provided in the request body'}), 400

    # Assign variables based on the request data
    max_driving_distance = patch_data.get('maxDrivingDistance')
    pic_score = patch_data.get('profilePictureScore')
    desc_score = patch_data.get('profileDescriptionScore')

    response_data = update_craftman_databases(DB, craftman_id, max_driving_distance, pic_score, desc_score)

    return jsonify(response_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, debug=False)
