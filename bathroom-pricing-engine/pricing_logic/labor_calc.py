"""
Labor Calculation Logic
Estimates labor time and cost for tasks, with city-based adjustments.
"""

import csv
import os
import re
from .city_pricing import get_city_labor_rate

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/price_templates.csv")


class LaborCalc:
    def __init__(self, data_path=DATA_PATH):
        self.templates = self.load_templates(data_path)

    def load_templates(self, path):
        templates = {}
        try:
            with open(path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if (
                        not row.get("task_name")
                        or not row.get("labor_hours")
                        or not row.get("base_labor_rate")
                    ):
                        print(f"Warning: Malformed labor template row: {row}")
                        continue
                    try:
                        hours = float(row["labor_hours"])
                        rate = float(row["base_labor_rate"])
                    except ValueError:
                        print(f"Warning: Invalid number in labor template row: {row}")
                        continue
                    templates[row["task_name"].strip().lower()] = {
                        "labor_hours": hours,
                        "base_labor_rate": rate,
                    }
        except Exception as e:
            print(f"Error loading labor templates: {e}")
        return templates

    def _normalize_task(self, task):
        # Remove adjectives and extra words, keep only verbs and nouns
        # Lowercase, remove 'old', 'new', etc.
        task = task.lower()
        task = re.sub(r"\bold\b|\bnew\b", "", task)
        task = re.sub(r"[^a-z\s]", "", task)
        return " ".join(task.split())

    def estimate_labor(self, task_name, city):
        # Try exact match first
        key = task_name.strip().lower()
        template = self.templates.get(key)
        # Fuzzy/partial match if not found
        if not template:
            norm_key = self._normalize_task(key)
            best_match = None
            best_score = 0
            for tname, entry in self.templates.items():
                norm_tname = self._normalize_task(tname)
                # Token overlap score
                key_tokens = set(norm_key.split())
                tname_tokens = set(norm_tname.split())
                score = len(key_tokens & tname_tokens)
                if score > best_score:
                    best_score = score
                    best_match = entry
            if best_match and best_score > 0:
                template = best_match
        if not template:
            print(f"Warning: No labor template found for task '{task_name}'.")
            return None, None
        hours = template["labor_hours"]
        base_rate = template["base_labor_rate"]
        city_rate = get_city_labor_rate(city, base_rate)
        return hours, hours * city_rate

    def print_templates(self):
        print("Loaded labor templates:")
        for name, entry in self.templates.items():
            print(f"- {name}: {entry}")
