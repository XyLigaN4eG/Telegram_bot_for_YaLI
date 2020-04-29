import requests
from flask_restful import Api
from requests import post
from data import db_session
from flask import Flask
app = Flask(__name__)
api = Api(app)
db_session.global_init("db/local_requests.sqlite")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
SUCCESS = 1
UNSUCCESS = 10


# Обращение к travelpayouts—API
def fly_requests(user_dict):
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
                rest_requests = 'http://localhost:5000/api/v2/tickets'
                params = {
                    "origin": "Город(аэропорт) отправления: " + i['origin'],
                    "destination": "Город(аэропорт) прибытия: " + i['destination'],
                    "depart_date": "Время отправления: " + str(i["depart_date"]).replace("-", '.'),
                    "return_date": "Время возвращения: " + str(i["return_date"]).replace("-", '.'),
                    "number_of_changes": "Количество пересадок: " + str(i['number_of_changes']).replace('None', '0'),
                    "value": str(i['value']) + " рублей",
                    "gate": i['gate']
                }
                print(post(rest_requests, params=params))
                print('200')
        return SUCCESS

    except KeyError:
        return UNSUCCESS
