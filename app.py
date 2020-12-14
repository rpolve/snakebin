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
    job[0]['complete'] = True
    job[0]['results'] = request.json['results']
    job[0]['elapsed'] = str(int(time() - job[0]['submitted']['seconds']) // 60) + ' minutes'
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
