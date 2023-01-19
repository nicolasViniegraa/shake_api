from utils import create_xe_request_headers
from bs4 import BeautifulSoup
import requests

#select method to get currencies based on website selected
def get_currencies(site):

    #if wise is the website then the currencies are obtained from wise
    if site == 'wise':
        return get_currencies_wise()
    #if xe is the website then the currencies are obtained from xe
    elif site == 'xe':
        return get_currencies_xe()
    #if an incorrect value is intered return None
    else:
        return None

#get the currencies from wise
def get_currencies_wise():

    currencies = {}

    url = "https://wise.com/gb/currency-converter/currencies#V"

    #make request
    response = requests.get(url)

    #if the response isn't successful return
    if response.status_code != 200:
        return -1

    #parse the response text into a BeautifulSoup instance
    soup = BeautifulSoup(response.text, "html.parser")

    #get the list of currency groups
    currency_groups = soup.find_all("div", {"class":"currency-group"})

    for group in currency_groups:
        #get a list with the elements of each currency inside a currency group
        cards = group.find_all("a")

        for card in cards:
            #get currency name and code
            currency_name = card.find("p").text
            currency_code = card.find("h5").text

            #add currency to the dictionary
            currencies[currency_name] = currency_code

    return currencies

#get the currencies from wise
def get_currencies_xe():
    
    currencies = {}

    #create the header with the authorization parameter using de xe api credentials
    headers = create_xe_request_headers()

    url = "https://xecdapi.xe.com/v1/currencies"

    #make request
    response = requests.get(url, headers=headers)

    #if the response isn't successful return
    if response.status_code != 200:
        return -1

    data = response.json()

    #for each currency get name and code
    for currency in data['currencies']:

        currency_name = currency['currency_name']
        currency_code = currency['iso']

        #add currency to dictionary
        currencies[currency_name] = currency_code

    return currencies







