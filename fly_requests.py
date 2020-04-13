import requests
from citytoiata import city_to_iata

iata = str(city_to_iata()).split(",")
if str(iata[0]).replace("(", "").replace("'", "") == str(iata[1]).replace(")", "").replace("'", "").replace(" ", ""):
    print(
        f"Ой-ой, мне кажется, что город, который Вы хотите полететь, совпадает с городом, куда Вы намереваетесь отправ"
        f"иться. Попробуйте ещё раз.")
    exit()
api_server = "http://api.travelpayouts.com/v2/prices/latest"
params = {
    "origin": str(iata[0]).replace("(", "").replace("'", ""),
    "destination": str(iata[1]).replace(")", "").replace("'", "").replace(" ", "")
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
        print(i["origin"])
        print(i["destination"])
        print(str(i["value"]) + " рублей")
        print("Время отправления: " + str(i["depart_date"]).replace("-", '.'))
        print("Время возвращения: " + str(i["return_date"]).replace("-", '.'))
        print("_____________________")
except KeyError:
    print("Мне кажется, что Вы ввели название города неправильно. Пожалуйста, попробуйте ещё раз.")
