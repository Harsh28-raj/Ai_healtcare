from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import joblib
import numpy as np
import os

from utils import review_to_words

app = FastAPI(title="Drug Condition Classifier API")

# -------- CORS (for web integration) --------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Paths (cloud safe) --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR,"model","passmodel_ngram_compressed.pkl")

vectorizer_path = os.path.join(BASE_DIR,"model","tfidfvectorizer_ngram_compressed.pkl")

# -------- Load model once --------
model = joblib.load(model_path)

vectorizer = joblib.load(vectorizer_path)


# -------- Drug recommendations --------
DRUG_RECOMMENDATIONS = {

    "Birth Control":[
        {"drugName":"Plan B","avg_rating":10.0,"total_useful_count":35},
        {"drugName":"Elinest","avg_rating":10.0,"total_useful_count":7},
        {"drugName":"Provera","avg_rating":10.0,"total_useful_count":0}
    ],

    "Depression":[
        {"drugName":"Norpramin","avg_rating":10.0,"total_useful_count":178},
        {"drugName":"Xanax XR","avg_rating":10.0,"total_useful_count":61},
        {"drugName":"Asendin","avg_rating":10.0,"total_useful_count":59}
    ],

    "Diabetes, Type 2":[
        {"drugName":"Glucophage XR","avg_rating":10.0,"total_useful_count":184},
        {"drugName":"Novolin N","avg_rating":10.0,"total_useful_count":46},
        {"drugName":"Glumetza","avg_rating":10.0,"total_useful_count":24}
    ],

    "High Blood Pressure":[
        {"drugName":"Minipress","avg_rating":10.0,"total_useful_count":37},
        {"drugName":"Plendil","avg_rating":10.0,"total_useful_count":28},
        {"drugName":"Aldactazide","avg_rating":10.0,"total_useful_count":27}
    ]
}

# -------- Request schema --------
class ReviewRequest(BaseModel):
    review:str


# -------- Prediction endpoint --------
@app.post("/predict")

def predict_condition(request:ReviewRequest):

    try:

        if not request.review.strip():

            return {"error":"Empty review text"}


        cleaned = review_to_words(request.review)

        transformed = vectorizer.transform([cleaned])

        predicted_condition = model.predict(transformed)[0]


        # confidence calculation
        scores = model.decision_function(transformed)[0]

        exp_scores = np.exp(scores - scores.max())

        probabilities = exp_scores / exp_scores.sum()

        confidence = round(float(probabilities.max())*100,2)


        top_drugs = DRUG_RECOMMENDATIONS.get(predicted_condition,[])


        return {

            "predicted_condition":predicted_condition,

            "confidence":f"{confidence}%",

            "top_3_recommended_drugs":top_drugs
        }


    except Exception as e:

        return {"error":str(e)}



# -------- Root endpoint --------
@app.get("/")

def root():

    return {"message":"Drug Condition Classifier API running"}


# -------- Health check --------
@app.get("/health")

def health():

    return {"status":"ok"}


# -------- Local run --------
if __name__ == "__main__":

    import uvicorn

    port = int(os.environ.get("PORT",10000))

    uvicorn.run(app,host="0.0.0.0",port=port)