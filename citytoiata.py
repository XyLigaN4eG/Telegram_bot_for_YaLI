import requests

error = -1


# Преобразует название городов в из IATA—коды
def city_to_iata(text, user_dict):
    api_server = "https://www.travelpayouts.com/widgets_suggest_params"
    params = {
        "q": text

    }
    try:
        response = requests.get(api_server, params=params)
        j_response = response.json()

        user_dict["not_iata_or"] = j_response["origin"]["name"]
        user_dict["not_iata_ds"] = j_response["destination"]["name"]
        return j_response["origin"]["iata"], j_response["destination"]["iata"]

    except KeyError:
        return error
