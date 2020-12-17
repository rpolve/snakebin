#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
    engine.py
    snakebin/

    Author: Roberto Polverelli Monti <rpolverelli at gmail>
    Created on: 2020 Dec 14
    Description: restful API for keeping track of time consuming jobs.
"""

from flask import redirect, url_for, send_from_directory
from flask import jsonify, abort, make_response, request
from snakebin import app, db
from snakebin.models import Job
from time import strftime, gmtime, time
from werkzeug.utils import secure_filename
from hashlib import sha1
import os


def new_filename(file_ext):
    filename = str(time()).encode("utf-8")
    filename = sha1(filename).hexdigest()[:4]
    filename += "." + file_ext
    if os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], filename)):
        new_filename(file_ext=file_ext)
    return filename


@app.route("/", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        abort(400)
    file = request.files["file"]
    try:
        file_ext = file.filename.rsplit(".", 1)[1].lower()
    except IndexError:
        file_ext = None
    if file_ext not in app.config["ALLOWED_EXTENSIONS"]:
        abort(400)
    else:
        filename = secure_filename(new_filename(file_ext))
        try:
            os.mkdir(app.config["UPLOAD_FOLDER"])
        except FileExistsError:
            pass
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return app.config["GATEWAY"] + url_for("uploaded_file", filename=filename) + "\n"


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


def get_human_time(seconds):
    minutes = seconds // 60
    hours = minutes // 60
    time_str = ""
    if hours > 0:
        time_str += "{} hour".format(hours)
        if hours > 1:
            time_str += "s"
        minutes = minutes % 60
    if minutes > 0:
        time_str += " {} minute".format(minutes)
        if minutes > 1:
            time_str += "s"
        seconds = seconds % 60
    if seconds >= 0 and hours < 1:
        time_str += " {} second".format(seconds)
        if seconds != 1:
            time_str += "s"
    return time_str.lstrip()


@app.route("/jobs/<int:id>", methods=["PUT"])
def post_results(id):
    query = Job.query.get(id)

    if not query:
        abort(404)
    if not request.json:
        abort(400)
    if "results" in request.json and type(request.json["results"]) != str:
        abort(400)
    if query.complete == True:
        abort(400)

    query.complete = True
    query.results = request.json["results"]
    query.elapsed = int(time() - query.submitted)
    db.session.commit()

    return get_job(id)


@app.route("/jobs", methods=["POST"])
def new_job():
    if not request.json or not "title" in request.json:
        abort(400)

    id = len(Job.query.all()) + 1

    db.session.add(
        Job(
            id=id,
            title=request.json["title"],
            complete=False,
            elapsed=0,
            submitted=int(time()),
            results="",
        )
    )
    db.session.commit()

    return get_job(id), 201


@app.route("/jobs", methods=["GET"])
def get_jobs():
    jobs_query = Job.query.all()

    jobs = []

    for j in jobs_query:
        if j.complete:
            elapsed = j.elapsed
        else:
            elapsed = int(time()) - j.submitted
        k = {
            "id": j.id,
            "title": j.title,
            "complete": j.complete,
            "results": j.results,
            "elapsed": {
                "seconds": elapsed,
                "human": get_human_time(elapsed),
            },
            "submitted": {
                "seconds": j.submitted,
                "human": strftime("%Y/%m/%d %H:%M", gmtime(j.submitted)),
            },
        }
        jobs.append(k)

    return jsonify({"jobs": jobs})


@app.route("/jobs/<int:id>", methods=["GET"])
def get_job(id):
    j = Job.query.get(id)
    if not j:
        abort(404)

    if j.complete:
        elapsed = j.elapsed
    else:
        elapsed = int(time()) - j.submitted
    job = {
        "id": j.id,
        "title": j.title,
        "complete": j.complete,
        "results": j.results,
        "elapsed": {
            "seconds": elapsed,
            "human": get_human_time(elapsed),
        },
        "submitted": {
            "seconds": j.submitted,
            "human": strftime("%Y/%m/%d %H:%M", gmtime(j.submitted)),
        },
    }

    return jsonify({"job": job})


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({"error": "Bad request"}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)


@app.errorhandler(405)
def not_found(error):
    return make_response(jsonify({"error": "Method not allowed"}), 404)


if __name__ == "__main__":
    app.run(debug=True)
