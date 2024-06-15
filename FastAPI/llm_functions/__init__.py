from .automation import function_schemas as automation_function_schemas, function_names as automation_function_names
from .carbon import function_schemas as carbon_function_schemas, function_names as carbon_function_names
from .pollution import function_schemas as pollution_function_schemas, function_names as pollution_function_names
from .pump import function_schemas as pump_function_schemas, function_names as pump_function_names
from .tariff import function_schemas as tariff_function_schemas, function_names as tariff_function_names
from .weather import function_schemas as weather_function_schemas, function_names as weather_function_names


function_schemas = automation_function_schemas + carbon_function_schemas  + pollution_function_schemas + pump_function_schemas + tariff_function_schemas + weather_function_schemas
function_names = automation_function_names | carbon_function_names | pollution_function_names | pump_function_names | tariff_function_names | weather_function_names


def call_function(name: str, args: dict=None) -> str:
    print(f"\nCalled Function {name} with args: {args}")
    try:
        function = function_names.get(name)
        # Unpacking the dictionary of arguments into kwargs:
        if args:
            result = function(args)
        else:
            result = function()
            
        print(f"Function {name} returned: {result}\n")
        return f"{result}"
    
    except Exception as e:
        print(f"Error during function call: {e}")
        return f"Function {name} failed with error: {e}"
    

# Specifying the list of module-level names that should be exported when from module import * is used:
__all__ = ["function_schemas", "call_function"]
