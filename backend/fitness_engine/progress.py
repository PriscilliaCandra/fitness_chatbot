import numpy as np
from models.user_model import UserData
from typing import List, Dict

def predict_progress(user: UserData, weeks: int = 12) -> List[Dict]:
    """
    Predict weight progress based on current weight, target weight, and user profile
    """
    current_weight = user.weight_kg
    target_weight = user.target_weight if user.target_weight else calculate_target_weight(user)
    
    # Calculate realistic weekly weight change based on goal and activity level
    weekly_change = calculate_weekly_weight_change(user, current_weight, target_weight)
    
    progress = []
    
    for week in range(weeks + 1):
        predicted_weight = current_weight + (weekly_change * week)
        
        # Stop when target weight is reached
        if (weekly_change > 0 and predicted_weight >= target_weight) or \
           (weekly_change < 0 and predicted_weight <= target_weight):
            predicted_weight = target_weight
        
        progress.append({
            "week": week,
            "predicted_weight": round(predicted_weight, 1),
            "weight_change": round(predicted_weight - current_weight, 1),
            "weekly_goal": round(weekly_change, 1)
        })
        
        # Stop adding weeks if target reached
        if predicted_weight == target_weight and week < weeks:
            # Fill remaining weeks with target weight
            for remaining_week in range(week + 1, weeks + 1):
                progress.append({
                    "week": remaining_week,
                    "predicted_weight": target_weight,
                    "weight_change": round(target_weight - current_weight, 1),
                    "weekly_goal": 0
                })
            break
    
    return progress

def calculate_target_weight(user: UserData) -> float:
    """
    Calculate realistic target weight based on BMI if not provided
    """
    height_m = user.height_cm / 100
    current_bmi = user.weight_kg / (height_m ** 2)
    
    if user.goal == "fat_loss":
        # Target BMI 22 (healthy range)
        target_bmi = 22.0
        return round(target_bmi * (height_m ** 2), 1)
    elif user.goal == "muscle_gain":
        # Allow slightly higher BMI for muscle gain
        target_bmi = min(current_bmi + 1.5, 25.0)  # Max BMI 25
        return round(target_bmi * (height_m ** 2), 1)
    else:  # maintenance
        return user.weight_kg

def calculate_weekly_weight_change(user: UserData, current_weight: float, target_weight: float) -> float:
    """
    Calculate realistic weekly weight change based on user profile
    """
    total_change = target_weight - current_weight
    if total_change == 0:
        return 0
    
    # Base weekly change rates (kg per week)
    if user.goal == "fat_loss":
        # Safe fat loss: 0.5-1kg per week
        base_rate = -0.7  # kg per week
    elif user.goal == "muscle_gain":
        # Realistic muscle gain: 0.2-0.5kg per week
        base_rate = 0.3   # kg per week
    else:  # maintenance
        base_rate = 0
    
    # Adjust based on activity level
    activity_multiplier = {
        "low": 0.7,
        "moderate": 1.0,
        "high": 1.3
    }.get(user.active_level, 1.0)
    
    # Adjust based on current weight (heavier people can lose/gain faster initially)
    weight_factor = 1.0
    if abs(total_change) > 10:  # If more than 10kg to lose/gain
        weight_factor = 1.2
    
    weekly_change = base_rate * activity_multiplier * weight_factor
    
    # Ensure change direction matches goal
    if total_change > 0 and weekly_change < 0:
        weekly_change = abs(weekly_change)
    elif total_change < 0 and weekly_change > 0:
        weekly_change = -abs(weekly_change)
    
    # Limit extreme changes
    if user.goal == "fat_loss":
        weekly_change = max(weekly_change, -1.5)  # Max 1.5kg loss per week
    elif user.goal == "muscle_gain":
        weekly_change = min(weekly_change, 0.8)   # Max 0.8kg gain per week
    
    return weekly_change

def calculate_time_to_target(user: UserData) -> Dict:
    """
    Calculate estimated time to reach target weight
    """
    current_weight = user.weight_kg
    target_weight = user.target_weight if user.target_weight else calculate_target_weight(user)
    
    weekly_change = calculate_weekly_weight_change(user, current_weight, target_weight)
    
    if weekly_change == 0:
        return {
            "weeks_to_target": 0,
            "months_to_target": 0,
            "is_achievable": True,
            "message": "You're already at your target weight!"
        }
    
    weeks_needed = abs((target_weight - current_weight) / weekly_change)
    months_needed = weeks_needed / 4.33  # Average weeks per month
    
    # Check if goal is realistic
    is_realistic = True
    message = "This is a realistic goal!"
    
    if user.goal == "fat_loss" and weeks_needed > 52:  # More than 1 year
        is_realistic = False
        message = "Consider setting a closer target weight for better motivation"
    elif user.goal == "muscle_gain" and weeks_needed > 78:  # More than 1.5 years
        is_realistic = False
        message = "Muscle gain takes time. Consider a more gradual target"
    
    return {
        "weeks_to_target": round(weeks_needed),
        "months_to_target": round(months_needed, 1),
        "is_achievable": is_realistic,
        "message": message,
        "weekly_change_goal": round(weekly_change, 1)
    }