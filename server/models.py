from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

#Ethan - I had some tests fail initially because some relationship names were different than what the test expected, even though the functionality was the same

class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    # Add relationship
    # cascades - when an activity is deleted all associated signups are deleted
    # cascades go on parent model
    signups = db.relationship('Signup', back_populates='activity', cascade="all, delete-orphan")
    # signups = db.relationship('Signup', back_populates='activity')

    #activity has many campers
    campers = association_proxy('signups', 'camper')
    # Add serialization rules

    
    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)


    # Add relationship
    signups = db.relationship('Signup', back_populates='camper', cascade="all, delete-orphan")
    #camper has many activities
    activities = association_proxy('signups', 'activity')
    # Add serialization rules
    #serialize_rules = ('-signups.camper',)
    
    # Add validation
    @validates('name')
    def validate_name(self, key, input_name):
        #1. check if user passes in a name
        if not input_name:
            #2. if user doesn't pass in name, raise value error
            raise ValueError('must have name')
        #3. if user passes in name, return
        return input_name
    
    @validates('age')
    def validates_age(self, key, input_age):
        if input_age < 8 or input_age > 18:
            raise ValueError('age must be between 8 and 18')
        return input_age

        #inverse of above
        # if input_age >= 8 and input_age <= 18:
        #     return input_age
        # raise ValueError('age must be between 8 and 18')

        # if not isinstance(age, int) or not (8 <= age <= 18):
        # if not 8 <= age <= 18
    
    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)

    # Add relationships
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    
    activity = db.relationship('Activity', back_populates="signups")
    camper = db.relationship('Camper', back_populates='signups')
    # Add serialization rules
    # prevent max recursion
    # foo = db.relationship('Bar', back_populates='bar') -> serialize_rules=('-foo.bar',)
    serialize_rules = ('-activity.signups', '-camper.signups')
    
    # Add validation
    @validates('time')
    def validate_time(self, key, input_time):
        if input_time < 0 or input_time > 23:
            raise ValueError('time must be between 0 and 23')
        return input_time
    
    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need.
