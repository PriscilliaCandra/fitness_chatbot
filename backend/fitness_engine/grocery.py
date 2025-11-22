# from collections import defaultdict
# from typing import List, Dict

# INGREDIENT_ALIAS = {
#     "vegetables": "vegetable mix",
#     "vegetable mix": "vegetable mix", 
#     "milk": "soy_milk",
#     "coconut_milk": "coconut_milk"
# }

# def generate_grocery_list(weekly_plan: List[Dict]) -> List[Dict]:
#     grocery = defaultdict(float)

#     for day in weekly_plan:
#         for meal_type in ["breakfast", "lunch", "dinner"]:
#             # Gunakan portions jika ada, fallback ke ingredients
#             portions = day.get("portions", {}).get(meal_type, [])
            
#             if portions and isinstance(portions, list) and len(portions) > 0:
#                 # Validasi structure portions
#                 for portion in portions:
#                     if isinstance(portion, dict) and "food" in portion and "grams" in portion:
#                         food = INGREDIENT_ALIAS.get(portion["food"], portion["food"])
#                         grams = portion["grams"]
#                         if isinstance(grams, (int, float)) and grams > 0:
#                             grocery[food] += grams
#             else:
#                 # Fallback ke ingredients
#                 ingredients = day.get("ingredients", {}).get(meal_type, [])
#                 for food in ingredients:
#                     if isinstance(food, str):
#                         food_key = INGREDIENT_ALIAS.get(food, food)
#                         estimated_grams = {
#                             "breakfast": 80,
#                             "lunch": 120, 
#                             "dinner": 100
#                         }.get(meal_type, 100)
#                         grocery[food_key] += estimated_grams

#     # Convert to final output structure
#     output = []
#     for food, grams in grocery.items():
#         # Skip items dengan grams 0 atau invalid
#         if grams > 0:
#             output.append({
#                 "item": food,
#                 "total_grams": round(grams, 1),
#                 "total_kg": round(grams / 1000, 2)
#             })
    
#     # Sort by item name
#     output.sort(key=lambda x: x["item"])
    
#     return output

from collections import defaultdict
from typing import List, Dict

# Tambahkan harga per 100g untuk setiap bahan
COST_PER_100G = {
    # Proteins
    "chicken_breast": 6000,
    "egg": 2500,
    "tofu": 2500,
    "tempeh": 3000,
    "tuna": 8500,
    "chickpea": 7000,
    "lentil": 6000,
    
    # Carbs
    "rice": 1500,
    "oats": 3000,
    "pasta": 3000,
    "bread": 2000,
    
    # Vegetables
    "vegetable mix": 2000,
    "spinach": 4000,
    "broccoli": 8000,
    
    # Dairy & Alternatives
    "soy_milk": 2000,
    "yogurt": 8000,
    "milk": 7000,
    
    # Seasonings
    "sugar": 1200,
    "salt": 500,
    "pepper": 8000,
    "cooking_oil": 12000,
    "olive_oil": 26000,
    "soy_sauce": 8000,
    "sweet_soy_sauce": 7000,
    "chili_sauce": 6000,
    "curry_powder": 10000,
    "coconut_milk": 5000,
    "butter": 18000,
    "margarine": 10000,
    "peanut_butter": 15000,
    
    # Aromatics
    "onion": 3000,
    "garlic": 4000,
}

INGREDIENT_ALIAS = {
    "vegetables": "vegetable mix",
    "vegetable mix": "vegetable mix", 
    "milk": "soy_milk",
    "coconut_milk": "coconut_milk"
}

def get_cost_per_100g(food: str) -> int:
    """Get cost per 100g for a food item, with fallback"""
    food_key = INGREDIENT_ALIAS.get(food, food)
    return COST_PER_100G.get(food_key, 3000)  # Default 3000 jika tidak ditemukan

def generate_grocery_list(weekly_plan: List[Dict]) -> List[Dict]:
    grocery = defaultdict(float)

    for day in weekly_plan:
        for meal_type in ["breakfast", "lunch", "dinner"]:
            # Gunakan portions jika ada, fallback ke ingredients
            portions = day.get("portions", {}).get(meal_type, [])
            
            if portions and isinstance(portions, list) and len(portions) > 0:
                # Validasi structure portions
                for portion in portions:
                    if isinstance(portion, dict) and "food" in portion and "grams" in portion:
                        food = INGREDIENT_ALIAS.get(portion["food"], portion["food"])
                        grams = portion["grams"]
                        if isinstance(grams, (int, float)) and grams > 0:
                            grocery[food] += grams
            else:
                # Fallback ke ingredients
                ingredients = day.get("ingredients", {}).get(meal_type, [])
                for food in ingredients:
                    if isinstance(food, str):
                        food_key = INGREDIENT_ALIAS.get(food, food)
                        estimated_grams = {
                            "breakfast": 80,
                            "lunch": 120, 
                            "dinner": 100
                        }.get(meal_type, 100)
                        grocery[food_key] += estimated_grams

    # Convert to final output structure dengan TOTAL COST
    output = []
    total_weekly_cost = 0
    
    for food, grams in grocery.items():
        # Skip items dengan grams 0 atau invalid
        if grams > 0:
            cost_per_100g = get_cost_per_100g(food)
            total_cost = (grams / 100) * cost_per_100g
            
            output.append({
                "item": food,
                "total_grams": round(grams, 1),
                "total_cost": round(total_cost)  # Total cost untuk item ini
            })
            
            total_weekly_cost += total_cost
    
    # Sort by item name
    output.sort(key=lambda x: x["item"])
    
    # Tambahkan summary total weekly cost
    output.append({
        "item": "TOTAL WEEKLY COST",
        "total_grams": round(sum(item["total_grams"] for item in output if item["item"] != "TOTAL WEEKLY COST"), 1),
        "total_cost": round(total_weekly_cost)
    })
    
    return output