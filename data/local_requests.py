import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class LocalRequests(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'local_requests'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    iata_origin = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    iata_destination = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    origin = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    destination = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    depart_date = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    return_date = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    number_of_changes = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    value = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    gate = sqlalchemy.Column(sqlalchemy.String, nullable=True)
