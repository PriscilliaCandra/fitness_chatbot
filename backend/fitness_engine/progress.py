import random
from typing import List, Dict
from models.user_model import UserData

def predict_progress(user, weeks: int = 8) -> List[Dict]:
    progress = []
    current_weight = float(user.weight_kg)
    
    # Estimate initial body fat (rough estimation)
    if user.gender.lower() in ["male", "m"]:
        body_fat_pct = 20 + (user.weight_kg - 70) * 0.5  # Rough estimate
    else:
        body_fat_pct = 28 + (user.weight_kg - 60) * 0.5
    
    body_fat_pct = max(10, min(40, body_fat_pct))  # Reasonable bounds

    for w in range(1, weeks + 1):
        water = random.uniform(-0.25, 0.25)
        
        if user.goal.lower() == "muscle_gain":
            if w == 1:
                base = random.uniform(0.25, 0.4)
                fat_change = random.uniform(-0.05, 0.05)  # Small fat changes
            else:
                base = random.uniform(0.15, 0.25)
                fat_change = random.uniform(-0.1, 0.1)
                
        elif user.goal.lower() == "fat_loss":
            if w == 1:
                base = random.uniform(-0.8, -0.4)
                fat_change = random.uniform(-0.3, -0.6)  # Mostly fat loss initially
            else:
                base = random.uniform(-0.45, -0.2)
                fat_change = random.uniform(-0.15, -0.3)
        else: 
            base = random.uniform(-0.1, 0.1)
            fat_change = random.uniform(-0.05, 0.05)

        change = base + water
        current_weight += change
        
        # Update body composition
        muscle_change = base - fat_change
        body_fat_pct = max(8, min(45, body_fat_pct + (fat_change / current_weight) * 100))
        
        progress.append({
            "week": w,
            "predicted_weight": round(current_weight, 1),
            "change_this_week": round(change, 2),
            "water_effect": round(water, 2),
            "estimated_muscle_change": round(muscle_change, 2),
            "estimated_fat_change": round(fat_change, 2),
            "estimated_body_fat_pct": round(body_fat_pct, 1)
        })

    return progress