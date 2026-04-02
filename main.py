import json
import numpy as np
import joblib
import re
import gc
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from difflib import get_close_matches

app = FastAPI(title="Disease Prediction Engine v1.0")

# 🌐 CORS Fix: Taaki Frontend Team connect kar sake
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 🧠 Model & Data Loading ---
model = None
symptoms_list = []

try:
    # Model load karo
    model = joblib.load("disease_rf_model.joblib")
    
    # Symptoms list load karo
    with open("symptoms_list.json", "r") as f:
        data = json.load(f)
        symptoms_list = data["symptoms"]
    
    # 🧹 RAM Saaf Karo (Very Important for Render Free Tier)
    gc.collect()
    print("✅ Backend Ready: Model and Symptoms Loaded!")
except Exception as e:
    print(f"❌ Error during startup: {e}")

# --- 📝 Data Models ---
class Vitals(BaseModel):
    systolic_bp: Optional[int] = 120
    diastolic_bp: Optional[int] = 80
    heart_rate: Optional[int] = 72

class PredictRequest(BaseModel):
    symptoms: List[str]
    vitals: Optional[Vitals]

# --- 🛠️ Helper Functions ---
def get_severity(vitals: Vitals):
    """Vitals ke basis pe khatra check karta hai"""
    if vitals.systolic_bp > 160 or vitals.diastolic_bp > 100 or vitals.heart_rate > 120:
        return "CRITICAL", "Emergency! Please consult a doctor immediately."
    elif vitals.systolic_bp > 140 or vitals.heart_rate > 100:
        return "HIGH", "High risk detected. Consult a specialist soon."
    return "NORMAL", "Stable. Follow the recommended advice."

# --- 🚀 API Endpoints ---

@app.get("/")
def home():
    return {"status": "AI Healthcare API is Running", "docs": "/docs"}

@app.get("/symptoms")
def get_all_symptoms():
    return {"count": len(symptoms_list), "symptoms": symptoms_list}

@app.post("/predict")
def predict(request: PredictRequest):
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded on server")
    
    if not request.symptoms:
        raise HTTPException(status_code=400, detail="Please select at least one symptom")

    # 1. Create Input Vector (Symptom Matching)
    input_vector = np.zeros(len(symptoms_list))
    for s in request.symptoms:
        if s in symptoms_list:
            idx = symptoms_list.index(s)
            input_vector[idx] = 1
    
    # 2. AI Prediction
    prediction = model.predict([input_vector])[0]
    
    # 3. Severity Logic from Vitals
    severity_level, advice = get_severity(request.vitals)

    return {
        "prediction": str(prediction),
        "severity": severity_level,
        "recommendation": advice,
        "specialist": "General Physician" if severity_level == "NORMAL" else "Specialist / Emergency Care"
    }

# 🧹 Final Garbage Collection
gc.collect()
