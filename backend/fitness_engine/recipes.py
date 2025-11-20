recipe_db = {
    "rice": {
        "method": "Rebus beras dengan air perbandingan 1:1.5 selama 15 menit.",
        "cost_per_100g": 1500
    },
    "chicken_breast": {
        "method": "Bumbui garam & lada, pan-fry 8 menit tiap sisi.",
        "cost_per_100g": 6000
    },
    "egg": {
        "method": "Rebus 7–9 menit atau orak-arik di teflon.",
        "cost_per_100g": 2500
    },
    "oats": {
        "method": "Rebus oats dengan air/promo susu murah 5 menit.",
        "cost_per_100g": 3000
    },
    "vegetables": {
        "method": "Tumis dengan sedikit minyak / rebus 3 menit.",
        "cost_per_100g": 2000
    },
    "tofu": {
        "method": "Potong, goreng/air-fry 6 menit atau tumis.",
        "cost_per_100g": 2500
    },
    "tempeh": {
        "method": "Goreng, panggang, atau tumis dengan kecap.",
        "cost_per_100g": 3000
    },
}

def generate_recipe(food: str, grams: int):
    data = recipe_db.get(food)
    if not data:
        return None

    cost = round((grams / 100) * data["cost_per_100g"])

    return {
        "food": food,
        "grams": grams,
        "cooking_method": data["method"],
        "estimated_cost": cost
    }
