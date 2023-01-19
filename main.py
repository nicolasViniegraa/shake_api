from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
from fastapi import Security, Depends, FastAPI, HTTPException, Query
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_503_SERVICE_UNAVAILABLE, HTTP_422_UNPROCESSABLE_ENTITY
from utils import set_key, set_credentials, get_api_key_from_file, create_conversions_file
from get_currencies import get_currencies
from convert import convert_currency
from pydantic import Required
import mongo
import json


#if the key.txt and/or credentials.txt files don't exist
#create encryption key and store it in the key.txt file
set_key()
#encrypt credentials and store them in the credentials.txt file
set_credentials()
#create conversions.txt file
create_conversions_file()

#define the name for the api_key
API_KEY_NAME = "api_key"

#create variables for each way to provide the api_key
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)

#validate if the api key is correct
async def get_api_key(
    #one parameter for each way to provide api key
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
    api_key_cookie: str = Security(api_key_cookie),
):

    #if the api key is provided in some way it's stored
    if api_key_query != None:
        provided_api_key = api_key_query
    elif api_key_header != None:
        provided_api_key = api_key_header
    elif api_key_cookie:
        provided_api_key = api_key_cookie
    #if not the value None is set in replacement
    else:
        provided_api_key = None
        
    #get the api key from the credentials.txt file
    stored_api_key = get_api_key_from_file()

    #compare the real api key with the api key provided in the requests
    #if they aren't the same raise a 403 exception
    if stored_api_key != provided_api_key:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

#return a Mongo instance
def get_connection():
    return mongo.mongo()

#create FastAPI instance
app = FastAPI()

#root endpoint
@app.get("/")
async def root():
    return {"message": "Hello World"}


#currencies endpoint
'''
    Receives website (xe/wise) as path parameter
    Can receive api key as query parameter (also can be provided in header or cookie)
'''
@app.get("/currencies/{website}")
async def root(website, api_key: APIKey = Depends(get_api_key)):
    
    #get the currency list from the website selected
    currencies = get_currencies(website)

    #if the value is None raise a 404 exception
    if not currencies:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Website Not Found"
        )
    #if the request for wise or xe api wasn't done successfully
    elif currencies == -1:
        raise HTTPException(
            status_code=HTTP_503_SERVICE_UNAVAILABLE, detail="Could not satisfy request"
        )
    else:
        return currencies

#convert endpoint
'''
    Receives website (xe/wise) as path parameter
    Receives amount, from_currency, to_currency as query parameters
    Can receive api key as query parameter (also can be provided in header or cookie)
'''
@app.get("/convert/{website}")
async def root(website,
        #apply validations to query parameters
        to_currency: str = Query(default = Required, min_length=3, max_length=3),
        from_currency: str = Query(default = Required, min_length=3, max_length=3),
        amount: str = Query(default = Required),
        api_key: APIKey = Depends(get_api_key)):

    if not amount.isnumeric():
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail="Amount param must be numeric"
        )

    #get the conversion from the website selected
    conversion = convert_currency(website, amount, from_currency, to_currency)

    #if the value is None raise a 404 exception
    if not conversion:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Website Not Found"
        )
    #if the request for wise or xe api wasn't done successfully
    elif conversion == -1:
        raise HTTPException(
            status_code=HTTP_503_SERVICE_UNAVAILABLE, detail="Could not satisfy request"
        )
    #if not store the conversion
    else:

        connection = get_connection()
        #if the Mongo instance is up store the conversion in the database
        if connection.is_connected:
            connection.insert("conversions", conversion)
            #delete the '_id' field generated when conversion is inserted in the database
            conversion.pop('_id')
        #if not store the conversion in the conversions.file
        else: 
            #parse the datetime value to string to be writable in the file
            string_datetime = conversion['metadata']['time_of_conversion']\
                                            .strftime('%Y-%m-%dT%H:%M:%SZ')

            conversion['metadata']['time_of_conversion'] = string_datetime

            #write conversion in the file
            with open('conversions.txt', 'a+') as file:
                file.write(json.dumps(conversion) + "\n")
            file.close()

        return conversion

#history endpoint
'''
    Can receive api key as query parameter (also can be provided in header or cookie)
'''
@app.get("/history")
async def root(api_key: APIKey = Depends(get_api_key)):

    historic_conversions = []

    connection = get_connection()
    #if the Mongo instance is up get the history of conversions from the database
    if connection.is_connected:
        #get all conversions
        query = connection.find("conversions")
        #create list of conversions
        historic_conversions = [item for item in query]

    #get the history of conversions from the conversions file
    #read conversions.txt file
    with open('conversions.txt', 'r') as file:
        for line in file:
            #parse each line of the file to dictionary
            conversion_to_dict = json.loads(line)
            #append the dictionary to the list
            historic_conversions.append(conversion_to_dict)
    file.close()

    return historic_conversions