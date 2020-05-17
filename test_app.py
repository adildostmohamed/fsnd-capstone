from db.models import setup_db, Movie, Actor
from app import create_app
from flask_sqlalchemy import SQLAlchemy
import json
import unittest
import os
from dotenv import load_dotenv
load_dotenv()


class CastingTestCase(unittest.TestCase):
    """This class represents the casting app test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = os.getenv('TEST_DB')
        self.database_path = "postgresql://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        self.token_assistant = os.getenv('ASSISTANT_TOKEN')
        self.token_director = os.getenv('DIRECTOR_TOKEN')
        self.token_producer = os.getenv('PRODUCER_TOKEN')

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after each test"""
        pass

    def test_get_movies(self):
        res = self.client().get('/movies', headers={
            "Authorization": 'bearer '+self.token_assistant})
        movies = Movie.query.all()
        total_movies = len(movies)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['movies'])
        self.assertEqual(data['total_movies'], total_movies)

    def test_error_get_movies_not_authenticated(self):
        res = self.client().get('/movies')

        self.assertEqual(res.status_code, 401)

    def test_create_movie_with_actors(self):
        new_movie = {
            'title': 'This is a new movie which should be created',
            'release_date': '2021-01-12',
            'actors': [158, 159, 160]
        }
        res = self.client().post('/movies', json=new_movie, headers={
            "Authorization": 'bearer '+self.token_producer})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['movie'])
        self.assertEqual(data['movie']['title'], new_movie['title'])
        self.assertTrue(data['movie']['release_date'])
        self.assertEqual(data['movie']['actors']['total_actors'], 3)
        new_movie = Movie.query.get(data['movie']['id'])
        new_movie.delete()

    def test_error_create_movie_no_permissions(self):
        new_movie = {
            'title': 'This is a new movie which should be created',
            'release_date': '2021-01-12',
            'actors': [158, 159, 160]
        }
        res = self.client().post('/movies', json=new_movie, headers={
            "Authorization": 'bearer '+self.token_assistant})

        self.assertEqual(res.status_code, 403)

    def test_create_movie_without_actors(self):
        new_movie = {
            'title': 'This is a new movie which should be created',
            'release_date': '2021-01-12',
        }
        res = self.client().post('/movies', json=new_movie, headers={
            "Authorization": 'bearer '+self.token_producer})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['movie'])
        self.assertEqual(data['movie']['title'], new_movie['title'])
        self.assertTrue(data['movie']['release_date'])
        self.assertEqual(data['movie']['actors']['total_actors'], 0)
        new_movie = Movie.query.get(data['movie']['id'])
        new_movie.delete()

    def test_error_create_movie_missing_data(self):
        res = self.client().post('/movies', headers={
            "Authorization": 'bearer '+self.token_producer})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            data['message'], 'Bad request - movie_data is required')

    def test_error_create_movie_missing_title(self):
        new_movie = {
            'release_date': '2020-01-12',
        }
        res = self.client().post('/movies', json=new_movie, headers={
            "Authorization": 'bearer '+self.token_producer})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            data['message'], 'Bad request - title is required')

    def test_error_create_movie_missing_release_date(self):
        new_movie = {
            'title': 'New movie',
        }
        res = self.client().post('/movies', json=new_movie, headers={
            "Authorization": 'bearer '+self.token_producer})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            data['message'], 'Bad request - release_date is required')

    def test_error_create_movie_unprocessable_release_date(self):
        new_movie = {
            'title': 'New movie',
            'release_date': '20da20-01-12',
        }
        res = self.client().post('/movies', json=new_movie, headers={
            "Authorization": 'bearer '+self.token_producer})

        self.assertEqual(res.status_code, 422)

    def test_get_movie(self):
        new_movie = {
            'title': 'This is a new movie',
            'release_date': '2020-01-12',
        }
        new_movie = Movie(title=new_movie['title'],
                          release_date=new_movie['release_date'])
        new_movie.insert()
        new_movie_formatted = new_movie.format()
        new_movie_id = new_movie_formatted['id']
        res = self.client().get('/movies/'+str(new_movie_id), headers={
            "Authorization": 'bearer '+self.token_assistant})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['movie']['id'], new_movie_id)
        self.assertEqual(data['movie']['title'], new_movie_formatted['title'])
        self.assertEqual(data['movie']['actors']['total_actors'], 0)
        new_movie.delete()

    def test_error_get_movie_not_authenticated(self):
        new_movie = {
            'title': 'This is a new movie',
            'release_date': '2020-01-12',
        }
        new_movie = Movie(title=new_movie['title'],
                          release_date=new_movie['release_date'])
        new_movie.insert()
        new_movie_formatted = new_movie.format()
        new_movie_id = new_movie_formatted['id']
        res = self.client().get('/movies/'+str(new_movie_id))
        self.assertEqual(res.status_code, 401)
        new_movie.delete()

    def test_error_get_movie_not_found(self):
        movie_id = 1111111
        res = self.client().get('/movies/'+str(movie_id), headers={
            "Authorization": 'bearer '+self.token_assistant})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(
            data['message'], 'Could not find movie with id ' + str(movie_id))

    def test_update_movie(self):
        new_movie = {
            'title': 'This is a new movie',
            'release_date': '2020-01-12',
        }
        new_movie = Movie(title=new_movie['title'],
                          release_date=new_movie['release_date'])
        new_movie.insert()
        new_movie_formatted = new_movie.format()
        new_movie_id = new_movie_formatted['id']
        updated_movie = {
            'title': 'updated movie title',
            'actors': [158, 159]
        }
        res = self.client().patch('/movies/'+str(new_movie_id), json=updated_movie, headers={
            "Authorization": 'bearer '+self.token_director})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['movie']['title'], updated_movie['title'])
        self.assertEqual(data['movie']['actors']['total_actors'], 2)
        new_movie.delete()

    def test_error_update_movie_not_authenticated(self):
        new_movie = {
            'title': 'This is a new movie',
            'release_date': '2020-01-12',
        }
        new_movie = Movie(title=new_movie['title'],
                          release_date=new_movie['release_date'])
        new_movie.insert()
        new_movie_formatted = new_movie.format()
        new_movie_id = new_movie_formatted['id']
        updated_movie = {
            'title': 'updated movie title',
            'actors': [158, 159]
        }
        res = self.client().patch('/movies/'+str(new_movie_id), json=updated_movie)

        self.assertEqual(res.status_code, 401)
        new_movie.delete()

    def test_error_update_movie_no_permissions(self):
        new_movie = {
            'title': 'This is a new movie',
            'release_date': '2020-01-12',
        }
        new_movie = Movie(title=new_movie['title'],
                          release_date=new_movie['release_date'])
        new_movie.insert()
        new_movie_formatted = new_movie.format()
        new_movie_id = new_movie_formatted['id']
        updated_movie = {
            'title': 'updated movie title',
            'actors': [158, 159]
        }
        res = self.client().patch('/movies/'+str(new_movie_id), json=updated_movie, headers={
            "Authorization": 'bearer '+self.token_assistant})

        self.assertEqual(res.status_code, 403)
        new_movie.delete()

    def test_error_update_movie_no_data(self):
        new_movie = {
            'title': 'This is a new movie',
            'release_date': '2020-01-12',
        }
        new_movie = Movie(title=new_movie['title'],
                          release_date=new_movie['release_date'])
        new_movie.insert()
        new_movie_formatted = new_movie.format()
        new_movie_id = new_movie_formatted['id']
        res = self.client().patch('/movies/'+str(new_movie_id), headers={
            "Authorization": 'bearer '+self.token_director})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            data['message'], 'Bad request - movie_data is required')
        new_movie.delete()

    def test_error_update_movie_unprocessable_release_date(self):
        new_movie = {
            'title': 'This is a new movie',
            'release_date': '2020-01-12',
        }
        new_movie = Movie(title=new_movie['title'],
                          release_date=new_movie['release_date'])
        new_movie.insert()
        new_movie_formatted = new_movie.format()
        new_movie_id = new_movie_formatted['id']
        updated_movie = {
            'release_date': 'sdsada'
        }
        res = self.client().patch('/movies/'+str(new_movie_id), json=updated_movie, headers={
            "Authorization": 'bearer '+self.token_director})

        self.assertEqual(res.status_code, 422)
        new_movie.delete()

    def test_error_update_movie_not_found(self):
        movie_id = 1111111
        updated_movie = {
            'release_date': 'sdsada'
        }
        res = self.client().patch('/movies/'+str(movie_id), json=updated_movie, headers={
            "Authorization": 'bearer '+self.token_director})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(
            data['message'], '404 Not Found: Could not find movie with id ' + str(movie_id))

    def test_delete_movie(self):
        new_movie = {
            'title': 'This is a new movie',
            'release_date': '2020-01-12',
        }
        new_movie = Movie(title=new_movie['title'],
                          release_date=new_movie['release_date'])
        new_movie.insert()
        new_movie_formatted = new_movie.format()
        new_movie_id = new_movie_formatted['id']
        res = self.client().delete('/movies/'+str(new_movie_id), headers={
            "Authorization": 'bearer '+self.token_producer})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['movie_id'], new_movie_id)

    def test_error_delete_movie_not_authenticated(self):
        new_movie = {
            'title': 'This is a new movie',
            'release_date': '2020-01-12',
        }
        new_movie = Movie(title=new_movie['title'],
                          release_date=new_movie['release_date'])
        new_movie.insert()
        new_movie_formatted = new_movie.format()
        new_movie_id = new_movie_formatted['id']
        res = self.client().delete('/movies/'+str(new_movie_id))

        self.assertEqual(res.status_code, 401)
        new_movie.delete()

    def test_error_delete_movie_no_permissions(self):
        new_movie = {
            'title': 'This is a new movie',
            'release_date': '2020-01-12',
        }
        new_movie = Movie(title=new_movie['title'],
                          release_date=new_movie['release_date'])
        new_movie.insert()
        new_movie_formatted = new_movie.format()
        new_movie_id = new_movie_formatted['id']
        res = self.client().delete('/movies/'+str(new_movie_id), headers={
            "Authorization": 'bearer '+self.token_assistant})

        self.assertEqual(res.status_code, 403)
        new_movie.delete()

    def test_error_delete_movie_not_found(self):
        movie_id = 1111111
        res = self.client().delete('/movies/'+str(movie_id), headers={
            "Authorization": 'bearer '+self.token_producer})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(
            data['message'], 'Could not find movie with id ' + str(movie_id))

    def test_get_actors(self):
        res = self.client().get('/actors', headers={
            "Authorization": 'bearer '+self.token_assistant})
        actors = Actor.query.all()
        total_actors = len(actors)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['actors'])
        self.assertEqual(data['total_actors'], total_actors)

    def test_error_get_actors_not_authenticated(self):
        res = self.client().get('/actors')

        self.assertEqual(res.status_code, 401)

    def test_create_actor_with_movies(self):
        new_actor = {
            'name': 'Jon Actor',
            'age': 45,
            'gender': 'male',
            'movies': [400, 401, 402]
        }
        res = self.client().post('/actors', json=new_actor, headers={
            "Authorization": 'bearer '+self.token_producer})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['actor'])
        self.assertEqual(data['actor']['name'], new_actor['name'])
        self.assertEqual(data['actor']['age'], new_actor['age'])
        self.assertEqual(data['actor']['gender'], new_actor['gender'])
        self.assertEqual(data['actor']['movies']['total_movies'], 3)
        new_actor = Actor.query.get(data['actor']['id'])
        new_actor.delete()

    def test_error_create_actor_with_movies_not_authenticated(self):
        new_actor = {
            'name': 'Jon Actor',
            'age': 45,
            'gender': 'male',
            'movies': [400, 401, 402]
        }
        res = self.client().post('/actors', json=new_actor)

        self.assertEqual(res.status_code, 401)

    def test_error_create_actor_with_movies_no_permissions(self):
        new_actor = {
            'name': 'Jon Actor',
            'age': 45,
            'gender': 'male',
            'movies': [400, 401, 402]
        }
        res = self.client().post('/actors', json=new_actor, headers={
            "Authorization": 'bearer '+self.token_assistant})

        self.assertEqual(res.status_code, 403)

    def test_create_actor_without_movies(self):
        new_actor = {
            'name': 'Jon Actor',
            'age': 45,
            'gender': 'male'
        }
        res = self.client().post('/actors', json=new_actor, headers={
            "Authorization": 'bearer '+self.token_producer})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['actor'])
        self.assertEqual(data['actor']['name'], new_actor['name'])
        self.assertEqual(data['actor']['age'], new_actor['age'])
        self.assertEqual(data['actor']['gender'], new_actor['gender'])
        self.assertEqual(data['actor']['movies']['total_movies'], 0)
        new_actor = Actor.query.get(data['actor']['id'])
        new_actor.delete()

    def test_error_create_actor_unproccessable_age(self):
        new_actor = {
            'name': 'Jon Actor',
            'age': 'dafasd',
            'gender': 'male'
        }
        res = self.client().post('/actors', json=new_actor, headers={
            "Authorization": 'bearer '+self.token_producer})

        self.assertEqual(res.status_code, 422)

    def test_create_actor_error_missing_data(self):
        res = self.client().post('/actors', headers={
            "Authorization": 'bearer '+self.token_producer})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            data['message'], 'Bad request - actor_data is required')

    def test_create_actor_error_missing_name(self):
        new_actor = {
            'age': 45,
            'gender': 'male'
        }
        res = self.client().post('/actors', json=new_actor, headers={
            "Authorization": 'bearer '+self.token_producer})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            data['message'], 'Bad request - name is required')

    def test_create_actor_error_missing_age(self):
        new_actor = {
            'name': 'Jon Actor',
            'gender': 'male'
        }
        res = self.client().post('/actors', json=new_actor, headers={
            "Authorization": 'bearer '+self.token_producer})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            data['message'], 'Bad request - age is required')

    def test_create_actor_error_missing_gender(self):
        new_actor = {
            'name': 'Jon Actor',
            'age': 45
        }
        res = self.client().post('/actors', json=new_actor, headers={
            "Authorization": 'bearer '+self.token_producer})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            data['message'], 'Bad request - gender is required')

    def test_get_actor(self):
        new_actor = {
            'name': 'Jon Actor',
            'age': 45,
            'gender': 'male'
        }
        new_actor = Actor(
            name=new_actor['name'], age=new_actor['age'], gender=new_actor['gender'])
        new_actor.insert()
        formated_actor = new_actor.format()
        formatted_actor_id = formated_actor['id']
        res = self.client().get('/actors/' + str(formatted_actor_id), headers={
            "Authorization": 'bearer '+self.token_assistant})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['actor']['id'], formatted_actor_id)
        self.assertEqual(data['actor']['name'], formated_actor['name'])
        self.assertEqual(data['actor']['movies']['total_movies'], 0)
        new_actor.delete()

    def test_error_get_actor_not_authenticated(self):
        new_actor = {
            'name': 'Jon Actor',
            'age': 45,
            'gender': 'male'
        }
        new_actor = Actor(
            name=new_actor['name'], age=new_actor['age'], gender=new_actor['gender'])
        new_actor.insert()
        formated_actor = new_actor.format()
        formatted_actor_id = formated_actor['id']
        res = self.client().get('/actors/' + str(formatted_actor_id))

        self.assertEqual(res.status_code, 401)
        new_actor.delete()

    def test_error_get_actor_not_found(self):
        actor_id = 1111111
        res = self.client().get('/actors/'+str(actor_id), headers={
            "Authorization": 'bearer '+self.token_assistant})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(
            data['message'], 'Could not find actor with id ' + str(actor_id))

    def test_update_actor(self):
        new_actor = {
            'name': 'Jon Actor',
            'age': 45,
            'gender': 'male'
        }
        new_actor = Actor(
            name=new_actor['name'], age=new_actor['age'], gender=new_actor['gender'])
        new_actor.insert()
        formated_actor = new_actor.format()
        formatted_actor_id = formated_actor['id']
        updated_actor = {
            'name': 'Buggsy Malone'
        }
        res = self.client().patch(
            '/actors/' + str(formatted_actor_id), json=updated_actor, headers={
                "Authorization": 'bearer '+self.token_director})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['actor']['id'], formatted_actor_id)
        self.assertEqual(data['actor']['name'], updated_actor['name'])
        self.assertEqual(data['actor']['movies']['total_movies'], 0)
        new_actor.delete()

    def test_error_update_actor_not_found(self):
        actor_id = 111111
        updated_actor = {
            'name': 'Buggsy Malone'
        }
        res = self.client().patch(
            '/actors/' + str(actor_id), json=updated_actor, headers={
                "Authorization": 'bearer '+self.token_director})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(
            data['message'], 'Could not find actor with id ' + str(actor_id))

    def test_error_update_actor_no_data(self):
        new_actor = {
            'name': 'Jon Actor',
            'age': 45,
            'gender': 'male'
        }
        new_actor = Actor(
            name=new_actor['name'], age=new_actor['age'], gender=new_actor['gender'])
        new_actor.insert()
        formated_actor = new_actor.format()
        formatted_actor_id = formated_actor['id']
        res = self.client().patch(
            '/actors/' + str(formatted_actor_id), headers={
                "Authorization": 'bearer '+self.token_director})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            data['message'], 'Bad request - actor_data is required')
        new_actor.delete()

    def test_delete_actor(self):
        new_actor = {
            'name': 'Jon Actor',
            'age': 45,
            'gender': 'male'
        }
        new_actor = Actor(
            name=new_actor['name'], age=new_actor['age'], gender=new_actor['gender'])
        new_actor.insert()
        formated_actor = new_actor.format()
        formatted_actor_id = formated_actor['id']
        res = self.client().delete('/actors/' + str(formatted_actor_id), headers={
            "Authorization": 'bearer '+self.token_producer})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['actor_id'], formatted_actor_id)
        new_actor.delete()

    def test_error_delete_actor_not_authenticated(self):
        new_actor = {
            'name': 'Jon Actor',
            'age': 45,
            'gender': 'male'
        }
        new_actor = Actor(
            name=new_actor['name'], age=new_actor['age'], gender=new_actor['gender'])
        new_actor.insert()
        formated_actor = new_actor.format()
        formatted_actor_id = formated_actor['id']
        res = self.client().delete('/actors/' + str(formatted_actor_id))

        self.assertEqual(res.status_code, 401)
        new_actor.delete()

    def test_error_delete_actor_no_permissions(self):
        new_actor = {
            'name': 'Jon Actor',
            'age': 45,
            'gender': 'male'
        }
        new_actor = Actor(
            name=new_actor['name'], age=new_actor['age'], gender=new_actor['gender'])
        new_actor.insert()
        formated_actor = new_actor.format()
        formatted_actor_id = formated_actor['id']
        res = self.client().delete('/actors/' + str(formatted_actor_id), headers={
            "Authorization": 'bearer '+self.token_assistant})

        self.assertEqual(res.status_code, 403)
        new_actor.delete()

    def test_error_delete_actor_not_found(self):
        actor_id = 1111111
        res = self.client().delete('/actors/'+str(actor_id), headers={
            "Authorization": 'bearer '+self.token_director})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(
            data['message'], 'Could not find actor with id ' + str(actor_id))


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
