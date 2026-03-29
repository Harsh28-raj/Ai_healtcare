from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np 
import pandas as pd
from utils import review_to_words

    
app = FastAPI(title="Drug Condition Classifier API")

# Load model, vectorizer, and dataset
model = joblib.load("model/passmodel_ngram.pkl")
vectorizer = joblib.load("model/tfidfvectorizer_ngram.pkl")
df = pd.read_csv("C:\\Users\\harsh\\OneDrive\\Desktop\\Patien_cnd_pred\\drugs_filtered.csv")

class ReviewRequest(BaseModel):
    review: str

@app.post("/predict")
def predict_condition(request: ReviewRequest):
    # Step 1: Preprocess
    cleaned = review_to_words(request.review)
    transformed = vectorizer.transform([cleaned])

    # Step 2: Predict condition
    predicted_condition = model.predict(transformed)[0]

    # Step 3: Confidence score
    scores = model.decision_function(transformed)[0]
    exp_scores = np.exp(scores - scores.max())
    probabilities = exp_scores / exp_scores.sum()
    confidence = round(float(probabilities.max()) * 100, 2)

    # Step 4: Top 3 drug recommendations
    drugs_for_condition = df[df['condition'] == predicted_condition]
    drug_recommendations = (
        drugs_for_condition
        .groupby('drugName')
        .agg(avg_rating=('rating', 'mean'), total_useful_count=('usefulCount', 'sum'))
        .reset_index()
        .sort_values(by=['avg_rating', 'total_useful_count'], ascending=[False, False])
    )
    top_drugs = drug_recommendations.head(3)[['drugName', 'avg_rating', 'total_useful_count']].to_dict(orient='records')

    return {
        "predicted_condition": predicted_condition,
        "confidence": f"{confidence}%",
        "top_3_recommended_drugs": top_drugs
    }

@app.get("/health")
def health():
    return {"status": "ok"}