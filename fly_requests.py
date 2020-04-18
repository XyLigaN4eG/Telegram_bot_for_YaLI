import requests
from data import db_session
from data.local_requests import LocalRequests


def fly_requests(user_dict):
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
            print(
                "Упс, мне сообщили, что таких рейсов сейчас нет. Мне очень жаль, попробуйте "
                "повторить запрос в другое время.")
        count = 0
        for i in json_response["data"]:
            data_list.append([])
            data_list[count].append("Город(аэропорт) отправления: " + i["origin"])
            data_list[count].append("Город(аэропорт) прибытия: " + i["destination"])
            data_list[count].append(str(i["value"]) + " рублей")
            data_list[count].append("Время отправления: " + str(i["depart_date"]).replace("-", '.'))
            data_list[count].append("Время возвращения: " + str(i["return_date"]).replace("-", '.'))
            data_list[count].append("количество пересадок: " + str(i["number_of_changes"]))
            count += 1
        return data_list
    except KeyError:
        return "К сожалению, один из городов отсутствует в моей базе данных. Проверьте написание или попытайтесь позже."


user = LocalRequests()
user.origin = "Пользователь 1"
user.destination = "биография пользователя 1"
session = db_session.create_session()
session.add(user)
session.commit()
