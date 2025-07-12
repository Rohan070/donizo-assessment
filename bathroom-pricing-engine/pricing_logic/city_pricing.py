"""
City Pricing Logic
Provides city-based multipliers for labor and materials.
"""

import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/city_multipliers.json")

_city_data = None


def _load_city_data():
    global _city_data
    if _city_data is None:
        try:
            with open(DATA_PATH, "r") as f:
                data = json.load(f)
            # Validate structure
            for city, entry in data.items():
                if (
                    not isinstance(entry, dict)
                    or "labor_multiplier" not in entry
                    or "material_multiplier" not in entry
                ):
                    print(
                        f"Warning: City '{city}' is missing required fields or is malformed."
                    )
            _city_data = data
        except Exception as e:
            print(f"Error loading city multipliers: {e}")
            _city_data = {}
    return _city_data


def get_city_labor_rate(city, base_rate):
    """
    Returns adjusted labor rate for a city.
    """
    data = _load_city_data()
    entry = data.get(city)
    if entry is None:
        print(f"Warning: City '{city}' not found in city multipliers. Using base rate.")
        return base_rate
    return base_rate * entry.get("labor_multiplier", 1.0)


def get_city_material_multiplier(city):
    """
    Returns material price multiplier for a city.
    """
    data = _load_city_data()
    entry = data.get(city)
    if entry is None:
        print(
            f"Warning: City '{city}' not found in city multipliers. Using default multiplier 1.0."
        )
        return 1.0
    return entry.get("material_multiplier", 1.0)


def print_city_multipliers():
    data = _load_city_data()
    print("Loaded city multipliers:")
    for city, entry in data.items():
        print(f"- {city}: {entry}")
