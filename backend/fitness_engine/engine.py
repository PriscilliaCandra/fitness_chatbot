from .calories import calculate_calories
from .workouts import generate_workouts
from .diet import generate_diet
from .progress import predict_progress
from .portions import estimate_portions
from .recipes import generate_meal_recipe, generate_recipe
from .grocery import generate_grocery_list
from models.user_model import UserData
from typing import List, Dict

def generate_calories_for_user(user) -> dict:
    return calculate_calories(user)

def generate_full_plan(user: UserData, weeks_progress: int = 8) -> Dict:
    # Calculate nutrition targets
    cal_data = calculate_calories(user)
    calories_target = cal_data["calories"]
    macros_target = cal_data["macros"]
    
    # Generate workout plan
    workout_plan = generate_workouts(user)
    
    # Generate basic diet plan structure
    diet_weekly = generate_diet(user, calories_target, macros_target)
    
    # Add portions and recipes to diet plan
    diet_plan_with_recipes = add_recipes_and_portions_to_diet(
        diet_weekly, macros_target, user.goal
    )
    
    # Generate grocery list from enhanced diet plan
    grocery_list = generate_grocery_list(diet_plan_with_recipes)
    
    # Generate progress prediction
    progress_prediction = predict_progress(user, weeks=weeks_progress)
    
    return {
        "user_info": {
            "name": user.name,
            "goal": user.goal,
            "vegan": user.vegan,
            "active_level": user.active_level
        },
        "nutrition": {
            "calories_target": calories_target,
            "macros_target": macros_target
        },
        "workout_plan": workout_plan,
        "diet_plan": diet_plan_with_recipes, 
        "grocery_list": grocery_list,
        "progress_prediction": progress_prediction
    }

# def add_recipes_and_portions_to_diet(
#     diet_weekly: List[Dict], 
#     macros_target: Dict, 
#     goal: str
# ) -> List[Dict]:
    
#     enhanced_diet = []
    
#     for day in diet_weekly:
#         enhanced_day = day.copy()
#         enhanced_day["portions"] = {}
#         enhanced_day["recipes"] = {}
#         enhanced_day["meal_details"] = {}
        
#         for meal_type, meal_name in day["meals"].items():
#             # Get ingredients untuk meal ini
#             ingredients = day["ingredients"][meal_type]
            
#             # Validasi ingredients
#             if not ingredients or not isinstance(ingredients, list):
#                 print(f"Warning: No ingredients for {meal_type}: {meal_name}")
#                 ingredients = []
            
#             # Estimate portions
#             portions = estimate_portions(ingredients, macros_target, goal)
            
#             # Validasi portions
#             if not portions:
#                 print(f"Warning: No portions generated for {meal_type}: {meal_name}")
#                 portions = []
            
#             # Generate recipes
#             try:
#                 meal_recipe = generate_meal_recipe(meal_name, por)
                
#                 # Generate individual food recipes dengan validasi
#                 food_recipes = []
#                 for p in portions:
#                     if isinstance(p, dict) and "food" in p and "grams" in p:
#                         recipe = generate_recipe(p["food"], p["grams"])
#                         food_recipes.append(recipe)
                
#                 # Add to enhanced day
#                 enhanced_day["portions"][meal_type] = portions
#                 enhanced_day["recipes"][meal_type] = food_recipes
#                 enhanced_day["meal_details"][meal_type] = meal_recipe
                
#             except Exception as e:
#                 print(f"Error generating recipe for {meal_type}: {e}")
#                 # Fallback
#                 enhanced_day["portions"][meal_type] = portions
#                 enhanced_day["recipes"][meal_type] = []
#                 enhanced_day["meal_details"][meal_type] = {
#                     "meal": meal_name,
#                     "error": "Failed to generate recipe"
#                 }
        
#         enhanced_diet.append(enhanced_day)
    
#     return enhanced_diet

def add_recipes_and_portions_to_diet(
    diet_weekly: List[Dict], 
    macros_target: Dict, 
    goal: str
) -> List[Dict]:
    """Enhanced dengan validasi data dan debugging DETAIL"""
    enhanced_diet = []
    
    for day in diet_weekly:
        print(f"=== PROCESSING DAY {day['day']} ===")
        enhanced_day = day.copy()
        enhanced_day["portions"] = {}
        enhanced_day["recipes"] = {}
        enhanced_day["meal_details"] = {}
        
        for meal_type, meal_name in day["meals"].items():
            print(f"🔍 Processing {meal_type}")
            print(f"   Meal name: '{meal_name}'")
            print(f"   Meal name type: {type(meal_name)}")
            
            # ✅ DEBUG: Check apa yang ada di day
            print(f"   Day keys: {list(day.keys())}")
            
            # ✅ PASTIKAN ambil dari ingredients
            ingredients = day.get("ingredients", {}).get(meal_type, [])
            print(f"   Ingredients: {ingredients}")
            print(f"   Ingredients type: {type(ingredients)}")
            
            # Validasi CRITICAL
            if not ingredients:
                print(f"   ❌ CRITICAL: No ingredients for {meal_type}")
                ingredients = []
            elif not isinstance(ingredients, list):
                print(f"   ❌ CRITICAL: Ingredients is not a list: {type(ingredients)}")
                ingredients = []
            elif ingredients and isinstance(ingredients[0], str) and len(ingredients[0]) == 1:
                print(f"   ❌ CRITICAL: Ingredients are single characters!")
                ingredients = []
            
            # DEBUG sebelum panggil estimate_portions
            print(f"   📤 Calling estimate_portions with:")
            print(f"      - ingredients: {ingredients}")
            print(f"      - ingredients count: {len(ingredients)}")
            print(f"      - first ingredient: {ingredients[0] if ingredients else 'None'}")
            
            # Estimate portions
            portions = estimate_portions(
                ingredients=ingredients,
                macros_target=macros_target,
                goal=goal
            )
            
            print(f"   📥 estimate_portions returned:")
            print(f"      - portions: {portions}")
            print(f"      - portions count: {len(portions)}")
            if portions:
                print(f"      - first portion: {portions[0]}")
            
            # Rest of recipe generation...
            try:
                meal_recipe = generate_meal_recipe(meal_name, portions)
                food_recipes = []
                for p in portions:
                    if isinstance(p, dict) and "food" in p and "grams" in p:
                        recipe = generate_recipe(p["food"], p["grams"])
                        food_recipes.append(recipe)
                
                enhanced_day["portions"][meal_type] = portions
                enhanced_day["recipes"][meal_type] = food_recipes
                enhanced_day["meal_details"][meal_type] = meal_recipe
                
            except Exception as e:
                print(f"   ❌ Error in recipe generation: {e}")
                enhanced_day["portions"][meal_type] = portions
                enhanced_day["recipes"][meal_type] = []
        
        enhanced_diet.append(enhanced_day)
        print(f"=== FINISHED DAY {day['day']} ===\n")
    
    return enhanced_diet

def generate_meal_plan_only(user: UserData) -> Dict:
    cal_data = calculate_calories(user)
    calories_target = cal_data["calories"]
    macros_target = cal_data["macros"]
    
    diet_weekly = generate_diet(user, calories_target, macros_target)
    diet_with_recipes = add_recipes_and_portions_to_diet(
        diet_weekly, macros_target, user.goal
    )
    
    grocery_list = generate_grocery_list(diet_with_recipes)
    
    return {
        "nutrition": {
            "calories_target": calories_target,
            "macros_target": macros_target
        },
        "meal_plan": diet_with_recipes,
        "grocery_list": grocery_list
    }

def generate_workout_plan_only(user: UserData) -> Dict:
    """
    Generate only workout plan
    Useful for chatbot responses about exercise only
    """
    workouts = generate_workouts(user)
    progress = predict_progress(user, weeks=4)  
    
    return {
        "workout_plan": workouts,
        "progress_prediction": progress
    }

# Utility functions for specific recipe needs (for chatbot commands)
def get_recipe_for_meal(meal_name: str, portions: List[Dict]) -> Dict:
    return generate_meal_recipe(meal_name, portions)

def get_food_recipe(food: str, grams: int = 100) -> Dict:
    return generate_recipe(food, grams)

def estimate_meal_cost(meal_name: str, portions: List[Dict]) -> Dict:
    from .recipes import get_total_cost, get_ingredient_cost_breakdown
    
    total_cost = get_total_cost(meal_name, portions)
    cost_breakdown = get_ingredient_cost_breakdown(meal_name, portions)
    
    return {
        "meal": meal_name,
        "estimated_cost": total_cost,
        "cost_breakdown": cost_breakdown
    }