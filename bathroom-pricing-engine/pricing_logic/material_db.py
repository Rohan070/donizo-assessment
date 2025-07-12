"""
Material Database Logic
Loads and provides access to material prices and details.
"""

import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/materials.json")


class MaterialDB:
    def __init__(self, data_path=DATA_PATH):
        self.materials = self.load_materials(data_path)

    def load_materials(self, path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
            # Validate structure
            for name, entry in data.items():
                if (
                    not isinstance(entry, dict)
                    or "unit" not in entry
                    or "unit_price" not in entry
                ):
                    print(
                        f"Warning: Material '{name}' is missing required fields or is malformed."
                    )
            return data
        except Exception as e:
            print(f"Error loading materials: {e}")
            return {}

    def get_price(self, material_name):
        entry = self.materials.get(material_name)
        if entry is None:
            print(f"Warning: Material '{material_name}' not found in database.")
            return None
        return entry.get("unit_price")

    def get_unit(self, material_name):
        entry = self.materials.get(material_name)
        if entry is None:
            print(f"Warning: Material '{material_name}' not found in database.")
            return None
        return entry.get("unit")

    def exists(self, material_name):
        return material_name in self.materials

    def print_materials(self):
        print("Loaded materials:")
        for name, entry in self.materials.items():
            print(f"- {name}: {entry}")
