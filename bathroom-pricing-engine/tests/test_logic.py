import unittest
from pricing_logic import (
    MaterialDB,
    LaborCalc,
    get_vat_rate,
    get_city_labor_rate,
    FeedbackMemory,
)


class TestPricingLogic(unittest.TestCase):
    def setUp(self):
        self.material_db = MaterialDB()
        self.labor_calc = LaborCalc()
        self.feedback = FeedbackMemory()

    def test_material_price(self):
        self.assertEqual(self.material_db.get_price("Disposal bags"), 2)
        self.assertIsNone(self.material_db.get_price("Nonexistent"))

    def test_labor_estimate(self):
        hours, cost = self.labor_calc.estimate_labor("Remove old tiles", "Marseille")
        if hours is not None and cost is not None:
            self.assertAlmostEqual(float(hours), 2.0)
            self.assertAlmostEqual(float(cost), 80.0)
        else:
            self.fail("Labor estimate returned None")

    def test_vat_rate(self):
        self.assertEqual(get_vat_rate("Repaint walls", "Marseille"), 0.10)
        self.assertEqual(get_vat_rate("Luxury task", "Paris"), 0.20)

    def test_city_labor_rate(self):
        self.assertAlmostEqual(get_city_labor_rate("Paris", 40), 48)
        self.assertAlmostEqual(get_city_labor_rate("Marseille", 40), 40)

    def test_feedback_memory(self):
        base_conf = 0.9
        self.feedback.add_feedback("test_quote", {"negative": True})
        adj_conf = self.feedback.adjust_confidence(base_conf)
        self.assertLess(adj_conf, base_conf)


if __name__ == "__main__":
    unittest.main()
