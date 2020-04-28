import requests
from requests import post
rest_requests = 'http://localhost:5000/api/v2/tickets'
params = {
    "iata_origin": "1",
    "iata_destination": '1',
    "origin": '1',
    "destination": '1',
    "depart_date": '1',
    "return_date": '1',
    "number_of_changes": 1,
    "value": 12,
    "gate": '1'
}
a = (post(rest_requests, params=params))
print(a)
if str(a) == '<Response [200]>':
    print(1)
