# from typing import List, Dict

# # Per 100 gram
# NUTRITION_DB = {
#     "chicken_breast": {"protein": 31, "carbs": 0, "fat": 3.6},
#     "egg": {"protein": 13, "carbs": 1, "fat": 11},
#     "tofu": {"protein": 8, "carbs": 2, "fat": 4},
#     "tempeh": {"protein": 19, "carbs": 12, "fat": 11},
#     "rice": {"protein": 2.7, "carbs": 28, "fat": 0.3},
#     "oats": {"protein": 17, "carbs": 66, "fat": 7},
#     "banana": {"protein": 1.1, "carbs": 23, "fat": 0.3},
#     "pasta": {"protein": 13, "carbs": 75, "fat": 1.5},
#     "vegetable_mix": {"protein": 2, "carbs": 8, "fat": 0.2},
#     "bread": {"protein": 8, "carbs": 49, "fat": 4},
#     "chickpea": {"protein": 19, "carbs": 61, "fat": 6},    
#     "spinach": {"protein": 2.9, "carbs": 3.6, "fat": 0.4},
#     "lentil": {"protein": 9, "carbs": 20, "fat": 0.4},   
#     "broccoli": {"protein": 2.8, "carbs": 7, "fat": 0.4},
#     "tuna": {"protein": 29, "carbs": 0, "fat": 0.8},     
#     "soy_milk": {"protein": 3.3, "carbs": 6, "fat": 1.8},
#     "peanut_butter": {"protein": 25, "carbs": 20, "fat": 50},
#     "sugar": {"protein": 0, "carbs": 100, "fat": 0},
#     "cooking_oil": {"protein": 0, "carbs": 0, "fat": 100},
#     "olive_oil": {"protein": 0, "carbs": 0, "fat": 100},
#     "salt": {"protein": 0, "carbs": 0, "fat": 0},
#     "pepper": {"protein": 0, "carbs": 0, "fat": 0},
#     "soy_sauce": {"protein": 8, "carbs": 4, "fat": 0},
#     "sweet_soy_sauce": {"protein": 4, "carbs": 45, "fat": 0},
#     "chili_sauce": {"protein": 2, "carbs": 25, "fat": 0},
#     "curry_powder": {"protein": 14, "carbs": 58, "fat": 14},
#     "coconut_milk": {"protein": 2, "carbs": 6, "fat": 24},
#     "butter": {"protein": 1, "carbs": 0, "fat": 81},
#     "margarine": {"protein": 0, "carbs": 0, "fat": 80},
#     "yogurt": {"protein": 3.5, "carbs": 5, "fat": 3.5},
#     "milk": {"protein": 3.4, "carbs": 5, "fat": 3.6}, 
# }

# # fallback untuk ingredient yang tidak ditemukan
# DEFAULT_MACROS = {"protein": 5, "carbs": 10, "fat": 1}

# INGREDIENT_ALIAS = {
#     "vegetable mix": "vegetable_mix",
#     "vegetables": "vegetable_mix",
#     "milk": "soy_milk", 
# }

# def estimate_portions(ingredients: List[str], macros_target: Dict,goal: str = "maintain") -> List[Dict]:

#     if not ingredients:
#         return []
    
#     normalized_ingredients = []
    
#     for ing in ingredients:
#         normalized = INGREDIENT_ALIAS.get(ing, ing)
#         normalized_ingredients.append(normalized)

#     # Faktor skala goal
#     goal_scale = {
#         "muscle_gain": 1.15,
#         "maintain": 1.0,
#         "fat_loss": 0.85
#     }.get(goal, 1.0)

#     total_calories_need = (macros_target["protein"] * 4 + 
#                           macros_target["carbs"] * 4 + 
#                           macros_target["fat"] * 9) * goal_scale

#     # Bagi calories per meal (3 meals per day)
#     meal_calories = total_calories_need / 3

#     result = []
    
#     for food in normalized_ingredients:
#         macros = NUTRITION_DB.get(food, DEFAULT_MACROS)
        
#         # Hitung calories per 100g
#         calories_per_100g = (macros["protein"] * 4 + macros["carbs"] * 4 + macros["fat"] * 9)
        
#         if calories_per_100g > 0:
#             # Distribusikan calories berdasarkan jenis makanan
#             if macros["protein"] > 10:  # Protein sources
#                 grams = (meal_calories * 0.35) / calories_per_100g * 100
#             elif macros["carbs"] > 20:  # Carb sources  
#                 grams = (meal_calories * 0.50) / calories_per_100g * 100
#             elif macros["fat"] > 10:    # Fat sources
#                 grams = (meal_calories * 0.15) / calories_per_100g * 100
#             else:                       # Vegetables/seasonings
#                 grams = 30  # Fixed small amount for seasonings
#         else:
#             grams = 30
            
#         if food in ["salt", "pepper", "sugar"]:
#             grams = max(1, min(grams, 10))
#         elif food in ["cooking_oil", "olive_oil", "butter"]:
#             grams = max(5, min(grams, 30))
#         elif any(seasoning in food for seasoning in ["_sauce", "powder"]):
#             grams = max(5, min(grams, 50))
#         else:
#             grams = max(30, min(grams, 300))
            
#         display_name = food.replace("_", " ")
        
#         result.append({
#             "food": display_name,
#             "grams": round(grams, 1),
#             "macros_per_100g": macros
#         })

#     return result

# from typing import List, Dict

# def estimate_portions(ingredients: List[str], macros_target: Dict, goal: str = "maintain") -> List[Dict]:
#     """
#     SIMPLE FIXED VERSION - Hanya menerima list ingredients yang valid
#     Tidak akan pernah memproses single characters
#     """
#     print(f"🎯 estimate_portions CALLED with:")
#     print(f"   - ingredients: {ingredients}")
#     print(f"   - ingredients type: {type(ingredients)}")
#     print(f"   - ingredients length: {len(ingredients) if ingredients else 0}")
    
#     # CRITICAL VALIDATION
#     if not ingredients:
#         print("   ❌ No ingredients provided")
#         return []
    
#     if not isinstance(ingredients, list):
#         print(f"   ❌ Ingredients is not a list: {type(ingredients)}")
#         return []
    
#     # FILTER OUT SINGLE CHARACTERS AND INVALID DATA
#     valid_ingredients = []
#     for i, ing in enumerate(ingredients):
#         if isinstance(ing, str) and len(ing) > 1:
#             valid_ingredients.append(ing)
#             print(f"   ✅ Valid ingredient {i}: '{ing}'")
#         else:
#             print(f"   ❌ INVALID ingredient {i}: '{ing}' (type: {type(ing)}, length: {len(ing) if isinstance(ing, str) else 'N/A'})")
    
#     if not valid_ingredients:
#         print("   ❌ No valid ingredients after filtering")
#         return []
    
#     print(f"   🎯 Final valid ingredients: {valid_ingredients}")
    
#     # SIMPLE FIXED PORTION SIZES
#     portion_sizes = {
#         # Proteins
#         "chicken_breast": 150, "egg": 100, "tofu": 150, "tempeh": 150, 
#         "tuna": 150, "chickpea": 120, "lentil": 120,
#         # Carbs
#         "rice": 150, "oats": 50, "pasta": 100, "bread": 50,
#         # Vegetables
#         "vegetable_mix": 100, "vegetable mix": 100, "spinach": 50, "broccoli": 80,
#         # Dairy & Alternatives
#         "soy_milk": 200, "yogurt": 100, "milk": 200,
#         # Seasonings
#         "sugar": 5, "salt": 2, "pepper": 1, "cooking_oil": 10, 
#         "olive_oil": 10, "soy_sauce": 10, "sweet_soy_sauce": 10,
#         "chili_sauce": 10, "curry_powder": 5, "coconut_milk": 100,
#         "butter": 5, "margarine": 5, "peanut_butter": 20,
#         # Aromatics
#         "onion": 20, "garlic": 10
#     }
    
#     result = []
#     for ingredient in valid_ingredients:
#         # Normalize ingredient name (replace space with underscore for lookup)
#         lookup_key = ingredient.replace(" ", "_")
#         grams = portion_sizes.get(lookup_key, portion_sizes.get(ingredient, 100))
        
#         result.append({
#             "food": ingredient,  # Keep original name for display
#             "grams": grams
#         })
#         print(f"   ➕ Portion: '{ingredient}' -> {grams}g")
    
#     print(f"   ✅ Final portions: {len(result)} items")
#     return result

from typing import List, Dict

def estimate_portions(ingredients: List[str], macros_target: Dict, goal: str = "maintain") -> List[Dict]:
    """
    ENHANCED SIMPLE VERSION - Dengan adjustment berdasarkan goal
    """
    if not ingredients or not isinstance(ingredients, list):
        return []
    
    # Filter valid ingredients
    valid_ingredients = []
    for ing in ingredients:
        if isinstance(ing, str) and len(ing) > 1:
            valid_ingredients.append(ing)
    
    if not valid_ingredients:
        return []
    
    # Base portion sizes
    portion_sizes = {
        # Proteins
        "chicken_breast": 150, "egg": 100, "tofu": 150, "tempeh": 150, 
        "tuna": 150, "chickpea": 120, "lentil": 120,
        # Carbs
        "rice": 150, "oats": 50, "pasta": 100, "bread": 50,
        # Vegetables
        "vegetable_mix": 100, "vegetable mix": 100, "spinach": 50, "broccoli": 80,
        # Dairy & Alternatives
        "soy_milk": 200, "yogurt": 100, "milk": 200,
        # Seasonings
        "sugar": 5, "salt": 2, "pepper": 1, "cooking_oil": 10, 
        "olive_oil": 10, "soy_sauce": 10, "sweet_soy_sauce": 10,
        "chili_sauce": 10, "curry_powder": 5, "coconut_milk": 100,
        "butter": 5, "margarine": 5, "peanut_butter": 20,
        # Aromatics
        "onion": 20, "garlic": 10
    }
    
    # Adjust based on goal
    goal_multiplier = {
        "muscle_gain": 1.2,
        "fat_loss": 0.8, 
        "maintain": 1.0
    }.get(goal, 1.0)
    
    result = []
    for ingredient in valid_ingredients:
        lookup_key = ingredient.replace(" ", "_")
        base_grams = portion_sizes.get(lookup_key, portion_sizes.get(ingredient, 100))
        
        # Apply goal adjustment (except for seasonings)
        if ingredient not in ["salt", "pepper", "sugar", "cooking_oil", "olive_oil"]:
            adjusted_grams = base_grams * goal_multiplier
        else:
            adjusted_grams = base_grams
            
        result.append({
            "food": ingredient,
            "grams": round(adjusted_grams)
        })
    
    return result