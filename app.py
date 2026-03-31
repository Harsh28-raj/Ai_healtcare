from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
from utils import review_to_words
import os

app = FastAPI(title="Drug Condition Classifier API")

model = joblib.load("model/passmodel_ngram.pkl")
vectorizer = joblib.load("model/tfidfvectorizer_ngram.pkl")

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
    "Diabetes, Type 2": [
        {"drugName": "Glucophage XR", "avg_rating": 10.0, "total_useful_count": 184},
        {"drugName": "Novolin N", "avg_rating": 10.0, "total_useful_count": 46},
        {"drugName": "Glumetza", "avg_rating": 10.0, "total_useful_count": 24}
    ],
    "High Blood Pressure": [
        {"drugName": "Minipress", "avg_rating": 10.0, "total_useful_count": 37},
        {"drugName": "Plendil", "avg_rating": 10.0, "total_useful_count": 28},
        {"drugName": "Aldactazide", "avg_rating": 10.0, "total_useful_count": 27}
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
    return {"predicted_condition": predicted_condition, "confidence": f"{confidence}%", "top_3_recommended_drugs": top_drugs}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
