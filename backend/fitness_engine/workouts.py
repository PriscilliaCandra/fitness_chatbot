from models.user_model import UserData
from typing import List, Dict
import random

def generate_workouts(user) -> List[Dict]:
    # Exercise database dengan sets dan reps yang sesuai
    exercises = {
        "push": [
            {"name": "Bench Press", "sets": 3, "reps": "8-12", "rest": "60-90s"},
            {"name": "Inclined Press", "sets": 3, "reps": "8-12", "rest": "60s"},
            {"name": "Overhead Press", "sets": 3, "reps": "8-12", "rest": "60s"},
            {"name": "Lateral Raise", "sets": 3, "reps": "12-15", "rest": "45s"},
            {"name": "Tricep Dip", "sets": 3, "reps": "10-15", "rest": "60s"},
            {"name": "Tricep Pushdown", "sets": 3, "reps": "12-15", "rest": "45s"}
        ],
        "pull": [
            {"name": "Barbell Row", "sets": 3, "reps": "8-12", "rest": "60-90s"},
            {"name": "Dumbbell Row", "sets": 3, "reps": "8-12", "rest": "60s"},
            {"name": "Lat Pull Down", "sets": 3, "reps": "8-12", "rest": "60s"},
            {"name": "Cable Row", "sets": 3, "reps": "10-12", "rest": "60s"},
            {"name": "Bicep Curl", "sets": 3, "reps": "10-15", "rest": "45s"},
            {"name": "Hammer Curl", "sets": 3, "reps": "10-15", "rest": "45s"}
        ],
        "leg": [
            {"name": "Barbell Squat", "sets": 4, "reps": "6-10", "rest": "90s"},
            {"name": "Romanian Deadlift", "sets": 3, "reps": "8-12", "rest": "90s"},
            {"name": "Lunges", "sets": 3, "reps": "10-12 each leg", "rest": "60s"},
            {"name": "Leg Press", "sets": 3, "reps": "10-15", "rest": "60s"},
            {"name": "Leg Extension", "sets": 3, "reps": "12-15", "rest": "45s"},
            {"name": "Calf Raise", "sets": 4, "reps": "15-20", "rest": "45s"}
        ],
        "core": [
            {"name": "Seated Crunch", "sets": 3, "reps": "15-20", "rest": "30s"},
            {"name": "Russian Twist", "sets": 3, "reps": "12-15 each side", "rest": "30s"},
            {"name": "Reverse Crunch", "sets": 3, "reps": "12-15", "rest": "30s"},
            {"name": "Leg Raise", "sets": 3, "reps": "10-15", "rest": "30s"},
            {"name": "Bicycle Crunch", "sets": 3, "reps": "15-20 each side", "rest": "30s"},
            {"name": "Plank", "sets": 3, "reps": "30-60 seconds", "rest": "30s"}
        ]
    }
    
    cardio_exercises = {
        "muscle_gain": [
            {"name": "Jogging", "duration": "15 min", "intensity": "Low"},
            {"name": "Cycling", "duration": "15 min", "intensity": "Moderate"},
            {"name": "Walking", "duration": "15 min", "intensity": "Low"}
        ],
        "fat_loss": [
            {"name": "Running", "duration": "30-40 min", "intensity": "Moderate-High"},
            {"name": "Cycling", "duration": "40 min", "intensity": "Moderate"},
            {"name": "HIIT Circuit", "duration": "25 min", "intensity": "High"},
            {"name": "Elliptical", "duration": "35 min", "intensity": "Moderate"}
        ],
        "maintain": [
            {"name": "Walking", "duration": "20-30 min", "intensity": "Low"},
            {"name": "Swimming", "duration": "20 min", "intensity": "Moderate"},
            {"name": "Cycling", "duration": "15 min", "intensity": "Moderate"},
            {"name": "Running", "duration": "30-40 min", "intensity": "Moderate-High"},
        ]
    }
        
    def adjust_for_goal(exercise_list, goal, active_level):
        """Adjust sets dan reps berdasarkan goal dan activity level"""
        adjusted_exercises = []
        
        for exercise in exercise_list:
            if isinstance(exercise, dict) and "sets" in exercise:
                # Copy exercise untuk modifikasi
                adjusted_exercise = exercise.copy()
                
                # Adjust berdasarkan goal
                if goal == "muscle_gain":
                    adjusted_exercise["sets"] = min(adjusted_exercise["sets"] + 1, 5)
                    adjusted_exercise["reps"] = "6-12"
                elif goal == "fat_loss":
                    adjusted_exercise["sets"] = adjusted_exercise["sets"]
                    adjusted_exercise["reps"] = "12-15"
                    
                if active_level == "beginner":
                    adjusted_exercise["sets"] = max(adjusted_exercise["sets"] - 1, 2)
                elif active_level == "advanced":
                    adjusted_exercise["sets"] = adjusted_exercise["sets"] + 1
                
                adjusted_exercises.append(adjusted_exercise)
            else:
                adjusted_exercises.append(exercise)
        
        return adjusted_exercises

    g = user.goal.lower()
    activity_level = user.active_level.lower()
    cardio_choice = random.choice(cardio_exercises.get(g, cardio_exercises["maintain"]))

    plan = []
    weekly_split = ["push", "pull", "leg", "push", "pull", "leg", "rest"]

    for day_idx, day_type in enumerate(weekly_split, start=1):
        
        if day_type == "rest":
            plan.append({
                "day": day_idx, 
                "workout": [{"name": "Rest - Recovery", "type": "rest"}],
                "type": "rest"
            })
            
            continue

        # Pilih 4-5 exercises untuk setiap workout day
        if day_type == "leg":
            # Untuk leg day, ambil 4 leg exercises + 2 core exercises
            selected_exercises = random.sample(exercises["leg"], 4)
            core_exercises = random.sample(exercises["core"], 2)
            daily_exercises = selected_exercises + core_exercises
        else:
            # Untuk push/pull day, ambil 5 exercises
            daily_exercises = random.sample(exercises[day_type], 5)

        cardio_with_type = cardio_choice.copy()
        cardio_with_type["type"] = "cardio"
        daily_exercises.append(cardio_with_type)
        
        # Adjust untuk goal dan activity level
        adjusted_exercises = adjust_for_goal(daily_exercises, g, activity_level)
        
        plan.append({
            "day": day_idx, 
            "workout": adjusted_exercises,
            "type": day_type,
            "total_exercises": len(adjusted_exercises),
            "estimated_duration": f"{len(adjusted_exercises) * 10} minutes" 
        })

    return plan

def generate_simple_workouts(user) -> List[Dict]:
    """Versi sederhana tanpa sets/reps detail untuk kompatibilitas"""
    workouts = generate_workouts(user)
    
    simplified_plan = []
    for day in workouts:
        simplified_workout = []
        for exercise in day["workout"]:
            if isinstance(exercise, str):
                simplified_workout.append(exercise)
            else:
                # Extract hanya nama exercise untuk format sederhana
                simplified_workout.append(exercise["name"])
        
        simplified_plan.append({
            "day": day["day"],
            "workout": simplified_workout
        })
    
    return simplified_plan
    
