# SHAKE API

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the libraries
specified in requirements.txt.

```bash
pip install -r requirements.txt
```

## Characteristics


1) 

The system has two storing methods:

    Mongo database
    Local file

You can try both of them. To use the mongo database you need to start a local server so that 
mongo can create a local connection. To do that install mongo in your pc and in cmd run "mongod".
That will start a local server and you'll be able to store data in the database.

If not, you can simply run the system and it will store conversions in the local file, it will
be created in the root directory of the project.

The system will always try to store first in the database and in second place in the file.



2)

The API has 3 functional endpoints:

/convert:

    - Convert receives a path parameter that is the site where we want to do the conversion
        It can be either Xe or Wise and it must be specified the following way:
        "/convert/xe" or "/convert/wise"

    - It also receives 3 query parameters:
        from_currency: The currency from which we want to do the conversion
        to_currency: The currency in which we want the amount to be converted
        amount: The number of the first currency that will be converted into a new currency

    - Some validations are applied to these parameters, if they are invalid, the system raises
        exceptions depending on which validation wasn't fulfilled
        If you not provide any of the query parameters, or provide it in a wrong format (e.g.
        from_currency with more or less than 3 letters, or a non numeric value for amount), 
        the system wil raise an exception
    
    - Depending on the website selected the system calls the API of the website to ask for a
        conversion providing the parameters. After receiving the response it builds the conversion dictionary and returns it. In addition to returning it, the system also 
        stores the conversion. 

        There are two storing methods available.

        First one is on a Mongo database, the system stores the conversion as a document in
        a collection name "conversions"
        The second method is in a local file, storing it as text in a single line, each line
        in the file represent a different conversion

    - The conversion dictionary has the following structure:

        conversion = {
            "converted_amount": float,
            "rate": float,
            # "site": str,
            "metadata": {
                "time_of_conversion": datetime,
                "from_currency": str,
                "to_currency": str,
            }
        }

        In addition to the fields provided, I also added a new field named "site", that 
        field contains the name of the site where the conversion was done. In the code 
        is commented because it wasn't a field that you asked for. But I believe it could 
        be interesting taking it into account so if you want to keep it you can just uncomment
        that line in the convert.py file.


/currencies:

    - Currencies receives a path parameter that is the site where we want to do the conversion
        It can be either Xe or Wise and it must be specified the following way:
        "/currencies/xe" or "/currencies/wise"

    - Depending on the website selected the system calls the API of the website to ask for all
        the currencies listed

        Wise doesn't provide an API for getting all the currencies so it requests directly to 
        the webpage and uses BeautifulSoup to get them from the html text

        Xe provides an API, so for that website it requests to the API to get all the currencies

        After requesting either website, the system creates a list with all the currencies an returns it


/history

    - History returns all the stored conversions done previously

        To retrieve them first the system tries to get the conversions stored in the Mongo database. If the database isn't connected it doesn't retrieve them. 
        Either way, the system then gets the conversions stored in the file "conversions.txt"

        The conversiones are loaded each one as a dictionary inside a list

        After that it returns the list



3)

All the endpoints are protected with API KEY Authentication. If you don't provide an API KEY
or provide a wrong API KEY the endpoint will return a 401 status code.

The api key is this: 1234567asdfgh

You can provide the API KEY in three different ways:

    - As a query parameter (?api_key=1234567asdfgh)
    - In the headers of the request
    - In the cookie of the request

You can try in Postman providing the API KEY in the headers or in the cookie, if not in a browser you can try providing it as a query parameter.

The API KEY is in the source code and as soon as the system is executed it's are stored in 
a local file named "credentials.txt". So when an endpoint is called, the systems gets the 
API KEY from that file and compares it to the API KEY given in the request to know if it's
the valid API KEY.



4)

To query the Xe API you need a username and a password, both of them are in the source code and as soon as the system is executed they are stored in the local file "credentials.txt", so you
don't have to worry about providing those parameters.

Each time the systems has to query the Xe API, it goes to the file and gets the credentials.

!!!IMPORTANT!!!
The credentials have a period of usage of 1 week, they'll become unavailable next Tuesday.
If you want to test the system after that day please let me know and I'll create new credentials 
and update them in the source code



5) 
    
Since the API KEY and the username and password of the Xe API are sensitive information, they
are encrypted before being stored in the "credentials.txt" file. To encrypt and decrypt them
each time the need to be accessed, an encryption key is generated and stored in the "key.txt"
file.

The system uses files to store the encrypted data and key. I thought about storing them encrypted
in the Mongo database too, but for sake of simplicity I did not.


## Usage

To use it first you need to install the dependencies specified in requirements.txt

run "pip install -r requirements.txt"

You need a uvicorn server running to test the API.

You can run the "server.py" file (python3 server.py) if you have Windows
Note: The port in the server.py file is set to 5000.

After that you can try the endpoints on a web browser or Postman.

Here's an example of each endpoint 

/convert: http://127.0.0.1:5000/convert/xe?from_currency=AED&to_currency=ALL&amount=950&api_key=1234567asdfgh
/currencies: http://127.0.0.1:5000/currencies/wise?api_key=1234567asdfgh
/history: http://127.0.0.1:5000/history?api_key=1234567asdfgh

If you use the MongoDB functionalities you can query or connect to localhost with a 
software like Studio 3T to see that the conversiones are being stored correctly.

You can open the "conversions.txt" file to see that the conversiones are being stored in 
that file.

Also you can open "credentials.txt" to see the encrypted values of the api key, xe api username 
and xe api password

In that file the api key is always the first element, the xe api username the second element and
xe api password is the third element.

You can also check "key.txt" to see the encryption key

"conversiones.txt", "credentials.txt" and "key.txt" are created when you run the server. You can
try to delete the files and run the server again to see how they are created again.

## Assumptions

I had doubts about two fields in the conversion dictionary

    conversion = {
        "converted_amount": float,
        "rate": float,
        # "site": str,
        "metadata": {
            "time_of_conversion": datetime,
            "from_currency": str,
            "to_currency": str,
        }
    }

I didn't know exactly what converted_amount and rate where referring to, so I assume the following:

    - Converted_amount is the amount in the new currency, the value of the converted 
        currency (to_currency)
    - Rate is the conversion rate between the new currency (to_currency) and the former 
        currency (from_currency)
