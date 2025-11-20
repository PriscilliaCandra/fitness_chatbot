food_db = {
    "rice": {"carbs": 28, "protein": 2, "fat": 0},
    "chicken_breast": {"carbs": 0, "protein": 31, "fat": 3},
    "egg": {"carbs": 0.6, "protein": 6, "fat": 5},
    "tofu": {"carbs": 2, "protein": 8, "fat": 4},
    "tempeh": {"carbs": 9, "protein": 19, "fat": 11},
    "oats": {"carbs": 66, "protein": 17, "fat": 7},
    "banana": {"carbs": 23, "protein": 1, "fat": 0},
    "vegetables": {"carbs": 5, "protein": 2, "fat": 0},
    "potato": {"carbs": 17, "protein": 2, "fat": 0},
    "pasta": {"carbs": 25, "protein": 5, "fat": 1}
}

def estimate_portions(meal: list, macros_target: dict):

    protein_need = macros_target["protein_g"] / 3
    carb_need = macros_target["carbs_g"] / 3
    fat_need = macros_target["fat_g"] / 3

    portions = []

    for food in meal:
        food = food.lower()

        if "nasi" in food:
            portions.append({"food": "rice", "grams": round((carb_need / 28) * 100)})
        if "ayam" in food:
            portions.append({"food": "chicken_breast", "grams": round((protein_need / 31) * 100)})
        if "oat" in food:
            portions.append({"food": "oats", "grams": round((carb_need / 66) * 100)})
        if "telur" in food:
            portions.append({"food": "egg", "grams": 100})
        if "tahu" in food:
            portions.append({"food": "tofu", "grams": 150})
        if "tempe" in food:
            portions.append({"food": "tempeh", "grams": 120})
        if "sayur" in food:
            portions.append({"food": "vegetables", "grams": 100})

    return portions
