from collections import defaultdict
from models.user_model import UserData

def generate_grocery_list(weekly_plan):

    grocery = defaultdict(int)

    for day in weekly_plan:
        for meal in ["breakfast", "lunch", "dinner"]:
            for item in day["portions"][meal]:
                food = item["food"]
                grams = item["grams"]
                grocery[food] += grams

    output = []
    for food, grams in grocery.items():
        output.append({
            "item": food,
            "total_grams": grams,
            "total_kg": round(grams / 1000, 2)
        })

    return output
