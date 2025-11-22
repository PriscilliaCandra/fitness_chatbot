import random
from typing import List, Dict
from fitness_engine.portions import estimate_portions
from fitness_engine.recipes import generate_recipe
from models.user_model import UserData

meal_to_ingredients = {
    # -------------------------------
    # Vegan Breakfast
    # -------------------------------
    "Oats + Soy Milk + Banana": ["oats", "soy_milk", "banana", "sugar"],
    "Peanut Butter Toast + Banana": ["bread", "peanut_butter", "banana"],
    "Tofu Scramble + Spinach": ["tofu", "spinach", "onion", "garlic", "cooking_oil", "salt", "pepper"],
    "Soy Yogurt + Fruit + Bread": ["soy_milk", "banana", "oats", "bread"],
    "Smoothie (Banana + Oats + Soy Milk)": ["banana", "oats", "soy_milk"],
    "Toast (no egg)": ["bread", "vegetable_mix", "olive_oil", "salt", "pepper"],
    "Fruit Bowl + Oat": ["banana", "oats"],

    # -------------------------------
    # Vegan Lunch
    # -------------------------------
    "Tempe Stir Fry + Rice": ["tempeh", "rice", "vegetable_mix", "garlic", "onion", "sweet_soy_sauce", "cooking_oil", "salt", "pepper"],
    "Lentil Soup + Bread": ["lentil", "vegetable_mix", "onion", "garlic", "cooking_oil", "salt", "pepper", "bread"],
    "Vegan Fried Rice (Tempe + Veggies)": ["rice", "tempeh", "vegetable_mix", "garlic", "onion", "sweet_soy_sauce", "cooking_oil", "salt", "pepper"],
    "Tofu Curry + Rice": ["tofu", "rice", "coconut_milk", "onion", "garlic", "curry_powder", "vegetable_mix", "cooking_oil", "salt", "pepper"],
    "Chickpea Stir Fry + Rice": ["chickpea", "rice", "vegetable_mix", "garlic", "onion", "cooking_oil", "salt", "pepper", "soy_sauce"],
    "Stir Fried Noodles + Veggies (no egg)": ["pasta", "vegetable_mix", "garlic", "onion", "cooking_oil", "soy_sauce", "salt", "pepper"],
    "Tofu Teriyaki + Rice": ["tofu", "rice", "vegetable_mix", "soy_sauce", "cooking_oil", "sugar", "garlic", "salt"],

    # -------------------------------
    # Vegan Dinner
    # -------------------------------
    "Chickpea Veggie Bowl": ["chickpea", "vegetable_mix", "garlic", "onion", "cooking_oil", "salt", "pepper"],
    "Tofu + Broccoli + Rice": ["tofu", "rice", "broccoli", "garlic", "onion", "cooking_oil", "salt", "pepper", "soy_sauce"],
    "Vegan Noodle Soup": ["pasta", "vegetable_mix", "garlic", "onion", "cooking_oil", "salt", "pepper", "soy_sauce"],
    "Veggie Stir Fry + Rice": ["vegetable_mix", "rice", "garlic", "onion", "cooking_oil", "soy_sauce", "salt", "pepper"],
    "Tempe + Mixed Vegetables + Rice": ["tempeh", "rice", "vegetable_mix", "garlic", "onion", "cooking_oil", "soy_sauce", "salt", "pepper"],
    "Tofu Sambal + Rice": ["tofu", "rice", "chili_sauce", "garlic", "onion", "cooking_oil", "salt"],
    "Vegetable Curry + Rice": ["vegetable_mix", "rice", "coconut_milk", "onion", "garlic", "curry_powder", "cooking_oil", "salt", "pepper"],

    # -------------------------------
    # Non-Vegan Breakfast
    # -------------------------------
    "Oatmeal + 2 Eggs": ["oats", "egg", "milk", "salt"],
    "Egg Sandwich": ["egg", "bread", "butter", "salt", "pepper"],
    "Yogurt + Banana + Granola": ["banana", "oats", "yogurt"],
    "Peanut Butter Toast": ["bread", "peanut_butter"],
    "Fried Rice + Egg": ["rice", "egg", "vegetable_mix", "garlic", "onion", "cooking_oil", "salt", "pepper"],
    "Chicken Porridge": ["rice", "chicken_breast", "salt", "pepper"],
    "Banana + Yogurt + Granola": ["banana", "yogurt", "oats"],

    # -------------------------------
    # Non-Vegan Lunch
    # -------------------------------
    "Chicken Breast + Rice + Veggies": ["chicken_breast", "rice", "vegetable_mix", "garlic", "onion", "cooking_oil", "salt", "pepper", "soy_sauce"],
    "Egg Fried Rice + Veggies": ["rice", "egg", "vegetable_mix", "garlic", "onion", "cooking_oil", "salt", "pepper", "soy_sauce"],
    "Tuna + Rice + Veggies": ["tuna", "rice", "vegetable_mix", "garlic", "onion", "cooking_oil", "salt", "pepper", "soy_sauce"],
    "Tempe + Rice + Sayur": ["tempeh", "rice", "vegetable_mix", "garlic", "onion", "cooking_oil", "sweet_soy_sauce", "salt", "pepper"],
    "Ayam Kecap + Rice": ["chicken_breast", "rice", "onion", "garlic", "sweet_soy_sauce", "cooking_oil", "salt", "pepper"],
    "Chicken Stir Fry + Rice": ["chicken_breast", "rice", "vegetable_mix", "garlic", "onion", "soy_sauce", "cooking_oil", "salt", "pepper"],
    "Noodle Soup + Egg + Veggies": ["pasta", "egg", "vegetable_mix", "onion", "garlic", "cooking_oil", "salt", "pepper", "soy_sauce"],

    # -------------------------------
    # Non-Vegan Dinner
    # -------------------------------
    "Chicken Soup + Rice": ["chicken_breast", "rice", "vegetable_mix", "onion", "garlic", "salt", "pepper", "cooking_oil"],
    "Tahu + Sayur + Rice": ["tofu", "rice", "vegetable_mix", "garlic", "onion", "soy_sauce", "cooking_oil", "salt", "pepper"],
    "Fried Rice + Egg + Veggies": ["rice", "egg", "vegetable_mix", "garlic", "onion", "cooking_oil", "soy_sauce", "salt", "pepper"],
    "Nasi Goreng Ayam (light oil)": ["rice", "chicken_breast", "vegetable_mix", "garlic", "onion", "cooking_oil", "soy_sauce", "salt", "pepper"],
    "Instant Noodles + Egg + Veggies": ["pasta", "egg", "vegetable_mix", "garlic", "onion", "salt", "pepper", "cooking_oil", "soy_sauce"],
    "Tuna + Stir Fry Veggies": ["tuna", "vegetable_mix", "garlic", "onion", "cooking_oil", "soy_sauce", "salt", "pepper"],
    "Chicken Teriyaki + Rice": ["chicken_breast", "rice", "vegetable_mix", "soy_sauce", "sugar", "garlic", "cooking_oil", "salt", "pepper"]
}

vegan_meals = {
    "breakfast": [
        "Oats + Soy Milk + Banana",
        "Peanut Butter Toast + Banana",
        "Tofu Scramble + Spinach",
        "Soy Yogurt + Fruit + Bread",
        "Smoothie (Banana + Oats + Soy Milk)",
        "Avocado Toast (no egg)",
        "Fruit Bowl + Oat"
    ],
    "lunch": [
        "Tempe Stir Fry + Rice",
        "Lentil Soup + Bread",
        "Vegan Fried Rice (Tempe + Veggies)",
        "Tofu Curry + Rice",
        "Chickpea Stir Fry + Rice",
        "Stir Fried Noodles + Veggies (no egg)",
        "Tofu Teriyaki + Rice"
    ],
    "dinner": [
        "Chickpea Veggie Bowl",
        "Tofu + Broccoli + Rice",
        "Vegan Noodle Soup",
        "Veggie Stir Fry + Rice",
        "Tempe + Mixed Vegetables + Rice",
        "Tofu Sambal + Rice",
        "Vegetable Curry + Rice"
    ]
}

non_vegan_meals = {
    "breakfast": [
        "Oatmeal + 2 Eggs",
        "Egg Sandwich",
        "Yogurt + Banana + Granola",
        "Peanut Butter Toast",
        "Fried Rice + Egg",
        "Chicken Porridge",
        "Banana + Yogurt + Granola"
    ],
    "lunch": [
        "Chicken Breast + Rice + Veggies",
        "Egg Fried Rice + Veggies",
        "Tuna + Rice + Veggies",
        "Tempe + Rice + Sayur",
        "Ayam Kecap + Rice",
        "Chicken Stir Fry + Rice",
        "Noodle Soup + Egg + Veggies"
    ],
    "dinner": [
        "Chicken Soup + Rice",
        "Tahu + Sayur + Rice",
        "Fried Rice + Egg + Veggies",
        "Nasi Goreng Ayam (light oil)",
        "Instant Noodles + Egg + Veggies",
        "Tuna + Stir Fry Veggies",
        "Chicken Teriyaki + Rice"
    ]
}

def generate_diet(user: UserData, calories_target, macros_target) -> List[Dict]:

    meals_set = vegan_meals if user.vegan else non_vegan_meals
    plan = []
    used_meals = {"breakfast": [], "lunch": [], "dinner": []}

    for day in range(1, 8):
        available_breakfast = [m for m in meals_set["breakfast"] if m not in used_meals["breakfast"][-2:]]
        available_lunch = [m for m in meals_set["lunch"] if m not in used_meals["lunch"][-2:]]
        available_dinner = [m for m in meals_set["dinner"] if m not in used_meals["dinner"][-2:]]
        
        breakfast = random.choice(available_breakfast or meals_set["breakfast"])
        lunch = random.choice(available_lunch or meals_set["lunch"])
        dinner = random.choice(available_dinner or meals_set["dinner"])

        plan.append({
            "day": day,
            "meals": {
                "breakfast": breakfast,
                "lunch": lunch,
                "dinner": dinner
            },
            "ingredients": {
                "breakfast": meal_to_ingredients.get(breakfast, []),
                "lunch": meal_to_ingredients.get(lunch, []),
                "dinner": meal_to_ingredients.get(dinner, [])
            }
        })

    return plan
