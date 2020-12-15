#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    engine.py
    snakebin/

    Author: Roberto Polverelli Monti <rpolverelli at gmail>
    Created on: 2020 Dec 14
    Description:
"""

from flask import jsonify, abort, make_response, request
from snakebin import app, db
from snakebin.models import Job
from time import strftime, gmtime, time


def get_human_time(seconds):
    minutes = seconds // 60
    hours = minutes // 60
    time_str = ""
    if hours > 0:
        time_str += "{} hour".format(hours)
        if hours > 1:
            time_str += 's'
        minutes = minutes % 60
    if minutes > 0:
        time_str += " {} minute".format(minutes)
        if minutes > 1:
            time_str += 's'
        seconds = seconds % 60
    if seconds >= 0 and hours < 1:
        time_str += " {} second".format(seconds)
        if seconds != 1:
            time_str += 's'
    return time_str.lstrip()


@app.route('/api/v1.0/jobs/<int:id>', methods=['PUT'])
def post_results(id):
    query = Job.query.get(id)

    if not query:
        abort(404)
    if not request.json:
        abort(400)
    if 'results' in request.json and type(request.json['results']) != str:
        abort(400)
    if query.complete == True:
        abort(400)

    query.complete = True
    query.results = request.json['results']
    query.elapsed = int(time() - query.submitted)
    db.session.commit()

    return get_job(id)


# curl -i -H "Content-Type: application/json" -X POST -d '{"title":"Read a book"}' http://localhost:5000/todo/api/v1.0/tasks
@app.route('/api/v1.0/jobs', methods=['POST'])
def new_job():
    if not request.json or not 'title' in request.json:
        abort(400)

    id = len(Job.query.all()) + 1

    db.session.add(Job(
        id     =  id,
        title      =  request.json['title'],
        complete   =  False,
        elapsed    =  0,
        submitted  =  int(time()),
        results    =  ""
    ))
    db.session.commit()

    return get_job(id), 201


@app.route('/api/v1.0/jobs', methods=['GET'])
def get_jobs():
    jobs_query = Job.query.all()

    jobs = []

    for j in jobs_query:
        if j.complete:
            elapsed = j.elapsed
        else:
            elapsed = int(time()) - j.submitted
        k = {
            'id': j.id,
            'title': j.title,
            'complete': j.complete,
            'results': j.results,
            'elapsed': {
                'seconds': elapsed,
                'human': get_human_time(elapsed),
            },
            'submitted': {
                'seconds': j.submitted,
                'human': strftime('%Y/%m/%d %H:%M', gmtime(j.submitted)),
            }
        }
        jobs.append(k)

    return jsonify({'jobs': jobs})


@app.route('/api/v1.0/jobs/<int:id>', methods=['GET'])
def get_job(id):
    j = Job.query.get(id)
    if not j:
        abort(404)

    if j.complete:
        elapsed = j.elapsed
    else:
        elapsed = int(time()) - j.submitted
    job = {
        'id': j.id,
        'title': j.title,
        'complete': j.complete,
        'results': j.results,
        'elapsed': {
            'seconds': elapsed,
            'human': get_human_time(elapsed),
        },
        'submitted': {
            'seconds': j.submitted,
            'human': strftime('%Y/%m/%d %H:%M', gmtime(j.submitted)),
        }
    }

    return jsonify({'job': job})


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True)
