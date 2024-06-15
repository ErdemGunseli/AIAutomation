import os
import requests

def get_air_quality(args: dict) -> dict:
    api_key = os.getenv('AIR_QUALITY_API_KEY')

    city = args.get("city")

    url = f"https://api.waqi.info/feed/{city}/?token={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        pollution_data = response.json()

        return pollution_data["data"]["iaqi"]
    else:
        return {"error": "Could not retrieve air quality data"}


function_names = {"get_air_quality": get_air_quality}

function_schemas = [
    {
        "type": "function",
        "function": {
            "name": "get_air_quality",
            "description": "Returns a dictionary with air pollutant quantities (µg/m3) for a given city and country.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city, e.g. London",
                    },
                    "country": {
                        "type": "string",
                        "description": "The country, e.g. GB",
                    },
                },
                "required": ["city", "country"],
            },
        }
    }
]
""" TODO: DELETE
{'status': 'ok', 'data': 
    {
    'aqi': 46, 'idx': 5724, 
    'attributions': 
        [
            {
                'url': 'https://londonair.org.uk/', 
                'name': "London Air Quality Network - Environmental Research Group, King's College London", 
                'logo': 'UK-London-Kings-College.png'
            }, 
            {
                'url': 'http://uk-air.defra.gov.uk/', 
                'name': 'UK-AIR, air quality information resource - Defra, UK', 
                'logo': 'UK-Department-for-environment-food-and-rural-affairs.png'
            }, 
            {
                'url': 'https://waqi.info/', 
                'name': 'World Air Quality Index Project'
            }
        ], 

    'city': {
        'geo': [51.5073509, -0.1277583], 
        'name': 'London', 
        'url': 'https://aqicn.org/city/london', 
        'location': ''
    }, 
    
    'dominentpol': 'pm25', 
    
    'iaqi': {
        'co': {'v': 2.7}, 
        'h': {'v': 68}, 
        'no2': {'v': 25.2}, 
        'o3': {'v': 30.3}, 'p': {'v': 1015.9}, 'pm10': {'v': 17}, 'pm25': {'v': 46}, 'so2': {'v': 4.5}, 't': {'v': 15.9}, 'w': {'v': 10}}, 'time': {'s': '2024-06-13 10:00:00', 'tz': '+01:00', 'v': 1718272800, 'iso': '2024-06-13T10:00:00+01:00'}, 'forecast': {'daily': {'o3': [{'avg': 20, 'day': '2024-06-11', 'max': 28, 'min': 15}, {'avg': 22, 'day': '2024-06-12', 'max': 33, 'min': 8}, {'avg': 25, 'day': '2024-06-13', 'max': 34, 'min': 15}, {'avg': 26, 'day': '2024-06-14', 'max': 34, 'min': 22}, {'avg': 26, 'day': '2024-06-15', 'max': 35, 'min': 21}, {'avg': 28, 'day': '2024-06-16', 'max': 35, 'min': 21}, {'avg': 24, 'day': '2024-06-17', 'max': 24, 'min': 21}], 'pm10': [{'avg': 9, 'day': '2024-06-11', 'max': 13, 'min': 7}, {'avg': 15, 'day': '2024-06-12', 'max': 18, 'min': 10}, {'avg': 10, 'day': '2024-06-13', 'max': 16, 'min': 6}, {'avg': 10, 'day': '2024-06-14', 'max': 14, 'min': 5}, {'avg': 9, 'day': '2024-06-15', 'max': 12, 'min': 6}, {'avg': 10, 'day': '2024-06-16', 'max': 15, 'min': 7}, {'avg': 10, 'day': '2024-06-17', 'max': 10, 'min': 10}], 'pm25': [{'avg': 31, 'day': '2024-06-11', 'max': 45, 'min': 20}, {'avg': 48, 'day': '2024-06-12', 'max': 57, 'min': 35}, {'avg': 32, 'day': '2024-06-13', 'max': 55, 'min': 16}, {'avg': 22, 'day': '2024-06-14', 'max': 26, 'min': 11}, {'avg': 19, 'day': '2024-06-15', 'max': 28, 'min': 13}, {'avg': 19, 'day': '2024-06-16', 'max': 26, 'min': 15}, {'avg': 22, 'day': '2024-06-17', 'max': 23, 'min': 22}], 'uvi': [{'avg': 0, 'day': '2022-10-24', 'max': 0, 'min': 0}]}}, 'debug': {'sync': '2024-06-13T19:39:22+09:00'}}}
Function get_air_quality returned: None

"""