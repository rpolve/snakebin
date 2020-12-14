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
from time import strftime, gmtime, time
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Job(db.Model):
    job_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True, unique=False)
    complete = db.Column(db.Boolean)
    elapsed = db.Column(db.Integer)
    results = db.Column(db.Text)
    submitted = db.Column(db.Integer)

    def __repr__(self):
        return '<Job_id {}>'.format(self.job_id)


jobs = []


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
    job[0]['elapsed']['human'] = get_human_time(seconds)

    return jsonify({'job': job[0]})


# curl -i -H "Content-Type: application/json" -X POST -d '{"title":"Read a book"}' http://localhost:5000/todo/api/v1.0/tasks
@app.route('/api/v1.0/jobs', methods=['POST'])
def new_job():
    if not request.json or not 'title' in request.json:
        abort(400)

    job_id = max([len(Job.query.all()), 1])

    job = {
        'id': job_id,
        'results': None,
        'elapsed': {
            'human': None,
            'seconds': 0
        },
        'title': request.json['title'][:64],
        'complete': False,
        'submitted': {
            'human': strftime('%Y/%m/%d %H:%M'),
            'seconds': int(time())
        }
    }

    # job_id = db.Column(db.Integer, primary_key=True)
    # title = db.Column(db.String(64), index=True, unique=False)
    # complete = db.Column(db.Boolean)
    # elapsed = db.Column(db.Integer)
    # results = db.Column(db.Text)
    # submitted = db.Column(db.Integer)
    db.session.add(Job(
        job_id     =  job['id'],
        title      =  job['title'],
        complete   =  job['complete'],
        elapsed    =  job['elapsed']['seconds'],
        submitted  =  job['submitted']['seconds'],
        results    =  job['results']
    ))
    db.session.commit()

    return jsonify({'job': job}), 201


@app.route('/api/v1.0/jobs', methods=['GET'])
def get_jobs():
    jobs_query = Job.query.all()

    jobs = []

    for j in jobs_query:
        k = {
            'id': j.job_id,
            'title': j.title,
            'complete': False,
            'results': j.results,
            'elapsed': {
                'seconds': j.elapsed,
                'human': get_human_time(j.elapsed),
            },
            'submitted': {
                'seconds': j.submitted,
                'human': strftime('%Y/%m/%d %H:%M', gmtime(j.submitted)),
            }
        }

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
