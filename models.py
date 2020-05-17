
import json
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, create_engine
import os
from dotenv import load_dotenv
load_dotenv()

# TODO: ADD ENV VARIABLES FOR LOCAL AND REMOTE DB

database_name = os.getenv('DEV_DB')
database_url = os.getenv('DATABASE_URL')
database_path = "postgres://{}/{}".format(database_url, database_name)

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


movie_actor_assoc = db.Table(
    'movie_actor_assoc',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey(
        'movies.id', ondelete="cascade")),
    db.Column('actor_id', db.Integer, db.ForeignKey(
        'actors.id', ondelete="cascade"))
)

'''
Movie
TODO: ADD RELEATIONSHIP BETWEEN MOVIE AND ACTOR
'''


class Movie(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    title = db.Column(db.String(120), nullable=False)
    release_date = db.Column(db.Date, nullable=False)

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format_movie_without_actors(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date,
        }

    def format(self):
        actors = list(
            map(lambda x: x.format_actor_without_movies(), self.actors))
        total_actors = len(actors)
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date,
            'actors': {
                'actors': actors,
                'total_actors': total_actors
            }
        }


'''
Actor
'''


class Actor(db.Model):
    __tablename__ = 'actors'

    id = Column(Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(120), nullable=False)
    movies = db.relationship(
        "Movie", secondary=movie_actor_assoc, backref=db.backref('actors'))

    def __init__(self, name, age, gender, movies=[]):
        self.name = name
        self.age = age
        self.gender = gender
        self.movies = movies

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format_actor_without_movies(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
        }

    def format(self):
        movies = list(
            map(lambda x: x.format_movie_without_actors(), self.movies))
        total_movies = len(movies)
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'movies': {
                'movies': movies,
                'total_movies': total_movies
            }
        }
