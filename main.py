from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import pickle

app = FastAPI(title="Disease Prediction API")

# Load artifacts
model = joblib.load("disease_model.pkl")

label_encoder = pickle.load(
    open("label_encoder.pkl","rb")
)

features = joblib.load("features.pkl")


# Request format
class Symptoms(BaseModel):

    symptoms: list[str]


@app.get("/")
def home():

    return {
        "message":"Disease prediction API running"
    }


@app.get("/symptoms")
def get_symptoms():

    return {
        "total_symptoms":len(features),
        "symptoms":features
    }


@app.post("/predict")

def predict(data:Symptoms):

    try:

        if len(data.symptoms) == 0:

            raise HTTPException(
                status_code=400,
                detail="Provide at least one symptom"
            )

        # Create input vector
        x = np.zeros(len(features))

        for symptom in data.symptoms:

            symptom = symptom.lower()

            if symptom in features:

                idx = features.index(symptom)

                x[idx] = 1

        x = x.reshape(1,-1)

        # Predict probabilities
        probs = model.predict_proba(x)[0]

        # Top 5 predictions
        top_idx = np.argsort(probs)[-5:][::-1]

        diseases = label_encoder.inverse_transform(top_idx)

        confidence = probs[top_idx]

        results = []

        for d,c in zip(diseases,confidence):

            results.append({

                "disease":d,

                "confidence":round(float(c),4)

            })

        return {

            "input_symptoms":data.symptoms,

            "predictions":results

        }

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )