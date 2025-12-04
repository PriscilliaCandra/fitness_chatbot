from .calories import calculate_calories
from .workouts import generate_workouts
from .diet import generate_diet
from .progress import predict_progress, calculate_time_to_target
from .portions import estimate_portions
from .recipes import generate_meal_recipe, generate_recipe
from .grocery import generate_grocery_list
from models.user_model import UserData
from typing import List, Dict, Optional, Union
import random
from datetime import datetime, timedelta


def generate_calories_for_user(user) -> dict:
    return calculate_calories(user)

def generate_full_plan(user: UserData, weeks_progress: int = None) -> Dict:
    if not weeks_progress:
        time_estimate = calculate_time_to_target(user)
        weeks_progress = min(time_estimate["weeks_to_target"], 16)  # Max 16 weeks display
        weeks_progress = max(weeks_progress, 8)
        
    # Calculate nutrition targets
    cal_data = calculate_calories(user)
    calories_target = cal_data["calories"]
    macros_target = cal_data["macros"]
    
    # Generate workout plan
    workout_plan = generate_workouts(user)
    
    if workout_plan and len(workout_plan) > 0:
        first_day = workout_plan[0]
        print(f"Day 1 type: {first_day.get('type')}")
        print(f"Workout count: {len(first_day.get('workout', []))}")
        if first_day.get('workout'):
            first_exercise = first_day['workout'][0]
            print(f"First exercise: {first_exercise}")
            print(f"Exercise type: {type(first_exercise)}")
            if isinstance(first_exercise, dict):
                print(f"Has sets: {'sets' in first_exercise}")
                print(f"Has reps: {'reps' in first_exercise}")
                print(f"Has rest: {'rest' in first_exercise}")
    
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
    time_estimate = calculate_time_to_target(user)
    
    return {
        "user_info": {
            "name": user.name,
            "goal": user.goal,
            "vegan": user.vegan,
            "active_level": user.active_level,
            "current_weight": user.weight_kg,
            "target_weight": user.target_weight if user.target_weight else calculate_target_weight(user)
        },
        "nutrition": {
            "calories_target": calories_target,
            "macros_target": macros_target
        },
        "workout_plan": workout_plan,
        "diet_plan": diet_plan_with_recipes, 
        "grocery_list": grocery_list,
        "progress_prediction": progress_prediction,
        "time_estimate": time_estimate
    }

def add_recipes_and_portions_to_diet(
    diet_weekly: List[Dict], 
    macros_target: Dict, 
    goal: str
) -> List[Dict]:
    enhanced_diet = []
    
    for day in diet_weekly:
        print(f"=== PROCESSING DAY {day['day']} ===")
        enhanced_day = day.copy()
        enhanced_day["portions"] = {}
        enhanced_day["recipes"] = {}
        enhanced_day["meal_details"] = {}
        
        for meal_type, meal_name in day["meals"].items():
            print(f"Processing {meal_type}")
            print(f"Meal name: '{meal_name}'")
            print(f"Meal name type: {type(meal_name)}")
            
            print(f"Day keys: {list(day.keys())}")
            
            ingredients = day.get("ingredients", {}).get(meal_type, [])
            print(f"Ingredients: {ingredients}")
            print(f"Ingredients type: {type(ingredients)}")
            
            # Validasi CRITICAL
            if not ingredients:
                print(f"CRITICAL: No ingredients for {meal_type}")
                ingredients = []
            elif not isinstance(ingredients, list):
                print(f"CRITICAL: Ingredients is not a list: {type(ingredients)}")
                ingredients = []
            elif ingredients and isinstance(ingredients[0], str) and len(ingredients[0]) == 1:
                print(f"CRITICAL: Ingredients are single characters!")
                ingredients = []
            
            # DEBUG sebelum panggil estimate_portions
            print(f"Calling estimate_portions with:")
            print(f"- ingredients: {ingredients}")
            print(f"- ingredients count: {len(ingredients)}")
            print(f"- first ingredient: {ingredients[0] if ingredients else 'None'}")
            
            # Estimate portions
            portions = estimate_portions(
                ingredients=ingredients,
                macros_target=macros_target,
                goal=goal
            )
            
            print(f"estimate_portions returned:")
            print(f"- portions: {portions}")
            print(f"- portions count: {len(portions)}")
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
                print(f"Error in recipe generation: {e}")
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
    

# ==================== NEW CHATBOT FUNCTIONS ====================

def handle_chat_query(user: UserData, query: str, context: Optional[Dict] = None) -> Dict:
    """
    Handle berbagai jenis pertanyaan dari user setelah plan digenerate
    """
    query_lower = query.lower()
    
    # Cek kategori pertanyaan
    if any(word in query_lower for word in ['workout', 'exercise', 'train', 'gym', 'cardio', 'strength']):
        return handle_workout_queries(user, query_lower, context)
    
    elif any(word in query_lower for word in ['diet', 'meal', 'food', 'eat', 'nutrition', 'calorie', 'protein']):
        return handle_diet_queries(user, query_lower, context)
    
    elif any(word in query_lower for word in ['progress', 'result', 'weight', 'lose', 'gain', 'fat']):
        return handle_progress_queries(user, query_lower, context)
    
    elif any(word in query_lower for word in ['health', 'healthy', 'wellness', 'lifestyle', 'tip']):
        return handle_health_queries(user, query_lower, context)
    
    elif any(word in query_lower for word in ['recipe', 'cook', 'ingredient', 'prepare', 'make']):
        return handle_recipe_queries(user, query_lower, context)
    
    elif any(word in query_lower for word in ['grocery', 'shop', 'buy', 'shopping', 'list']):
        return handle_grocery_queries(user, query_lower, context)
    
    else:
        return handle_general_queries(user, query_lower)

# ==================== WORKOUT-RELATED QUERIES ====================

def handle_workout_queries(user: UserData, query: str, context: Optional[Dict]) -> Dict:
    """Handle pertanyaan tentang workout"""
    
    if 'today' in query or 'now' in query or 'day' in query:
        return get_todays_workout(user, context)
    
    elif 'schedule' in query or 'week' in query or 'plan' in query:
        return get_workout_schedule(user, context)
    
    elif 'intensity' in query or 'hard' in query or 'easy' in query:
        return get_workout_intensity_advice(user)
    
    elif 'rest' in query or 'recover' in query:
        return get_recovery_tips()
    
    elif any(word in query for word in ['push', 'pull', 'leg', 'split']):
        return explain_workout_split()
    
    elif 'cardio' in query:
        return get_cardio_advice(user)
    
    elif any(word in query for word in ['form', 'technique', 'proper', 'correct']):
        return get_exercise_form_tips(query)
    
    elif 'alternative' in query or 'replace' in query or 'instead' in query:
        return get_exercise_alternatives(query)
    
    elif 'duration' in query or 'long' in query or 'time' in query:
        return get_workout_duration_advice(user)
    
    else:
        return {
            "type": "workout_general",
            "response": f"Based on your {user.goal.replace('_', ' ')} goal and {user.active_level} activity level, here are general workout tips:\n\n" +
                       get_general_workout_tips(user),
            "suggestions": [
                "Show me today's workout",
                "What's my workout schedule?",
                "How should I do cardio?",
                "Give me recovery tips",
                "Explain push/pull/leg split"
            ]
        }

def get_todays_workout(user: UserData, context: Optional[Dict]) -> Dict:
    """Get workout untuk hari ini berdasarkan konteks"""
    if context and 'current_day' in context:
        day_number = context['current_day']
        if context.get('workout_plan'):
            for day in context['workout_plan']:
                if day['day'] == day_number:
                    return format_workout_day_response(day)
    
    # Fallback: generate simple workout untuk hari ini
    workouts = generate_workouts(user)
    if workouts and len(workouts) > 0:
        today_workout = workouts[0]
    else:
        today_workout = {"day": 1, "type": "full_body", "workout": [{"name": "No workout generated yet"}]}
    
    return {
        "type": "todays_workout",
        "response": f"Here's your workout for Day {today_workout['day']}:\n\n" +
                   format_workout_list(today_workout.get('workout', [])),
        "workout_day": today_workout
    }

def get_workout_schedule(user: UserData, context: Optional[Dict]) -> Dict:
    """Get seluruh workout schedule"""
    workouts = generate_workouts(user)
    
    schedule_text = "Here's your weekly workout schedule:\n\n"
    for day in workouts:
        day_type = day.get('type', 'unknown').upper() if day.get('type') != 'rest' else 'REST'
        schedule_text += f"Day {day['day']}: {day_type} Day\n"
        if day.get('type') != 'rest':
            exercises = []
            for ex in day.get('workout', [])[:3]:
                if isinstance(ex, dict):
                    exercises.append(ex.get('name', 'Exercise'))
                else:
                    exercises.append(str(ex))
            schedule_text += f"   Exercises: {', '.join(exercises)}...\n"
        schedule_text += "\n"
    
    return {
        "type": "workout_schedule",
        "response": schedule_text,
        "full_schedule": workouts
    }

def get_general_workout_tips(user: UserData) -> str:
    """Get general workout tips berdasarkan goal user"""
    tips = {
        "muscle_gain": [
            "Focus on progressive overload - increase weights gradually",
            "Train each muscle group 2-3 times per week",
            "Prioritize compound movements (squats, deadlifts, bench press)",
            "Aim for 6-12 reps per set for hypertrophy",
            "Ensure adequate protein intake (1.6-2.2g per kg body weight)"
        ],
        "fat_loss": [
            "Combine strength training with cardio",
            "Maintain high intensity with shorter rest periods",
            "Focus on full-body workouts or circuit training",
            "Aim for 12-15 reps per set",
            "Prioritize consistency over perfection"
        ],
        "maintain": [
            "Balance strength training and cardio",
            "Focus on overall fitness and mobility",
            "Listen to your body - adjust intensity as needed",
            "Incorporate variety to prevent boredom",
            "Aim for 8-12 reps for balanced results"
        ]
    }
    
    goal_tips = tips.get(user.goal, tips["maintain"])
    level_tips = {
        "beginner": [
            "Start with lighter weights to focus on form",
            "Allow 48 hours rest between training the same muscle group",
            "Don't skip warm-up and cool-down",
            "Track your progress in a workout journal"
        ],
        "intermediate": [
            "Incorporate periodization in your training",
            "Try different training techniques (supersets, drop sets)",
            "Focus on weak points and imbalances",
            "Consider working with a trainer occasionally"
        ],
        "advanced": [
            "Implement advanced training techniques",
            "Focus on competition-specific preparation if applicable",
            "Pay attention to recovery as much as training",
            "Consider deload weeks every 4-8 weeks"
        ]
    }
    
    active_tips = level_tips.get(user.active_level, [])
    
    return "• " + "\n• ".join(goal_tips[:3]) + "\n\nFor your activity level:\n• " + "\n• ".join(active_tips[:2])

# ==================== DIET & NUTRITION QUERIES ====================

def handle_diet_queries(user: UserData, query: str, context: Optional[Dict]) -> Dict:
    """Handle pertanyaan tentang diet dan nutrisi"""
    
    # Calculate user's nutrition needs
    cal_data = calculate_calories(user)
    
    if 'calorie' in query or 'calories' in query:
        return get_calorie_info(user, cal_data)
    
    elif 'protein' in query:
        return get_protein_info(user, cal_data)
    
    elif 'carb' in query or 'carbohydrate' in query:
        return get_carb_info(user, cal_data)
    
    elif 'fat' in query or 'lipid' in query:
        return get_fat_info(user, cal_data)
    
    elif 'meal plan' in query or 'what eat' in query or 'food' in query:
        return get_meal_plan_suggestions(user, cal_data)
    
    elif any(word in query for word in ['supplement', 'vitamin', 'mineral']):
        return get_supplement_advice(user)
    
    elif any(word in query for word in ['water', 'hydrate', 'hydration']):
        return get_hydration_advice(user)
    
    elif any(word in query for word in ['cheat', 'treat', 'off plan']):
        return get_cheat_meal_advice(user)
    
    elif 'vegan' in query and user.vegan:
        return get_vegan_nutrition_tips()
    
    elif 'time' in query and ('eat' in query or 'meal' in query):
        return get_meal_timing_advice(user)
    
    else:
        return {
            "type": "diet_general",
            "response": f"Based on your profile, here's your nutrition overview:\n\n" +
                       format_nutrition_overview(user, cal_data),
            "suggestions": [
                "Tell me about my calorie needs",
                "How much protein should I eat?",
                "What about carbohydrates?",
                "Give me meal timing advice",
                "Hydration tips"
            ]
        }

def get_calorie_info(user: UserData, cal_data: Dict) -> Dict:
    """Get detailed calorie information"""
    calories = cal_data["calories"]
    bmr = cal_data.get("bmr", calories * 0.7)
    
    response = f"**Your Daily Calorie Needs:**\n\n"
    response += f"• Maintenance: {calories:,} calories/day\n"
    response += f"• BMR (Basal Metabolic Rate): {bmr:,.0f} calories/day\n"
    
    if user.goal == "fat_loss":
        deficit = calories * 0.2  # 20% deficit
        response += f"• For fat loss: {calories - deficit:,.0f} calories/day (20% deficit)\n"
        response += f"• Weekly deficit: {(deficit * 7)/7700:.1f} kg fat loss potential\n"
    elif user.goal == "muscle_gain":
        surplus = calories * 0.1  # 10% surplus
        response += f"• For muscle gain: {calories + surplus:,.0f} calories/day (10% surplus)\n"
        response += f"• Aim for 0.25-0.5 kg muscle gain per month\n"
    
    response += f"\n**Macro Breakdown:**\n"
    response += f"• Protein: {cal_data['macros'].get('protein', cal_data['macros'].get('protein_g', 0))}g\n"
    response += f"• Carbs: {cal_data['macros'].get('carbs', cal_data['macros'].get('carbs_g', 0))}g\n"
    response += f"• Fat: {cal_data['macros'].get('fat', cal_data['macros'].get('fat_g', 0))}g\n"
    
    return {
        "type": "calorie_info",
        "response": response,
        "data": cal_data
    }

def get_meal_plan_suggestions(user: UserData, cal_data: Dict) -> Dict:
    """Get meal plan suggestions"""
    meal_ideas = {
        "breakfast": [
            "Oatmeal with protein powder and berries",
            "Greek yogurt with nuts and honey",
            "Egg scramble with vegetables",
            "Protein smoothie with spinach and banana"
        ],
        "lunch": [
            "Grilled chicken salad with quinoa",
            "Tuna wrap with whole wheat tortilla",
            "Vegetable stir-fry with tofu/tempeh",
            "Lean beef with sweet potato and greens"
        ],
        "dinner": [
            "Salmon with roasted vegetables",
            "Turkey chili with beans",
            "Chicken breast with brown rice and broccoli",
            "Lentil curry with whole grain rice"
        ],
        "snacks": [
            "Apple with almond butter",
            "Protein bar or shake",
            "Cottage cheese with fruit",
            "Handful of nuts and seeds"
        ]
    }
    
    # Adjust based on user goal
    if user.goal == "fat_loss":
        meal_ideas["snacks"] = [
            "Celery sticks with hummus",
            "Greek yogurt",
            "Hard-boiled eggs",
            "Vegetable sticks"
        ]
    
    response = "**Sample Meal Ideas for Your Goals:**\n\n"
    for meal_type, ideas in meal_ideas.items():
        response += f"**{meal_type.title()}:**\n"
        for idea in ideas[:2]:
            response += f"• {idea}\n"
        response += "\n"
    
    response += f"\n**Daily Target:** {cal_data['calories']:,} calories\n"
    protein = cal_data['macros'].get('protein', cal_data['macros'].get('protein_g', 0))
    response += f"**Protein:** Aim for {protein}g daily\n"
    
    return {
        "type": "meal_suggestions",
        "response": response,
        "meal_ideas": meal_ideas
    }

# ==================== PROGRESS & RESULTS QUERIES ====================

def handle_progress_queries(user: UserData, query: str, context: Optional[Dict]) -> Dict:
    """Handle pertanyaan tentang progress dan results"""
    
    if 'how long' in query or 'time' in query or 'when' in query:
        return get_time_to_results(user)
    
    elif 'expect' in query or 'result' in query or 'achieve' in query:
        return get_expected_results(user)
    
    elif 'track' in query or 'measure' in query or 'progress' in query:
        return get_progress_tracking_tips(user)
    
    elif any(word in query for word in ['plateau', 'stuck', 'not losing', 'not gaining']):
        return handle_plateau_advice(user)
    
    elif 'motivat' in query or 'stick' in query or 'consistent' in query:
        return get_motivation_tips(user)
    
    else:
        progress = predict_progress(user, weeks=12)
        
        return {
            "type": "progress_overview",
            "response": format_progress_prediction(progress),
            "data": progress,
            "suggestions": [
                "How long until I see results?",
                "What results can I expect?",
                "How to track my progress?",
                "Tips for staying motivated",
                "What if I hit a plateau?"
            ]
        }

def get_time_to_results(user: UserData) -> Dict:
    """Calculate and explain time to see results"""
    time_estimate = calculate_time_to_target(user)
    
    response = f"**Time to See Results:**\n\n"
    
    if user.goal == "fat_loss":
        response += f"• **Initial changes:** 2-4 weeks (energy, measurements)\n"
        response += f"• **Visible changes:** 4-8 weeks (clothes fitting better)\n"
        response += f"• **Significant changes:** 8-12 weeks (noticeable difference)\n"
        response += f"• **Reach target:** {time_estimate.get('weeks_to_target', 12)} weeks\n\n"
        
        if time_estimate.get('weeks_to_target', 12) > 12:
            response += "**Tip:** Focus on weekly progress, not just the end goal. "
            response += "Celebrate non-scale victories like increased energy and better sleep."
        else:
            response += "**Tip:** Consistency is key! Stick to your plan and results will come."
    
    elif user.goal == "muscle_gain":
        response += f"• **Initial strength gains:** 2-4 weeks\n"
        response += f"• **Visible muscle growth:** 8-12 weeks\n"
        response += f"• **Significant changes:** 16-24 weeks\n"
        response += f"• **Reach target:** {time_estimate.get('weeks_to_target', 12)} weeks\n\n"
        response += "**Realistic expectations:** 0.5-1 kg muscle per month for beginners\n"
    
    else:  # maintain
        response += f"• **Improved fitness:** 4-6 weeks\n"
        response += f"• **Habit formation:** 8-12 weeks\n"
        response += f"• **Lifestyle integration:** 12+ weeks\n\n"
        response += "**Focus:** Consistency and sustainability over rapid results"
    
    return {
        "type": "time_to_results",
        "response": response,
        "time_estimate": time_estimate
    }

# ==================== HEALTH & WELLNESS QUERIES ====================

def handle_health_queries(user: UserData, query: str, context: Optional[Dict]) -> Dict:
    """Handle pertanyaan tentang kesehatan dan wellness"""
    
    if any(word in query for word in ['sleep', 'rest', 'recover']):
        return get_sleep_advice()
    
    elif any(word in query for word in ['stress', 'anxiety', 'mental']):
        return get_stress_management_tips()
    
    elif any(word in query for word in ['energy', 'tired', 'fatigue']):
        return get_energy_boost_tips(user)
    
    elif 'immune' in query or 'sick' in query or 'health' in query:
        return get_immune_boost_tips()
    
    elif any(word in query for word in ['age', 'older', 'senior']):
        return get_age_specific_advice(user)
    
    elif any(word in query for word in ['women', 'female', 'menstrual']):
        return get_womens_health_tips()
    
    elif any(word in query for word in ['men', 'male', 'testosterone']):
        return get_mens_health_tips()
    
    else:
        return {
            "type": "health_general",
            "response": get_general_health_tips(user),
            "suggestions": [
                "Sleep optimization tips",
                "Stress management techniques",
                "How to boost energy levels",
                "Immune system support",
                "Age-specific advice"
            ]
        }

# ==================== HELPER FUNCTIONS ====================

def format_workout_list(workouts: List) -> str:
    """Format workout list untuk response"""
    if not workouts:
        return "No exercises planned for today."
    
    formatted = ""
    for i, exercise in enumerate(workouts, 1):
        if isinstance(exercise, dict):
            name = exercise.get('name', 'Exercise')
            if 'sets' in exercise and 'reps' in exercise:
                reps = exercise['reps']
                if isinstance(reps, dict):
                    reps = str(reps)
                formatted += f"{i}. {name} - {exercise['sets']} sets x {reps} reps\n"
                if 'rest' in exercise:
                    rest = exercise['rest']
                    if isinstance(rest, dict):
                        rest = str(rest)
                    formatted += f"   Rest: {rest} seconds between sets\n"
            elif 'duration' in exercise:
                duration = exercise['duration']
                if isinstance(duration, dict):
                    duration = str(duration)
                formatted += f"{i}. {name} - {duration} ({exercise.get('intensity', 'Moderate')})\n"
            else:
                formatted += f"{i}. {name}\n"
        else:
            formatted += f"{i}. {exercise}\n"
    
    return formatted

def format_nutrition_overview(user: UserData, cal_data: Dict) -> str:
    """Format nutrition overview"""
    response = f"**Nutrition Overview for {user.goal.replace('_', ' ').title()}:**\n\n"
    response += f"• Daily Calories: {cal_data['calories']:,}\n"
    
    # Handle different macro key formats
    macros = cal_data['macros']
    protein = macros.get('protein', macros.get('protein_g', 0))
    carbs = macros.get('carbs', macros.get('carbs_g', 0))
    fat = macros.get('fat', macros.get('fat_g', 0))
    
    response += f"• Protein: {protein}g\n"
    response += f"• Carbs: {carbs}g\n"
    response += f"• Fat: {fat}g\n\n"
    
    response += "**Key Principles:**\n"
    if user.goal == "fat_loss":
        response += "• Calorie deficit is key\n• Prioritize protein to preserve muscle\n• Include fiber for satiety\n• Stay hydrated\n"
    elif user.goal == "muscle_gain":
        response += "• Calorie surplus required\n• High protein intake essential\n• Carbs fuel workouts\n• Consistent eating schedule\n"
    else:
        response += "• Maintain calorie balance\n• Balanced macronutrients\n• Whole foods focus\n• Listen to hunger cues\n"
    
    return response

def format_progress_prediction(progress: List[Dict]) -> str:
    """Format progress prediction untuk response"""
    if not progress:
        return "No progress prediction available."
    
    response = "**Progress Prediction:**\n\n"
    
    if isinstance(progress, list) and len(progress) > 0:
        response += "**Weekly Breakdown (first 4 weeks):**\n"
        for week in progress[:4]:  # First 4 weeks
            week_num = week.get('week', 0)
            predicted = week.get('predicted_weight', 0)
            change = week.get('weight_change', 0)
            response += f"Week {week_num}: {predicted}kg ({'+' if change >= 0 else ''}{change}kg)\n"
        response += "\n"
    
    # Add estimated target timeframe
    if len(progress) > 0:
        last_week = progress[-1]
        target_weight = last_week.get('predicted_weight', 0)
        response += f"**Target Weight:** {target_weight}kg in {len(progress)} weeks\n"
    
    return response

# ==================== UPDATE MAIN FUNCTIONS ====================

def generate_full_plan_with_chat(user: UserData, weeks_progress: int = None) -> Dict:
    """Generate full plan dengan chat capabilities"""
    full_plan = generate_full_plan(user, weeks_progress)
    
    # Add chatbot context
    full_plan["chat_context"] = {
        "user_profile": {
            "name": user.name,
            "goal": user.goal,
            "active_level": user.active_level,
            "weight": user.weight_kg,
            "target_weight": user.target_weight if user.target_weight else calculate_target_weight(user)
        },
        "generated_at": datetime.now().isoformat(),
        "current_day": 1,  # Start at day 1
        "workout_plan": full_plan.get("workout_plan", []),
        "diet_plan": full_plan.get("diet_plan", []),
        "progress_data": full_plan.get("progress_prediction", {})
    }
    
    # Add initial chat suggestions
    full_plan["initial_chat_suggestions"] = [
        "What's my workout for today?",
        "Tell me about my calorie needs",
        "How long until I see results?",
        "Give me meal ideas",
        "Sleep and recovery tips"
    ]
    
    return full_plan

# ==================== NEW API ENDPOINT FOR CHAT ====================

# Di plan_generator.py, pastikan fungsi ini ada:

def process_chat_message(user: UserData, message: str, context: Optional[Dict] = None) -> Dict:
    """
    Main function untuk memproses chat messages
    Dipanggil dari API endpoint
    """
    response = handle_chat_query(user, message, context)
    
    # Update context jika ada
    updated_context = context.copy() if context else {}
    if response.get("update_context"):
        updated_context.update(response["update_context"])
    
    return {
        "success": True,
        "response": response.get("response", "I'm here to help with your fitness journey!"),
        "type": response.get("type", "general"),
        "data": response.get("data", {}),
        "suggestions": response.get("suggestions", []),
        "updated_context": updated_context
    }

# ==================== IMPLEMENTASI FUNGSI YANG BELUM LENGKAP ====================

def get_workout_intensity_advice(user: UserData) -> Dict:
    """Memberikan saran intensitas workout berdasarkan level user"""
    intensity_advice = {
        "beginner": {
            "rpe": "5-7/10 (Rate of Perceived Exertion)",
            "rest": "60-90 seconds between sets",
            "volume": "2-3 sets per exercise, 8-12 reps",
            "frequency": "3-4 days per week",
            "focus": "Form and technique over heavy weights"
        },
        "intermediate": {
            "rpe": "7-8/10",
            "rest": "45-90 seconds for hypertrophy, 2-3 minutes for strength",
            "volume": "3-4 sets per exercise, 6-15 reps depending on goal",
            "frequency": "4-5 days per week with split routines",
            "focus": "Progressive overload and periodization"
        },
        "advanced": {
            "rpe": "8-9/10 with occasional 10/10",
            "rest": "30-60 seconds for metabolic stress, 3-5 minutes for max strength",
            "volume": "4-6 sets per exercise, varied rep ranges",
            "frequency": "5-6 days per week with specialized splits",
            "focus": "Advanced techniques and competition prep"
        }
    }
    
    advice = intensity_advice.get(user.active_level, intensity_advice["beginner"])
    
    response = f"**Workout Intensity Advice for {user.active_level.title()}:**\n\n"
    for key, value in advice.items():
        response += f"• **{key.replace('_', ' ').title()}:** {value}\n"
    
    # Goal-specific tips
    if user.goal == "fat_loss":
        response += "\n**For Fat Loss:**\n• Higher reps (12-15)\n• Shorter rest periods (30-60s)\n• Include HIIT cardio\n• Focus on calorie burn"
    elif user.goal == "muscle_gain":
        response += "\n**For Muscle Gain:**\n• Moderate reps (6-12)\n• Adequate rest (60-90s)\n• Progressive overload essential\n• Focus on mind-muscle connection"
    
    return {
        "type": "workout_intensity",
        "response": response,
        "advice": advice
    }

def get_recovery_tips() -> Dict:
    """Memberikan tips recovery dan pemulihan"""
    tips = [
        "**Sleep:** Aim for 7-9 hours of quality sleep per night",
        "**Hydration:** Drink at least 3-4 liters of water daily, more if you sweat heavily",
        "**Nutrition:** Consume protein (20-40g) within 30 minutes post-workout",
        "**Active Recovery:** Light walking, swimming, or stretching on rest days",
        "**Foam Rolling:** 10-15 minutes daily to reduce muscle soreness",
        "**Compression:** Consider compression garments for improved circulation",
        "**Cold Therapy:** Cold showers or ice baths for inflammation reduction",
        "**Mindfulness:** Meditation or deep breathing for stress management",
        "**Deload Weeks:** Reduce volume by 40-60% every 4-8 weeks",
        "**Listen to Body:** Rest when feeling excessively fatigued or sore"
    ]
    
    return {
        "type": "recovery_tips",
        "response": "**Comprehensive Recovery Strategies:**\n\n• " + "\n• ".join(tips),
        "tips": tips
    }

def explain_workout_split() -> Dict:
    """Menjelaskan berbagai jenis workout split"""
    splits = {
        "Full Body": {
            "description": "Train all major muscle groups each session",
            "frequency": "2-3 times per week",
            "best_for": "Beginners, fat loss, time-constrained individuals",
            "example": "Day 1: Full Body, Day 2: Rest/Cardio, Day 3: Full Body"
        },
        "Push/Pull/Legs": {
            "description": "Push (chest, shoulders, triceps), Pull (back, biceps), Legs (quads, hamstrings, calves)",
            "frequency": "3-6 days per week",
            "best_for": "Intermediate to advanced, muscle building",
            "example": "Day 1: Push, Day 2: Pull, Day 3: Legs, Day 4: Rest"
        },
        "Upper/Lower": {
            "description": "Alternate between upper body and lower body days",
            "frequency": "4 days per week",
            "best_for": "All levels, balanced development",
            "example": "Day 1: Upper, Day 2: Lower, Day 3: Rest, Day 4: Upper, Day 5: Lower"
        },
        "Body Part Split": {
            "description": "Focus on 1-2 muscle groups per day",
            "frequency": "5-6 days per week",
            "best_for": "Advanced, bodybuilders, specific muscle focus",
            "example": "Day 1: Chest, Day 2: Back, Day 3: Shoulders, Day 4: Legs, Day 5: Arms"
        }
    }
    
    response = "**Common Workout Splits Explained:**\n\n"
    for split_name, details in splits.items():
        response += f"**{split_name} Split:**\n"
        response += f"• Description: {details['description']}\n"
        response += f"• Frequency: {details['frequency']}\n"
        response += f"• Best For: {details['best_for']}\n"
        response += f"• Example: {details['example']}\n\n"
    
    response += "**Recommendation:** Beginners start with Full Body, progress to Upper/Lower, then PPL as you advance."
    
    return {
        "type": "workout_split_explanation",
        "response": response,
        "splits": splits
    }

def get_cardio_advice(user: UserData) -> Dict:
    """Memberikan saran cardio berdasarkan goal user"""
    
    cardio_types = {
        "fat_loss": {
            "HIIT": "20-30 minutes, 2-3x/week (30s max effort, 60s rest)",
            "Moderate": "30-45 minutes, 3-4x/week (65-75% max heart rate)",
            "LISS": "45-60 minutes, 2-3x/week (walking, cycling)"
        },
        "muscle_gain": {
            "LISS": "20-30 minutes, 2-3x/week (to avoid interference)",
            "Conditioning": "15-20 minutes post-workout, 2x/week"
        },
        "maintain": {
            "Varied": "Mix of HIIT and steady state, 3x/week",
            "Recreational": "Sports or activities you enjoy"
        }
    }
    
    goal_cardio = cardio_types.get(user.goal, cardio_types["maintain"])
    
    response = f"**Cardio Recommendations for {user.goal.replace('_', ' ').title()}:**\n\n"
    for cardio_type, advice in goal_cardio.items():
        response += f"• **{cardio_type}:** {advice}\n"
    
    # Additional tips
    response += "\n**General Cardio Tips:**\n"
    response += "• Time cardio appropriately (fasted morning for fat loss, post-workout for muscle gain)\n"
    response += "• Monitor heart rate zones for optimal results\n"
    response += "• Combine with strength training for best body composition changes\n"
    response += "• Stay hydrated and fuel properly around cardio sessions\n"
    
    return {
        "type": "cardio_advice",
        "response": response,
        "recommendations": goal_cardio
    }

def get_exercise_form_tips(query: str) -> Dict:
    """Memberikan tips form untuk exercise tertentu"""
    
    # Extract exercise name from query
    exercises_keywords = {
        "squat": "Back Squat",
        "deadlift": "Deadlift",
        "bench": "Bench Press",
        "pull": "Pull-up",
        "row": "Bent-over Row",
        "shoulder": "Overhead Press",
        "lunge": "Lunge",
        "pushup": "Push-up"
    }
    
    exercise_name = None
    for keyword, name in exercises_keywords.items():
        if keyword in query:
            exercise_name = name
            break
    
    if not exercise_name:
        return {
            "type": "general_form_tips",
            "response": "**General Exercise Form Tips:**\n\n"
                       "1. **Warm Up Properly:** 5-10 minutes dynamic stretching\n"
                       "2. **Start Light:** Master form before adding weight\n"
                       "3. **Control the Movement:** 2 seconds concentric, 2 seconds eccentric\n"
                       "4. **Full Range of Motion:** Complete each rep fully\n"
                       "5. **Brace Your Core:** Engage abs throughout movement\n"
                       "6. **Proper Breathing:** Exhale on exertion, inhale on return\n"
                       "7. **Mind-Muscle Connection:** Focus on target muscles\n"
                       "8. **Record Yourself:** Check form via video periodically",
            "suggestions": ["Squat form tips", "Deadlift technique", "Bench press form", "Pull-up form"]
        }
    
    # Specific exercise form tips
    form_tips = {
        "Back Squat": [
            "Feet shoulder-width apart, toes slightly out",
            "Break at hips first, then knees",
            "Keep chest up and back straight",
            "Descend until thighs parallel to floor",
            "Drive through heels, not toes",
            "Keep knees tracking over toes"
        ],
        "Deadlift": [
            "Feet hip-width under barbell",
            "Hinge at hips, maintain neutral spine",
            "Grip just outside legs",
            "Pull slack out of bar before lifting",
            "Drag bar up legs, keep it close",
            "Lock out hips at top, don't hyperextend"
        ],
        "Bench Press": [
            "Retract shoulder blades (create shelf)",
            "Arms at 45-degree angle from body",
            "Lower bar to mid-chest",
            "Keep wrists straight, not bent",
            "Drive through whole foot, not just toes",
            "Touch chest lightly, don't bounce"
        ]
    }
    
    tips = form_tips.get(exercise_name, form_tips["Back Squat"])
    
    response = f"**{exercise_name} Form Checklist:**\n\n"
    for i, tip in enumerate(tips, 1):
        response += f"{i}. {tip}\n"
    
    response += f"\n**Common {exercise_name} Mistakes to Avoid:**\n"
    response += "• Rounded back\n• Using momentum instead of muscle\n• Partial range of motion\n• Poor breathing technique\n• Going too heavy too soon"
    
    return {
        "type": "exercise_form",
        "response": response,
        "exercise": exercise_name,
        "tips": tips
    }

def get_exercise_alternatives(query: str) -> Dict:
    """Menyediakan alternatif exercise"""
    
    alternatives = {
        "squat": ["Leg Press", "Goblet Squat", "Bulgarian Split Squat", "Lunges", "Step-ups"],
        "deadlift": ["Romanian Deadlift", "Hip Thrust", "Good Morning", "Kettlebell Swing", "Back Extension"],
        "bench press": ["Push-ups", "Dumbbell Press", "Chest Press Machine", "Cable Flyes", "Floor Press"],
        "pull-up": ["Lat Pulldown", "Assisted Pull-up", "Inverted Row", "Bent-over Row", "Face Pull"],
        "shoulder press": ["Dumbbell Press", "Machine Press", "Landmine Press", "Push Press", "Arnold Press"],
        "barbell row": ["Dumbbell Row", "Cable Row", "T-bar Row", "Seated Row", "Inverted Row"]
    }
    
    # Find which exercise user wants alternatives for
    target_exercise = None
    for exercise in alternatives.keys():
        if exercise in query.lower():
            target_exercise = exercise
            break
    
    if not target_exercise:
        return {
            "type": "exercise_alternatives_general",
            "response": "**Common Exercise Alternatives:**\n\n"
                       "If you need alternatives due to:\n"
                       "• **Equipment limitations:** Look for bodyweight or minimal equipment options\n"
                       "• **Injury/pain:** Choose lower impact, controlled movements\n"
                       "• **Variety:** Rotate exercises every 4-8 weeks\n\n"
                       "**Ask specifically:** 'Alternatives for squats' or 'Replace bench press'",
            "suggestions": ["Alternatives for squats", "Replace deadlifts", "Bench press alternatives"]
        }
    
    response = f"**Alternatives for {target_exercise.title()}:**\n\n"
    for i, alt in enumerate(alternatives[target_exercise], 1):
        response += f"{i}. **{alt}** - "
        
        # Add brief description
        desc = {
            "Leg Press": "Machine-based, less spinal loading",
            "Goblet Squat": "Dumbbell/kettlebell front-loaded, good for form",
            "Push-ups": "Bodyweight, adjustable difficulty",
            "Lat Pulldown": "Machine-based, adjustable weight",
            "Dumbbell Press": "Unilateral, better shoulder health"
        }.get(alt, "Excellent alternative with similar muscle activation")
        
        response += f"{desc}\n"
    
    response += f"\n**When to use alternatives:**\n"
    response += "• No access to required equipment\n• Working around injury\n• Adding variety to prevent plateaus\n• Focusing on specific muscle activation"
    
    return {
        "type": "exercise_alternatives",
        "response": response,
        "original_exercise": target_exercise,
        "alternatives": alternatives[target_exercise]
    }

def get_workout_duration_advice(user: UserData) -> Dict:
    """Memberikan saran durasi workout optimal"""
    
    duration_guidelines = {
        "beginner": {
            "strength": "45-60 minutes",
            "cardio": "20-30 minutes",
            "total_weekly": "3-4 hours",
            "focus": "Quality over quantity, learn proper form"
        },
        "intermediate": {
            "strength": "60-75 minutes",
            "cardio": "30-45 minutes",
            "total_weekly": "5-7 hours",
            "focus": "Balanced volume and intensity"
        },
        "advanced": {
            "strength": "75-90 minutes",
            "cardio": "45-60 minutes",
            "total_weekly": "8-12+ hours",
            "focus": "Specialized training, high volume"
        }
    }
    
    guidelines = duration_guidelines.get(user.active_level, duration_guidelines["beginner"])
    
    response = f"**Optimal Workout Duration for {user.active_level.title()}:**\n\n"
    for key, value in guidelines.items():
        response += f"• **{key.replace('_', ' ').title()}:** {value}\n"
    
    # Goal-specific adjustments
    response += f"\n**For {user.goal.replace('_', ' ').title()} Goal:**\n"
    if user.goal == "fat_loss":
        response += "• Consider adding 10-15 minutes HIIT\n• Shorter rest periods (30-45s)\n• Higher volume circuits\n• Include active rest periods"
    elif user.goal == "muscle_gain":
        response += "• Longer rest between heavy sets (2-3 minutes)\n• Focus on compound movements\n• Include drop sets for time efficiency\n• Prioritize strength portion"
    
    response += "\n**Efficiency Tips:**\n"
    response += "• Superset opposing muscle groups\n• Use rest periods for mobility work\n• Have workout planned beforehand\n• Limit phone/social breaks\n• Stay hydrated to maintain performance"
    
    return {
        "type": "workout_duration",
        "response": response,
        "guidelines": guidelines
    }

def get_protein_info(user: UserData, cal_data: Dict) -> Dict:
    """Memberikan informasi detail tentang protein"""
    protein = cal_data['macros'].get('protein', cal_data['macros'].get('protein_g', 0))
    weight_kg = user.weight_kg
    
    response = f"**Protein Requirements for Your Goals:**\n\n"
    response += f"• **Current Target:** {protein}g daily\n"
    response += f"• **Per kg body weight:** {protein/weight_kg:.1f}g/kg\n\n"
    
    response += "**General Protein Guidelines:**\n"
    response += "• Sedentary: 0.8g/kg\n"
    response += "• Recreational athlete: 1.2-1.4g/kg\n"
    response += "• Endurance athlete: 1.4-1.6g/kg\n"
    response += "• Strength athlete: 1.6-2.2g/kg\n"
    response += "• Muscle building: 1.6-2.2g/kg\n"
    response += "• Fat loss: 2.2-2.6g/kg (preserve muscle)\n\n"
    
    response += "**Timing & Distribution:**\n"
    response += "• Spread over 3-5 meals (20-40g per meal)\n"
    response += "• Post-workout: 20-40g within 2 hours\n"
    response += "• Before bed: 20-40g casein protein\n\n"
    
    response += "**High-Quality Protein Sources:**\n"
    if user.vegan:
        response += "• Tofu/Tempeh: 15-20g per 100g\n• Lentils: 9g per 100g cooked\n• Chickpeas: 9g per 100g cooked\n• Quinoa: 8g per cup\n• Seitan: 25g per 100g\n• Protein powder (pea, rice, hemp)\n"
    else:
        response += "• Chicken breast: 31g per 100g\n• Salmon: 25g per 100g\n• Eggs: 6g per large egg\n• Greek yogurt: 10g per 100g\n• Cottage cheese: 11g per 100g\n• Lean beef: 26g per 100g\n"
    
    return {
        "type": "protein_info",
        "response": response,
        "daily_target": protein,
        "per_kg": protein/weight_kg
    }

def get_carb_info(user: UserData, cal_data: Dict) -> Dict:
    """Memberikan informasi detail tentang karbohidrat"""
    carbs = cal_data['macros'].get('carbs', cal_data['macros'].get('carbs_g', 0))
    
    response = f"**Carbohydrate Requirements for Your Goals:**\n\n"
    response += f"• **Current Target:** {carbs}g daily\n\n"
    
    response += "**Carbohydrate Functions:**\n"
    response += "• Primary energy source for exercise\n• Spares protein for muscle building\n• Fuels brain and nervous system\n• Supports recovery\n\n"
    
    response += "**Timing Strategies:**\n"
    response += "• **Pre-workout:** 20-40g complex carbs 1-2 hours before\n"
    response += "• **Intra-workout:** 15-30g simple carbs during long sessions (>90 min)\n"
    response += "• **Post-workout:** 30-60g simple + complex within 2 hours\n"
    response += "• **Non-training days:** Reduce by 20-30%\n\n"
    
    response += "**Quality Carbohydrate Sources:**\n"
    response += "• **Complex:** Sweet potatoes, oats, brown rice, quinoa, whole grains\n"
    response += "• **Fiber-rich:** Vegetables, fruits, legumes, whole grains\n"
    response += "• **Simple (timed):** Bananas, dates, honey, white rice (post-workout)\n\n"
    
    response += "**Activity Level Adjustments:**\n"
    activity_multipliers = {
        "sedentary": 2,
        "light": 3,
        "moderate": 4,
        "active": 5,
        "very_active": 6
    }
    
    multiplier = activity_multipliers.get(user.active_level, 4)
    response += f"For {user.active_level} activity: {multiplier}-{multiplier+1}g/kg body weight\n"
    
    return {
        "type": "carb_info",
        "response": response,
        "daily_target": carbs
    }

def get_fat_info(user: UserData, cal_data: Dict) -> Dict:
    """Memberikan informasi detail tentang lemak"""
    fat = cal_data['macros'].get('fat', cal_data['macros'].get('fat_g', 0))
    
    response = f"**Fat Requirements for Your Goals:**\n\n"
    response += f"• **Current Target:** {fat}g daily\n"
    response += f"• **Minimum for health:** 0.5-0.7g/kg body weight\n\n"
    
    response += "**Fat Functions:**\n"
    response += "• Hormone production (testosterone, estrogen)\n• Vitamin absorption (A, D, E, K)\n• Cell membrane structure\n• Brain health and cognitive function\n• Satiety and meal satisfaction\n\n"
    
    response += "**Types of Dietary Fat:**\n"
    response += "• **Monounsaturated (best):** Olive oil, avocados, nuts\n"
    response += "• **Polyunsaturated (essential):** Fish oil, flaxseeds, walnuts\n"
    response += "• **Saturated (moderate):** Coconut oil, butter, red meat\n"
    response += "• **Trans (avoid):** Processed foods, fried foods\n\n"
    
    response += "**Essential Fatty Acids:**\n"
    response += "• Omega-3: Anti-inflammatory, brain health (fish, chia, flax)\n"
    response += "• Omega-6: Pro-inflammatory in excess (vegetable oils, nuts)\n"
    response += "• Target ratio: 1:1 to 1:4 (Omega-3:Omega-6)\n\n"
    
    response += "**Practical Tips:**\n"
    response += "• Include healthy fats with each meal\n• Cook with stable fats (olive oil, coconut oil)\n• Add nuts/seeds to meals\n• Eat fatty fish 2-3x per week\n• Limit processed vegetable oils"
    
    return {
        "type": "fat_info",
        "response": response,
        "daily_target": fat
    }

def get_supplement_advice(user: UserData) -> Dict:
    """Memberikan saran supplement berdasarkan goal dan kebutuhan"""
    
    tier_1 = ["Protein Powder", "Creatine Monohydrate", "Omega-3/Fish Oil", "Multivitamin", "Vitamin D"]
    tier_2 = ["Caffeine", "Beta-Alanine", "Citrulline Malate", "BCAAs", "Pre-workout"]
    tier_3 = ["Testosterone Boosters", "Fat Burners", "Nootropics", "Specialized Stacks"]
    
    response = "**Supplement Recommendations (Tiered Approach):**\n\n"
    
    response += "**Tier 1 - Foundational (Consider for everyone):**\n"
    for supp in tier_1:
        response += f"• {supp}\n"
    response += "\n"
    
    response += "**Tier 2 - Performance (Based on specific goals):**\n"
    for supp in tier_2:
        response += f"• {supp}\n"
    response += "\n"
    
    response += "**Tier 3 - Specialized (Consult professional):**\n"
    for supp in tier_3:
        response += f"• {supp}\n"
    response += "\n"
    
    # Goal-specific recommendations
    response += f"**For {user.goal.replace('_', ' ').title()}: **\n"
    if user.goal == "fat_loss":
        response += "• Consider: Green tea extract, caffeine, L-carnitine\n"
        response += "• Focus on diet first, supplements second\n"
        response += "• Avoid stimulant overload\n"
    elif user.goal == "muscle_gain":
        response += "• Priority: Creatine, protein powder, HMB\n"
        response += "• Ensure calorie surplus before supplements\n"
        response += "• Consider intra-workout carbs/EAAs\n"
    
    response += "\n**Important Notes:**\n"
    response += "• Supplements complement, don't replace, good nutrition\n"
    response += "• Third-party tested brands only (NSF, Informed Sport)\n"
    response += "• Start with one new supplement at a time\n"
    response += "• Monitor effects and adjust as needed\n"
    response += "• Consult healthcare provider if on medications"
    
    return {
        "type": "supplement_advice",
        "response": response,
        "tiers": {"tier_1": tier_1, "tier_2": tier_2, "tier_3": tier_3}
    }

def get_hydration_advice(user: UserData) -> Dict:
    """Memberikan saran hidrasi"""
    weight_kg = user.weight_kg
    
    # Calculate baseline hydration
    baseline_ml = weight_kg * 30  # 30ml per kg
    baseline_liters = baseline_ml / 1000
    
    # Adjust for activity
    activity_adjustment = {
        "sedentary": 0,
        "light": 0.5,
        "moderate": 1.0,
        "active": 1.5,
        "very_active": 2.0
    }
    
    extra_liters = activity_adjustment.get(user.active_level, 1.0)
    total_liters = baseline_liters + extra_liters
    
    response = f"**Hydration Guidelines for Your Profile:**\n\n"
    response += f"• **Body weight:** {weight_kg}kg → Baseline: {baseline_liters:.1f}L\n"
    response += f"• **Activity level:** {user.active_level} → Add: {extra_liters:.1f}L\n"
    response += f"• **Total Daily Target:** {total_liters:.1f}-{total_liters+0.5:.1f}L\n\n"
    
    response += "**Timing Strategies:**\n"
    response += "• Upon waking: 500ml water\n"
    response += "• Pre-workout: 250-500ml 2-3 hours before\n"
    response += "• During workout: 200-300ml every 15-20 minutes\n"
    response += "• Post-workout: 500ml per pound lost during exercise\n"
    response += "• With meals: 250ml per meal\n"
    response += "• Before bed: 250ml\n\n"
    
    response += "**Electrolyte Considerations:**\n"
    response += "• Add electrolytes for sessions >60 minutes\n"
    response += "• Key electrolytes: Sodium, potassium, magnesium\n"
    response += "• Natural sources: Coconut water, banana, salty foods\n"
    response += "• Consider electrolyte tabs for intense/hot workouts\n\n"
    
    response += "**Hydration Indicators:**\n"
    response += "• Urine color: Pale yellow (goal), clear (overhydrated), dark (dehydrated)\n"
    response += "• Thirst: Drink before feeling thirsty\n"
    response += "• Performance: Dehydration reduces strength by 2%, power by 3%\n"
    response += "• Cognition: 1-2% dehydration impairs focus and mood\n\n"
    
    response += "**Special Considerations:**\n"
    if user.goal == "fat_loss":
        response += "• Water before meals can reduce calorie intake\n"
        response += "• Cold water increases calorie burn slightly\n"
    elif user.goal == "muscle_gain":
        response += "• Proper hydration supports protein synthesis\n"
        response += "• Muscle is 75% water - stay hydrated for fullness"
    
    return {
        "type": "hydration_advice",
        "response": response,
        "daily_target_liters": total_liters,
        "baseline": baseline_liters,
        "activity_adjustment": extra_liters
    }

def get_cheat_meal_advice(user: UserData) -> Dict:
    """Memberikan saran tentang cheat meals dan flexibility diet"""
    
    response = "**Smart Approach to Cheat Meals/Treats:**\n\n"
    
    response += "**Frequency Guidelines:**\n"
    if user.goal == "fat_loss":
        response += "• 1-2 cheat meals per week (not days)\n"
        response += "• Time strategically (post-workout, social events)\n"
        response += "• Keep to 20-25% of daily calories for the meal\n"
    elif user.goal == "muscle_gain":
        response += "• More flexibility due to calorie surplus\n"
        response += "• 2-3 higher calorie meals per week\n"
        response += "• Focus on hitting protein goals first\n"
    else:  # maintain
        response += "• 1-2 treats per week\n"
        response += "• Practice moderation, not deprivation\n"
        response += "• Listen to cravings mindfully\n\n"
    
    response += "**Strategies for Success:**\n"
    response += "1. **Plan Ahead:** Schedule cheat meals, don't impulse\n"
    response += "2. **Earn It:** Have productive workout before\n"
    response += "3. **Protein First:** Eat protein before cheat meal\n"
    response += "4. **Hydrate:** Drink water before and during\n"
    response += "5. **Slow Down:** Savor each bite, eat mindfully\n"
    response += "6. **No Guilt:** Enjoy it, then return to plan\n"
    response += "7. **Log It:** Track to maintain awareness\n\n"
    
    response += "**Healthier Alternatives:**\n"
    response += "• **Craving sweets:** Greek yogurt with honey, dark chocolate, protein bars\n"
    response += "• **Craving salty:** Homemade popcorn, baked sweet potato fries, roasted chickpeas\n"
    response += "• **Craving crunchy:** Apple slices, carrot sticks, rice cakes\n"
    response += "• **Craving creamy:** Protein pudding, avocado chocolate mousse, cottage cheese bowl\n\n"
    
    response += "**Post-Cheat Recovery:**\n"
    response += "• Next meal: Return to normal healthy eating\n"
    response += "• Hydrate well the next day\n"
    response += "• Light cardio or walking\n"
    response += "• Don't compensate with extreme restriction\n"
    response += "• Remember: One meal doesn't ruin progress\n"
    
    return {
        "type": "cheat_meal_advice",
        "response": response,
        "frequency": "1-2 per week" if user.goal == "fat_loss" else "2-3 per week"
    }

def get_vegan_nutrition_tips() -> Dict:
    """Memberikan tips nutrisi khusus untuk vegan"""
    response = "**Complete Vegan Nutrition Guide:**\n\n"
    
    response += "**Protein Sources (Combine for complete amino acids):**\n"
    response += "• Legumes + Grains = Complete protein (rice & beans)\n"
    response += "• Nuts/Seeds + Legumes\n"
    response += "• Soy products: Tofu, tempeh, edamame (complete)\n"
    response += "• Seitan (wheat gluten): High protein\n"
    response += "• Protein powders: Pea, rice, hemp, soy\n\n"
    
    response += "**Key Nutrients to Monitor:**\n"
    response += "• **Vitamin B12:** Supplement required (2.4mcg daily)\n"
    response += "• **Iron:** Plant sources + Vitamin C for absorption\n"
    response += "• **Calcium:** Fortified plant milks, tofu, leafy greens\n"
    response += "• **Omega-3:** Algae oil, flax, chia, walnuts\n"
    response += "• **Vitamin D:** Sun exposure or supplement\n"
    response += "• **Zinc:** Legumes, nuts, seeds, whole grains\n"
    response += "• **Iodine:** Iodized salt or seaweed\n\n"
    
    response += "**Meal Planning Tips:**\n"
    response += "• Include protein with every meal\n"
    response += "• Variety ensures nutrient completeness\n"
    response += "• Soak legumes/grains to reduce anti-nutrients\n"
    response += "• Consider fortified foods for key nutrients\n"
    response += "• Plan ahead for social situations\n\n"
    
    response += "**Vegan Fitness Specifics:**\n"
    response += "• Protein timing still important\n"
    response += "• May need slightly higher protein for muscle building\n"
    response += "• Creatine supplementation beneficial (all diets)\n"
    response += "• Beta-alanine good for performance\n"
    response += "• Watch calorie density - vegan can be high or low calorie\n"
    
    return {
        "type": "vegan_nutrition",
        "response": response,
        "key_nutrients": ["B12", "Iron", "Calcium", "Omega-3", "Vitamin D", "Zinc", "Iodine"]
    }

def get_meal_timing_advice(user: UserData) -> Dict:
    """Memberikan saran timing makan berdasarkan goal"""
    
    response = "**Optimal Meal Timing Strategies:**\n\n"
    
    response += "**General Principles:**\n"
    response += "• **Consistency:** Eat at similar times daily\n"
    response += "• **Frequency:** 3-5 meals based on preference\n"
    response += "• **Hunger cues:** Don't ignore true hunger\n"
    response += "• **Practicality:** Fit schedule, not force rigid timing\n\n"
    
    response += "**For Muscle Building:**\n"
    response += "• Pre-workout: Meal 2-3 hours before, snack 30-60 min before\n"
    response += "• Post-workout: Protein + carbs within 2 hours\n"
    response += "• Before bed: Casein protein or slow-digesting meal\n"
    response += "• Overnight fast: 8-10 hours maximum\n"
    response += "• Protein every 3-4 hours\n\n"
    
    response += "**For Fat Loss:**\n"
    response += "• Consider time-restricted eating (14:10 or 16:8)\n"
    response += "• Larger meals earlier in day\n"
    response += "• Last meal 2-3 hours before bed\n"
    response += "• Protein with every meal for satiety\n"
    response += "• Stay hydrated between meals\n\n"
    
    response += "**Workout Nutrition Timing:**\n"
    response += "**Pre-workout (1-2 hours before):**\n"
    response += "• Complex carbs + moderate protein + low fat\n"
    response += "• Example: Oats with protein powder\n\n"
    
    response += "**Intra-workout (if >90 minutes):**\n"
    response += "• BCAAs or electrolyte drink\n"
    response += "• Simple carbs for endurance\n\n"
    
    response += "**Post-workout (within 2 hours):**\n"
    response += "• Protein (20-40g) + Carbs (30-60g)\n"
    response += "• Example: Protein shake + banana\n\n"
    
    response += "**Special Considerations:**\n"
    response += "• Morning workouts: May train fasted or with small snack\n"
    response += "• Evening workouts: Post-workout meal = dinner\n"
    response += "• Shift workers: Maintain consistency relative to wake time\n"
    response += "• Intermittent fasting: Align workout with feeding window\n"
    
    return {
        "type": "meal_timing",
        "response": response,
        "recommended_frequency": "3-5 meals daily"
    }

def get_expected_results(user: UserData) -> Dict:
    """Memberikan ekspektasi hasil yang realistis"""
    
    response = f"**Realistic Expectations for {user.goal.replace('_', ' ').title()}:**\n\n"
    
    if user.goal == "fat_loss":
        response += "**Weekly Progress:**\n"
        response += "• Weight loss: 0.5-1% body weight per week (safe, sustainable)\n"
        response += "• Measurements: 0.5-1cm reduction in waist per month\n"
        response += "• Strength: Maintain or slight increase in lifts\n"
        response += "• Energy: Initial dip, then improvement\n\n"
        
        response += "**Monthly Expectations:**\n"
        response += "• 2-4kg fat loss (first month may be higher)\n"
        response += "• Noticeable clothing fit changes\n"
        response += "• Improved energy and sleep\n"
        response += "• Better workout endurance\n\n"
        
        response += "**3-Month Transformation:**\n"
        response += "• Significant visible changes\n"
        response += "• 6-12kg fat loss (depending on starting point)\n"
        response += "• Muscle definition emerging\n"
        response += "• Established healthy habits\n"
        
    elif user.goal == "muscle_gain":
        response += "**Weekly Progress:**\n"
        response += "• Weight gain: 0.25-0.5% body weight per week\n"
        response += "• Strength: 2.5-5kg increase on main lifts monthly\n"
        response += "• Measurements: Slow but steady increases\n"
        response += "• Recovery: Improving over time\n\n"
        
        response += "**Monthly Expectations:**\n"
        response += "• 1-2kg lean mass gain (beginners)\n"
        response += "• Noticeable pump and fullness\n"
        response += "• Clothes fitting tighter in right places\n"
        response += "• Improved workout capacity\n\n"
        
        response += "**3-Month Transformation:**\n"
        response += "• Visible muscle growth\n"
        response += "• 3-6kg lean mass (with proper training/nutrition)\n"
        response += "• Significant strength gains\n"
        response += "• Changed body composition\n"
        
    else:  # maintain
        response += "**Weekly Progress:**\n"
        response += "• Weight: Stable within 1-2kg range\n"
        response += "• Fitness: Gradual improvements\n"
        response += "• Energy: Consistent and stable\n"
        response += "• Wellbeing: Improving lifestyle habits\n\n"
        
        response += "**Monthly Expectations:**\n"
        response += "• Maintained weight and measurements\n"
        response += "• Improved workout performance\n"
        response += "• Better sleep and stress management\n"
        response += "• Sustainable routine established\n\n"
        
        response += "**3-Month Transformation:**\n"
        response += "• Solidified healthy habits\n"
        response += "• Consistent energy levels\n"
        response += "• Improved body composition\n"
        response += "• Long-term lifestyle established\n"
    
    response += "\n**Factors Affecting Results:**\n"
    response += "• Consistency (most important)\n• Sleep quality\n• Stress management\n• Genetic factors\n• Age and hormone levels\n• Previous training experience\n"
    
    return {
        "type": "expected_results",
        "response": response,
        "timeframes": ["weekly", "monthly", "3_months"]
    }

def get_progress_tracking_tips(user: UserData) -> Dict:
    """Memberikan tips melacak progress"""
    
    response = "**Comprehensive Progress Tracking Guide:**\n\n"
    
    response += "**What to Track:**\n"
    response += "1. **Weight:** Daily morning, weekly average (account for fluctuations)\n"
    response += "2. **Measurements:** Weekly (chest, waist, hips, arms, thighs)\n"
    response += "3. **Photos:** Monthly (same lighting, pose, clothing)\n"
    response += "4. **Strength:** Workout logs (weights, reps, sets)\n"
    response += "5. **Performance:** Cardio times, endurance, recovery\n"
    response += "6. **How You Feel:** Energy, sleep, mood, confidence\n\n"
    
    response += "**Tracking Methods:**\n"
    response += "• **Apps:** MyFitnessPal, Strong, Hevy, Google Sheets\n"
    response += "• **Journal:** Physical notebook for mindfulness\n"
    response += "• **Photos:** Monthly comparison shots\n"
    response += "• **Measurements:** Soft tape measure\n"
    response += "• **Scales:** Smart scales for body composition (estimate)\n\n"
    
    response += f"**Goal-Specific Tracking for {user.goal.replace('_', ' ')}:**\n"
    if user.goal == "fat_loss":
        response += "• Focus: Waist measurement, weekly weight trend\n"
        response += "• Non-scale victories: Clothing fit, energy, workout performance\n"
        response += "• Beware: Daily fluctuations, water weight, menstrual cycle effects\n"
    elif user.goal == "muscle_gain":
        response += "• Focus: Strength increases, measurements, photos\n"
        response += "• Track: Progressive overload in workouts\n"
        response += "• Patience: Muscle growth slower than fat loss visually\n"
    
    response += "\n**Common Tracking Mistakes to Avoid:**\n"
    response += "• Obsessing over daily scale weight\n"
    response += "• Comparing to others (genetics vary)\n"
    response += "• Not tracking consistently\n"
    response += "• Only tracking one metric\n"
    response += "• Getting discouraged by temporary plateaus\n\n"
    
    response += "**When to Adjust Your Plan:**\n"
    response += "• Weight unchanged for 3-4 weeks (with consistency)\n"
    response += "• Measurements not changing\n"
    response += "• Strength plateauing for multiple sessions\n"
    response += "• Feeling constantly fatigued or sore\n"
    response += "• Lifestyle changes requiring adaptation\n"
    
    return {
        "type": "progress_tracking",
        "response": response,
        "metrics": ["weight", "measurements", "photos", "strength", "performance", "subjective"]
    }

def handle_plateau_advice(user: UserData) -> Dict:
    """Memberikan saran untuk mengatasi plateau"""
    
    response = "**Breaking Through Plateaus:**\n\n"
    
    response += "**First: Identify the Cause**\n"
    response += "1. **Nutrition:** Calories not adjusted as weight changes\n"
    response += "2. **Training:** No progressive overload\n"
    response += "3. **Recovery:** Insufficient sleep or stress management\n"
    response += "4. **Adaptation:** Body adapted to current routine\n"
    response += "5. **Compliance:** Not following plan consistently\n\n"
    
    response += f"**Plateau Solutions for {user.goal.replace('_', ' ')}:**\n"
    
    if user.goal == "fat_loss":
        response += "**Nutrition Adjustments:**\n"
        response += "• Recalculate TDEE at new weight\n"
        response += "• Reduce calories by 10-15% (or increase activity)\n"
        response += "• Increase protein to preserve muscle\n"
        response += "• Try carb cycling or refeed day\n"
        response += "• Track more accurately (weigh food)\n\n"
        
        response += "**Training Adjustments:**\n"
        response += "• Increase workout intensity or volume\n"
        response += "• Add HIIT sessions\n"
        response += "• Change exercise selection\n"
        response += "• Increase daily activity (NEAT)\n"
        response += "• Deload week if overtrained\n"
        
    elif user.goal == "muscle_gain":
        response += "**Nutrition Adjustments:**\n"
        response += "• Increase calories by 10-15%\n"
        response += "• Ensure adequate protein (1.6-2.2g/kg)\n"
        response += "• Adjust macro ratios\n"
        response += "• Consider peri-workout nutrition\n"
        response += "• Track to ensure surplus\n\n"
        
        response += "**Training Adjustments:**\n"
        response += "• Increase training volume\n"
        response += "• Change rep ranges (try lower reps for strength)\n"
        response += "• Incorporate new exercises\n"
        response += "• Focus on weak points\n"
        response += "• Ensure adequate rest between sets\n"
    
    response += "\n**General Strategies:**\n"
    response += "• **Deload Week:** Reduce volume 40-60% for recovery\n"
    response += "• **Change Stimulus:** New exercises, different rep schemes\n"
    response += "• **Increase NEAT:** Non-exercise activity thermogenesis\n"
    response += "• **Sleep Optimization:** Aim for 7-9 hours quality sleep\n"
    response += "• **Stress Management:** High cortisol affects results\n"
    response += "• **Patience:** Plateaus are normal, part of process\n\n"
    
    response += "**When to Seek Help:**\n"
    response += "• Plateau lasts >8 weeks with perfect compliance\n"
    response += "• Experiencing signs of overtraining\n"
    response += "• Suspected metabolic adaptation\n"
    response += "• Considering extreme measures\n"
    
    return {
        "type": "plateau_advice",
        "response": response,
        "strategies": ["nutrition_adjustment", "training_change", "recovery_focus", "deload"]
    }

def get_motivation_tips(user: UserData) -> Dict:
    """Memberikan tips motivasi dan konsistensi"""
    
    response = "**Staying Motivated & Consistent:**\n\n"
    
    response += "**Mindset Shifts:**\n"
    response += "• **Process over outcome:** Focus on daily habits\n"
    response += "• **Identity-based:** \"I am someone who...\"\n"
    response += "• **Progress, not perfection:** Celebrate small wins\n"
    response += "• **Long-term perspective:** This is a lifestyle\n"
    response += "• **Self-compassion:** Forgive slip-ups, move forward\n\n"
    
    response += "**Practical Strategies:**\n"
    response += "1. **Habit Stacking:** Link new habits to existing ones\n"
    response += "2. **Environment Design:** Make healthy choices easy\n"
    response += "3. **Accountability:** Workout buddy, coach, or app\n"
    response += "4. **Schedule It:** Treat workouts like important meetings\n"
    response += "5. **Preparation:** Meal prep, gym bag ready\n"
    response += "6. **The 2-Minute Rule:** Just start for 2 minutes\n"
    response += "7. **Track Progress:** Visual evidence keeps you going\n"
    response += "8. **Reward System:** Non-food rewards for milestones\n\n"
    
    response += "**When Motivation is Low:**\n"
    response += "• **Scale back:** Do half the workout\n"
    response += "• **Change it up:** Try a new activity\n"
    response += "• **Remember why:** Revisit your original reasons\n"
    response += "• **5-minute commitment:** Just show up for 5 minutes\n"
    response += "• **Social support:** Call a friend, join a class\n"
    response += "• **Focus on feeling:** How you feel after, not before\n\n"
    
    response += f"**Goal-Specific Motivation for {user.goal.replace('_', ' ')}:**\n"
    if user.goal == "fat_loss":
        response += "• Take monthly progress photos\n"
        response += "• Notice non-scale victories\n"
        response += "• Focus on how clothes fit\n"
        response += "• Celebrate every 5% body weight lost\n"
    elif user.goal == "muscle_gain":
        response += "• Track strength increases\n"
        response += "• Notice pump and fullness\n"
        response += "• Celebrate new personal records\n"
        response += "• Focus on how you perform, not just look\n"
    
    response += "\n**Building Lasting Habits:**\n"
    response += "• **Consistency > Intensity:** Regular moderate effort beats sporadic maximum effort\n"
    response += "• **Identity:** \"I'm a healthy person\" not \"I'm on a diet\"\n"
    response += "• **Small Changes:** 1% better daily compounds\n"
    response += "• **Flexibility:** Life happens, adapt and continue\n"
    response += "• **Enjoyment:** Find activities and foods you genuinely like\n"
    
    return {
        "type": "motivation_tips",
        "response": response,
        "strategies": ["mindset", "practical", "low_motivation", "habit_building"]
    }

def get_sleep_advice() -> Dict:
    """Memberikan saran optimasi tidur"""
    
    response = "**Sleep Optimization for Fitness & Recovery:**\n\n"
    
    response += "**Why Sleep Matters for Fitness:**\n"
    response += "• Muscle repair and growth occurs during sleep\n"
    response += "• Hormone regulation (growth hormone, testosterone)\n"
    response += "• Recovery from training stress\n"
    response += "• Appetite regulation (leptin/ghrelin)\n"
    response += "• Cognitive function and motivation\n\n"
    
    response += "**Optimal Sleep Guidelines:**\n"
    response += "• **Duration:** 7-9 hours for adults, athletes may need 8-10\n"
    response += "• **Consistency:** Same bed/wake times (±30 minutes)\n"
    response += "• **Quality:** Uninterrupted, deep sleep cycles\n\n"
    
    response += "**Sleep Hygiene Checklist:**\n"
    response += "1. **Temperature:** 18-21°C (cool room)\n"
    response += "2. **Darkness:** Blackout curtains, no electronics\n"
    response += "3. **Quiet:** White noise if needed\n"
    response += "4. **Routine:** Wind down 60 minutes before bed\n"
    response += "5. **Bed:** Comfortable mattress and pillows\n"
    response += "6. **Electronics:** No screens 60 minutes before\n"
    response += "7. **Caffeine:** None after 2 PM\n"
    response += "8. **Alcohol:** Limits sleep quality\n"
    response += "9. **Exercise:** Morning/afternoon better than evening\n"
    response += "10. **Light:** Morning sunlight exposure\n\n"
    
    response += "**Pre-Bed Routine Suggestions:**\n"
    response += "• **60 min before:** Dim lights, no screens\n"
    response += "• **30 min before:** Reading, meditation, gentle stretching\n"
    response += "• **15 min before:** Gratitude journal, breathing exercises\n"
    response += "• **Bedtime:** Consistent signal (herbal tea, etc.)\n\n"
    
    response += "**Nutrition for Sleep:**\n"
    response += "• **Evening meal:** 2-3 hours before bed, not too large\n"
    response += "• **Protein:** Casein protein before bed can aid recovery\n"
    response += "• **Carbohydrates:** May help tryptophan conversion to melatonin\n"
    response += "• **Magnesium:** Natural muscle relaxant (leafy greens, nuts)\n"
    response += "• **Hydration:** Balance - hydrated but not waking to urinate\n\n"
    
    response += "**When Sleep is Poor:**\n"
    response += "• **Next day:** Lighter workout, focus on recovery\n"
    response += "• **Nutrition:** Ensure adequate protein for recovery\n"
    response += "• **Hydration:** Particularly important\n"
    response += "• **Patience:** One bad night won't ruin progress\n"
    
    return {
        "type": "sleep_advice",
        "response": response,
        "key_points": ["7-9 hours", "consistency", "sleep hygiene", "pre-bed routine"]
    }

def get_stress_management_tips() -> Dict:
    """Memberikan tips manajemen stress"""
    
    response = "**Stress Management for Optimal Fitness Results:**\n\n"
    
    response += "**How Stress Affects Fitness:**\n"
    response += "• **Cortisol:** Chronic high levels promote fat storage (especially abdominal)\n"
    response += "• **Recovery:** Impairs muscle repair and growth\n"
    response += "• **Motivation:** Reduces drive to exercise\n"
    response += "• **Sleep:** Disrupts sleep quality\n"
    response += "• **Appetite:** Often increases cravings for high-calorie foods\n\n"
    
    response += "**Stress Identification:**\n"
    response += "• Physical signs: Headaches, muscle tension, fatigue\n"
    response += "• Emotional signs: Irritability, anxiety, overwhelm\n"
    response += "• Behavioral signs: Sleep changes, appetite changes, procrastination\n"
    response += "• Cognitive signs: Racing thoughts, difficulty concentrating\n\n"
    
    response += "**Effective Stress Management Techniques:**\n"
    response += "**Physical:**\n"
    response += "• Exercise (moderate, not excessive)\n"
    response += "• Yoga or stretching\n"
    response += "• Deep breathing exercises\n"
    response += "• Progressive muscle relaxation\n\n"
    
    response += "**Mental/Emotional:**\n"
    response += "• Meditation (even 5-10 minutes daily)\n"
    response += "• Journaling thoughts and feelings\n"
    response += "• Gratitude practice\n"
    response += "• Time in nature\n"
    response += "• Digital detox periods\n\n"
    
    response += "**Lifestyle:**\n"
    response += "• Time management and prioritization\n"
    response += "• Setting boundaries\n"
    response += "• Saying no when needed\n"
    response += "• Social connection and support\n"
    response += "• Hobbies and leisure activities\n\n"
    
    response += "**Nutrition for Stress Management:**\n"
    response += "• **Magnesium:** Natural relaxant (leafy greens, nuts, seeds)\n"
    response += "• **Omega-3:** Anti-inflammatory (fatty fish, flaxseeds)\n"
    response += "• **B Vitamins:** Energy and nervous system (whole grains, eggs)\n"
    response += "• **Adaptogens:** Ashwagandha, rhodiola (consult professional)\n"
    response += "• **Hydration:** Dehydration increases cortisol\n"
    response += "• **Limit:** Caffeine, alcohol, processed foods\n\n"
    
    response += "**When to Adjust Training for Stress:**\n"
    response += "• High stress periods: Reduce intensity/volume 20-30%\n"
    response += "• Focus on movement you enjoy\n"
    response += "• Prioritize recovery activities\n"
    response += "• Consider deload week\n"
    response += "• Listen to body signals\n"
    
    return {
        "type": "stress_management",
        "response": response,
        "techniques": ["physical", "mental", "lifestyle", "nutritional"]
    }

def get_energy_boost_tips(user: UserData) -> Dict:
    """Memberikan tips meningkatkan energi"""
    
    response = "**Sustainable Energy Boost Strategies:**\n\n"
    
    response += "**Identify Energy Drains:**\n"
    response += "• Poor sleep quality or duration\n"
    response += "• Nutritional deficiencies\n"
    response += "• Dehydration\n"
    response += "• Chronic stress\n"
    response += "• Overtraining or insufficient recovery\n"
    response += "• Blood sugar fluctuations\n\n"
    
    response += "**Nutrition for Steady Energy:**\n"
    response += "• **Regular meals:** Every 3-4 hours to stabilize blood sugar\n"
    response += "• **Protein with each meal:** Slows digestion, sustained energy\n"
    response += "• **Complex carbohydrates:** Oats, sweet potatoes, quinoa\n"
    response += "• **Healthy fats:** Avocado, nuts, olive oil\n"
    response += "• **Iron-rich foods:** Especially important for women (leafy greens, red meat)\n"
    response += "• **B vitamins:** Energy metabolism (whole grains, eggs, legumes)\n"
    response += "• **Hydration:** Even mild dehydration causes fatigue\n"
    response += "• **Limit:** Sugar crashes, excessive caffeine\n\n"
    
    response += "**Lifestyle Energy Boosters:**\n"
    response += "• **Morning sunlight:** Regulates circadian rhythm\n"
    response += "• **Movement breaks:** 5-minute walk every hour\n"
    response += "• **Posture:** Sitting upright improves energy\n"
    response += "• **Power nap:** 10-20 minutes (not longer)\n"
    response += "• **Cold exposure:** Cold shower boosts alertness\n"
    response += "• **Social interaction:** Positive social energy\n\n"
    
    response += f"**For {user.goal.replace('_', ' ')} Training Energy:**\n"
    if user.goal == "fat_loss":
        response += "• Pre-workout: Small protein + complex carb snack\n"
        response += "• Timing: Train when natural energy is highest\n"
        response += "• Intensity: Moderate, sustainable sessions\n"
        response += "• Recovery: Adequate between sessions\n"
    elif user.goal == "muscle_gain":
        response += "• Pre-workout: Carbohydrate focused meal 2-3 hours before\n"
        response += "• Intra-workout: BCAAs or electrolyte drink if long session\n"
        response += "• Post-workout: Quick carbs + protein for recovery\n"
        response += "• Volume: Manage to avoid chronic fatigue\n"
    
    response += "\n**When Fatigue Persists:**\n"
    response += "• Check sleep quality and duration\n"
    response += "• Consider blood tests for deficiencies\n"
    response += "• Evaluate training volume\n"
    response += "• Assess stress levels\n"
    response += "• Consult healthcare provider if chronic\n"
    
    return {
        "type": "energy_boost",
        "response": response,
        "strategies": ["nutrition", "lifestyle", "training_specific", "investigation"]
    }

def get_immune_boost_tips() -> Dict:
    """Memberikan tips meningkatkan sistem imun"""
    
    response = "**Immune System Support for Active Individuals:**\n\n"
    
    response += "**Why Athletes Need Immune Support:**\n"
    response += "• Intense exercise temporarily suppresses immune function\n"
    response += "• Training stress increases susceptibility\n"
    response += "• Adequate recovery is crucial\n"
    response += "• Nutrition plays key role in immune health\n\n"
    
    response += "**Nutrition for Immune Function:**\n"
    response += "• **Vitamin C:** Citrus, bell peppers, broccoli (500-1000mg daily)\n"
    response += "• **Vitamin D:** Sun exposure, fatty fish, fortified foods\n"
    response += "• **Zinc:** Meat, shellfish, legumes, seeds (15-30mg daily)\n"
    response += "• **Selenium:** Brazil nuts, tuna, eggs\n"
    response += "• **Probiotics:** Yogurt, kefir, fermented foods\n"
    response += "• **Protein:** Adequate for antibody production\n"
    response += "• **Antioxidants:** Colorful fruits and vegetables\n\n"
    
    response += "**Lifestyle Immune Support:**\n"
    response += "• **Sleep:** 7-9 hours for immune cell production\n"
    response += "• **Stress management:** Chronic stress suppresses immunity\n"
    response += "• **Hydration:** Mucous membrane health\n"
    response += "• **Hand hygiene:** Basic but effective\n"
    response += "• **Moderate exercise:** Boosts immunity, excessive can suppress\n\n"
    
    response += "**Training Considerations:**\n"
    response += "• **Listen to body:** Train, don't strain when feeling off\n"
    response += "• **Recovery:** Allow adaptation to training stress\n"
    response += "• **Deload:** Regular planned recovery weeks\n"
    response += "• **Intensity management:** Periodize training\n"
    response += "• **Post-exercise:** Refuel within 30-60 minutes\n\n"
    
    response += "**When Sick:**\n"
    response += "• **Above the neck rule:** Light activity okay if symptoms above neck only\n"
    response += "• **Below the neck rule:** Rest if symptoms below neck (fever, body aches)\n"
    response += "• **Nutrition:** Hydration, easy to digest foods\n"
    response += "• **Return gradually:** Don't jump back to full intensity\n"
    response += "• **Listen to body:** Recovery is priority\n\n"
    
    response += "**Supplements for Immune Support (Consider):**\n"
    response += "• Vitamin D (if deficient)\n"
    response += "• Zinc (short-term during illness)\n"
    response += "• Vitamin C (may reduce duration)\n"
    response += "• Probiotics (gut-immune connection)\n"
    response += "• Elderberry (some evidence for viral illnesses)\n"
    
    return {
        "type": "immune_support",
        "response": response,
        "key_nutrients": ["Vitamin C", "Vitamin D", "Zinc", "Probiotics", "Protein"]
    }

def get_age_specific_advice(user: UserData) -> Dict:
    """Memberikan saran berdasarkan usia"""
    
    response = "**Age-Specific Fitness Considerations:**\n\n"
    
    response += "**General Age-Related Changes:**\n"
    response += "• **Muscle mass:** Decreases ~3-8% per decade after 30\n"
    response += "• **Metabolism:** Slows 1-2% per decade\n"
    response += "• **Recovery:** Takes longer with age\n"
    response += "• **Hormones:** Gradual changes affect body composition\n"
    response += "• **Joint health:** Wear and tear considerations\n\n"
    
    response += "**Teens & 20s (16-29):**\n"
    response += "• **Strengths:** Peak recovery, hormone optimization\n"
    response += "• **Focus:** Build foundation, learn proper form\n"
    response += "• **Nutrition:** Support growth and activity\n"
    response += "• **Recovery:** Quick but don't overdo volume\n"
    response += "• **Caution:** Avoid ego lifting, prioritize longevity\n\n"
    
    response += "**30s & 40s (30-49):**\n"
    response += "• **Strengths:** Discipline, life experience\n"
    response += "• **Focus:** Maintain muscle, manage stress\n"
    response += "• **Nutrition:** Protein emphasis, manage calories\n"
    response += "• **Recovery:** More important, prioritize sleep\n"
    response += "• **Training:** Smart programming, listen to body\n\n"
    
    response += "**50s & Beyond (50+):**\n"
    response += "• **Strengths:** Wisdom, consistency\n"
    response += "• **Focus:** Mobility, strength maintenance, bone health\n"
    response += "• **Nutrition:** Higher protein, bone-support nutrients\n"
    response += "• **Recovery:** Essential, allow more time\n"
    response += "• **Training:** Lower impact options, joint-friendly\n\n"
    
    response += "**Training Adjustments with Age:**\n"
    response += "• **Warm-up:** Longer, more comprehensive\n"
    response += "• **Volume:** May need to decrease or manage\n"
    response += "• **Intensity:** Can remain high with proper recovery\n"
    response += "• **Frequency:** May benefit from more frequent, shorter sessions\n"
    response += "• **Variety:** Include mobility and flexibility work\n\n"
    
    response += "**Nutritional Considerations:**\n"
    response += "• **Protein:** Higher needs to combat sarcopenia\n"
    response += "• **Calcium/Vitamin D:** Bone health emphasis\n"
    response += "• **Fiber:** Digestive health\n"
    response += "• **Hydration:** Thirst sensation may decrease\n"
    response += "• **Micronutrients:** Possible increased needs\n\n"
    
    response += "**Mindset for Aging Well:**\n"
    response += "• Focus on function, not just appearance\n"
    response += "• Celebrate what body can do\n"
    response += "• Patience with progress\n"
    response += "• Consistency over intensity\n"
    response += "• Healthspan over lifespan\n"
    
    return {
        "type": "age_specific_advice",
        "response": response,
        "age_groups": {"teens_20s": "16-29", "30s_40s": "30-49", "50s_plus": "50+"}
    }

def get_womens_health_tips() -> Dict:
    """Memberikan tips kesehatan khusus wanita"""
    
    response = "**Women's Health & Fitness Considerations:**\n\n"
    
    response += "**Menstrual Cycle Awareness:**\n"
    response += "• **Follicular phase (day 1-14):** Higher energy, better strength\n"
    response += "• **Ovulation (day 14):** Peak performance potential\n"
    response += "• **Luteal phase (day 15-28):** Lower energy, increased cravings\n"
    response += "• **Menstruation (day 1-5):** Listen to body, adjust as needed\n"
    response += "• **Tracking:** Helps understand energy patterns\n\n"
    
    response += "**Cycle-Synced Training Suggestions:**\n"
    response += "• **Menstrual phase:** Light activity, yoga, walking\n"
    response += "• **Follicular phase:** Strength training, new exercises\n"
    response += "• **Ovulation:** Peak performance, PR attempts\n"
    response += "• **Luteal phase:** Maintenance, moderate intensity\n"
    response += "• **Listen to body:** Individual variation exists\n\n"
    
    response += "**Nutrition Considerations:**\n"
    response += "• **Iron:** Women need more due to menstruation\n"
    response += "• **Calcium:** Bone health, especially pre-menopause\n"
    response += "• **Protein:** Same needs as men relative to body weight\n"
    response += "• **Cravings:** May increase pre-menstrually\n"
    response += "• **Hydration:** Important throughout cycle\n\n"
    
    response += "**Strength Training for Women:**\n"
    response += "• **Myth busting:** Lifting heavy won't make you bulky\n"
    response += "• **Benefits:** Bone density, metabolism, body composition\n"
    response += "• **Program design:** Similar principles to men\n"
    response += "• **Progressive overload:** Essential for results\n"
    response += "• **Recovery:** May vary through cycle\n\n"
    
    response += "**Life Stage Considerations:**\n"
    response += "• **Pregnancy:** Consult provider, modified exercise\n"
    response += "• **Postpartum:** Gradual return, pelvic floor focus\n"
    response += "• **Perimenopause:** Hormone changes, adjust nutrition\n"
    response += "• **Menopause:** Focus on bone health, muscle maintenance\n"
    response += "• **Post-menopause:** Continue strength training\n\n"
    
    response += "**Common Concerns:**\n"
    response += "• **Body image:** Focus on strength and health\n"
    response += "• **Time management:** Efficient workouts effective\n"
    response += "• **Social support:** Find community\n"
    response += "• **Consistency:** Over perfection\n"
    response += "• **Self-compassion:** Especially through hormonal changes\n"
    
    return {
        "type": "womens_health",
        "response": response,
        "key_topics": ["menstrual_cycle", "nutrition", "strength_training", "life_stages"]
    }

def get_mens_health_tips() -> Dict:
    """Memberikan tips kesehatan khusus pria"""
    
    response = "**Men's Health & Fitness Considerations:**\n\n"
    
    response += "**Testosterone & Hormone Health:**\n"
    response += "• **Natural optimization:** Sleep, stress management, nutrition\n"
    response += "• **Strength training:** Compound lifts support testosterone\n"
    response += "• **Body fat:** Excess fat converts testosterone to estrogen\n"
    response += "• **Sleep:** Critical for hormone production\n"
    response += "• **Age-related decline:** Gradual, can be mitigated\n\n"
    
    response += "**Common Men's Health Issues:**\n"
    response += "• **Prostate health:** Regular check-ups, healthy diet\n"
    response += "• **Heart health:** Cardio important, manage cholesterol\n"
    response += "• **Mental health:** Often overlooked, seek support\n"
    response += "• **Injuries:** Ego lifting common cause\n"
    response += "• **Recovery:** May ignore signs of overtraining\n\n"
    
    response += "**Training Considerations:**\n"
    response += "• **Balanced development:** Don't just train \"mirror muscles\"\n"
    response += "• **Posture correction:** Desk jobs create imbalances\n"
    response += "• **Mobility:** Often neglected, crucial for longevity\n"
    response += "• **Recovery:** Allow for adaptation, not just more volume\n"
    response += "• **Form:** Quality over weight on bar\n\n"
    
    response += "**Nutrition for Men's Health:**\n"
    response += "• **Zinc:** Important for testosterone (oysters, meat, nuts)\n"
    response += "• **Magnesium:** Muscle function, stress management\n"
    response += "• **Healthy fats:** Hormone production\n"
    response += "• **Fiber:** Digestive health, heart health\n"
    response += "• **Antioxidants:** Combat oxidative stress\n\n"
    
    response += "**Life Stage Considerations:**\n"
    response += "• **20s-30s:** Build foundation, prevent future issues\n"
    response += "• **40s-50s:** Maintain muscle, manage stress\n"
    response += "• **60s+:** Focus on mobility, strength maintenance\n"
    response += "• **Andropause:** Gradual hormone changes\n"
    response += "• **Longevity:** Train for quality of life\n\n"
    
    response += "**Mindset & Mental Health:**\n"
    response += "• **Vulnerability:** Strength in asking for help\n"
    response += "• **Balance:** Fitness as part of life, not entire identity\n"
    response += "• **Purpose:** Beyond appearance\n"
    response += "• **Community:** Training partners, support systems\n"
    response += "• **Consistency:** Over years, not weeks\n\n"
    
    response += "**Prevention Focus:**\n"
    response += "• **Regular check-ups:** Don't avoid doctors\n"
    response += "• **Injury prevention:** Warm-up, proper form\n"
    response += "• **Health metrics:** Blood pressure, cholesterol, blood sugar\n"
    response += "• **Lifestyle factors:** Sleep, stress, relationships\n"
    response += "• **Long-term view:** Healthspan over lifespan\n"
    
    return {
        "type": "mens_health",
        "response": response,
        "key_topics": ["hormone_health", "common_issues", "training", "nutrition", "life_stages"]
    }

def get_general_health_tips(user: UserData) -> str:
    """Memberikan tips kesehatan umum"""
    
    tips = [
        "**Sleep:** Prioritize 7-9 hours quality sleep - it's when recovery happens",
        "**Hydration:** Drink 3-4L water daily, more if active - affects every bodily function",
        "**Movement:** Don't just exercise - move throughout day (walk, stand, stretch)",
        "**Stress Management:** Chronic stress affects body composition and health",
        "**Whole Foods:** Base diet on minimally processed foods",
        "**Social Connection:** Relationships impact health as much as diet/exercise",
        "**Sunlight:** Morning sun regulates circadian rhythm and vitamin D",
        "**Mindfulness:** Reduce stress, improve eating habits, enhance workout focus",
        "**Consistency:** Small daily habits beat occasional perfection",
        "**Enjoyment:** Find physical activities and foods you genuinely like"
    ]
    
    response = "**Holistic Health & Wellness Tips:**\n\n"
    response += "• " + "\n• ".join(tips)
    
    response += f"\n\n**For Your {user.goal.replace('_', ' ')} Goal:**\n"
    if user.goal == "fat_loss":
        response += "• Focus on sustainable changes, not quick fixes\n"
        response += "• Build habits that last beyond reaching goal weight\n"
        response += "• Celebrate non-scale victories\n"
    elif user.goal == "muscle_gain":
        response += "• Patience - muscle growth takes time\n"
        response += "• Recovery is when growth happens\n"
        response += "• Nutrition supports training efforts\n"
    
    return response

def format_workout_day_response(day: Dict) -> Dict:
    """Format response untuk workout day tertentu"""
    workout_text = f"**Day {day.get('day', 1)}: {day.get('type', 'workout').upper()} DAY**\n\n"
    
    if day.get('type') == 'rest':
        workout_text += "**Rest & Recovery Day**\n\n"
        workout_text += "**Active Recovery Suggestions:**\n"
        workout_text += "• Light walking (20-30 minutes)\n"
        workout_text += "• Stretching or yoga\n"
        workout_text += "• Foam rolling\n"
        workout_text += "• Focus on hydration and nutrition\n"
    else:
        workout_text += "**Workout Plan:**\n\n"
        workout_text += format_workout_list(day.get('workout', []))
        
        workout_text += "\n**Workout Notes:**\n"
        if 'focus' in day:
            workout_text += f"• Focus: {day['focus']}\n"
        workout_text += "• Warm-up: 5-10 minutes dynamic stretching\n"
        workout_text += "• Cool-down: 5 minutes static stretching\n"
        workout_text += "• Hydrate throughout workout\n"
        workout_text += "• Listen to your body, adjust as needed\n"
    
    return {
        "type": "workout_day_detail",
        "response": workout_text,
        "workout_day": day
    }

def calculate_target_weight(user: UserData) -> float:
    """Calculate reasonable target weight based on current weight and goal"""
    if user.target_weight:
        return user.target_weight
    
    if user.goal == "fat_loss":
        # Reasonable 10-15% weight loss as initial target
        return user.weight_kg * 0.85
    elif user.goal == "muscle_gain":
        # Reasonable 5-10% weight gain
        return user.weight_kg * 1.08
    else:
        # Maintenance - stay within 3% of current
        return user.weight_kg

def handle_grocery_queries(user: UserData, query: str, context: Optional[Dict]) -> Dict:
    """Handle pertanyaan tentang grocery list"""
    
    if 'list' in query or 'grocery' in query:
        # Generate meal plan to get grocery list
        meal_plan_data = generate_meal_plan_only(user)
        grocery_list = meal_plan_data.get("grocery_list", [])
        
        response = "**Your Smart Grocery List:**\n\n"
        
        # Organize by category
        categories = {}
        for item in grocery_list:
            if isinstance(item, dict):
                item_name = item.get('item', '')
                # Simple categorization
                if any(protein in item_name for protein in ['chicken', 'egg', 'tofu', 'tempeh', 'tuna', 'chickpea', 'lentil']):
                    category = "Proteins"
                elif any(carb in item_name for carb in ['rice', 'oats', 'pasta', 'bread']):
                    category = "Carbs"
                elif any(veg in item_name for veg in ['vegetable', 'spinach', 'broccoli', 'onion', 'garlic']):
                    category = "Vegetables"
                elif any(dairy in item_name for dairy in ['milk', 'yogurt', 'soy_milk']):
                    category = "Dairy & Alternatives"
                else:
                    category = "Seasonings & Others"
                
                if category not in categories:
                    categories[category] = []
                
                categories[category].append(item)
        
        for category, items in categories.items():
            response += f"**{category.upper()}:**\n"
            for item in items:
                if isinstance(item, dict):
                    name = item.get('item', '').replace('_', ' ').title()
                    grams = item.get('total_grams', 0)
                    cost = item.get('total_cost', 0)
                    response += f"• {name}: {grams}g"
                    if cost and cost > 0:
                        response += f" (Rp{cost:,})"
                    response += "\n"
            response += "\n"
        
        # Add total cost if available
        if grocery_list and isinstance(grocery_list[-1], dict) and grocery_list[-1].get('item') == "TOTAL WEEKLY COST":
            total_cost = grocery_list[-1].get('total_cost', 0)
            if total_cost > 0:
                response += f"**Total Weekly Cost:** Rp{total_cost:,}\n"
        
        response += "\n**Shopping Tips:**\n"
        response += "• Shop perimeter of store first (produce, meat, dairy)\n"
        response += "• Buy in-season produce for cost savings\n"
        response += "• Consider frozen fruits/vegetables for longevity\n"
        response += "• Bulk buy staples like rice, oats, beans\n"
        response += "• Read labels for added sugars and sodium\n"
        
        return {
            "type": "grocery_list",
            "response": response,
            "grocery_data": grocery_list
        }
    
    elif any(word in query for word in ['budget', 'cost', 'expensive', 'cheap']):
        response = "**Budget-Friendly Nutrition Tips:**\n\n"
        response += "**Protein Sources:**\n"
        response += "• Eggs (excellent cost:protein ratio)\n"
        response += "• Canned tuna/salmon\n"
        response += "• Chicken thighs (often cheaper than breast)\n"
        response += "• Legumes (beans, lentils, chickpeas)\n"
        response += "• Greek yogurt (bulk containers)\n\n"
        
        response += "**Produce Tips:**\n"
        response += "• Buy in-season fruits/vegetables\n"
        response += "• Frozen is often more nutritious and cheaper\n"
        response += "• Root vegetables last longer\n"
        response += "• Local farmers markets can be affordable\n\n"
        
        response += "**Smart Shopping:**\n"
        response += "• Plan meals for the week\n"
        response += "• Buy generic/store brands\n"
        response += "• Use unit pricing to compare\n"
        response += "• Bulk buy staples\n"
        response += "• Limit processed/convenience foods\n"
        
        return {
            "type": "budget_nutrition",
            "response": response
        }
    
    else:
        return {
            "type": "grocery_general",
            "response": "I can help with your grocery shopping! Ask me for:\n\n• Your personalized grocery list\n• Budget-friendly nutrition tips\n• How to shop smart for your meal plan\n• Storage and meal prep advice",
            "suggestions": [
                "Show me my grocery list",
                "Budget-friendly food options",
                "Meal prep tips",
                "How to store food properly"
            ]
        }

def handle_recipe_queries(user: UserData, query: str, context: Optional[Dict]) -> Dict:
    """Handle pertanyaan tentang resep dan memasak"""
    
    if 'easy' in query or 'simple' in query or 'quick' in query:
        response = "**Quick & Easy Healthy Recipes:**\n\n"
        
        response += "**Breakfast (5 minutes):**\n"
        response += "• Overnight oats: Mix oats, milk, protein powder, refrigerate overnight\n"
        response += "• Protein smoothie: Protein powder, banana, spinach, milk\n"
        response += "• Greek yogurt bowl: Yogurt, berries, nuts, drizzle of honey\n\n"
        
        response += "**Lunch (10 minutes):**\n"
        response += "• Tuna salad: Canned tuna, Greek yogurt, celery, on whole wheat\n"
        response += "• Leftover protein + microwaveable rice/quinoa + frozen veggies\n"
        response += "• Large salad with canned beans, pre-cut veggies, bottled dressing\n\n"
        
        response += "**Dinner (15 minutes):**\n"
        response += "• Sheet pan salmon/vegetables: Everything on one pan, bake\n"
        response += "• Stir-fry: Protein + frozen stir-fry vegetables + sauce\n"
        response += "• Turkey/chicken burgers: Season, pan cook, whole wheat bun\n\n"
        
        response += "**Meal Prep Tips:**\n"
        response += "• Cook grains in bulk (rice, quinoa)\n"
        response += "• Roast vegetables in large batches\n"
        response += "• Pre-portion snacks\n"
        response += "• Use slow cooker for proteins\n"
        
        return {
            "type": "quick_recipes",
            "response": response
        }
    
    elif any(word in query for word in ['prep', 'meal prep', 'cook in advance']):
        response = "**Meal Prep Guide for Busy People:**\n\n"
        
        response += "**Weekly Prep Strategy:**\n"
        response += "1. **Plan:** Choose 3-4 meals, make grocery list\n"
        response += "2. **Shop:** Get all ingredients at once\n"
        response += "3. **Prep Day (Sunday):** 2-3 hours\n"
        response += "4. **Store:** Proper containers, label dates\n"
        response += "5. **Reheat:** Safely throughout week\n\n"
        
        response += "**What to Prep:**\n"
        response += "• **Proteins:** Chicken, fish, tofu, hard-boiled eggs\n"
        response += "• **Grains:** Rice, quinoa, pasta, oats\n"
        response += "• **Vegetables:** Roasted, chopped raw, salad greens\n"
        response += "• **Snacks:** Cut fruit, portioned nuts, protein shakes\n\n"
        
        response += "**Container System:**\n"
        response += "• **Glass containers:** Best for reheating\n"
        response += "• **Compartment containers:** Keep foods separate\n"
        response += "• **Mason jars:** Salads, overnight oats\n"
        response += "• **Freezer bags:** For freezing portions\n\n"
        
        response += "**Time-Saving Tips:**\n"
        response += "• Use slow cooker/pressure cooker\n"
        response += "• Buy pre-cut vegetables\n"
        response += "• Cook double batches, freeze half\n"
        response += "• Clean as you go\n"
        
        return {
            "type": "meal_prep_guide",
            "response": response
        }
    
    elif any(word in query for word in ['season', 'flavor', 'tasty', 'bland']):
        response = "**Making Healthy Food Taste Great:**\n\n"
        
        response += "**Healthy Flavor Boosters:**\n"
        response += "• **Fresh herbs:** Basil, cilantro, parsley, mint\n"
        response += "• **Spices:** Cumin, paprika, turmeric, cinnamon\n"
        response += "• **Aromatics:** Garlic, ginger, onions, shallots\n"
        response += "• **Acids:** Lemon/lime juice, vinegar\n"
        response += "• **Heat:** Chili flakes, hot sauce, jalapeños\n\n"
        
        response += "**Healthy Sauce Ideas:**\n"
        response += "• Greek yogurt based sauces (add herbs, garlic)\n"
        response += "• Tahini dressing (tahini, lemon, water, garlic)\n"
        response += "• Pesto (basil, garlic, nuts, olive oil)\n"
        response += "• Salsa (tomatoes, onions, cilantro, lime)\n"
        response += "• Hummus (chickpeas, tahini, lemon, garlic)\n\n"
        
        response += "**Cooking Methods for Flavor:**\n"
        response += "• **Roasting:** Caramelizes natural sugars\n"
        response += "• **Grilling:** Adds smoky flavor\n"
        response += "• **Searing:** Creates flavorful crust\n"
        response += "• **Sautéing:** Quick, retains texture\n"
        
        return {
            "type": "healthy_flavor",
            "response": response
        }
    
    else:
        return {
            "type": "recipe_general",
            "response": "I can help with recipes and cooking! Ask me about:\n\n• Quick and easy recipes\n• Meal prep strategies\n• Making healthy food taste great\n• Cooking techniques\n• Ingredient substitutions",
            "suggestions": [
                "Quick healthy recipes",
                "Meal prep guide",
                "How to make healthy food tasty",
                "Easy cooking techniques"
            ]
        }

def handle_general_queries(user: UserData, query: str) -> Dict:
    """Handle pertanyaan umum yang tidak masuk kategori spesifik"""
    
    greetings = ['hello', 'hi', 'hey', 'greetings']
    farewells = ['bye', 'goodbye', 'see you', 'farewell']
    thanks = ['thanks', 'thank you', 'appreciate']
    
    if any(word in query for word in greetings):
        return {
            "type": "greeting",
            "response": f"Hello {user.name}! 👋 I'm your fitness assistant. How can I help you today?",
            "suggestions": [
                "What's my workout for today?",
                "Tell me about my nutrition plan",
                "How do I track my progress?",
                "Give me some motivation tips"
            ]
        }
    
    elif any(word in query for word in farewells):
        return {
            "type": "farewell",
            "response": f"Goodbye {user.name}! Remember: consistency beats perfection. See you next time! 💪",
            "update_context": {"last_interaction": datetime.now().isoformat()}
        }
    
    elif any(word in query for word in thanks):
        return {
            "type": "thanks",
            "response": f"You're welcome, {user.name}! I'm here to support your fitness journey. Keep up the great work! 🎯"
        }
    
    elif any(word in query for word in ['help', 'what can you do', 'capabilities']):
        response = f"**I can help you with:**\n\n"
        response += "**🏋️ Workouts:**\n• Today's workout\n• Weekly schedule\n• Exercise form tips\n• Alternative exercises\n• Cardio advice\n\n"
        response += "**🥗 Nutrition:**\n• Calorie and macro needs\n• Meal ideas\n• Protein/carb/fat information\n• Meal timing\n• Supplement advice\n\n"
        response += "**📊 Progress:**\n• Expected results\n• Progress tracking\n• Plateau solutions\n• Motivation tips\n• Time estimates\n\n"
        response += "**💪 Health:**\n• Sleep optimization\n• Stress management\n• Energy boost tips\n• Age-specific advice\n• Women's/Men's health\n\n"
        response += "**🛒 Practical:**\n• Grocery lists\n• Recipes\n• Meal prep\n• Budget tips\n\n"
        response += "**Just ask me anything about your fitness journey!**"
        
        return {
            "type": "capabilities",
            "response": response,
            "suggestions": [
                "What's my workout for today?",
                "How much protein do I need?",
                "Sleep optimization tips",
                "Give me a grocery list"
            ]
        }
    
    elif 'motivation' in query or 'quote' in query or 'inspire' in query:
        quotes = [
            "The only bad workout is the one that didn't happen.",
            "It's not about having time, it's about making time.",
            "Don't wish for a good body, work for it.",
            "Success is the sum of small efforts, repeated day in and day out.",
            "The pain of discipline is less than the pain of regret.",
            "You don't have to be great to start, but you have to start to be great.",
            "Your body can stand almost anything. It's your mind you have to convince.",
            "Progress, not perfection.",
            "The hardest lift is lifting your butt off the couch.",
            "A year from now you'll wish you started today."
        ]
        
        return {
            "type": "motivation_quote",
            "response": f"**💪 Fitness Motivation:**\n\n\"{random.choice(quotes)}\"\n\nKeep going, {user.name}! You've got this!",
            "quote": quotes[0]
        }
    
    else:
        return {
            "type": "general_response",
            "response": f"I'm here to help with your fitness journey, {user.name}! Try asking me about:\n\n• Your workout plan\n• Nutrition questions\n• Progress tracking\n• Health and wellness tips\n\nOr say 'help' to see everything I can do!",
            "suggestions": [
                "What can you help me with?",
                "Workout advice",
                "Nutrition tips",
                "How to stay motivated"
            ]
        }