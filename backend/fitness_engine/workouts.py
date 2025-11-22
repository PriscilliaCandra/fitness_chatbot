import random
from typing import List, Dict
from models.user_model import UserData

def generate_workouts(user) -> List[Dict]:

    exercises = {
        "push": [
            "Bench Press", "Inclined Press", "Overhead Press",
            "Lateral Raise", "Tricep Dip", "Tricep Pushdown"
        ],
        "pull": [
            "Barbell Row", "Dumbbell Row", "Lat Pull Down",
            "Cable Row", "Bicep Curl", "Hammer Curl"
        ],
        "leg": [
            "Barbell Squat", "Romanian Deadlift", "Lunges",
            "Leg Press", "Leg Extension", "Calf Raise"
        ],
        "core": [
            "Seated Crunch", "Russian Twist", "Reverse Crunch",
            "Leg Raise", "Bicycle Crunch", "Plank"
        ]
    }

    g = user.goal.lower()
    
    if g == "muscle_gain":
        cardio_text = "15 min cardio"
    elif g == "fat_loss":
        cardio_text = "40 min cardio"
    else:
        cardio_text = "20 min cardio"

    plan = []
    weekly_split = ["push", "pull", "leg", "push", "pull", "leg", "rest"]

    for day_idx, day_type in enumerate(weekly_split, start=1):
        
        if day_type == "rest":
            plan.append({"day": day_idx, "workout": ["Rest"]})
            continue

        if day_type == "leg":
            core_choices = random.sample(exercises["core"], 3)
            daily = exercises["leg"] + core_choices + [cardio_text]
            
        else:
            daily = exercises[day_type] + [cardio_text]

        plan.append({"day": day_idx, "workout": daily})

    return plan
