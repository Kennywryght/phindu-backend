def to_kg(quantity, unit):
    if unit == "g":
        return quantity / 1000
    if unit == "kg":
        return quantity
    return quantity  # fallback