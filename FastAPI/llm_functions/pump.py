
from enum import Enum


class CirculationType (Enum):
    INDOOR = "indoor"
    OUTDOOR = "outdoor"


thermostat: int = 21
circulation: CirculationType = CirculationType.OUTDOOR
electricity_usage: int = 100


def get_thermostat_value() -> dict:
    global thermostat
    return {"thermostat": thermostat}


def set_thermostat_value(args: dict) -> dict:
    global thermostat
    thermostat = args.get("temperature")
    return {"success": f"Thermostat set to {thermostat}."}


def get_circulation_type() -> dict:
    return {"circulation": circulation.value}


def set_circulation_type(args: dict) -> dict:
    global circulation
    circulation = CirculationType(args.get("circulation"))
    return {"success": f"Circulation set to {circulation.value}."}


def get_electricity_use(args: dict) -> dict:
    outside_temperature = args.get("outside_temperature")

    # Estimating the heating capacity for a 1200 sq ft house
    heating_capacity_kw = (1200 * 15) / 1000  # Heating capacity in kW

    # Approximate COP calculation based on the temperature difference
    if outside_temperature < -10:
        cop = 1.5  # Very low efficiency at very low temperatures
    elif -10 <= outside_temperature < 0:
        cop = 2.0  # Low efficiency
    elif 0 <= outside_temperature < 10:
        cop = 3.0  # Moderate efficiency
    elif 10 <= outside_temperature < 20:
        cop = 4.0  # High efficiency
    else:
        cop = 5.0  # Very high efficiency
    
    # Estimate the instantaneous electrical power usage (kW)
    power_usage_kw = heating_capacity_kw / cop
    
    # TODO: CHECK UNITS
    return {"usage_kw": power_usage_kw}


function_names = {"get_thermostat_value": get_thermostat_value, "set_thermostat_value": set_thermostat_value,
                  "get_circulation_type": get_circulation_type, "set_circulation_type": set_circulation_type,
                  "get_electricity_use": get_electricity_use}


function_schemas = [
    {
        "type": "function",
        "function": {
            "name": "get_thermostat_value",
            "description": "Returns a dictionary with the current heat pump thermostat value in celsius.",
            "parameters": {},
        }
    },

    {
        "type": "function",
        "function": {
            "name": "set_thermostat_value",
            "description": "Sets the the heat pump thermostat value in celsius.",
            "parameters": {
                "type": "object",
                "properties": {
                    "temperature": {
                        "type": "integer",
                        "description": "The temperature to set the thermostat to in celsius, e.g. 21.",
                    },
                   },
                "required": ["temperature"],
            },
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_circulation_type",
            "description": "Returns whether air is recirculated from indoors ('indoor') or retrieved from outdoors ('outdoor').",
            "parameters": {},
        }
    },

    {
        "type": "function",
        "function": {
            "name": "set_circulation_type",
            "description": "Sets the circulation type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "circulation": {
                        "type": "string",
                        "description": "Whether air is recirculated from indoors ('indoor') or retrieved from outdoors ('outdoor').",
                    },
                   },
                "required": ["circulation"],
            },
        }
    },

   {
        "type": "function",
        "function": {
            "name": "get_electricity_use",
            "description": "Returns the power usage from the heat pump in kW",
            "parameters": {
                "type": "object",
                "properties": {
                    "outside_temperature": {
                        "type": "integer",
                        "description": "The outside temperature in celsius, e.g. 10. Get this from the weather API based on user location.",
                    },
                   },
                "required": ["outside_temperature"],
            },
        }
    },

]

