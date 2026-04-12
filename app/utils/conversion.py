def to_kg(quantity: float, unit: str) -> float:
    unit = unit.lower().strip()
    if unit in ("kg", "kgs", "kilogram", "kilograms"):
        return quantity
    elif unit in ("g", "gram", "grams"):
        return quantity / 1000
    elif unit in ("lb", "lbs", "pound", "pounds"):
        return quantity * 0.453592
    elif unit in ("oz", "ounce", "ounces"):
        return quantity * 0.0283495
    elif unit in ("ton", "tons", "tonne", "tonnes"):
        return quantity * 1000
    else:
        raise ValueError(f"Unknown unit: {unit}")