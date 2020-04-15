import requests
from citytoiata import city_to_iata

ONE_WAY = "false"
CURRENCY = "rub"
BEGINNING_OF_PERIOD = "2020-05-01"
TRIP_DURATION = "2"
CORRECT_DATE = 0
ORIGIN = 0
DESTINATION = 0


def fly_requests():
    data_list = []

    iata = str(city_to_iata()).split(",")

    if str(iata[0]).replace("(", "").replace("'", "") == str(iata[1]).replace(")", "").replace("'", "").replace(" ",
                                                                                                                ""):
        return f"Ой-ой, мне кажется, что город, который Вы хотите полететь, совпадает с городом, куда Вы" \
               f" намереваетесь отправиться. Попробуйте ещё раз."

    api_server = "http://api.travelpayouts.com/v2/prices/latest"
    params = {
        "origin": ORIGIN,
        "destination": DESTINATION,
        "show_to_affiliates": "false",
        "limit": LIMIT,
        "one_way": ONE_WAY,
        "beginning_of_period ": BEGINNING_OF_PERIOD,
        "trip_duration": TRIP_DURATION
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
            data_list[count].append(count)
            data_list[count].append("Город(аэропорт) отправления: " + i["origin"])
            data_list[count].append("Город(аэропорт) прибытия: " + i["destination"])
            data_list[count].append(str(i["value"]) + " рублей")
            data_list[count].append("Время отправления: " + str(i["depart_date"]).replace("-", '.'))
            if str(i["return_date"]).replace("-", '.') != "None":
                data_list[count].append("Время возвращения: " + str(i["return_date"]).replace("-", '.'))
            if i["number_of_changes"] != 0:
                data_list[count].append("количество пересадок: " + str(i["number_of_changes"]))
            count += 1
        return data_list
    except KeyError:
        return "К сожалению, один из городов отсутствует в моей базе данных. Проверьте написание или попытайтесь позже."
