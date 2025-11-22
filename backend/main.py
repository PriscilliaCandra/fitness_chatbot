from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from database import get_db, init_db
from models.user_auth import UserRegister, UserLogin
from auth import create_token, decode_token
import json
from models.user_model import UserData
from fitness_engine.engine import generate_full_plan, generate_meal_plan_only, generate_workout_plan_only  # ✅ IMPORT YANG BENAR

init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register")
def register(user: UserRegister):
    conn = get_db()
    c = conn.cursor()

    try:
        c.execute("INSERT INTO users(name, email, password) VALUES (?, ?, ?)",
                  (user.name, user.email, user.password))
        conn.commit()
        return {"message": "Register successful"}
    except:
        raise HTTPException(400, "Email already used")
    
@app.post("/login")
def login(user: UserLogin):
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", 
              (user.email, user.password))
    row = c.fetchone()

    if not row:
        raise HTTPException(401, "Invalid credentials")

    token = create_token(row["id"])
    return {"token": token, "name": row["name"], "user_id": row["id"]}

@app.post("/plan")
def generate_plan(user: UserData):
    if user.age <= 0 or user.weight_kg <= 0 or user.height_cm <= 0:
        raise HTTPException(400, "Invalid user data")
    
    try:
        # ✅ GUNAKAN FUNCTION DARI ENGINE.PY
        plan = generate_full_plan(user)
        
        # DEBUG: Print untuk troubleshooting
        print("=== GENERATED PLAN STRUCTURE ===")
        print(f"Diet plan days: {len(plan['diet_plan'])}")
        if plan['diet_plan']:
            day1 = plan['diet_plan'][0]
            print(f"Day 1 meals: {day1['meals']}")
            print(f"Day 1 portions: {day1.get('portions', {})}")
            print(f"Day 1 recipes: {day1.get('recipes', {})}")
            print(f"Grocery items: {len(plan.get('grocery_list', []))}")
        
        return plan
        
    except Exception as e:
        print(f"Error generating plan: {e}")
        raise HTTPException(500, f"Plan generation failed: {str(e)}")

# Endpoint untuk meal plan only
@app.post("/meal_plan")
def generate_meal_plan(user: UserData):
    try:
        plan = generate_meal_plan_only(user)
        return plan
    except Exception as e:
        raise HTTPException(500, f"Meal plan generation failed: {str(e)}")

# Endpoint untuk workout plan only  
@app.post("/workout_plan")
def generate_workout_plan(user: UserData):
    try:
        plan = generate_workout_plan_only(user)
        return plan
    except Exception as e:
        raise HTTPException(500, f"Workout plan generation failed: {str(e)}")

@app.post("/save_history")
def save_history(plan: dict, Authorization: str = Header(None)):
    user_id = decode_token(Authorization.replace("Bearer ", ""))

    if not user_id:
        raise HTTPException(401, "Invalid token")

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO history(user_id, plan_json) VALUES (?, ?)",
              (user_id, json.dumps(plan)))
    conn.commit()

    return {"message": "Saved"}

@app.get("/history")
def get_history(Authorization: str = Header(None)):
    user_id = decode_token(Authorization.replace("Bearer ", ""))

    if not user_id:
        raise HTTPException(401, "Invalid token")

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM history WHERE user_id = ?", (user_id,))
    rows = c.fetchall()

    return [dict(r) for r in rows]

@app.get("/")
def root():
    return {"message": "AI Fitness API is running!"}