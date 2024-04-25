#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

'''
{
    id,
    name,
    age,
    signups: {
        id,
        time,
        camper: {
            id,
            name,
            age,
            signups: {
                id, 
                time, 
                camper: {
                    id, 
                    name, 
                    age,
                    signups
                }
            }
        },
        activity: {
            id,
            name,
            difficulty,
            signups: {
                id,
                time,
                camper,
                activity: {
                    id,
                    name,
                    difficulty,
                    signups: {
                        id,
                        time,
                        camper,
                        activity
                    }
                }
            }
        }
    }
}

'''
@app.route('/campers')
def all_campers():
    q = Camper.query.all()
    q_json = [camper.to_dict(rules=('-signups',)) for camper in q]
    return make_response(q_json)

@app.route('/campers/<int:camper_id>')
def get_camper_by_id(camper_id):
    q = Camper.query.filter_by(id=camper_id).first()
    if not q:
        return make_response({'message': 'not found'}, 404)
    q_json = q.to_dict()
    return make_response(q_json)

@app.route('/activities')
def all_activities():
    q = Activity.query.all()
    q_json = [activity.to_dict(rules=('-signups',)) for activity in q]
    return make_response(q_json)

@app.route('/signups')
def all_signups():
    q = Signup.query.all()
    q_json = [signup.to_dict() for signup in q]
    return make_response(q_json)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
