from typing import List, Dict
import math

# ----- dasar cost per 100g (dipakai untuk estimasi cost) -----
COST_PER_100G = {
    # Karbo
    "rice": 1500,           
    "oats": 3000,           
    "pasta": 3000,         
    "bread": 2000,         

    # Protein
    "tofu": 2500,            
    "tempeh": 3000,          
    "chicken_breast": 6000,  
    "egg": 2500,            
    "tuna": 8500,  
    "soy_milk": 2000,  
    "chickpea": 7000,       
    "lentil": 6000,   
    
    # Buah / Sayur
    "banana": 2000,         
    "vegetable mix": 2000,     
    "tomato": 3000,              
    "garlic": 3000,        
    "chilies": 5000,
    "carrot": 2500,      
    "broccoli": 8000,
    "spinach": 4000,     

    # Bumbu
    "salt": 500,          
    "sugar": 1200,           
    "pepper": 8000,           
    "soy_sauce": 8000,        
    "sweet_soy_sauce": 7000, 
    "chili_sauce": 6000,     
    "tomato_sauce": 6000,  
    "oyster_sauce": 15000,    
    "cooking_oil": 12000,     
    "olive_oil": 26000,     
    "butter": 18000,
    "margarine": 10000,
    "garlic": 4000,           
    "onion": 3000,            
    "shallot": 3000,           
    "ginger": 3000,         
    "lemongrass": 2000,       
    "lime": 3000,       
    
    # Tambahan
    "peanut_butter": 15000,
    "yogurt": 8000,
    "milk": 7000, 
    "curry_powder": 10000,
    "coconut_milk": 5000,          
}

# ----- alias ingredient supaya konsisten -----
INGREDIENT_ALIAS = {
    "vegetables": "vegetable mix",
    "milk": "soy_milk",
    "coconut_milk": "coconut_milk",  # tetap sama
}

# ----- default recipe fallback -----
DEFAULT_RECIPE = {
    "ingredients": {},
    "steps": ["Ikuti preferensi memasak masing-masing bahan."],
    "notes": "Meal ini belum tersedia di database."
}

RECIPE_DB = {
    # -------------------------------
    # Vegan Breakfast
    # -------------------------------
    "Oats + Soy Milk + Banana": {
        "ingredients": {"oats": 50, "soy_milk": 150, "banana": 100, "sugar": 5},
        "steps": [
            "Campur oats dengan soy milk, masak sebentar hingga agak mengental.",
            "Iris pisang dan tambahkan di atas oats.",
            "Tambahkan gula jika suka manis."
        ],
        "notes": "Porsi 1 orang, sarapan cepat dan bergizi."
    },
    "Peanut Butter Toast + Banana": {
        "ingredients": {"bread": 50, "peanut_butter": 20, "banana": 100},
        "steps": [
            "Oleskan peanut butter di atas roti panggang.",
            "Tambahkan irisan pisang di atasnya."
        ],
        "notes": "Porsi 1 orang, kaya protein."
    },
    "Tofu Scramble + Spinach": {
        "ingredients": {"tofu": 150, "spinach": 50, "onion": 20, "garlic": 10, "cooking_oil": 10, "salt": 2, "pepper": 1},
        "steps": [
            "Tumis bawang & bawang putih hingga harum.",
            "Masukkan tofu, hancurkan sedikit, tambahkan spinach.",
            "Bumbui garam dan lada, masak sebentar."
        ],
        "notes": "Sarapan tinggi protein."
    },
    "Soy Yogurt + Fruit + Bread": {
        "ingredients": {"soy_milk": 100, "banana": 50, "oats": 20, "bread": 50},
        "steps": [
            "Campur soy milk dengan oats, tambahkan potongan buah.",
            "Sajikan dengan roti panggang."
        ],
        "notes": "Ringan dan sehat."
    },
    "Smoothie (Banana + Oats + Soy Milk)": {
        "ingredients": {"banana": 100, "oats": 30, "soy_milk": 150},
        "steps": [
            "Masukkan semua bahan ke blender.",
            "Haluskan hingga smooth, sajikan dingin."
        ],
        "notes": "Cepat, sarapan bergizi."
    },
    "Toast (no egg)": {
        "ingredients": {"bread": 50, "vegetable mix": 30, "olive_oil": 5, "salt": 2, "pepper": 1},
        "steps": [
            "Panggang roti hingga renyah.",
            "Tumbuk avocado (vegetable mix) lalu oleskan di atas roti.",
            "Taburi garam dan lada sesuai selera."
        ],
        "notes": "Sehat dan mengenyangkan."
    },
    "Fruit Bowl + Oat": {
        "ingredients": {"banana": 50, "oats": 30, "vegetable mix": 50},
        "steps": [
            "Campur oats dengan buah potong (banana).",
            "Sajikan sebagai sarapan cepat."
        ],
        "notes": "Kaya serat, porsi 1 orang."
    },

    # -------------------------------
    # Vegan Lunch
    # -------------------------------
    "Tempe Stir Fry + Rice": {
        "ingredients": {"tempeh": 150, "rice": 150, "vegetable mix": 80, "garlic": 10, "onion": 20, "sweet_soy_sauce": 10, "cooking_oil": 10, "pepper": 1, "salt": 2},
        "steps": [
            "Tumis bawang & bawang putih dengan minyak.",
            "Masukkan tempeh, tumis hingga matang.",
            "Tambahkan sayuran dan nasi, beri kecap manis, garam, dan lada."
        ],
        "notes": "Porsi 1 orang, menu makan siang lengkap."
    },
    "Lentil Soup + Bread": {
        "ingredients": {"lentil": 100, "vegetable mix": 80, "onion": 20, "garlic": 10, "cooking_oil": 10, "salt": 2, "pepper": 1, "bread": 50},
        "steps": [
            "Tumis bawang & bawang putih, masukkan lentil dan sayuran.",
            "Tambahkan air, masak hingga lentil empuk.",
            "Sajikan dengan roti panggang."
        ],
        "notes": "Menu siang sehat."
    },
    "Vegan Fried Rice (Tempe + Veggies)": {
        "ingredients": {"rice": 150, "tempeh": 100, "vegetable mix": 80, "garlic": 10, "onion": 20, "sweet_soy_sauce": 10, "cooking_oil": 10, "salt": 2, "pepper": 1},
        "steps": [
            "Tumis bawang & bawang putih, masukkan tempeh dan sayuran.",
            "Tambahkan nasi dan kecap manis, bumbui garam & lada."
        ],
        "notes": "Menu siang lengkap."
    },
    "Tofu Curry + Rice": {
        "ingredients": {"tofu": 150, "rice": 150, "coconut_milk": 100, "onion": 40, "garlic": 10, "curry_powder": 8, "vegetable mix": 80, "cooking_oil": 10, "salt": 2, "pepper": 1},
        "steps": [
            "Potong tofu kotak-kotak, goreng sebentar sampai kekuningan.",
            "Tumis bawang & bawang putih, masukkan bubuk kari.",
            "Tambahkan santan dan sayuran, masak hingga setengah matang.",
            "Masukkan tofu, masak hingga kuah agak mengental.",
            "Sajikan dengan nasi hangat."
        ],
        "notes": "Tambahkan cabai jika suka pedas."
    },
    "Chickpea Stir Fry + Rice": {
        "ingredients": {"chickpea": 100, "rice": 150, "vegetable mix": 80, "garlic": 10, "onion": 20, "cooking_oil": 10, "salt": 2, "pepper": 1, "soy_sauce": 5},
        "steps": [
            "Tumis bawang & bawang putih.",
            "Masukkan chickpea dan sayuran, masak sebentar.",
            "Tambahkan nasi, bumbui dengan garam, lada, dan kecap."
        ],
        "notes": "Menu siang protein nabati."
    },
    "Stir Fried Noodles + Veggies (no egg)": {
        "ingredients": {"pasta": 100, "vegetable mix": 80, "garlic": 10, "onion": 20, "cooking_oil": 10, "soy_sauce": 10, "salt": 2, "pepper": 1},
        "steps": [
            "Rebus pasta hingga matang, tiriskan.",
            "Tumis bawang & bawang putih, masukkan sayuran.",
            "Tambahkan pasta dan bumbui dengan kecap, garam, lada."
        ],
        "notes": "Menu siang cepat dan sehat."
    },
    "Tofu Teriyaki + Rice": {
        "ingredients": {"tofu": 150, "rice": 150, "vegetable mix": 80, "soy_sauce": 15, "cooking_oil": 10, "sugar": 5, "garlic": 10, "salt": 2},
        "steps": [
            "Goreng tofu hingga agak kecoklatan.",
            "Tumis sayuran sebentar, masukkan tofu.",
            "Tambahkan saus teriyaki (kecap + gula + garlic), sajikan dengan nasi."
        ],
        "notes": "Menu siang 1 porsi, gurih manis."
    },

    # -------------------------------
    # Vegan Dinner
    # -------------------------------
    "Chickpea Veggie Bowl": {
        "ingredients": {"chickpea": 120, "vegetable mix": 100, "garlic": 10, "onion": 20, "cooking_oil": 10, "salt": 2, "pepper": 1},
        "steps": [
            "Tumis bawang & bawang putih, masukkan chickpea dan sayuran.",
            "Masak hingga matang dan bumbui dengan garam & lada."
        ],
        "notes": "Dinner protein nabati."
    },
    "Tofu + Broccoli + Rice": {
        "ingredients": {"tofu": 150, "rice": 150, "broccoli": 80, "garlic": 10, "onion": 20, "cooking_oil": 10, "salt": 2, "pepper": 1, "soy_sauce": 5},
        "steps": [
            "Goreng tofu sebentar, tumis bawang dan brokoli.",
            "Tambahkan tofu dan nasi, bumbui dengan garam, lada, dan kecap."
        ],
        "notes": "Dinner sehat dan lengkap."
    },
    "Vegan Noodle Soup": {
        "ingredients": {"pasta": 100, "vegetable mix": 80, "garlic": 10, "onion": 20, "cooking_oil": 10, "salt": 2, "pepper": 1, "soy_sauce": 5},
        "steps": [
            "Rebus pasta, tumis bawang dan sayuran, tambahkan air.",
            "Campur pasta ke kuah sayur, bumbui dengan garam, lada, dan kecap."
        ],
        "notes": "Menu ringan dan hangat."
    },
    "Veggie Stir Fry + Rice": {
        "ingredients": {"vegetable mix": 120, "rice": 150, "garlic": 10, "onion": 20, "cooking_oil": 10, "soy_sauce": 5, "salt": 2, "pepper": 1},
        "steps": [
            "Tumis sayuran hingga layu, masukkan nasi.",
            "Tambahkan kecap, garam, dan lada."
        ],
        "notes": "Menu mudah dan cepat."
    },
    "Tempe + Mixed Vegetables + Rice": {
        "ingredients": {"tempeh": 150, "rice": 150, "vegetable mix": 100, "garlic": 10, "onion": 20, "cooking_oil": 10, "soy_sauce": 5, "salt": 2, "pepper": 1},
        "steps": [
            "Tumis tempeh dengan bawang, masukkan sayuran.",
            "Tambahkan nasi, kecap, garam, dan lada."
        ],
        "notes": "Dinner protein nabati."
    },
    "Tofu Sambal + Rice": {
        "ingredients": {"tofu": 150, "rice": 150, "chili_sauce": 15, "garlic": 10, "onion": 20, "cooking_oil": 10, "salt": 2},
        "steps": [
            "Goreng tofu, tumis bawang & garlic.",
            "Tambahkan saus sambal, masukkan nasi dan aduk rata."
        ],
        "notes": "Pedas, porsi 1 orang."
    },
    "Vegetable Curry + Rice": {
        "ingredients": {"vegetable mix": 120, "rice": 150, "coconut_milk": 100, "onion": 20, "garlic": 10, "curry_powder": 8, "cooking_oil": 10, "salt": 2, "pepper": 1},
        "steps": [
            "Tumis bawang & bawang putih, tambahkan bubuk kari.",
            "Masukkan sayuran dan santan, masak hingga matang.",
            "Sajikan dengan nasi hangat."
        ],
        "notes": "Menu dinner sehat."
    },

    # -------------------------------
    # Non-Vegan Breakfast
    # -------------------------------
    "Oatmeal + 2 Eggs": {
        "ingredients": {"oats": 50, "egg": 100, "milk": 100, "salt": 2},
        "steps": [
            "Rebus oats dengan susu hingga mengental.",
            "Rebus atau orak-arik telur, sajikan bersama oats."
        ],
        "notes": "Sarapan kaya protein."
    },
    "Egg Sandwich": {
        "ingredients": {"egg": 100, "bread": 50, "butter": 5, "salt": 2, "pepper": 1},
        "steps": [
            "Goreng telur, bumbui dengan garam & lada.",
            "Sajikan di antara roti dengan butter."
        ],
        "notes": "Porsi 1 orang."
    },
    "Yogurt + Banana + Granola": {
        "ingredients": {"banana": 50, "oats": 20, "yogurt": 100},
        "steps": [
            "Campur yogurt dengan irisan pisang dan granola.",
            "Sajikan dingin."
        ],
        "notes": "Ringan dan sehat."
    },
    "Peanut Butter Toast": {
        "ingredients": {"bread": 50, "peanut_butter": 20},
        "steps": ["Oleskan peanut butter di atas roti panggang."],
        "notes": "Cepat dan praktis."
    },
    "Fried Rice + Egg": {
        "ingredients": {"rice": 150, "egg": 100, "vegetable mix": 80, "garlic": 10, "onion": 20, "cooking_oil": 10, "salt": 2, "pepper": 1},
        "steps": [
            "Tumis bawang & bawang putih, masukkan sayuran.",
            "Tambahkan nasi, masukkan telur orak-arik, aduk rata."
        ],
        "notes": "Sarapan lengkap."
    },
    "Chicken Porridge": {
        "ingredients": {"rice": 150, "chicken_breast": 100, "salt": 2, "pepper": 1},
        "steps": [
            "Rebus nasi dengan air, tambahkan ayam suwir, garam, dan lada hingga matang."
        ],
        "notes": "Hangat dan bergizi."
    },
    "Banana + Yogurt + Granola": {
        "ingredients": {"banana": 50, "yogurt": 100, "oats": 20},
        "steps": [
            "Campur semua bahan dan sajikan dingin."
        ],
        "notes": "Ringan, cepat saji."
    },

    # -------------------------------
    # Non-Vegan Lunch
    # -------------------------------
    "Chicken Breast + Rice + Veggies": {
        "ingredients": {"chicken_breast": 150, "rice": 150, "vegetable mix": 80, "garlic": 10, "onion": 20, "cooking_oil": 10, "salt": 2, "pepper": 1, "soy_sauce": 5},
        "steps": [
            "Goreng ayam hingga matang, bumbui garam & lada.",
            "Tumis bawang & sayuran, tambahkan nasi dan ayam.",
            "Tambahkan kecap, aduk rata."
        ],
        "notes": "Porsi 1 orang, menu makan siang lengkap."
    },
    "Egg Fried Rice + Veggies": {
        "ingredients": {"rice": 150, "egg": 100, "vegetable mix": 80, "garlic": 10, "onion": 20, "cooking_oil": 10, "salt": 2, "pepper": 1, "soy_sauce": 5},
        "steps": [
            "Tumis bawang & sayuran, tambahkan nasi.",
            "Masukkan telur orak-arik, aduk rata dengan bumbu."
        ],
        "notes": "Menu cepat dan bergizi."
    },
    "Tuna + Rice + Veggies": {
        "ingredients": {"tuna": 150, "rice": 150, "vegetable mix": 80, "garlic": 10, "onion": 20, "cooking_oil": 10, "salt": 2, "pepper": 1, "soy_sauce": 5},
        "steps": [
            "Tumis bawang & sayuran, masukkan tuna.",
            "Tambahkan nasi dan bumbu, aduk rata."
        ],
        "notes": "Menu siang kaya protein."
    },
    "Tempe + Rice + Sayur": {
        "ingredients": {"tempeh": 150, "rice": 150, "vegetable mix": 80, "garlic": 10, "onion": 20, "cooking_oil": 10, "sweet_soy_sauce": 10, "salt": 2, "pepper": 1},
        "steps": [
            "Tumis tempeh dengan bawang, masukkan sayur.",
            "Tambahkan nasi, beri kecap manis, garam, dan lada."
        ],
        "notes": "Protein nabati, menu siang lengkap."
    },
    "Ayam Kecap + Rice": {
        "ingredients": {"chicken_breast": 150, "rice": 150, "onion": 20, "garlic": 10, "sweet_soy_sauce": 15, "cooking_oil": 10, "salt": 2, "pepper": 1},
        "steps": [
            "Goreng ayam hingga setengah matang.",
            "Tumis bawang & garlic, masukkan ayam, tambahkan kecap manis, garam, dan lada.",
            "Sajikan dengan nasi hangat."
        ],
        "notes": "Manis gurih, porsi 1 orang."
    },
    "Chicken Stir Fry + Rice": {
        "ingredients": {"chicken_breast": 150, "rice": 150, "vegetable mix": 80, "garlic": 10, "onion": 20, "soy_sauce": 10, "cooking_oil": 10, "salt": 2, "pepper": 1},
        "steps": [
            "Tumis bawang & sayuran, masukkan ayam.",
            "Tambahkan nasi dan kecap, aduk rata."
        ],
        "notes": "Menu cepat dan lezat."
    },
    "Noodle Soup + Egg + Veggies": {
        "ingredients": {"pasta": 100, "egg": 100, "vegetable mix": 80, "onion": 20, "garlic": 10, "salt": 2, "pepper": 1, "cooking_oil": 5, "soy_sauce": 5},
        "steps": [
            "Rebus pasta, tumis bawang & sayuran, masukkan kuah.",
            "Tambahkan telur orak-arik, bumbui garam, lada, dan kecap."
        ],
        "notes": "Hangat, kaya protein."
    },

    # -------------------------------
    # Non-Vegan Dinner
    # -------------------------------
    "Chicken Soup + Rice": {
        "ingredients": {"chicken_breast": 150, "rice": 150, "vegetable mix": 80, "onion": 20, "garlic": 10, "salt": 2, "pepper": 1, "cooking_oil": 5},
        "steps": [
            "Rebus ayam dengan air, tambahkan bawang & sayuran.",
            "Masak hingga ayam matang dan kuah terasa gurih.",
            "Sajikan dengan nasi."
        ],
        "notes": "Dinner hangat & bergizi."
    },
    "Tahu + Sayur + Rice": {
        "ingredients": {"tofu": 150, "rice": 150, "vegetable mix": 80, "garlic": 10, "onion": 20, "soy_sauce": 10, "cooking_oil": 10, "salt": 2, "pepper": 1},
        "steps": [
            "Goreng tofu sebentar, tumis bawang & sayuran.",
            "Masukkan nasi, tambahkan kecap, garam, dan lada."
        ],
        "notes": "Dinner protein nabati & sayuran."
    },
    "Fried Rice + Egg + Veggies": {
        "ingredients": {"rice": 150, "egg": 100, "vegetable mix": 80, "garlic": 10, "onion": 20, "cooking_oil": 10, "soy_sauce": 5, "salt": 2, "pepper": 1},
        "steps": [
            "Tumis bawang & sayuran, tambahkan nasi.",
            "Masukkan telur orak-arik, aduk rata dengan bumbu."
        ],
        "notes": "Menu cepat dan bergizi."
    },
    "Nasi Goreng Ayam (light oil)": {
        "ingredients": {"rice": 150, "chicken_breast": 150, "vegetable mix": 80, "garlic": 10, "onion": 20, "cooking_oil": 5, "soy_sauce": 10, "salt": 2, "pepper": 1},
        "steps": [
            "Tumis bawang & ayam, masukkan sayuran.",
            "Tambahkan nasi, kecap, garam, dan lada.",
            "Masak sebentar hingga matang."
        ],
        "notes": "Menu ringan dan lezat."
    },
    "Instant Noodles + Egg + Veggies": {
        "ingredients": {"pasta": 100, "egg": 100, "vegetable mix": 80, "garlic": 10, "onion": 20, "salt": 2, "pepper": 1, "cooking_oil": 5, "soy_sauce": 5},
        "steps": [
            "Rebus pasta, tumis bawang & sayuran, tambahkan telur.",
            "Bumbui dengan garam, lada, dan kecap."
        ],
        "notes": "Dinner cepat saji."
    },
    "Tuna + Stir Fry Veggies": {
        "ingredients": {"tuna": 150, "vegetable mix": 100, "garlic": 10, "onion": 20, "cooking_oil": 10, "soy_sauce": 5, "salt": 2, "pepper": 1},
        "steps": [
            "Tumis bawang & sayuran, masukkan tuna.",
            "Tambahkan kecap, garam, dan lada, aduk rata."
        ],
        "notes": "Porsi 1 orang, kaya protein."
    },
    "Chicken Teriyaki + Rice": {
        "ingredients": {"chicken_breast": 150, "rice": 150, "vegetable mix": 80, "soy_sauce": 15, "sugar": 5, "garlic": 10, "cooking_oil": 10, "salt": 2, "pepper": 1},
        "steps": [
            "Goreng ayam hingga matang.",
            "Tumis sayuran sebentar, tambahkan ayam dan saus teriyaki (kecap + gula + garlic).",
            "Sajikan dengan nasi hangat."
        ],
        "notes": "Gurih manis, porsi 1 orang."
    }
}

RECIPE_DB["default"] = DEFAULT_RECIPE

def get_cost_per_100g(item: str) -> int:
    item = INGREDIENT_ALIAS.get(item, item)
    return COST_PER_100G.get(item, 3000)

# ----- fungsi utama: generate_meal_recipe -----
def generate_meal_recipe(meal_name: str, portions: List[Dict]) -> Dict:
    template = RECIPE_DB.get(meal_name, DEFAULT_RECIPE)
    base_ings = template.get("ingredients", {})
    steps = template.get("steps", [])
    notes = template.get("notes", "")
    
    if portions:
            for portion in portions:
                if "food" not in portion or "grams" not in portion:
                    raise ValueError("Invalid portion structure")

    # Buat map dari portions untuk akses cepat
    portion_map = {INGREDIENT_ALIAS.get(p["food"], p["food"]): p["grams"] for p in portions}

    # Kita akan skala setiap ingredient template berdasarkan porsi yang ada.
    ingredients_scaled = {}
    total_cost = 0.0
    cost_breakdown = []

    for ing, base_g in base_ings.items():
        ing_key = INGREDIENT_ALIAS.get(ing, ing)
        target_g = portion_map.get(ing_key)
        
        if target_g is not None:
            scaled_g = target_g
        else:
            if portion_map:
                avg = sum(portion_map.values()) / len(portion_map)
                scaled_g = round(base_g * (avg / 100))
            else:
                scaled_g = base_g

        ingredients_scaled[ing] = int(scaled_g)
        ingredient_cost = (scaled_g / 100.0) * get_cost_per_100g(ing)
        total_cost += ingredient_cost
        
        cost_breakdown.append({
            "ingredient": ing,
            "grams": int(scaled_g),
            "cost_per_100g": get_cost_per_100g(ing),
            "ingredient_cost": round(ingredient_cost)
        })

    return {
        "meal": meal_name,
        "ingredients": ingredients_scaled,
        "steps": steps,
        "notes": notes,
        "estimated_cost": int(round(total_cost)), 
        "cost_breakdown": cost_breakdown,
        "portion_count": len(portions) if portions else 0,
    }

def generate_recipe(food: str, grams: int) -> Dict:
    food_key = INGREDIENT_ALIAS.get(food, food)
    
    steps_map = {
        "rice": ["Cuci beras, masak dengan rice cooker atau panci sampai matang."],
        "chicken_breast": ["Bumbui ayam, panggang/pan-fry 7-10 menit tiap sisi."],
        "tuna": ["Bumbui tuna, panggang/pan-fry 5-7 menit tiap sisi."],
        "egg": ["Rebus atau orak-arik sesuai selera."],
        "tofu": ["Potong tofu, goreng atau tumis dengan bumbu sederhana."],
        "tempeh": ["Potong tempe, goreng atau tumis dengan kecap/tumis."],
        "oats": ["Masak oats dengan air atau susu selama 3-5 menit."],
        "vegetable mix": ["Cuci dan tumis/rebus sayuran sampai matang."],
        "pasta": ["Rebus pasta 7-10 menit hingga al dente."],
        "soy_milk": ["Susu nabati bisa diminum langsung atau dicampur oats/smoothie."],
        "coconut_milk": ["Gunakan untuk kuah/curry, masak sebentar."],
        "peanut_butter": ["Oleskan pada roti atau campur dengan smoothie."],
        "yogurt": ["Bisa dimakan langsung atau dicampur dengan buah dan granola."],
        "milk": ["Bisa diminum langsung atau digunakan untuk masak/membuat smoothie."],
        "bread": ["Panggang atau makan langsung."],
        "banana": ["Kupas dan makan langsung, atau potong untuk campuran."],
        "sugar": ["Gunakan sebagai pemanis secukupnya."],
        "salt": ["Gunakan sebagai penambah rasa secukupnya."],
        "pepper": ["Taburkan sebagai penambah rasa."],
        "cooking_oil": ["Gunakan untuk menumis atau menggoreng."],
        "soy_sauce": ["Gunakan sebagai penyedap rasa."],
        "sweet_soy_sauce": ["Gunakan untuk memberi rasa manis dan warna."],
        "chili_sauce": ["Gunakan untuk rasa pedas."],
        "curry_powder": ["Tumis dengan bawang sebagai dasar kari."],
    }

    steps = steps_map.get(food_key, ["Masak sesuai preferensi (tumis/rebus/panggang)."])
    est_cost = int(round((grams / 100.0) * get_cost_per_100g(food_key)))

    return {
        "food": food,
        "grams": int(grams),
        "cooking_method": steps,
        "estimated_cost": est_cost,
        "cost_per_100g": get_cost_per_100g(food_key)
    }
    
def get_total_cost(meal_name: str, portions: List[Dict] = []) -> int:
    recipe = generate_meal_recipe(meal_name, portions)
    return recipe["estimated_cost"]

def get_ingredient_cost_breakdown(meal_name: str, portions: List[Dict] = []) -> List[Dict]:
    recipe = generate_meal_recipe(meal_name, portions)
    return recipe.get("cost_breakdown", [])
