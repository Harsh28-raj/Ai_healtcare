from fastapi import FastAPI, HTTPException
import requests
import joblib
import numpy as np
import uvicorn

app = FastAPI(title="Food Health Score API", version="1.0.0")

# 1. Load Models with Error Handling
try:
    # Tumhare saved files ka naam yahi hona chahiye
    model = joblib.load('health_model.pkl')
    scaler = joblib.load('scaler.pkl')
    print("✅ ML Model aur Scaler load ho gaye hain!")
except Exception as e:
    print(f"❌ Error loading pkl files: {e}")

# Home route taaki check kar sako API chal rahi hai
@app.get("/")
def home():
    return {"status": "Online", "message": "ML Health API is running. Use /predict/{barcode}"}

@app.get("/predict/{barcode}")
def predict_health(barcode: str):
    # --- STEP A: Open Food Facts API Configuration ---
    off_url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    
    # Headers zaroori hain taaki OFF block na kare (Very Important)
    headers = {
        "User-Agent": "FoodHealthApp/1.0 (Contact: harsh@example.com)"
    }

    try:
        print(f"🔍 Fetching data for barcode: {barcode}...")
        # Timeout 15 seconds rakha hai agar internet slow ho
        response = requests.get(off_url, headers=headers, timeout=15)
        response.raise_for_status() 
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        raise HTTPException(status_code=503, detail=f"Cannot reach Open Food Facts: {str(e)}")

    # Agar product database mein nahi hai
    if data.get('status') == 0 or 'product' not in data:
        print(f"⚠️ Product not found for barcode: {barcode}")
        raise HTTPException(status_code=404, detail="Product not found in Open Food Facts database")

    # --- STEP B: Extract Nutrients (Feature Extraction) ---
    p = data['product']
    nutrients = p.get('nutriments', {})

    # Wahi 8 features jo tune Heatmap aur Training mein dekhe the
    # .get(key, 0) use kiya hai taaki agar data missing ho toh model crash na kare
    input_vector = [
        float(nutrients.get('energy-kcal_100g', 0)),
        float(nutrients.get('fat_100g', 0)),
        float(nutrients.get('saturated-fat_100g', 0)),
        float(nutrients.get('carbohydrates_100g', 0)),
        float(nutrients.get('sugars_100g', 0)),
        float(nutrients.get('fiber_100g', 0)),
        float(nutrients.get('proteins_100g', 0)),
        float(nutrients.get('salt_100g', 0))
    ]

    # --- STEP C: ML Prediction ---
    try:
        # 1. Scaling
        features_scaled = scaler.transform([input_vector])
        
        # 2. Prediction (Nutrition Score)
        predicted_score = model.predict(features_scaled)[0]
        
        # 3. Simple Grade Logic (A/B/C/D/E)
        # OFF standard: <0 is A, <3 is B, <11 is C, <19 is D, else E
        if predicted_score <= 0: grade, cat = "A", "Very Healthy"
        elif predicted_score <= 2: grade, cat = "B", "Healthy"
        elif predicted_score <= 10: grade, cat = "C", "Moderate"
        elif predicted_score <= 18: grade, cat = "D", "Unhealthy"
        else: grade, cat = "E", "Very Unhealthy"

        print(f"✅ Prediction Success for {p.get('product_name', 'Unknown')}: {predicted_score}")

        # --- STEP D: Final Response ---
        return {
            "barcode": barcode,
            "product_name": p.get('product_name', 'Unknown Product'),
            "brand": p.get('brands', 'Unknown Brand'),
            "health_score_raw": round(float(predicted_score), 2),
            "final_grade": grade,
            "category": cat,
            "input_nutrients": {
                "energy_kcal": input_vector[0],
                "sugars": input_vector[4],
                "fat": input_vector[1],
                "fiber": input_vector[5],
                "salt": input_vector[7]
            }
        }

    except Exception as e:
        print(f"❌ Prediction Error: {e}")
        raise HTTPException(status_code=500, detail="Error during model prediction")

# API run karne ke liye
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)