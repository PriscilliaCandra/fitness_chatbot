from .calories import calculate_calories
from .workouts import generate_workouts
from .diet import generate_diet
from .progress import predict_progress
from fitness_engine.grocery import generate_grocery_list
from models.user_model import UserData

def generate_calories_for_user(user) -> int:
    return calculate_calories(user)

def generate_full_plan(user, weeks_progress: int = 8):
    cal_data = calculate_calories(user)
    calories = cal_data["calories"]
    macros = cal_data["macros"]

    workouts = generate_workouts(user)
    diet = generate_diet(user, calories, macros)
    grocery = generate_grocery_list(diet)
    progress = predict_progress(user, weeks=weeks_progress)

    return {
        "calories_target": calories,
        "macros": macros,
        "workout_plan": workouts,
        "diet_plan": diet,
         "grocery_list": grocery,
        "progress": progress
    }

