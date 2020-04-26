import requests
from requests import post
from data import db_session
from data.local_requests import LocalRequests
from flask import Flask

db_session.global_init("db/local_requests.sqlite")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def fly_requests(user_dict):
    success = 8
    data_list = []
    if user_dict['or'] == user_dict['dest']:
        return f"Ой-ой, мне кажется, что город, который Вы хотите полететь, совпадает с городом, куда Вы" \
               f" намереваетесь отправиться. Попробуйте ещё раз."

    api_server = "http://api.travelpayouts.com/v2/prices/latest"
    params = {
        "origin": user_dict['or'],
        "destination": user_dict['dest'],
        "show_to_affiliates": "false",
        "limit": user_dict['limit'],
        "one_way": user_dict['one_way'],
        "beginning_of_period ": user_dict['date'],
        "trip_duration": user_dict['trip_duration']

    }

    header = {"X-Access-Token": "89e51b8e23c27d19fed4665455236f7f"}

    response = requests.get(api_server, headers=header, params=params)

    json_response = response.json()
    try:
        if len(json_response["data"]) == 0:
            return "Упс, мне сообщили, что таких рейсов сейчас нет. Мне очень жаль, попробуйте повторить запрос" \
                   " в другое время."
        else:
            for i in json_response["data"]:
                rest_requests = 'http://localhost:5000/api/news'
                params = {
                    "id": i['id'],
                    "iata_origin": i['iata_origin'],
                    "iata_destination": i['iata_destination'],
                    "origin": i['origin'],
                    "destination": i['destination'],
                    "depart_date": i['depart_date'],
                    "return_date": i['return_date'],
                    "number_of_changes": i['number_of_changes'],
                    "value": i['value'],
                    "gate": i['gate']
                }
                response = requests.post(rest_requests, params=params)
        return success

    except KeyError:
        return "К сожалению, один из городов отсутствует в моей базе данных. Проверьте написание или попытайтесь позже."
