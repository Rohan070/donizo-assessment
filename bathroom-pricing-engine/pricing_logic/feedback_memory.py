"""
Feedback Memory Logic
Stores and uses user feedback to adjust future quotes.
Provides methods to add and print feedback for CLI/admin use.
"""

import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/feedback.json")


class FeedbackMemory:
    def __init__(self, data_path=DATA_PATH):
        self.data_path = data_path
        self.feedback = self.load_feedback()

    def load_feedback(self):
        try:
            with open(self.data_path, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_feedback(self):
        with open(self.data_path, "w") as f:
            json.dump(self.feedback, f, indent=2)

    def add_feedback(self, quote_id, feedback):
        self.feedback[quote_id] = feedback
        self.save_feedback()

    def adjust_confidence(self, base_confidence):
        """
        Adjusts confidence score based on feedback history.
        """
        # Example: if negative feedback exists, reduce confidence
        if any(f.get("negative", False) for f in self.feedback.values()):
            return max(0.7, base_confidence - 0.1)
        return base_confidence

    def print_feedback(self):
        print("Feedback memory:")
        if not self.feedback:
            print("(No feedback yet)")
        for quote_id, fb in self.feedback.items():
            print(f"- {quote_id}: {fb}")

    def add_feedback_cli(self):
        quote_id = input("Enter quote ID: ")
        negative = input("Was the feedback negative? (y/n): ").strip().lower() == "y"
        notes = input("Any notes? (optional): ")
        self.add_feedback(quote_id, {"negative": negative, "notes": notes})
        print("Feedback added.")
