from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import joblib
import pandas as pd
import numpy as np
import os

from utils import review_to_words


# -------- FastAPI init --------
app = FastAPI(title="Drug Condition Classifier API")


# -------- CORS (frontend support) --------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------- Paths --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR,"model","model.pkl")

vectorizer_path = os.path.join(BASE_DIR,"model","vectorizer.pkl")

drug_path = os.path.join(BASE_DIR,"drug_recommendations.csv")


# -------- Load assets once --------
model = joblib.load(model_path)

vectorizer = joblib.load(vectorizer_path)

drug_df = pd.read_csv(drug_path)


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


        # Get scores
        scores = model.decision_function(transformed)[0]

        classes = model.classes_


        # Softmax probability
        exp_scores = np.exp(scores - scores.max())

        probabilities = exp_scores / exp_scores.sum()


        # Top 3 predictions
        top3_idx = probabilities.argsort()[-3:][::-1]

        top_predictions = []


        for idx in top3_idx:

            top_predictions.append({

                "condition":classes[idx],

                "confidence":f"{round(probabilities[idx]*100,2)}%"

            })


        predicted_condition = top_predictions[0]['condition']

        confidence = top_predictions[0]['confidence']


        # Drug lookup
        top_drugs = drug_df[
            drug_df['condition'].str.lower() ==
            predicted_condition.lower()
        ].head(3)


        drug_list = []


        if not top_drugs.empty:

            for _,row in top_drugs.iterrows():

                drug_list.append({

                    "drugName":row['drugName'],

                    "avg_rating":float(row['avg_rating']),

                    "total_useful_count":int(row['total_useful_count'])

                })


        return {

            "predicted_condition":predicted_condition,

            "confidence":confidence,

            "top_3_predictions":top_predictions,

            "top_3_recommended_drugs":drug_list

        }


    except Exception as e:

        return {"error":str(e)}

        predicted_condition = model.predict(transformed)[0]

        scores = model.decision_function(transformed)[0]

        exp_scores = np.exp(scores - scores.max())

        probabilities = exp_scores / exp_scores.sum()

        confidence = round(float(probabilities.max())*100,2)

        # Drug recommendations
        top_drugs = drug_df[
        drug_df['condition'].str.lower() ==
        predicted_condition.lower()
        ].head(3)


        drug_list = []

        if not top_drugs.empty:

            for _,row in top_drugs.iterrows():

             drug_list.append({

             "drugName":row['drugName'],

             "avg_rating":float(row['avg_rating']),

              "total_useful_count":int(row['total_useful_count'])

             })


            return {

            "predicted_condition":predicted_condition,

            "confidence":confidence,

            "top_3_predictions":top_predictions,

            "top_3_recommended_drugs":drug_list
            }
    except Exception as e:

        return {"error":str(e)}



# -------- Root endpoint --------
@app.get("/")

def root():

    return {

        "message":"Drug Condition Classifier API running",

        "model":"TFIDF + PassiveAggressive",

        "supported_conditions":30

    }


# -------- Health check --------
@app.get("/health")

def health():

    return {"status":"ok"}



# -------- Local run --------
if __name__ == "__main__":

    import uvicorn

    port = int(os.environ.get("PORT",10000))

    uvicorn.run(app,host="0.0.0.0",port=port)