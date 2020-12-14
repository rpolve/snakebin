#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    app.py
    snakebin/

    Author: Roberto Polverelli Monti <rpolverelli at gmail>
    Created on: 2020 Dec 14
    Description:
"""

from flask import Flask, jsonify, abort, make_response, request
from time import strftime, time

app = Flask(__name__)


jobs = []


@app.route('/api/v1.0/jobs/<int:job_id>', methods=['PUT'])
def post_results(job_id):
    job = [job for job in jobs if job['id'] == job_id]
    if len(job) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'results' in request.json and type(request.json['results']) != str:
        abort(400)
    if job[0]['complete'] == True:
        abort(400)
    job[0]['complete'] = True
    job[0]['results'] = request.json['results']
    seconds = int(time() - job[0]['submitted']['seconds'])
    job[0]['elapsed'] = {
        'seconds': seconds,
        'human': ""
    }
    job[0]['elapsed']['seconds'] = seconds
    minutes = seconds // 60
    hours = minutes // 60
    job[0]['elapsed']['human'] = ""
    if hours > 0:
        job[0]['elapsed']['human'] += "{} hour".format(hours)
        if hours > 1:
            job[0]['elapsed']['human'] += 's'
        minutes = minutes % 60
    if minutes > 0:
        job[0]['elapsed']['human'] += " {} minute".format(minutes)
        if minutes > 1:
            job[0]['elapsed']['human'] += 's'
        seconds = seconds % 60
    if seconds >= 0 and hours < 1:
        job[0]['elapsed']['human'] += " {} second".format(seconds)
        if seconds != 1:
            job[0]['elapsed']['human'] += 's'
    job[0]['elapsed']['human'] = job[0]['elapsed']['human'].lstrip()

    return jsonify({'job': job[0]})


# curl -i -H "Content-Type: application/json" -X POST -d '{"title":"Read a book"}' http://localhost:5000/todo/api/v1.0/tasks
@app.route('/api/v1.0/jobs', methods=['POST'])
def new_job():
    if not request.json or not 'title' in request.json:
        abort(400)

    try:
        job_id = jobs[-1]['id'] + 1
    except IndexError:
        job_id = 1

    job = {
        'id': job_id,
        'results': None,
        'elapsed': None,
        'title': request.json['title'],
        'complete': False,
        'submitted': {
            'human': strftime('%Y/%m/%d %H:%M'),
            'seconds': int(time())
            }
    }

    jobs.append(job)

    return jsonify({'job': job}), 201


@app.route('/api/v1.0/jobs', methods=['GET'])
def get_jobs():
    return jsonify({'jobs': jobs})


@app.route('/api/v1.0/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = [job for job in jobs if job['id'] == job_id]
    if len(job) == 0:
        abort(404)
    return jsonify({'job': job[0]})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True)
