import requests
from citytoiata import city_to_iata

ONE_WAY = "false"

CURRENCY = "rub"



BEGINNING_OF_PERIOD = "2020-05-01"

TRIP_DURATION = "2"

correct_date = 0
iata = str(city_to_iata()).split(",")

if str(iata[0]).replace("(", "").replace("'", "") == str(iata[1]).replace(")", "").replace("'", "").replace(" ", ""):
    print(
        f"Ой-ой, мне кажется, что город, который Вы хотите полететь, совпадает с городом, куда Вы намереваетесь отправ"
        f"иться. Попробуйте ещё раз.")
    exit()

one_way_asker = input("Нужны ли Вам обратные билеты?(Да/Нет)\n")
if one_way_asker.lower() == "нет":
    ONE_WAY = "true"

duration_asker = input("Сколько дней будет длиться Ваше прибывание в другом городе?(В неделях)\n")
if " " in duration_asker:
    duration_asker.split(" ")
    TRIP_DURATION = duration_asker[0]
else:
    TRIP_DURATION = duration_asker

beginning_of_period_asker = input(
    "Введите дату, когда бы Вы хотели отправиться.(будут показаны результаты на месяц с даты отправления."
    "Формат ввода: DD.MM.YYYY)\n")
correct_date = beginning_of_period_asker.split(".")
BEGINNING_OF_PERIOD = correct_date[2] + "-" + correct_date[1] + "-" + correct_date[0]
LIMIT = input("Какое максимальное количество предложений предложений Вы хотите увидеть?\n")
ORIGIN = str(iata[0]).replace("(", "").replace("'", "")

DESTINATION = str(iata[1]).replace(")", "").replace("'", "").replace(" ", "")

api_server = "http://api.travelpayouts.com/v2/prices/latest"
params = {
    "origin": ORIGIN,
    "destination": DESTINATION,
    "show_to_affiliates": "false",
    "limit": LIMIT,
    "one_way": ONE_WAY,
    "beginning_of_period": BEGINNING_OF_PERIOD,
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

    for i in json_response["data"]:
        print("Город(аэропорт) отправления: " + i["origin"])
        print("Город(аэропорт) прибытия: " + i["destination"])
        print(str(i["value"]) + " рублей")
        print("Время отправления: " + str(i["depart_date"]).replace("-", '.'))
        if str(i["return_date"]).replace("-", '.') != "None":
            print("Время возвращения: " + str(i["return_date"]).replace("-", '.'))
        else:
            pass
        if i["number_of_changes"] != 0:
            print("количество пересадок: " + str(i["number_of_changes"]))
        else:
            pass
        print("______________________________________________")
except KeyError:
    print("К сожалению, один из городов отсутствует в моей базе данных. Проверьте написание или попытайтесь позже.")
