import json

from flask import request, Response, url_for
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

import models
import decorators
from chords import app
from database import session


@app.route("/api/songs", methods=["GET"])
@decorators.accept("application/json")
def songs_get():
    songs = session.query(models.Song).all()

    data = [song.asDictionary() for song in songs]
    return Response(json.dumps(data), 200, mimetype="application/json")

@app.route("/api/songs", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def songs_post():
    print "here"
    data = request.json
    print data
    file = session.query(models.File).get(data["file"]["id"])
    if not file:
        return

    song = models.Song(file=file)
    session.add(song)
    session.commit()

    data = song.asDictionary()
    return Response(json.dumps(data), 201, mimetype="application/json")

@app.route("/api/files", methods=["POST"])
@decorators.require("multipart/form-data")
@decorators.accept("application/json")
def file_post():
    file = request.files.get("file")
    if not file:
        return

    filename = secure_filename(file.filename)
    db_file = models.File(filename=filename)
    session.add(db_file)
    session.commit()
    file.save(db_file.local_path())

    data = db_file.asDictionary()
    return Response(json.dumps(data), 201, mimetype="application/json")

@app.route("/uploads/<filename>", methods=["GET"])
def uploaded_file():
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


