import argparse
from flask_restful import reqparse, abort, Api, Resource
import flask
from flask import Flask, jsonify
from data import db_session
from data.local_requests import LocalRequests

db_session.global_init("db/local_requests.sqlite")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


app = Flask(__name__)
api = Api(app)
blueprint = flask.Blueprint('tickets_requests', __name__,
                            template_folder='templates')


def abort_if_news_not_found(id):
    session = db_session.create_session()
    news = session.query(LocalRequests).get(id)
    if not news:
        abort(404, message=f"News {id} not found")


class RESTForOneObject(Resource):

    def get(self, id):
        abort_if_news_not_found(id)
        session = db_session.create_session()
        news = session.query(LocalRequests).get(id)
        return jsonify({'news': news.to_dict(
            only=('destination', 'origin', 'value', 'id'))})

    def delete(self, id):
        abort_if_news_not_found(id)
        session = db_session.create_session()
        news = session.query(LocalRequests).get(id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})


class RestForCollection(Resource):
    def get(self):
        session = db_session.create_session()
        news = session.query(LocalRequests).all()
        return jsonify({'news': [item.to_dict(
            only=('destination', 'origin', 'value')) for item in news]})

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', required=True, type=int)
        parser.add_argument('value', required=True, type=int)
        parser = argparse.ArgumentParser()
        args = parser.parse_args()

        session = db_session.create_session()
        news = LocalRequests()
        news.id = args.id
        news.value = args.value
        session.add(news)
        session.commit()
        return jsonify({'success': 'OK'})


api.add_resource(RestForCollection, '/api/v2/news')

api.add_resource(RESTForOneObject, '/api/v2/news/<int:id>')
if __name__ == '__main__':
    app.run()
