# backend/main.py

from flask import Flask, jsonify, request
from interact_db import *
import sys

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


@app.route('/craftsmen', methods=['GET'])
def get_craftsmen():
    try:
        postalcode = request.args.get('postalcode')
        if not postalcode:
            raise ValueError("postal code is required")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    con = sqlite3.connect(DB)
    cursor = con.cursor()

    # get long/lat for postcode
    cursor.execute(f"SELECT lat, lon, postcode_extension_distance_group FROM postcode WHERE postcode={postalcode}")
    post_lat, post_lon, postcode_extension_distance_group = cursor.fetchone()
    print(post_lon, ";", post_lat, file=sys.stderr)
    cursor.close()

    # filter by reichweite
    cursor = con.cursor()
    R = 6371  # radius of earth in km
    postcode_extension_distance_bonus = {'a': 0, 'b': 2, 'c': 5}[postcode_extension_distance_group[-1]]
    print("bonus: ", postcode_extension_distance_bonus, file=sys.stderr)
    query = f"""
        WITH MALER_DIST as (
            SELECT *, abs((acos((sin(lat)*sin({post_lat})) + (cos(lat) * cos({post_lat}) * cos(lon - {post_lon})) )*{R})) as dist
            FROM service_provider_profile
        ),
        NEAR_MALER_DIST as (
            SELECT *
            FROM MALER_DIST
            WHERE dist < CAST(((max_driving_distance/1000) + {postcode_extension_distance_bonus}) AS float)
        ),
        NEAR_MALER_WITH_PROFILE_SCORE as(
            SELECT m.*, (0.4 * q.profile_picture_score) + (0.6 * q.profile_description_score) as profile_score
            FROM NEAR_MALER_DIST m JOIN quality_factor_score q ON m.id = q.profile_id
        ),
        NEAR_MALER_WITH_RANK_HELPER as(
            SELECT *, 1-(dist/80) as dist_score, CASE WHEN dist>80 THEN 0.01 ELSE 0.15 END as dist_weight
            FROM NEAR_MALER_WITH_PROFILE_SCORE
        ),
        NEAR_MALER_WITH_RANK as (
            SELECT *, (dist_weight * dist_score + (1 - dist_weight) * profile_score) as rank
            FROM NEAR_MALER_WITH_RANK
        )
        SELECT *
        FROM NEAR_MALER_WITH_RANK
        ORDER BY rank desc
        LIMIT 20
    """
    print("query:", query, file=sys.stderr)
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    leudde_list = [dict(zip(columns, row)) for row in rows]
    print("nr rows:", len(rows), file=sys.stderr)

    cursor.close()
    con.close()

    # todo: translate plz into location NO!

    """craftsman = {
        "id": 123,
        "name": "CraftsMan1",
        "postalCode": 8049,
        "rankingScore": 1
    }"""

    return jsonify({"craftsmen": leudde_list})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, debug=True)
