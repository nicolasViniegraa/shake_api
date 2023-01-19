from utils import create_xe_request_headers
from datetime import datetime
import requests

#select method to do convertion based on website selected
def convert_currency(site, amount, from_currency, to_currency):

    #if wise is the website then the conversion is done with wise api
    if site == 'wise':
        return convert_currency_wise(amount, from_currency, to_currency)
    #if xe is the website then the conversion is done with xe api
    elif site == 'xe':
        return convert_currency_xe(amount, from_currency, to_currency)
    #if an incorrect value is intered return None
    else:
        return None

#convert an amount of a specific currency into another with xe api
def convert_currency_xe(amount, from_currency, to_currency):
 
    url = "https://xecdapi.xe.com/v1/convert_from?from={}&to={}&amount={}"

    #create the header with the authorization parameter using de xe api credentials
    headers = create_xe_request_headers()

    #request the data providing the parameters
    response = requests.get(url.format(from_currency, to_currency, amount), headers=headers)

    #if the response isn't successful return
    if response.status_code != 200:
        return -1

    data = response.json()

    #parse the timestamp into datetime to respect the format
    date_time = datetime.strptime(data["timestamp"], '%Y-%m-%dT%H:%M:%SZ')

    #calculate the rate
    rate = round(data["to"][0]["mid"] / float(amount), 4)

    #create the dictionary with the values of the conversion
    conversion = {
        "converted_amount": round(data["to"][0]["mid"], 2),
        "rate": rate,
        # "site": "Xe",
        "metadata": {
            "time_of_conversion": date_time,
            "from_currency": from_currency,
            "to_currency": to_currency,
        }
    }

    return conversion

#convert an amount of a specific currency into another with wise api
def convert_currency_wise(amount, from_currency, to_currency):

    url = "https://api.wise.com/v1/rates?source={}&target={}"

    headers = {
        'authorization': 'Basic OGNhN2FlMjUtOTNjNS00MmFlLThhYjQtMzlkZTFlOTQzZDEwOjliN2UzNmZkLWRjYjgtNDEwZS1hYzc3LTQ5NGRmYmEyZGJjZA==',
    }

    #request the data providing the parameters
    response = requests.get(url.format(from_currency, to_currency), headers=headers)

    #if the response isn't successful return
    if response.status_code != 200:
        return -1

    data = response.json()

    rate = data[0]['rate']

    #parse the timestamp into datetime to respect the format
    date_time = datetime.strptime(data[0]["time"], '%Y-%m-%dT%H:%M:%S+0000')

    #create the dictionary with the values of the conversion
    conversion = {
        "converted_amount": round(float(amount) * rate, 4),
        "rate": rate,
        # "site": 'Wise',
        "metadata": {
            "time_of_conversion": date_time,
            "from_currency": from_currency,
            "to_currency": to_currency,
        }
    }

    return conversion


