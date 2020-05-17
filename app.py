import os
import sys
from flask import Flask, request, abort, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError, DataError
from flask_cors import CORS
from werkzeug.exceptions import NotFound
from db.models import setup_db, Actor, Movie
from auth.auth import AuthError, requires_auth


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    CORS(app)
    setup_db(app)

    @app.route('/')
    def index():
        return jsonify({'hello': 'world'})

    # MOVIES ROUTES
    '''
      Movies routes helpers
    '''
    def get_movie_by_id(movie_id):
        movie = Movie.query.get(movie_id)
        if movie is None:
            return abort(404, 'Could not find movie with id ' + str(movie_id))
        else:
            return movie
    '''
        GET /movies
        returns status code 200 and json
        {"success": True, "movies": movies, "total_movies": int}
        where movies is the list of movies and total_movies is the count of all movies
    '''
    @app.route('/movies', methods=['GET'])
    @requires_auth('read:movies')
    def get_movies(token):
        try:
            movies = Movie.query.order_by(Movie.id).all()
            formatted_movies = list(map(lambda x: x.format(), movies))
            total_movies = len(formatted_movies)
            response = {
                "success": True,
                "movies": formatted_movies,
                "total_movies": total_movies
            }
            return make_response(jsonify(response), 200)
        except DataError as e:
            print(sys.exc_info())
            error = str(e.__dict__['orig'])
            return abort(422, error)
        except SQLAlchemyError as e:
            print(sys.exc_info())
            error = str(e.__dict__['orig'])
            return abort(500, error)
        except:
            print(sys.exc_info())
            return abort(500)
    '''
        POST /movies
        returns status code 201 and json
        {"success": True, "movie": movie}
        where movies is an object with the new movie
    '''
    @app.route('/movies', methods=['POST'])
    @requires_auth('create:movies')
    def create_movie(token):
        movie_data = request.get_json()
        if movie_data is None:
            abort(400, 'Bad request - movie_data is required')
        else:
            title = movie_data.get('title', None)
            if ((not title) or (title is None)):
                abort(400, 'Bad request - title is required')
            release_date = movie_data.get('release_date', None)
            if ((not release_date) or (release_date is None)):
                abort(400, 'Bad request - release_date is required')
            try:
                movie = Movie(title=title, release_date=release_date)
                actors = movie_data.get('actors', [])
                if(len(actors) > 0):
                    for actor_id in actors:
                        actor = get_actor_by_id(actor_id)
                        movie.actors.append(actor)
                movie.insert()
                formatted_movie = movie.format()
                response = {
                    "success": True,
                    "movie": formatted_movie
                }
                return make_response(jsonify(response), 201)
            except NotFound as e:
                print(sys.exc_info())
                return abort(404, str(e))
            except DataError as e:
                print(sys.exc_info())
                error = str(e.__dict__['orig'])
                return abort(422, error)
            except SQLAlchemyError as e:
                print(sys.exc_info())
                error = str(e.__dict__['orig'])
                return abort(500, error)
            except:
                print(sys.exc_info())
                return abort(500)

    '''
        GET /movies/movie_id
        returns status code 200 and json
        {"success": True, "movie": movie}
    '''
    @app.route('/movies/<int:movie_id>', methods=['GET'])
    @requires_auth('read:movies')
    def get_movie(token, movie_id):
        movie = get_movie_by_id(movie_id)
        try:
            formatted_movie = movie.format()
            response = {
                'success': True,
                'movie': formatted_movie
            }
            return make_response(jsonify(response), 200)
        except DataError as e:
            print(sys.exc_info())
            error = str(e.__dict__['orig'])
            return abort(422, error)
        except SQLAlchemyError as e:
            print(sys.exc_info())
            error = str(e.__dict__['orig'])
            return abort(500, error)
        except:
            print(sys.exc_info())
            return abort(500)

    '''
        PATCH /movies
        returns status code 200 and json
        {"success": True, "movie": movie}
        where movies is an object with the updated movie
    '''
    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('update:movies')
    def update_movie(token, movie_id):
        movie_data = request.get_json()
        if movie_data is None:
            abort(400, 'Bad request - movie_data is required')
        else:
            try:
                movie = get_movie_by_id(movie_id)
                title = movie_data.get('title', None)
                if (title):
                    movie.title = title
                release_date = movie_data.get('release_date', None)
                if (release_date):
                    movie.release_date = release_date
                actors = movie_data.get('actors', [])
                if(len(actors) > 0):
                    for actor_id in actors:
                        actor = get_actor_by_id(actor_id)
                        movie.actors.append(actor)
                movie.update()
                formatted_movie = movie.format()
                response = {
                    "success": True,
                    "movie": formatted_movie
                }
                return make_response(jsonify(response), 200)
            except NotFound as e:
                print(sys.exc_info())
                return abort(404, str(e))
            except DataError as e:
                print(sys.exc_info())
                error = str(e.__dict__['orig'])
                return abort(422, error)
            except SQLAlchemyError as e:
                print(sys.exc_info())
                error = str(e.__dict__['orig'])
                return abort(500, error)
            except:
                print(sys.exc_info())
                return abort(500)

    '''
        DELETE /movies/movie_id
        returns status code 200 and json
        {"success": True, "movie_id": id}
    '''
    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(token, movie_id):
        movie = get_movie_by_id(movie_id)
        try:
            movie.delete()
            response = {
                'success': True,
                'movie_id': movie_id
            }
            return make_response(jsonify(response), 200)
        except DataError as e:
            print(sys.exc_info())
            error = str(e.__dict__['orig'])
            return abort(422, error)
        except SQLAlchemyError as e:
            print(sys.exc_info())
            error = str(e.__dict__['orig'])
            return abort(500, error)
        except:
            print(sys.exc_info())
            return abort(500)

    # Actors ROUTES
    '''
      Actors routes helpers
    '''
    def get_actor_by_id(actor_id):
        actor = Actor.query.get(actor_id)
        if actor is None:
            return abort(404, 'Could not find actor with id ' + str(actor_id))
        else:
            return actor
    '''
        GET /actors
        returns status code 200 and json
        {"success": True, "actors": actors, "total_actors": int}
        where movies is the list of movies and total_movies is the count of all movies
    '''
    @app.route('/actors', methods=['GET'])
    @requires_auth('read:actors')
    def get_actors(token):
        try:
            actors = Actor.query.order_by(Actor.id).all()
            formatted_actors = list(map(lambda x: x.format(), actors))
            total_actors = len(formatted_actors)
            response = {
                "success": True,
                "actors": formatted_actors,
                "total_actors": total_actors
            }
            return make_response(jsonify(response), 200)
        except DataError as e:
            print(sys.exc_info())
            error = str(e.__dict__['orig'])
            return abort(422, error)
        except SQLAlchemyError as e:
            print(sys.exc_info())
            error = str(e.__dict__['orig'])
            return abort(500, error)
        except:
            print(sys.exc_info())
            return abort(500)
    '''
        POST /actors
        returns status code 201 and json
        {"success": True, "actor": actor}
        where actor is an object with the new actor
    '''
    @app.route('/actors', methods=['POST'])
    @requires_auth('create:actors')
    def create_actor(token):
        actor_data = request.get_json()
        if actor_data is None:
            abort(400, 'Bad request - actor_data is required')
        else:
            name = actor_data.get('name', None)
            if ((not name) or (name is None)):
                abort(400, 'Bad request - name is required')

            age = actor_data.get('age', None)
            if ((not age) or (age is None)):
                abort(400, 'Bad request - age is required')

            gender = actor_data.get('gender', None)
            if ((not gender) or (gender is None)):
                abort(400, 'Bad request - gender is required')
            try:
                actor = Actor(name=name, age=age, gender=gender)
                actor.insert()

                movies = actor_data.get('movies', [])
                if(len(movies) > 0):
                    for movie_id in movies:
                        movie = get_movie_by_id(movie_id)
                        actor.movies.append(movie)
                actor.insert()
                formatted_actor = actor.format()
                response = {
                    "success": True,
                    "actor": formatted_actor
                }
                return make_response(jsonify(response), 201)
            except NotFound as e:
                print(sys.exc_info())
                return abort(404, str(e))
            except DataError as e:
                print(sys.exc_info())
                error = str(e.__dict__['orig'])
                return abort(422, error)
            except SQLAlchemyError as e:
                print(sys.exc_info())
                error = str(e.__dict__['orig'])
                return abort(500, error)
            except:
                print(sys.exc_info())
                return abort(500)
    '''
        GET /actors/actor_id
        returns status code 200 and json
        {"success": True, "actor": actor}
    '''
    @app.route('/actors/<int:actor_id>', methods=['GET'])
    @requires_auth('read:actors')
    def get_actor(token, actor_id):
        actor = get_actor_by_id(actor_id)
        try:
            formatted_actor = actor.format()
            response = {
                'success': True,
                'actor': formatted_actor
            }
            return make_response(jsonify(response), 200)
        except DataError as e:
            print(sys.exc_info())
            error = str(e.__dict__['orig'])
            return abort(422, error)
        except SQLAlchemyError as e:
            print(sys.exc_info())
            error = str(e.__dict__['orig'])
            return abort(500, error)
        except:
            print(sys.exc_info())
            return abort(500)

    '''
        PATCH /actors/actor_id
        returns status code 200 and json
        {"success": True, "actor": actor}
    '''

    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('update:actors')
    def update_actor(token, actor_id):
        actor_data = request.get_json()
        if actor_data is None:
            abort(400, 'Bad request - actor_data is required')
        else:
            actor = get_actor_by_id(actor_id)
            name = actor_data.get('name', None)
            if (name):
                actor.name = name
            gender = actor_data.get('gender', None)
            if (gender):
                actor.gender = gender
            age = actor_data.get('age', None)
            if (age):
                actor.age = age
            try:
                movies = actor_data.get('movies', [])
                if(len(movies) > 0):
                    for movie_id in movies:
                        movie = get_movie_by_id(movie_id)
                        actor.movies.append(movie)
                actor.update()
                formatted_actor = actor.format()
                response = {
                    "success": True,
                    "actor": formatted_actor
                }
                return make_response(jsonify(response), 200)
            except NotFound as e:
                print(sys.exc_info())
                return abort(404, str(e))
            except DataError as e:
                print(sys.exc_info())
                error = str(e.__dict__['orig'])
                return abort(422, error)
            except SQLAlchemyError as e:
                print(sys.exc_info())
                error = str(e.__dict__['orig'])
                return abort(500, error)
            except:
                print(sys.exc_info())
                return abort(500)

    '''
        DELETE /actors/actor_id
        returns status code 200 and json
        {"success": True, "actor_id": actor_id}
    '''
    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(token, actor_id):
        actor = get_actor_by_id(actor_id)
        try:
            actor.delete()
            response = {
                'success': True,
                'actor_id': actor_id
            }
            return make_response(jsonify(response), 200)
        except DataError as e:
            print(sys.exc_info())
            error = str(e.__dict__['orig'])
            return abort(422, error)
        except SQLAlchemyError as e:
            print(sys.exc_info())
            error = str(e.__dict__['orig'])
            return abort(500, error)
        except:
            print(sys.exc_info())
            return abort(500)

    # Error Handling
    '''
        Errors for common error types
    '''
    @app.errorhandler(422)
    def unprocessable(error):
        message = error.description if error.description else 'bad request'
        return jsonify({
            "success": False,
            "error": 422,
            "message": message
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        message = error.description if error.description else 'bad request'
        return jsonify({
            "success": False,
            "error": 400,
            "message": message
        }), 400

    @app.errorhandler(500)
    def internal_server(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": 'internal server error'
        }), 500

    @app.errorhandler(404)
    def not_found(error):
        message = error.description if error.description else 'resource not found'
        return jsonify({
            "success": False,
            "error": 404,
            "message": message
        }), 404

    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify(error.error), error.status_code

    return app


APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
