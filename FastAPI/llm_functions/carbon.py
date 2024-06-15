import requests


def get_carbon_intensity(args: dict) -> str:
    carbon_data = send_request(args)
    
    # Returning the CO2 intensity:
    co2_intensity = carbon_data["intensity"]["forecast"]

    return f"{co2_intensity}gCO2/kWh"


def get_generation_mix(args: dict) -> dict:
    carbon_data = send_request(args)
    generation_mix = carbon_data["generationmix"]

    # Formatting the generation mix in the form {"fuel type": "percentage}
    formatted_generation_mix = {}
    for item in generation_mix:
        formatted_generation_mix[item["fuel"]] = item["perc"]

    return formatted_generation_mix


def send_request(args: dict) -> dict:
    postcode = args.get("postcode")

    url = f"https://api.carbonintensity.org.uk/regional/postcode/{postcode}"

    headers = {"Accept": "application/json"} 
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # If successful, extracting and returning the weather data:
        carbon_data = response.json()
        return carbon_data["data"][0]["data"][0]
    else:
        return {"error": "Could not retrieve carbon data"}


function_names = {"get_carbon_intensity": get_carbon_intensity, "get_generation_mix": get_generation_mix}

function_schemas = [
    {
        "type": "function", 
        "function": {
            "name": "get_carbon_intensity",
            "description": "Returns a string with the grams of CO2 emitted per kWh of energy for the current half-hour at the given postcode.",
            "parameters": {
                "type": "object", 
                "properties": {
                    "postcode": {
                        "type": "string", 
                        "description": "The outward UK postcode, e.g. SW1A and not SW1A 2AA",        
                    },
                },
            "required": ["postcode"],
            },
        }
    },
   {
        "type": "function", 
        "function": {
            "name": "get_generation_mix",
            "description": "Returns a dictionary of fuel types and percentage of total electricity they generate at the given postcode.",
            "parameters": {
                "type": "object", 
                "properties": {
                    "postcode": {
                        "type": "string", 
                        "description": "The outward UK postcode, e.g. SW1A and not SW1A 2AA",        
                    },
                },
            "required": ["postcode"],
            },
        }
  }
]

