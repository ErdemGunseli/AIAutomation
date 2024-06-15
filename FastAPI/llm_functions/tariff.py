import requests

def get_tariff_plans() -> dict:
    return """
    Plan 1: Fixed electricity rate of 10p/kWh

    Plan 2: Fixed day rate of 18p/kWh and night rate of 8p/kWh
    """


function_names = {"get_tariff_plans": get_tariff_plans}

function_schemas = [
    {
        "type": "function",
        "function": {
            "name": "get_tariff_plans",
            "description": "Returns a string with the available tariff plans and their rates.",
        }
    }
]
