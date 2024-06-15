import requests

def get_weather(args: dict) -> dict:
    city = args.get("city")
    country = args.get("country")

    # Constructing the URL with both city and country
    location = f"{city},{country}"
    url = f"http://wttr.in/{location}?format=j1"

    response = requests.get(url)

    if response.status_code == 200:
        # If successful, extracting and returning the weather data
        weather_data = response.json()
        return weather_data["current_condition"][0]
    else:
        return {"error": "Could not retrieve weather data"}


function_names = {"get_weather": get_weather}

function_schemas = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Returns a dictionary with the current weather data for a given city and country. You can determine the city and country from the user's postcode.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city, e.g. London",
                    },
                    "country": {
                        "type": "string",
                        "description": "The country, e.g. UK",
                    },
                },
                "required": ["city", "country"],
            },
        }
    }
]
