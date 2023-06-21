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
    return 'Hello, World'

# Campers is different from model Camper
class Campers(Resource):
    def get(self):
        q = Camper.query.all()
        q_dict = [c.to_dict(only=('id', 'name', 'age')) for c in q]
        return make_response(q_dict, 200)
    def post(self):
        #1. get data
        data = request.get_json()
        try:
            #2. make new camper with data
            new_camper = Camper(name=data.get('name'), age=data.get('age'))
            #3. add to database
            db.session.add(new_camper)
            db.session.commit()
        except: 
            #4. if there was an exception, return an error response
            return make_response({"errors": ["validation errors"]}, 400)
        #5. if everything worked out, return response
        return make_response(new_camper.to_dict(), 201)
    
api.add_resource(Campers, '/campers')

class OneCamper(Resource):
    def get(self, camper_id):
        camper = Camper.query.filter_by(id=camper_id).first()
        if not camper: 
            return make_response({'error': 'Camper not found'}, 404)
        return make_response(camper.to_dict(), 200)
    def patch(self, camper_id):
        camper = Camper.query.filter_by(id=camper_id).first()
        if not camper: 
            return make_response({'error': 'Camper not found'}, 404)
        #1. get the data
        data = request.get_json()
        try:
            #2. update values in camper
            for attr in data:
                setattr(camper, attr, data.get(attr))
            #3. add / commit 
            db.session.add(camper)
            db.session.commit()
        except: 
            #4. catch any exceptions
            return make_response({'errors': ["validation errors"]}, 400)
        #5. return response
        #return make_response(camper.to_dict(), 202)
        return camper.to_dict(), 202
    
api.add_resource(OneCamper, '/campers/<int:camper_id>')


class Activities(Resource):
    def get(self):
        activities = Activity.query.all()
        act_dict = [a.to_dict(only=('id', 'name', 'difficulty')) for a in activities]
        return act_dict, 200
api.add_resource(Activities, '/activities')

class OneActivity(Resource):
    def delete(self, activity_id):
        #1. get the activity
        activity = Activity.query.filter_by(id=activity_id).first()
        if not activity: 
            return make_response({'error': 'Activity not found'}, 404)
        #2. delete the activity
        db.session.delete(activity)
        db.session.commit()
        return {}, 204
        
api.add_resource(OneActivity, '/activities/<int:activity_id>')

class Signups(Resource):
    def post(self):
        #1. data
        data = request.get_json()
        try:
            #2. new signup
            new_signup = Signup(time=data.get('time'), activity_id=data.get('activity_id'), camper_id=data.get('camper_id'))
            #3. add to db
            db.session.add(new_signup)
            db.session.commit()
        except: 
            #4. in case something goes wrong
            return make_response({"errors": ["validation errors"] }, 400)
        #5. return new signup
        return make_response(new_signup.to_dict(), 201)
api.add_resource(Signups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
