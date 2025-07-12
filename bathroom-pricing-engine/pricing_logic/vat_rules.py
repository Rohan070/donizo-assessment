"""
VAT Rules Logic
Provides VAT rates based on task or city.
"""


def get_vat_rate(task_name, city):
    """
    Returns VAT rate for a given task and city.
    TODO: Make this data-driven if needed.
    """
    # Example: 10% for renovation, 20% for luxury tasks
    if "paint" in task_name.lower() or "tile" in task_name.lower():
        return 0.10
    if city.lower() == "paris":
        return 0.20
    return 0.10
