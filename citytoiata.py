import requests


def city_to_iata(text):
    api_server = "https://www.travelpayouts.com/widgets_suggest_params"
    params = {
        "q": text

    }
    try:
        response = requests.get(api_server, params=params)
        j_response = response.json()
        return j_response["origin"]["iata"], j_response["destination"]["iata"]

    except KeyError:
        pass
