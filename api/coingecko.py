    # lets us send requests to the internet
import requests
    # lets us read values from the computer environment
import os
    # lets us read the .env file
from dotenv import load_dotenv

    # opens the .env file and loads everything in it into memory
load_dotenv()

    # pulls the api key value out of the .env file and stores it in a variable
gekoAPI = os.getenv("COINGECKO_API_KEY")

    # defines the function, coinList is whatever list of coins gets passed in when called     
def coinGekoAPI(coinList):

        # start with an empty id badge to send with the request
    header = {}
        # if we actually have an api key, add it to the badge
    if gekoAPI:

        header["x-cg-demo-api-key"] = gekoAPI
    
    # build the questions we are asking coingecko — which coins, what currency,include 24hr change
    params = {"vs_currencies": 'usd', "include_24hr_change": "true", "ids": ",".join(coinList)}

        # send the request to coingecko with our id badge and questions attached
    response = requests.get('https://api.coingecko.com/api/v3/simple/price', headers=header, params=params)

        # if something went wrong, crash loudly so we know about it
    response.raise_for_status()

        # convert the response into a python dictionary and return it
    return response.json()