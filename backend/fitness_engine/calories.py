def calculate_bmr(user) -> float:
    gender = user.gender.lower()
    if gender in ("male", "m"):
        return 10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age + 5
    else:
        return 10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age - 161


def activity_factor(active_level: str) -> float:
    mapping = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    return mapping.get(active_level.lower(), 1.2)


def adaptive_surplus_deficit(tdee: float, bmi: float, goal: str) -> float:
    goal = goal.lower()

    if goal == "muscle_gain":
        if bmi < 20:
            pct = 0.12
        elif bmi < 25:
            pct = 0.10
        elif bmi < 30:
            pct = 0.07
        else:
            pct = 0.05
        return tdee + tdee * pct

    elif goal == "fat_loss":
        if bmi < 20:
            pct = 0.12
        elif bmi < 25:
            pct = 0.15
        elif bmi < 30:
            pct = 0.20
        else:
            pct = 0.25
        return tdee - tdee * pct

    return tdee  


def calculate_macros(calories: float, user) -> dict:
    weight = user.weight_kg
    goal = user.goal.lower()

    if goal == "fat_loss":
        protein_g = weight * 2.0
    elif goal == "muscle_gain":
        protein_g = weight * 1.8
    else:
        protein_g = weight * 1.6

    protein_cal = protein_g * 4

    if goal == "fat_loss":
        fat_pct = 0.20
    else:
        fat_pct = 0.25

    fat_cal = calories * fat_pct
    fat_g = fat_cal / 9

    remaining_cal = calories - (protein_cal + fat_cal)
    carbs_g = remaining_cal / 4

    return {
        "protein_g": round(protein_g),
        "fat_g": round(fat_g),
        "carbs_g": round(carbs_g)
    }


def calculate_calories(user) -> dict:
    bmr = calculate_bmr(user)
    factor = activity_factor(user.active_level)
    tdee = bmr * factor

    height_m = user.height_cm / 100
    bmi = user.weight_kg / (height_m ** 2)

    adjusted = adaptive_surplus_deficit(tdee, bmi, user.goal)
    adjusted = int(round(adjusted))

    macros = calculate_macros(adjusted, user)

    return {
        "calories": adjusted,
        "macros": macros
    }
