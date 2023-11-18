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
        start_index = request.args.get("index", type=int)
    except:
        return jsonify({"error": "index must be numerical"}), 404

    # todo: access db to get 20 craftsmen

    craftsman = get_hardcoded_craftsman()

    return jsonify({"craftsmen": craftsman})


@app.route('/craftman/<id>', methods=['PATCH'])
def user(id):
    """interface PatchRequest {
          // At least one of the attributes should be defined
          maxDrivingDistance?: number;
          profilePictureScore?: number;
          profileDescriptionScore?: number;
    }
    interface PatchResponse {
      id: number;
      updated: {
        maxDrivingDistance: number;
        profilePictureScore: number;
        profileDescriptionScore: number;
      }
    }
    """
    # update MAX_DRIVING_DISTANCE
    # update PROFILE_PICTURE_SCORE
    # update PROFILE_DESCRIPTION_SCORE

    maxDrivingDistance = request.form["maxDrivingDistance"]
    profilePictureScore = request.form["profilePictureScore"]
    profileDescriptionScore = request.form["profileDescriptionScore"]

    # recalculate rankings?

    return jsonify({"patchresponse": {
        "id": id,
        "updated":{
            "maxDrivingDistance": 0,
            "profilePictureScore": 0,
            "profileDescriptionScore": 0,
        },
    }})



if __name__ == "__main__":
    app.run()
    # app.run(host="0.0.0.0", port=4321)