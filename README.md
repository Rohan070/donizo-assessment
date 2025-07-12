# donizo-assessment# Donizo – Smart Bathroom Renovation Pricing Engine

## Overview
This project is a robust, modular pricing engine that generates structured, detailed quotes for full bathroom renovations from natural language transcripts. It is designed for extensibility, city-based pricing, and feedback-driven improvements.

---

## Architecture Diagram
![Functional Structure](bathroom-pricing-engine/Functional%20Structure.png)
*Functional structure of the smart pricing engine pipeline.*

---

## Features
- **Transcript Parsing:** Converts renovation requests into structured tasks.
- **Material & Labor Breakdown:** Itemized costs, time, and rates per task.
- **City-Based Pricing:** Adjusts prices for cities (e.g., Marseille vs Paris).
- **VAT & Margin Logic:** Per-task VAT and margin calculations.
- **Confidence/Error Flags:** Indicates quote reliability and issues.
- **Feedback Memory:** Learns from user feedback to improve future quotes.
- **Extensible Data:** Materials, labor, and city multipliers are data-driven.

---

## Directory Structure
```
/bathroom-pricing-engine/
├── pricing_engine.py
├── pricing_logic/
│   ├── __init__.py
│   ├── material_db.py
│   ├── labor_calc.py
│   ├── vat_rules.py
│   ├── city_pricing.py
│   └── feedback_memory.py
├── data/
│   ├── materials.json
│   ├── price_templates.csv
│   ├── city_multipliers.json
│   └── feedback.json
├── output/
│   └── sample_quote.json
├── tests/
│   └── test_logic.py
├── README.md
└── LICENSE
```

---

## How to Run
1. **Install Python 3.8+**
2. *(Optional)* Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Run the engine:**
   ```bash
   python3 pricing_engine.py --transcript "<your transcript here>" --city "Marseille"
   ```
   Output will be saved to `output/sample_quote.json`.

---

## Output JSON Schema
```json
{
  "city": "Marseille",
  "zone": "Bathroom",
  "tasks": [
    {
      "name": "Remove old tiles",
      "materials": [
        {"name": "Disposal bags", "quantity": 5, "unit_price": 2, "total": 10}
      ],
      "labor": {
        "hours": 2,
        "rate_per_hour": 40,
        "total": 80
      },
      "estimated_time_hours": 2.5,
      "vat_rate": 0.10,
      "margin": 0.15,
      "total_price": 110,
      "confidence": 0.95
    }
  ],
  "total": 1200,
  "vat_total": 120,
  "margin_total": 180,
  "confidence": 0.92,
  "error_flag": false
}
```

---

## Pricing Logic
- **Material Costs:** Loaded from `materials.json`, multiplied by quantity.
- **Labor Costs:** Estimated per task, city-adjusted rates from `city_multipliers.json`.
- **VAT:** Per-task, from `vat_rules.py`.
- **Margin:** Applied per task, logic in `pricing_engine.py`.
- **Confidence/Error:** Based on data completeness and parsing certainty.
- **Feedback:** User feedback in `feedback.json` can adjust future confidence or suggest improvements.

---

## Assumptions & Edge Cases
- Handles missing/ambiguous tasks with warnings and lower confidence.
- If city is unknown, defaults to national average rates.
- Materials/labor not found in DB are flagged in output.

---

## Bonus Features
- **City-based pricing** (dynamic multipliers)
- **Feedback memory** (learns from user feedback)
- **Supply hooks** (stub for real-time price APIs)
- **Extensible parsing** (easy to add new tasks/zones)

---

## License
MIT (see LICENSE)
