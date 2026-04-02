import json
import numpy as np
import joblib
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from difflib import get_close_matches # Fuzzy matching ke liye

app = FastAPI(title="Disease Prediction Engine v1.0")

# 🛡️ CORS Fix for Web Team
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and symptoms
try:
    # Check if files exist before loading
    model = joblib.load("disease_rf_model.joblib")
    with open("symptoms_list.json", "r") as f:
        symptoms_list = json.load(f)
    symptom_to_idx = {sym: idx for idx, sym in enumerate(symptoms_list)}
    print("✅ Model & Symptoms Loaded Successfully")
except Exception as e:
    print(f"❌ Error loading model or symptoms: {e}")
    model = None
    symptoms_list = []
    symptom_to_idx = {}

class Vitals(BaseModel):
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    heart_rate: Optional[int] = None

class PredictionRequest(BaseModel):
    symptoms: List[str]
    vitals: Optional[Vitals] = None

@app.get("/symptoms")
def get_symptoms():
    return {"count": len(symptoms_list), "symptoms": symptoms_list}

def analyze_vitals(vitals: Vitals):
    severity = "Normal"
    emergency_alert = False
    reasons = []

    if vitals:
        if vitals.systolic_bp and vitals.diastolic_bp:
            if vitals.systolic_bp > 180 or vitals.diastolic_bp > 120:
                severity, emergency_alert = "Critical", True
                reasons.append("Hypertensive Crisis Detected")
            elif vitals.systolic_bp > 140 or vitals.diastolic_bp > 90:
                severity = "Elevated"
                reasons.append("High Blood Pressure")
        
        if vitals.heart_rate:
            if vitals.heart_rate > 120 or vitals.heart_rate < 50:
                severity, emergency_alert = "Critical", True
                reasons.append("Abnormal Heart Rate (Tachycardia/Bradycardia)")
    
    return severity, emergency_alert, reasons

def get_next_steps(disease, severity):
    if severity == "Critical":
        return ["Emergency Room Visit Immediately", "Do not drive yourself", "Keep medical history ready"]
    return ["Schedule appointment with specialist", "Monitor symptoms for 24 hours", "Maintain hydration and rest"]

def map_specialist(disease: str):
    d = disease.lower()
    if any(x in d for x in ['heart', 'angina', 'coronary', 'hypertension']): return "Cardiologist"
    if any(x in d for x in ['diabetes', 'thyroid', 'goitre']): return "Endocrinologist"
    if any(x in d for x in ['pneumonia', 'asthma', 'bronchitis', 'copd']): return "Pulmonologist"
    if any(x in d for x in ['stroke', 'epilepsy', 'parkinson', 'migraine']): return "Neurologist"
    if any(x in d for x in ['gastritis', 'ulcer', 'hepatitis']): return "Gastroenterologist"
    if any(x in d for x in ['psoriasis', 'rash', 'acne', 'dermatitis']): return "Dermatologist"
    return "General Physician"

@app.post("/predict")
def predict_disease(request: PredictionRequest):
    if model is None:
        return {"error": "AI Model not initialized on server."}
    
    # 🧠 Smart Symptom Matching (Fuzzy Search)
    processed_inputs = []
    for s in request.symptoms:
        s_clean = s.lower().strip()
        if s_clean in symptom_to_idx:
            processed_inputs.append(s_clean)
        else:
            # Match agar spelling thodi galat ho (e.g. 'chestpain' -> 'chest pain')
            matches = get_close_matches(s_clean, symptoms_list, n=1, cutoff=0.7)
            if matches:
                processed_inputs.append(matches[0])

    if not processed_inputs:
        return {"error": "Symptoms not recognized. Use /symptoms to see supported list."}
        
    # Vectorization
    vector = np.zeros((1, len(symptoms_list)))
    for sym in processed_inputs:
        vector[0, symptom_to_idx[sym]] = 1
        
    # Model Prediction
    probabilities = model.predict_proba(vector)[0]
    best_idx = np.argmax(probabilities)
    confidence = float(probabilities[best_idx])
    disease = str(model.classes_[best_idx])
    
    # Vitals & Emergency Logic
    severity, emergency, vitals_reasons = analyze_vitals(request.vitals)
    
    # Critical Symptoms Trigger
    critical_words = ['chest pain', 'shortness of breath', 'unresponsiveness', 'seizure']
    if any(cw in processed_inputs for cw in critical_words):
        emergency, severity = True, "Critical"
        vitals_reasons.append("High-risk symptom detected")

    return {
        "prediction": {
            "disease": disease.replace('_', ' ').title(),
            "confidence": f"{round(confidence * 100, 1)}%",
            "specialist": map_specialist(disease),
            "severity": severity,
            "emergency_alert": emergency
        },
        "analysis": {
            "detected_symptoms": processed_inputs,
            "vitals_notes": vitals_reasons,
            "next_steps": get_next_steps(disease, severity)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)