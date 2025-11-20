from pydantic import BaseModel

class UserData(BaseModel):
    name: str
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    goal: str
    active_level: str    
    vegan: bool = False
