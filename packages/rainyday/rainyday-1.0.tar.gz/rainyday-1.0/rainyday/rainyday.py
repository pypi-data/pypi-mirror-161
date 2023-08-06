import requests
import pandas as pd

api_key = "4ec07cff4a7b304f56b6943b994576e4"


def flatten(self):
    flat_list = list()

    for sub_list in self:
        flat_list += sub_list
    return flat_list

class Weather:

    """
    The Weather class requires an api key location.
    The api key can be obtained by making an account on https://openweathermap.org.
    The location can be passed either as a string with the city name, or a tuple with
    the coordinates as (latitude, longitude).

    home = Weather(api_key, 'Paris')
    office = Weather(api_key, (52.31, 13.24))

    To get a detailed report of the weather for the next 12 hours, use the method get_weather()

    office.get_forecast()

    For a result simplified for human readability, use simple_weather()

    home.simple_forecast()

    Methods defined here:

    __init__(self, api_key, location)
        Initializes an object of class Weather with api_key to scrape the data for the given location.

    get_forecast()
        returns a list of 5 dictionaries, each carrying weather data at intervals of 3 hour.

    simple_forecast()
        get simplified forecast for 5 timepoints at intervals of 3 hours around the current time
    """

    def __init__(self, api_key, location):

        if isinstance(location,str):
            url_loc = f"q={location}"
        elif isinstance(location,tuple):
            url_loc = f"lat={location[0]}&lon={location[1]}"
        else:
            raise TypeError("Please enter location as a city or tuple of (latitude, longitude).")

        self.url = "http://api.openweathermap.org/data/2.5/forecast?" + url_loc + "&APPID=" + api_key

    def get_forecast(self):

        result = requests.get(self.url)
        data = result.json()
        if data['cod'] == '200':
            return data['list'][:5]
        else:
            raise ValueError(data['message'])

    def simple_forecast(self):

        data_first5 = self.get_forecast()
        data_dic = {'time': [y['dt_txt']  for y in data_first5],
                    'weather': [y['weather'][0]['main']+ " : "+y['weather'][0]['description']  for y in data_first5],
                    'humidity': [str(y['main']['humidity']) for y in data_first5],
                    'temp': [str(y['main']['temp']) for y in data_first5]}
        df = pd.DataFrame(data_dic)

        return df