import random
from fitness_engine.portions import estimate_portions
from fitness_engine.recipes import generate_recipe
from typing import List, Dict
from models.user_model import UserData

vegan_meals = {
    "breakfast": [
        "Oats + Soy Milk + Banana",
        "Peanut Butter Toast + Banana",
        "Tofu Scramble + Spinach",
        "Granola + Soy Yogurt + Fruit",
        "Smoothie (Banana + Oats + Soy Milk)",
        "Avocado Toast (no egg)",
        "Fruit Bowl + Granola"
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

def generate_diet(user, calories_target, macros_target) -> List[Dict]:

    meals_set = vegan_meals if user.vegan else non_vegan_meals
    plan = []

    for day in range(1, 8):
        breakfast = random.choice(meals_set["breakfast"])
        lunch = random.choice(meals_set["lunch"])
        dinner = random.choice(meals_set["dinner"])

        portions = {
            "breakfast": estimate_portions(breakfast, macros_target),
            "lunch": estimate_portions(lunch, macros_target),
            "dinner": estimate_portions(dinner, macros_target),
        }

        recipes = {
            "breakfast": [generate_recipe(p["food"], p["grams"]) for p in portions["breakfast"]],
            "lunch": [generate_recipe(p["food"], p["grams"]) for p in portions["lunch"]],
            "dinner": [generate_recipe(p["food"], p["grams"]) for p in portions["dinner"]],
        }
        
        plan.append({
            "day": day,
            "meals": {
                "breakfast": breakfast,
                "lunch": lunch,
                "dinner": dinner
            },
            "portions": portions,
            "recipes": recipes
        })

    return plan
