from . import app
import os
import json
import pymongo
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401
from pymongo import MongoClient
from bson import json_util
from pymongo.errors import OperationFailure
from pymongo.results import InsertOneResult
from bson.objectid import ObjectId
import sys

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "songs.json")
songs_list: list = json.load(open(json_url))

# client = MongoClient(
#     f"mongodb://{app.config['MONGO_USERNAME']}:{app.config['MONGO_PASSWORD']}@localhost")
mongodb_service = os.environ.get('MONGODB_SERVICE')
mongodb_username = os.environ.get('MONGODB_USERNAME')
mongodb_password = os.environ.get('MONGODB_PASSWORD')
mongodb_port = os.environ.get('MONGODB_PORT')

print(f'The value of MONGODB_SERVICE is: {mongodb_service}')

if mongodb_service == None:
    app.logger.error('Missing MongoDB server in the MONGODB_SERVICE variable')
    # abort(500, 'Missing MongoDB server in the MONGODB_SERVICE variable')
    sys.exit(1)

if mongodb_username and mongodb_password:
    url = f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_service}"
else:
    url = f"mongodb://{mongodb_service}"


print(f"connecting to url: {url}")

try:
    client = MongoClient(url)
except OperationFailure as e:
    app.logger.error(f"Authentication error: {str(e)}")

db = client.songs
db.songs.drop()
db.songs.insert_many(songs_list)

def parse_json(data):
    return json.loads(json_util.dumps(data))

######################################################################
# INSERT CODE HERE
######################################################################

@app.route('/health')
def health():
    return jsonify({"status": "OK"})

@app.route("/count")
def count():
    """return length of data"""
    if songs_list:
        return jsonify(length=len(songs_list)), 200

    return {"message": "Internal server error"}, 500

@app.route("/song", methods=["GET"])
def songs():
    """return all songs from the database"""
    try:
        # Get all documents from the songs collection
        songs_cursor = db.songs.find({})
        # Convert cursor to list and parse JSON
        songs_list = parse_json(list(songs_cursor))
        # Return in the required format
        return jsonify({"songs": songs_list}), 200
    except Exception as e:
        return {"message": f"Error retrieving songs: {str(e)}"}, 500

@app.route("/song/<int:id>", methods=["GET"])
def get_song_by_id(id):
    """return a song by id"""
    try:
        # Find the song by id in the database
        song = db.songs.find_one({"id": id})
        
        if song:
            # Parse and return the song
            parsed_song = parse_json(song)
            return jsonify(parsed_song), 200
        else:
            # Song not found
            return {"message": "song with id not found"}, 404
    except Exception as e:
        return {"message": f"Error retrieving song: {str(e)}"}, 500

@app.route("/song", methods=["POST"])
def create_song():
    """create a new song"""
    try:
        # Extract song data from request body
        song = request.get_json()
        
        # Check if song with the same id already exists
        existing_song = db.songs.find_one({"id": song["id"]})
        if existing_song:
            return {"Message": f"song with id {song['id']} already present"}, 302
        
        # Insert the new song into the database
        db.songs.insert_one(song)
        
        # Parse and return the created song
        parsed_song = parse_json(song)
        return jsonify(parsed_song), 201
    except Exception as e:
        return {"message": f"Error creating song: {str(e)}"}, 500

@app.route("/song/<int:id>", methods=["PUT"])
def update_song(id):
    """update a song by id"""
    try:
        # Extract song data from request body
        song_data = request.get_json()
        
        # Find the song in the database
        existing_song = db.songs.find_one({"id": id})
        
        if existing_song:
            # Update the song with the incoming request data
            db.songs.update_one({"id": id}, {"$set": song_data})
            
            # Get the updated song and return it
            updated_song = db.songs.find_one({"id": id})
            parsed_song = parse_json(updated_song)
            return jsonify(parsed_song), 200
        else:
            # Song not found
            return {"message": "song not found"}, 404
    except Exception as e:
        return {"message": f"Error updating song: {str(e)}"}, 500

@app.route("/song/<int:id>", methods=["DELETE"])
def delete_song(id):
    """delete a song by id"""
    try:
        # Delete the song from the database
        result = db.songs.delete_one({"id": id})
        
        # Check the deleted_count attribute
        if result.deleted_count == 0:
            # Song not found
            return {"message": "song not found"}, 404
        elif result.deleted_count == 1:
            # Song successfully deleted - return empty body with 204 status
            return "", 204
    except Exception as e:
        return {"message": f"Error deleting song: {str(e)}"}, 500