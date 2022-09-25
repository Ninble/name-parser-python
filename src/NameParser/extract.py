# clsExtractNames
#
# Parse a name into useful components.
# This class is meant to integrate the Name Parser API into your Python project.
# This class contains all functionality of the "extract" endpoint which can be found on:
# https://parser.name/api/extract-names/

import urllib.parse
import requests
from array import array

class clsExtractNames:
    __apiKey = ""
    __min_frequency = 0
    _response = {}
    _list = []
    __remaining_hour = 250  # Default rate limit
    __remaining_day = 250  # Default rate limit

    def __init__(self, apiKey, min_frequency=100):

        if(apiKey == ""):
            raise ValueError("Missing API key or API key is invalid.")

        self.__apiKey = apiKey
        self.__min_frequency = min_frequency

    def list(self) -> array:
        return self._list

    def details(self, name) -> array:
        return self._response[name]

    def response(self) -> array:
        return self._response

    def remainingHour(self) -> int:
        return self.__remaining_hour

    def remainingDay(self)-> int:
        return self.__remaining_day
    
    # This endpoint extracts all possible names from a piece of text.
    def extract(self,text)->bool:

        if(len(text)<=2):
            raise ValueError("Text is to short to contain any names.")
        elif(len(text)>2048):
             raise ValueError("Text is to long to send to API.")
        
        # Create the URL with parameters depending on the input.
        url = "https://api.parser.name/?api_key=" + self.__apiKey + "&endpoint=extract&text="+urllib.parse.quote_plus(text)

        return self._cUrl(url)

    def _cUrl(self,url:str) ->bool:

        # Execute API request.
        response=requests.get(url)

        # Retrieve status code, header and body from response object.
        status_code=response.status_code
        header=response.headers
        json=response.json()

        # Heading contains information about rate limits.
        self._processHeader(header)

        # Process the response if possible.
        if(status_code==200):
            if "data" in json:
                self._processResponse(json["data"])
            else:
                raise ValueError("Response is missing data.")
        else:
            raise ValueError("API returned status code "+status_code+".")

        return True

    def _processResponse(self,response) -> None:
        
        for object in response:
            if(object["frequency"]>= self.__min_frequency):
                self._list.append(object['name'])
                self._response[object['name']]=object['parsed']

    def _processHeader(self,header):
        
        for key,val in header.items():
            if(key=="X-Requests-Remaining-Hour"):
                self.__remaining_hour=int(val)
            if(key=="X-Requests-Remaining-Day"):
                self.__remaining_day=int(val)