"""
Donizo Smart Bathroom Renovation Pricing Engine

Main entry point: Parses transcript, applies pricing logic, outputs structured JSON.
"""

import argparse
import json
import re
import spacy
import datetime
import os
from pricing_logic import (
    material_db,
    labor_calc,
    vat_rules,
    city_pricing,
    feedback_memory,
)

OUTPUT_PATH = "output/sample_quote.json"


class NLPTranscriptParser:
    """
    Uses spaCy to extract tasks, materials, quantities, and city from transcript.
    """

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.material_db = material_db.MaterialDB()
        # Expanded task templates for better coverage
        self.task_templates = [
            "remove",
            "redo",
            "replace",
            "install",
            "paint",
            "lay",
            "repaint",
        ]
        # Map task keywords to likely materials for more precise matching
        self.task_material_map = {
            "tiles": ["Ceramic tiles"],
            "floor tiles": ["Ceramic tiles"],
            "plumbing": ["Plumbing kit"],
            "toilet": ["Toilet"],
            "vanity": ["Vanity"],
            "paint": ["Paint"],
            "walls": ["Paint"],
            "floor": ["Ceramic tiles"],
        }

    def extract_room_size(self, text):
        # Look for patterns like '4m²', '4 m2', etc.
        match = re.search(r"(\d+(?:\.\d+)?)\s*(m²|m2)", text)
        if match:
            return float(match.group(1))
        return None

    def extract_city(self, text):
        # Look for 'City: <city>' or 'located in <city>' (case-insensitive)
        patterns = [
            r"city[:\s]+([A-Za-z\- ]+)[.\n]?",
            r"located in ([A-Za-z\- ]+)[.\n]?",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def get_relevant_materials(self, obj_phrase):
        # Assign only materials that match the object phrase
        relevant = set()
        obj_phrase_lower = obj_phrase.lower()
        for keyword, mats in self.task_material_map.items():
            if keyword in obj_phrase_lower:
                relevant.update(mats)
        # Fallback: match by material name in object phrase
        for mat in self.material_db.materials.keys():
            if mat.lower() in obj_phrase_lower:
                relevant.add(mat)
        return [{"name": mat} for mat in relevant]

    def parse(self, transcript):
        doc = self.nlp(transcript)
        room_size = self.extract_room_size(transcript)
        city = self.extract_city(transcript)
        tasks = []
        seen = set()  # For deduplication
        for sent in doc.sents:
            # Find all verbs in the sentence that match task_templates
            verbs = [
                token
                for token in sent
                if token.pos_ == "VERB" and token.lemma_ in self.task_templates
            ]
            for verb in verbs:
                # Find all conjuncted verbs (e.g., "remove ... and replace ...")
                verb_group = [verb]
                verb_group += [
                    child
                    for child in verb.conjuncts
                    if child.lemma_ in self.task_templates
                ]
                for v in verb_group:
                    # Find direct object(s) for each verb
                    objs = [
                        child
                        for child in v.children
                        if child.dep_ in ("dobj", "attr", "pobj")
                    ]
                    if not objs:
                        # Try to find object in the next token (for short commands)
                        next_token = v.nbor(1) if v.i + 1 < len(doc) else None
                        if next_token and next_token.pos_ in ("NOUN", "PROPN"):
                            objs = [next_token]
                    for obj in objs:
                        # Also handle conjunctions in objects (e.g., "tiles and grout")
                        obj_group = [obj]
                        obj_group += [c for c in obj.conjuncts]
                        for o in obj_group:
                            # Compose task name and deduplicate
                            task_name = f"{v.lemma_} {o.text.lower()}"
                            if task_name in seen:
                                continue
                            seen.add(task_name)
                            # Assign only relevant materials
                            materials = self.get_relevant_materials(o.text)
                            tasks.append(
                                {
                                    "name": task_name,
                                    "zone": "Bathroom",
                                    "materials": materials,
                                    "room_size_m2": room_size,
                                    "city": city,
                                }
                            )
        # Fallback: if no tasks found, treat whole transcript as one task
        if not tasks:
            tasks = [
                {
                    "name": "General renovation",
                    "zone": "Bathroom",
                    "materials": [],
                    "room_size_m2": room_size,
                    "city": city,
                }
            ]
        return tasks, room_size, city


def parse_transcript(transcript):
    """
    Parses the transcript and returns a list of tasks with details using NLP.
    """
    parser = NLPTranscriptParser()
    tasks, room_size, city = parser.parse(transcript)
    return tasks


def get_margin_for_city(city):
    # Example: higher margin for Paris, lower for Marseille, else default
    city = city.lower()
    if city == "paris":
        return 0.20
    elif city == "marseille":
        return 0.12
    else:
        return 0.15


def generate_quote(tasks, city):
    material_db_inst = material_db.MaterialDB()
    labor_calc_inst = labor_calc.LaborCalc()
    feedback_mem = feedback_memory.FeedbackMemory()
    total = 0
    vat_total = 0
    margin_total = 0
    error_flag = False
    confidences = []
    city_material_multiplier = city_pricing.get_city_material_multiplier(city)
    margin = get_margin_for_city(city)
    quote_tasks = []
    for task in tasks:
        task_confidence = 1.0
        # --- Material cost ---
        material_costs = []
        material_total = 0
        for mat in task.get("materials", []):
            mat_name = mat["name"]
            unit_price = material_db_inst.get_price(mat_name)
            unit = material_db_inst.get_unit(mat_name)
            if unit and unit in ["m2", "liter"] and task.get("room_size_m2"):
                quantity = task["room_size_m2"]
            else:
                quantity = 1
            if unit_price is None:
                error_flag = True
                task_confidence -= 0.2
                unit_price = 0
            mat_total = quantity * unit_price * city_material_multiplier
            material_costs.append(
                {
                    "name": mat_name,
                    "quantity": round(quantity, 2),
                    "unit_price": round(unit_price, 2),
                    "unit": unit,
                    "total": round(mat_total, 2),
                }
            )
            material_total += mat_total
        # --- Labor cost ---
        hours, labor_cost = labor_calc_inst.estimate_labor(task["name"], city)
        if hours is None or labor_cost is None:
            error_flag = True
            task_confidence -= 0.2
            hours = 1
            labor_cost = 0
        # --- VAT & Margin ---
        vat_rate = vat_rules.get_vat_rate(task["name"], city)
        subtotal = material_total + labor_cost
        margin_amt = subtotal * margin
        vat_amt = (subtotal + margin_amt) * vat_rate
        total_price = subtotal + margin_amt + vat_amt
        total += total_price
        vat_total += vat_amt
        margin_total += margin_amt
        confidences.append(task_confidence)
        quote_tasks.append(
            {
                "name": task["name"],
                "materials": material_costs,
                "labor": {
                    "hours": round(hours, 2),
                    "rate_per_hour": round(labor_cost / hours, 2) if hours else 0,
                    "total": round(labor_cost, 2),
                },
                "estimated_time_hours": round(hours, 2),
                "vat_rate": vat_rate,
                "margin": margin,
                "total_price": round(total_price, 2),
                "confidence": round(task_confidence, 2),
            }
        )
    avg_confidence = sum(confidences) / len(confidences) if confidences else 1.0
    avg_confidence = feedback_mem.adjust_confidence(avg_confidence)
    quote = {
        "city": city,
        "zone": "Bathroom",
        "tasks": quote_tasks,
        "total": round(total, 2),
        "vat_total": round(vat_total, 2),
        "margin_total": round(margin_total, 2),
        "confidence": round(avg_confidence, 2),
        "error_flag": error_flag,
    }
    return quote


def main():
    parser = argparse.ArgumentParser(description="Donizo Smart Bathroom Pricing Engine")
    parser.add_argument("--transcript", type=str, help="Renovation transcript")
    parser.add_argument(
        "--city",
        type=str,
        default=None,
        help="City for pricing (if not provided, will extract from transcript or default to Marseille)",
    )
    parser.add_argument(
        "--add-feedback", action="store_true", help="Add feedback interactively via CLI"
    )
    parser.add_argument(
        "--print-feedback", action="store_true", help="Print all feedback entries"
    )
    args = parser.parse_args()

    if args.add_feedback:
        feedback_memory.FeedbackMemory().add_feedback_cli()
        return
    if args.print_feedback:
        feedback_memory.FeedbackMemory().print_feedback()
        return
    if not args.transcript:
        print(
            "Error: --transcript is required unless using --add-feedback or --print-feedback."
        )
        return

    # Parse transcript and extract city if not provided
    parser_nlp = NLPTranscriptParser()
    tasks, _, extracted_city = parser_nlp.parse(args.transcript)
    city = args.city if args.city else extracted_city
    if not city:
        city = "Marseille"  # fallback default
    quote = generate_quote(tasks, city)

    # Generate unique quote ID (timestamp-based)
    quote_id = datetime.datetime.now().strftime("quote_%Y-%m-%dT%H-%M-%S")
    output_path = os.path.join("output", f"{quote_id}.json")
    with open(output_path, "w") as f:
        json.dump(quote, f, indent=2)
    print(f"Quote generated and saved to {output_path}")
    print(f"Quote ID: {quote_id} (use this for feedback)")


if __name__ == "__main__":
    main()
