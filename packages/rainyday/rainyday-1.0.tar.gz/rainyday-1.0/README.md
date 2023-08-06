The Weather class requires an api key location.
    The api key can be obtained by making an account on https://openweathermap.org.
    The location can be passed either as a string with the city name, or a tuple with
    the coordinates as (latitude, longitude).

    home = Weather(api_key, 'Paris')
    office = Weather(api_key, (52.31, 13.24))

To get a detailed report of the weather for the next 12 hours, use the method get_forecast()

    office.get_forecast()

For a result simplified for human readability, use simple_forecast()

    home.simple_forecast()

Methods defined here:

    __init__(self, api_key, location)
        Initializes an object of class Weather with api_key to scrape the data for the given location.

    get_forecast()
        returns a list of 5 dictionaries, each carrying weather data at intervals of 3 hour.

    simple_forecast()
        get simplified forecast for 5 timepoints at intervals of 3 hours around the current time