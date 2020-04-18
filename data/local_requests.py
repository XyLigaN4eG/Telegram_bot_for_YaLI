import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class LocalRequests(SqlAlchemyBase):
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
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

