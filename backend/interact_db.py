import sqlite3
import sys
from sqlite3 import Error


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


def query_postcode_infos(db_file, postalcode):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Get longitude, latitude and group of a postalcode
    cursor.execute(f"SELECT lat, lon, postcode_extension_distance_group FROM postcode WHERE postcode={postalcode}")
    post_lat, post_lon, group = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return {'lon': post_lon, 'lat': post_lat, 'group': group}


def query_ranking(db_file, post_lon, post_lat, group):
    # Connect to database
    con = sqlite3.connect(db_file)
    cursor = con.cursor()

    r = 6371  # radius of earth in km

    postcode_extension_distance_bonus = {'a': 0, 'b': 2, 'c': 5}[group[-1]]

    query = f"""
            WITH MALER_DIST as (
                SELECT *, abs((acos((sin(lat)*sin({post_lat})) + (cos(lat) * cos({post_lat}) * cos(lon - {post_lon})) )*{r})) as dist
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
                FROM NEAR_MALER_WITH_RANK_HELPER
            )
            SELECT *
            FROM NEAR_MALER_WITH_RANK
            ORDER BY rank desc
            LIMIT 20
        """

    cursor.execute(query)
    # Extract column header of the table
    columns = [col[0] for col in cursor.description]
    # Get all entries
    rows = cursor.fetchall()
    # Combine header and entries
    ranking_list = [dict(zip(columns, row)) for row in rows]

    cursor.close()
    con.close()

    return ranking_list


def update_craftman_databases(db_file, craftman_id, max_driving_distance, pic_score, desc_score):
    # Connect to database
    con = sqlite3.connect(db_file)
    cursor = con.cursor()
    updated = {}

    if max_driving_distance:
        query = f"UPDATE service_provider_profile SET max_driving_distance = {max_driving_distance} WHERE id = {craftman_id};"
        cursor.execute(query)
        updated["maxDrivingDistance"] = max_driving_distance

    if pic_score:
        query = f"UPDATE quality_factor_score SET profile_picture_score = {pic_score} WHERE profile_id = {craftman_id};"
        cursor.execute(query)
        updated["profilePictureScore"] = pic_score


    if desc_score:
        query = f"UPDATE quality_factor_score SET profile_description_score = {desc_score} WHERE profile_id = {craftman_id};"
        cursor.execute(query)
        updated["profileDescriptionScore"] = desc_score

    cursor.close()
    con.close()

    return {'id': craftman_id, 'updates': updated}
