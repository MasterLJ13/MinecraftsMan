#!/usr/bin/env python3
import json
import sqlite3
from sqlite3 import Error
from flask import Flask, request, jsonify
import re

DB_PATH = "worker.db"
app = Flask(__name__)

def get_db():
    return sqlite3.connect(DB_PATH)

def get_hardcoded_craftsman():
    craftsman = {
        "id": 123,
        "name": "CraftsMan1",
        "postalCode": 8049,
        "rankingScore": 1
    }
    return craftsman

# ~~~ Routes ~~~

 # todo: pagination (i.e. support "load another 20" )
@app.route('/craftsmen', methods=['GET'])
def get_craftsmen():
    try:
        postalcode = request.args.get('postalcode', type=int)
    except ValueError:
        return jsonify({"error": "Postal code must be numerical"}), 400

    if not postalcode:
        return jsonify({"error": "Postal code is required"}), 400

    # optional pagination arg

    try:
        start_index = request.args.get("index", default=0, type=int)
    except ValueError:
        return jsonify({"error": "index must be numerical"}), 400

    # todo: translate plz into location

    #in case plz not found in database -> thow error about invalid plz

    # todo: access db to get 20 craftsmen
    # use index to get first 20, or second 20... use start_index
    craftsman = get_hardcoded_craftsman()

    return jsonify({"craftsmen": craftsman})


@app.route('/craftman/<craftsman_id>', methods=['PATCH'])
def user(craftsman_id):
    maxDrivingDistance = request.form.get("maxDrivingDistance")
    profilePictureScore = request.form.get("profilePictureScore")
    profileDescriptionScore = request.form.get("profileDescriptionScore")

    if maxDrivingDistance is None and profilePictureScore is None and profileDescriptionScore is None:
        return jsonify({"error": "maxDrivingDistance or profilePictureScore or profileDescriptionScore needs to be specified"}), 400

    # todo recalculate rankings based on the new values

    return jsonify({"patchresponse": {
        "id": id,
        "updated": {
            "maxDrivingDistance": maxDrivingDistance,
            "profilePictureScore": profilePictureScore,
            "profileDescriptionScore": profileDescriptionScore,
        },
    }})



if __name__ == "__main__":
    app.run()
    # app.run(host="0.0.0.0", port=4321)