import random
from typing import List, Dict
from models.user_model import UserData

def predict_progress(user, weeks: int = 8) -> List[Dict]:

    progress = []
    current = float(user.weight_kg)

    for w in range(1, weeks + 1):
        # water fluctuation
        water = random.uniform(-0.25, 0.25)

        if user.goal.lower() == "muscle_gain":
            # Natural muscle gain rates vary; beginners faster.
            if w == 1:
                base = random.uniform(0.25, 0.4) 
            else:
                base = random.uniform(0.15, 0.25)
                
            change = base + water

        elif user.goal.lower() == "fat_loss":
            # Fat loss faster first week (water/glycogen)
            if w == 1:
                base = random.uniform(-0.8, -0.4)
            else:
                base = random.uniform(-0.45, -0.2)
                
            change = base + water

        else: 
            change = random.uniform(-0.25, 0.25) 

        current += change
        
        progress.append({
            "week": w,
            "predicted_weight": round(current, 1),
            "change_this_week": round(change, 2),
            "water_effect": round(water, 2)
        })

    return progress
