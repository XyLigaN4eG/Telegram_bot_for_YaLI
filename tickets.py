import flask
from flask import jsonify, Flask
from flask_restful import reqparse, abort, Api, Resource
from data import db_session
from data.local_requests import LocalRequests


def get_tickets():
    session = db_session.create_session()
    rqst = session.query(LocalRequests).all()
    return jsonify(
        {
            'rqst':
                [item.to_dict
                 for item in rqst]
        }
    )

