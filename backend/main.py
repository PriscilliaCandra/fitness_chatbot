from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from database import get_db, init_db
from models.user_auth import UserRegister, UserLogin
from auth import create_token, decode_token
import json
from models.user_model import UserData
from fitness_engine.calories import calculate_calories
from fitness_engine.workouts import generate_workouts
from fitness_engine.diet import generate_diet
from fitness_engine.progress import predict_progress
from fitness_engine.grocery import generate_grocery_list

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
def generate_full_plan(user: UserData):

    cal_data = calculate_calories(user)
    calories_target = cal_data["calories"]
    macros_target = cal_data["macros"]

    workouts = generate_workouts(user)
    diet_weekly = generate_diet(user, calories_target, macros_target)
    grocery = generate_grocery_list(diet_weekly)
    progress = predict_progress(user, weeks=8)

    return {
        "user": user,
        "calories_target": calories_target,
        "macros_target": macros_target,
        "workout_plan": workouts,
        "diet_plan": diet_weekly,
        "grocery_list": grocery,
        "progress_prediction": progress
    }
    
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
