from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
import random

from data import db_session
from data.local_requests import LocalRequests

app = Flask(__name__)
api = Api(app)
db_session.global_init("db/local_requests.sqlite")
ai_quotes = LocalRequests()


class REST(Resource):
    def get(self):
        return 'it is alive!'


api.add_resource(REST, "/tickets/1")
if __name__ == '__main__':
    app.run(debug=True)
