from fastapi import FastAPI, Query
from database import food_log_collection, check_and_create_alerts
from datetime import datetime
from pydantic import BaseModel
from rapidfuzz import fuzz, process
import json

app = FastAPI()

# Database Load
try:
    with open('food_db.json', 'r') as f:
        FOOD_DB = json.load(f)
except FileNotFoundError:
    FOOD_DB = {}

ACTIVITIES = ["walk", "run", "dauda", "gym", "yoga", "khela", "workout"]
NEGATIVE_WORDS = ["nahi", "skipped", "miss", "no", "not"]

class LogRequest(BaseModel):
    text: str

@app.post("/analyze-log")
async def analyze_log(request: LogRequest, user_id: str = Query(default="guest")):
    user_text = request.text.lower()
    user_words = user_text.split()
    
    detected_items = {} # Dictionary to store unique best matches
    risk_flags = set()
    
    # 1. SMART FOOD DETECTION (Preventing Over-detection)
    food_keys = list(FOOD_DB.keys())
    
    for word in user_words:
        if len(word) < 3: continue
        
        # Har word ke liye pure DB mein se sabse best 1 match dhundo
        # extractOne return karta hai: (match_string, score, index)
        best_match = process.extractOne(word, food_keys, scorer=fuzz.token_set_ratio)
        
        if best_match and best_match[1] > 85: # 85% accuracy threshold
            matched_name = best_match[0]
            if matched_name not in detected_items:
                data = FOOD_DB[matched_name]
                detected_items[matched_name] = data
                if "flags" in data:
                    for flag in data["flags"]:
                        risk_flags.add(flag)

    # 2. CALCULATION
    total_calories = sum(item["calories"] for item in detected_items.values())

    # 3. ACTIVITY DETECTION
    activity_level = "Sedentary"
    if any(act in user_text for act in ACTIVITIES):
        if any(neg in user_text for neg in NEGATIVE_WORDS):
            activity_level = "Sedentary (Skipped)"
        else:
            activity_level = "Active"

    # 4. HEALTH SCORE
    base_score = 100
    base_score -= len(risk_flags) * 10
    if activity_level == "Active":
        base_score += 15
    else:
        base_score -= 10
    
    health_score = max(0, min(base_score, 100))

    # 5. RECOMMENDATION LOGIC
    recommendation = "Great day! Keep it up."
    if total_calories > 1500:
        recommendation = "Calorie intake is very high. Try a long walk."
    elif "High Sodium" in risk_flags or "High Fat" in risk_flags:
        recommendation = "Watch out for salt and fried items in your next meal."
    elif activity_level != "Active":
        recommendation = "Try to add at least 15 mins of movement today."

    food_log_collection.insert_one({
        "user_id": user_id,
        "items": list(detected_items.keys()),
        "calories": total_calories,
        "health_score": health_score,
        "risk_flags": list(risk_flags),
        "activity_level": activity_level,
        "recommendation": recommendation,
        "timestamp": datetime.utcnow()
    })
    check_and_create_alerts(user_id)

    return {
        "status": "success",
        "detected_items": list(detected_items.keys()),
        "estimated_calories": total_calories,
        "activity_level": activity_level,
        "risk_flags": list(risk_flags),
        "health_score": health_score,
        "recommendation": recommendation
    }