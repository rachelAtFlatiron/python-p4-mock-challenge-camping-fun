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
api = Api(app)

db.init_app(app)


@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        q = Camper.query.all()
        if q:
            return make_response([c.to_dict(only=('id', 'name', 'age')) for c in q], 200)
        return make_response({"error": "not found"}, 404)
    
    def post(self):
        data = request.get_json()
        try: 
            c = Camper(age=data.get('age'), name=data.get('name'))
            db.session.add(c)
            db.session.commit()
        except:
            return make_response({"errors": ["validation errors"]}, 400)
        return make_response(c.to_dict(), 201)
api.add_resource(Campers, '/campers')

class OneCamper(Resource):
    def get(self, id):
        q = Camper.query.filter_by(id=id).first()
        if not q:
            return make_response({"error": "Camper not found"}, 404)
        return make_response(q.to_dict(), 200)
    def patch(self, id):
        q = Camper.query.filter_by(id=id).first()
        if not q:
            return make_response({"error": "Camper not found"}, 404)
        try:
            data = request.get_json()
            for attr in data:
                setattr(q, attr, data.get(attr))
            db.session.add(q)
            db.session.commit()
        except:
            return make_response({"errors": ["validation errors"]}, 400)
        return make_response(q.to_dict(), 202)
api.add_resource(OneCamper, '/campers/<int:id>')

class Activities(Resource):
    def get(self):
        q = Activity.query.all()
        if not q:
            return make_response("not found", 404)
        return make_response([a.to_dict(only=('id', 'name', 'difficulty')) for a in q], 200)
api.add_resource(Activities, '/activities')
class OneActivity(Resource):
    def delete(self, id):
        q = Activity.query.filter_by(id=id).first()
        if not q:
            return make_response({"error": "Activity not found"}, 404)
        db.session.delete(q)
        db.session.commit()
        return make_response({}, 204)
api.add_resource(OneActivity, '/activities/<int:id>')

class Signups(Resource):
    def post(self):
        data = request.get_json()
        try:
            s = Signup(activity_id=data.get('activity_id'), camper_id=data.get('camper_id'), time=data.get('time'))
            db.session.add(s)
            db.session.commit()
        except: 
            return make_response({"errors": ["validation errors"]}, 400)
        return make_response(s.to_dict(), 201)
api.add_resource(Signups, '/signups')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
