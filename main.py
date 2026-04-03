from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
from utils import review_to_words
import os

app = FastAPI(title="Drug Condition Classifier API")

model = joblib.load("model/passmodel.pkl")
vectorizer = joblib.load("model/tfidfvectorizer.pkl")

DRUG_RECOMMENDATIONS = {
    "Birth Control": [
        {"drugName": "Plan B", "avg_rating": 10.0, "total_useful_count": 35},
        {"drugName": "Elinest", "avg_rating": 10.0, "total_useful_count": 7},
        {"drugName": "Provera", "avg_rating": 10.0, "total_useful_count": 0}
    ],
    "Depression": [
        {"drugName": "Norpramin", "avg_rating": 10.0, "total_useful_count": 178},
        {"drugName": "Xanax XR", "avg_rating": 10.0, "total_useful_count": 61},
        {"drugName": "Asendin", "avg_rating": 10.0, "total_useful_count": 59}
    ],
    "Pain": [
        {"drugName": "Ultram ODT", "avg_rating": 10.0, "total_useful_count": 133},
        {"drugName": "Roxicodone Intensol", "avg_rating": 10.0, "total_useful_count": 123},
        {"drugName": "Oxyfast", "avg_rating": 10.0, "total_useful_count": 78}
    ],
    "Anxiety": [
        {"drugName": "Wellbutrin", "avg_rating": 10.0, "total_useful_count": 300},
        {"drugName": "Diazepam Intensol", "avg_rating": 10.0, "total_useful_count": 136},
        {"drugName": "Alprazolam Intensol", "avg_rating": 10.0, "total_useful_count": 90}
    ],
    "Acne": [
        {"drugName": "Septra", "avg_rating": 10.0, "total_useful_count": 39},
        {"drugName": "Clindagel", "avg_rating": 10.0, "total_useful_count": 32},
        {"drugName": "Ery Pads", "avg_rating": 10.0, "total_useful_count": 27}
    ],
    "Bipolar Disorder": [
        {"drugName": "Eskalith-CR", "avg_rating": 10.0, "total_useful_count": 75},
        {"drugName": "Klonopin Wafer", "avg_rating": 10.0, "total_useful_count": 30},
        {"drugName": "Tiagabine", "avg_rating": 10.0, "total_useful_count": 9}
    ],
    "Insomnia": [
        {"drugName": "Seconal Sodium", "avg_rating": 10.0, "total_useful_count": 114},
        {"drugName": "Secobarbital", "avg_rating": 10.0, "total_useful_count": 105},
        {"drugName": "Pentobarbital", "avg_rating": 10.0, "total_useful_count": 27}
    ],
    "Weight Loss": [
        {"drugName": "T-Diet", "avg_rating": 10.0, "total_useful_count": 72},
        {"drugName": "Megace", "avg_rating": 10.0, "total_useful_count": 68},
        {"drugName": "Megace ES", "avg_rating": 9.67, "total_useful_count": 124}
    ],
    "Obesity": [
        {"drugName": "Desoxyn", "avg_rating": 10.0, "total_useful_count": 107},
        {"drugName": "Methamphetamine", "avg_rating": 10.0, "total_useful_count": 98},
        {"drugName": "Fastin", "avg_rating": 10.0, "total_useful_count": 81}
    ],
    "ADHD": [
        {"drugName": "Selegiline", "avg_rating": 10.0, "total_useful_count": 17},
        {"drugName": "ProCentra", "avg_rating": 10.0, "total_useful_count": 2},
        {"drugName": "Desoxyn", "avg_rating": 9.56, "total_useful_count": 1343}
    ],
    "Diabetes, Type 2": [
        {"drugName": "Glucophage XR", "avg_rating": 10.0, "total_useful_count": 184},
        {"drugName": "Novolin N", "avg_rating": 10.0, "total_useful_count": 46},
        {"drugName": "Glumetza", "avg_rating": 10.0, "total_useful_count": 24}
    ],
    "Emergency Contraception": [
        {"drugName": "Take Action", "avg_rating": 10.0, "total_useful_count": 0},
        {"drugName": "Plan B One-Step", "avg_rating": 8.71, "total_useful_count": 8267},
        {"drugName": "Plan B", "avg_rating": 8.66, "total_useful_count": 7273}
    ],
    "High Blood Pressure": [
        {"drugName": "Minipress", "avg_rating": 10.0, "total_useful_count": 37},
        {"drugName": "Plendil", "avg_rating": 10.0, "total_useful_count": 28},
        {"drugName": "Aldactazide", "avg_rating": 10.0, "total_useful_count": 27}
    ],
    "Vaginal Yeast Infection": [
        {"drugName": "Sporanox", "avg_rating": 10.0, "total_useful_count": 27},
        {"drugName": "Nizoral", "avg_rating": 10.0, "total_useful_count": 24},
        {"drugName": "Gynazole-1", "avg_rating": 10.0, "total_useful_count": 13}
    ],
    "Abnormal Uterine Bleeding": [
        {"drugName": "Megace", "avg_rating": 10.0, "total_useful_count": 107},
        {"drugName": "Lo / Ovral-28", "avg_rating": 10.0, "total_useful_count": 9},
        {"drugName": "CamreseLo", "avg_rating": 10.0, "total_useful_count": 2}
    ],
    "Bowel Preparation": [
        {"drugName": "PEG-3350 with Electolytes", "avg_rating": 10.0, "total_useful_count": 7},
        {"drugName": "GaviLyte-G", "avg_rating": 9.0, "total_useful_count": 59},
        {"drugName": "Correctol", "avg_rating": 9.0, "total_useful_count": 21}
    ],
    "Fibromyalgia": [
        {"drugName": "Cesamet", "avg_rating": 10.0, "total_useful_count": 104},
        {"drugName": "Glucosamine", "avg_rating": 10.0, "total_useful_count": 39},
        {"drugName": "Gralise", "avg_rating": 9.0, "total_useful_count": 131}
    ],
    "Smoking Cessation": [
        {"drugName": "Pamelor", "avg_rating": 9.5, "total_useful_count": 94},
        {"drugName": "Nortriptyline", "avg_rating": 9.5, "total_useful_count": 63},
        {"drugName": "Nicoderm CQ", "avg_rating": 9.15, "total_useful_count": 770}
    ],
    "Migraine": [
        {"drugName": "Migergot", "avg_rating": 10.0, "total_useful_count": 46},
        {"drugName": "Acetaminophen / aspirin / caffeine", "avg_rating": 10.0, "total_useful_count": 11},
        {"drugName": "Sansert", "avg_rating": 10.0, "total_useful_count": 10}
    ],
    "Anxiety and Stress": [
        {"drugName": "Luvox CR", "avg_rating": 10.0, "total_useful_count": 40},
        {"drugName": "Elavil", "avg_rating": 9.89, "total_useful_count": 1315},
        {"drugName": "Prazosin", "avg_rating": 9.83, "total_useful_count": 512}
    ]
}

class ReviewRequest(BaseModel):
    review: str

@app.post("/predict")
def predict_condition(request: ReviewRequest):
    cleaned = review_to_words(request.review)
    transformed = vectorizer.transform([cleaned])
    predicted_condition = model.predict(transformed)[0]
    scores = model.decision_function(transformed)[0]
    exp_scores = np.exp(scores - scores.max())
    probabilities = exp_scores / exp_scores.sum()
    confidence = round(float(probabilities.max()) * 100, 2)
    top_drugs = DRUG_RECOMMENDATIONS.get(predicted_condition, [])
    return {
        "predicted_condition": predicted_condition,
        "confidence": f"{confidence}%",
        "top_3_recommended_drugs": top_drugs
    }

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)