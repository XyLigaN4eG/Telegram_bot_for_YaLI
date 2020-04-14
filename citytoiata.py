import requests


def city_to_iata():
    api_server = "https://www.travelpayouts.com/widgets_suggest_params"
    params = {
        "q": input("Введите пункт отправления и пункт назначения. Например: из Сочи в Москву\n")

    }
    try:
        response = requests.get(api_server, params=params)
        j_response = response.json()
        return j_response["origin"]["iata"], j_response["destination"]["iata"]

    except KeyError:
        return "Мне кажется, что Вы ввели название города неправильно. Пожалуйста, попробуйте ещё раз."
