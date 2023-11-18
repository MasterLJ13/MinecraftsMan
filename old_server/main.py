#!/usr/bin/env python3
from Crypto.Cipher import AES
import json
import sqlite3
import math
import threading
import time
from sqlite3 import Error
from flask import Flask, request, jsonify
import requests

DB_PATH = "paint.db"
app = Flask(__name__)

def distance(longA, latA, longB, latB):
    r = 6371  # radius of Earth (KM)
    p = 0.017453292519943295  # Pi/180
    a = 0.5 - math.cos((latB - latA) * p) / 2 + math.cos(latA * p) * math.cos(latB * p) * (1 - math.cos((longB - longA) * p)) / 2
    d = 2 * r * math.asin(math.sqrt(a))  # 2*R*asin
    return d

def get_db():
    return sqlite3.connect(DB_PATH)

def team_to_dict(team):
    return {'id': team[0], 'color': team[1]}

def user_to_dict(user, team=None, db=None):
    if team:
        return {'id': user[0], 'name': user[1], 'team': team_to_dict(team)}
    if not db:
        db = get_db()
    c = db.cursor()
    c = c.execute("SELECT * FROM teams WHERE id=?", (user[2],))
    return {'id': user[0], 'name': user[1], 'team': team_to_dict(c.fetchone())}

def zone_to_dict(zone, db=None):
    user = None if zone[1] is None else user_to_dict(zone[1], db=db)
    return {'id': zone[0], 'owner': user, 'long': zone[2], 'lat': zone[3], 'osmid': zone[4]}

def getuser(db):
    name = request.args.get('user')
    c = db.cursor()
    c = c.execute("SELECT * FROM users where name=?", (name,))
    return c.fetchone()


# ~~~ Routes ~~~

# Example:  {url}/api/teams
# Returns:  {data=[{id=<teamid>, color=<teamcolor>}, ...]}
@app.route('/api/teams', methods=['GET'])
def teams():
    db = get_db()
    c = db.cursor()
    c = c.execute('SELECT * FROM teams')
    teams = []
    for t in c.fetchall():
        teams.append(team_to_dict(t))
    return jsonify({'data': teams})


# Example:  {url}/api/user?name=arthur
# Returns: {data={id=3, name=arthur, team={id=<teamid>, color=<teamcolor>}}}
@app.route('/api/user', methods=['GET'])
def user():
    db = get_db()
    c = db.cursor()
    c = c.execute('SELECT * FROM users WHERE name=?', (request.args.get("name"), ))
    return jsonify({'data': user_to_dict(c.fetchone(), db=db)})


# Example:  {url}/api/users
# Returns: {data=[{id=<userid>, name=<username>, team={id=<teamid>, color=<teamcolor>}}, ...]}
@app.route('/api/users', methods=['GET'])
def users():
    db = get_db()
    c = db.cursor()
    c = c.execute('SELECT * FROM users')
    users = []
    for u in c.fetchall():
        users.append(user_to_dict(u, db=db))
    return jsonify({'data': users})


# Example:  URL/api/splatzones/long=48.1548252&lat=11.4014102&radius=1
# returns:  {'data': [{
#                  'id'=2, 'owner'=<user Wie oben>, 'long'=11.612, 'lat'=48.111, 'osmid'=12345
#              }, ...]   }
@app.route("/api/splatzones", methods=['GET'])
def splatzones():
    db = get_db()

    userlong, userlat, radius = request.args.get('long', type=float), request.args.get('lat', type=float), request.args.get('radius', type=float)

    if not radius:
        radius = 1.0

    c = db.cursor()
    c = c.execute("SELECT * from splatzones")
    zones = c.fetchall()
    close_zones = []
    # get zones close to user
    if zones:
        for z in zones:
            (zId, zTeam, zLong, zLat, zOSMid) = z
            if not userlong or not userlat or distance(userlong, userlat, zLong, zLat) <= radius:
                close_zones.append(zone_to_dict(z))

    return jsonify({'data': close_zones})


@app.route("/api/stats", methods=['GET'])
def stats():
    # Total OSM Issues resolved
    # Team  [#splatzones,  amountInk,  percentage]
    # best players / team + current user
    pass


# Example img := {width=256, height=256, type="JPG", datab64="..."}
# Example post {data=[img1, img2, ...]}
@app.route('/api/upload', methods=['POST'])
def upload():
    db = get_db()
    uID = request.data.find("userID")
    zID = request.data.find("zoneID")
    c = db.cursor()
    c.execute("UPDATE splatzones SET owner_id = ? WHERE id = ?", (uID, zID, ))
    # todo send image to ML model



if __name__ == "__main__":
    # print(distance(48.1548252, 11.4014102, 53.5584898, 9.7873967))
    #t = threading.Thread(target=delayed_req)
    #t.start()
    app.run()
    # app.run(host="0.0.0.0", port=4321)



