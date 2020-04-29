from flask_restful import reqparse, abort, Api, Resource
import flask
from flask import Flask
from data import db_session
from data.local_requests import LocalRequests
import main as main1

parser = reqparse.RequestParser()
parser.add_argument('origin', type=str, required=True)
parser.add_argument('destination', type=str, required=True)
parser.add_argument('gate', type=str, required=True)
parser.add_argument('return_date', type=str, required=True)
parser.add_argument('number_of_changes', type=str, required=True)
parser.add_argument('depart_date', type=str, required=True)
parser.add_argument('value', type=str, required=True)
db_session.global_init("db/local_requests.sqlite")

app = Flask(__name__)
api = Api(app)
blueprint = flask.Blueprint('tickets_requests', __name__,
                            template_folder='templates')


def abort_if_ticket_not_found(id):
    session = db_session.create_session()
    tick = session.query(LocalRequests).get(id)
    if not tick:
        abort(404, message=f"Tickets {id} not found")


class RESTForOneObject(Resource):

    def get(self, id):
        abort_if_ticket_not_found(id)
        session = db_session.create_session()
        tick = session.query(LocalRequests).get(id)
        return {'tick': tick.to_dict(
            only=('destination', 'origin', 'value', 'id'))}

    def delete(self, id):
        abort_if_ticket_not_found(id)
        session = db_session.create_session()
        tick = session.query(LocalRequests).get(id)
        session.delete(tick)
        session.commit()
        return {'success': 'OK'}


class RestForCollection(Resource):
    def get(self):
        session = db_session.create_session()
        tick = session.query(LocalRequests).all()
        return {'ticket': [item.to_dict(
            only=('destination', 'origin', 'value')) for item in tick]}

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        tikc = LocalRequests()
        tikc.origin = args.origin
        tikc.destination = args.destination
        tikc.gate = args.gate
        tikc.return_date = args.return_date
        tikc.depart_date = args.depart_date
        tikc.number_of_changes = args.number_of_changes
        tikc.value = args.value
        session.add(tikc)
        session.commit()
        return {'success': 'OK'}


api.add_resource(RestForCollection, '/api/v2/tickets')
api.add_resource(RESTForOneObject, '/api/v2/tickets/<int:id>')

if __name__ == '__main__':
    app.run()
