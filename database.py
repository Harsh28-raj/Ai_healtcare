from pymongo import MongoClient
from datetime import datetime

MONGO_URL = "mongodb+srv://Amresh:amresh887@buymeachai.yz2y62f.mongodb.net/HealthCareAi?retryWrites=true&w=majority&appName=BuyMeAChai"

client = MongoClient(MONGO_URL)
db = client["HealthCareAi"]

disease_collection = db["disease_history"]
food_log_collection = db["food_logs"]
medicine_collection = db["medicine_logs"]
food_barcode_collection = db["food_barcode_logs"]
alerts_collection = db["alerts"]

def check_and_create_alerts(user_id: str):
    conflicts = {
        "Diabetes": ["Aspirin", "Steroids", "Thiazide"],
        "Hypertension": ["NSAIDs", "Decongestants"],
        "Liver Disease": ["Paracetamol", "Statins"]
    }
    
    latest_disease = disease_collection.find_one(
        {"user_id": user_id},
        sort=[("timestamp", -1)]
    )
    latest_medicine = medicine_collection.find_one(
        {"user_id": user_id},
        sort=[("timestamp", -1)]
    )
    last_3_food = list(food_log_collection.find(
        {"user_id": user_id}
    ).sort("timestamp", -1).limit(3))
    
    if latest_disease and latest_disease.get("confidence", 0) > 0.80:
        alerts_collection.insert_one({
            "user_id": user_id,
            "type": "High Confidence Disease",
            "message": f"High confidence disease detected: {latest_disease['disease']} ({latest_disease['confidence']*100:.0f}%)",
            "is_read": False,
            "timestamp": datetime.utcnow()
        })
    
    if len(last_3_food) == 3:
        if all(log.get("health_score", 100) < 40 for log in last_3_food):
            alerts_collection.insert_one({
                "user_id": user_id,
                "type": "Low Health Score",
                "message": "Health score below 40 for 3 consecutive days. Please improve your diet.",
                "is_read": False,
                "timestamp": datetime.utcnow()
            })
    
    if latest_disease and latest_medicine:
        disease_name = latest_disease.get("disease", "")
        medicine_name = latest_medicine.get("medicine_name", "")
        for disease, meds in conflicts.items():
            if disease.lower() in disease_name.lower():
                for med in meds:
                    if med.lower() in medicine_name.lower():
                        alerts_collection.insert_one({
                            "user_id": user_id,
                            "type": "Drug Interaction Warning",
                            "message": f"Warning: {medicine_name} may conflict with {disease_name}. Consult your doctor.",
                            "is_read": False,
                            "timestamp": datetime.utcnow()
                        })
