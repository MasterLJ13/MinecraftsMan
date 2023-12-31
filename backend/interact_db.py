import sqlite3
import time

DB = "/data/check24.db"


def create_db(db_file, f1, f2, f3):
    # Connect to database
    conn = sqlite3.connect(db_file)
    # Read and import all three sql files
    with open(f1) as f:
        conn.executescript(f.read())
    with open(f2) as f:
        conn.executescript(f.read())
    with open(f3) as f:
        conn.executescript(f.read())
    conn.close()


# Add new service provider table to the database
def add_new_service_provider_table(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""DROP TABLE service_provider_profile_with_pscore""")
    cursor.execute("""
    CREATE TABLE service_provider_profile_with_pscore AS 
       SELECT *, 0 as profile_score FROM service_provider_profile""")
    conn.commit()
    cursor.close()
    conn.close()


# Precalculate the profile_score of every craftsman
def add_profile_score_to_providers(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    query = f"""
    UPDATE service_provider_profile_with_pscore
    SET profile_score = (
        SELECT 0.4 * q.profile_picture_score + 0.6 * q.profile_description_score
        FROM quality_factor_score q
        WHERE service_provider_profile_with_pscore.id = q.profile_id
        )
    WHERE service_provider_profile_with_pscore.id IN (
    SELECT q.profile_id
    FROM quality_factor_score q
    );
    """
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()


# Query postal codes information about longitude, latitude and group
def query_postcode_infos(db_file, postalcode):
    # Connect to database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Get longitude, latitude and group of a postalcode
    cursor.execute(f"""
                   SELECT lon, lat, postcode_extension_distance_group
                   FROM postcode 
                   WHERE postcode LIKE '{postalcode}'
                   """)
    res = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return res


# Query craftsman from the database and assign a ranking
def query_ranking(db_file, post_lon, post_lat, group, index):
    # Connect to database
    con = sqlite3.connect(db_file)
    cursor = con.cursor()

    r = 6371  # Radius of earth in km
    postcode_extension_distance_bonus = {'a': 0, 'b': 2, 'c': 5}[group[-1]]

    # Query structure:
    # 1. Calculate the distance between the customer and the craftsman
    # 2. Filter every craftsman which max driving range is greater than the distance
    # 3. & 4. & 5.  Calculate profile score & distance weight & final score
    # 6. Select all relevant columns
    query = f"""
            WITH CRAFTSMEN_DIST as (
                SELECT *, abs((acos((sin(lat)*sin({post_lat})) + (cos(lat) * cos({post_lat}) * cos(lon - {post_lon})) ) * {r})) as dist
                FROM service_provider_profile
            ),
            NEAR_CRAFTSMEN_DIST as (
                SELECT *
                FROM CRAFTSMEN_DIST
                WHERE dist < CAST(((max_driving_distance / 1000) + {postcode_extension_distance_bonus}) AS float)
            ),
            NEAR_CRAFTSMEN_WITH_PROFILE_SCORE as(
                SELECT m.*, (0.4 * q.profile_picture_score) + (0.6 * q.profile_description_score) as profile_score
                FROM NEAR_CRAFTSMEN_DIST m JOIN quality_factor_score q ON m.id = q.profile_id
            ),
            NEAR_CRAFTSMEN_WITH_RANK_HELPER as(
                SELECT *, 1 - (dist / 80) as dist_score, CASE WHEN dist > 80 THEN 0.01 ELSE 0.15 END as dist_weight
                FROM NEAR_CRAFTSMEN_WITH_PROFILE_SCORE
            ),
            NEAR_CRAFTSMEN_WITH_RANK as (
                SELECT *, (dist_weight * dist_score + (1 - dist_weight) * profile_score) as rankingScore
                FROM NEAR_CRAFTSMEN_WITH_RANK_HELPER
            )
            SELECT id, first_name || ' ' || last_name as name, rankingScore, city, street, house_number, dist
            FROM NEAR_CRAFTSMEN_WITH_RANK
            ORDER BY rankingScore desc
            LIMIT {index}, 20
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


# Another, potentially faster, version of querying the sorted craftsman by using precalculated profile_scores
def query_ranking_opt1(db_file, post_lon, post_lat, group, index):
    # Connect to database
    con = sqlite3.connect(db_file)
    cursor = con.cursor()

    r = 6371  # Radius of earth in km
    postcode_extension_distance_bonus = {'a': 0, 'b': 2, 'c': 5}[group[-1]]

    # Query structure:
    # 1. Calculate the distance between the customer and the craftsman
    # 2. Filter every craftsman which max driving range is greater than the distance
    # 3. & 4. Calculate distance weight & final score with **precalculated profile_score** for potential speedup
    # 6. Select all relevant columns
    query = f"""
            WITH CRAFTSMEN_DIST as (
                SELECT *, abs((acos((sin(lat)*sin({post_lat})) + (cos(lat) * cos({post_lat}) * cos(lon - {post_lon})) )*{r})) as dist
                FROM service_provider_profile_with_pscore
            ),
            NEAR_CRAFTSMEN_DIST as (
                SELECT *
                FROM CRAFTSMEN_DIST
                WHERE dist < CAST(((max_driving_distance/1000) + {postcode_extension_distance_bonus}) AS float)
            ),
            NEAR_CRAFTSMEN_WITH_RANK_HELPER as(
                SELECT *, 1-(dist/80) as dist_score, CASE WHEN dist>80 THEN 0.01 ELSE 0.15 END as dist_weight
                FROM NEAR_CRAFTSMEN_DIST
            ),
            NEAR_CRAFTSMEN_WITH_RANK as (
                SELECT *, (dist_weight * dist_score + (1 - dist_weight) * profile_score) as rankingScore
                FROM NEAR_CRAFTSMEN_WITH_RANK_HELPER
            )
            SELECT id, first_name || ' ' || last_name as name, rankingScore
            FROM NEAR_CRAFTSMEN_WITH_RANK
            ORDER BY rankingScore desc
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


# Performance test comparing two implementations
def performance_comparison():
    # get the start time
    st = time.time()
    query_ranking(DB, 13.719, 51.06, 'group_a', 0)
    # get the end time
    et = time.time()

    st1 = time.time()
    query_ranking_opt1(DB, 13.719, 51.06, 'group_a', 0)
    et1 = time.time()

    # get the execution time
    elapsed_time = et - st
    elapsed_time1 = et1 - st1
    print('Execution time for query_ranking:', elapsed_time, 'seconds')
    print('Execution time for query_ranking_opt1:', elapsed_time1, 'seconds')


# Update the databases with the given parameters
def update_craftman_databases(db_file, craftman_id, max_driving_distance, pic_score, desc_score):
    # Connect to database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    updated = {}

    # Each of the values gets checked whether it is set. If so the database entries get updated.
    if max_driving_distance is not None:
        query = f"UPDATE service_provider_profile SET max_driving_distance = {max_driving_distance} WHERE id = {craftman_id};"
        cursor.execute(query)
        updated["maxDrivingDistance"] = max_driving_distance

    if pic_score is not None:
        query = f"UPDATE quality_factor_score SET profile_picture_score = {pic_score} WHERE profile_id = {craftman_id};"
        cursor.execute(query)
        updated["profilePictureScore"] = pic_score

    if desc_score is not None:
        query = f"UPDATE quality_factor_score SET profile_description_score = {desc_score} WHERE profile_id = {craftman_id};"
        cursor.execute(query)
        updated["profileDescriptionScore"] = desc_score

    conn.commit()
    cursor.close()
    conn.close()

    return {'id': craftman_id, 'updates': updated}
