from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import search
import requests
from database import medicine_collection, check_and_create_alerts
from datetime import datetime

app = FastAPI(title="Healthcare App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/medicine/search")
def search_med(name: str = Query(..., description="Name of the medicine to search"), user_id: str = Query(default="guest")):
    result = search.search_medicine(name)
    if not result:
        raise HTTPException(status_code=404, detail="Medicine not found")

    medicine_collection.insert_one({
        "user_id": user_id,
        "medicine_name": result.get("name", name),
        "category": result.get("category", "N/A"),
        "composition": result.get("composition", "N/A"),
        "side_effects": result.get("side_effects", "N/A"),
        "manufacturer": result.get("manufacturer", "N/A"),
        "timestamp": datetime.utcnow()
    })
    check_and_create_alerts(user_id)

    return result

@app.get("/medicine/suggest")
def suggest_med(q: str = Query(..., description="Query to suggest medicines")):
    try:
        suggestions = search.suggest_medicine(q)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch suggestions: {str(e)}")

@app.get("/medicine/barcode")
def barcode_med(code: str = Query(..., description="Barcode to search"), user_id: str = Query(default="guest")):
    try:
        # Fix 1: No quotes in URL, no async — simple requests
        url = f"https://api.fda.gov/drug/ndc.json?search=product_ndc:{code}&limit=1"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                res = data["results"][0]
                drug_name = res.get("brand_name") or res.get("generic_name")

                if drug_name:
                    # Fix 2: CSV se details dhundho
                    result = search.search_medicine(drug_name)
                    if result:
                        medicine_collection.insert_one({
                            "user_id": user_id,
                            "medicine_name": result.get("name", drug_name),
                            "category": result.get("category", "N/A"),
                            "composition": result.get("composition", "N/A"),
                            "side_effects": result.get("side_effects", "N/A"),
                            "manufacturer": result.get("manufacturer", "N/A"),
                            "timestamp": datetime.utcnow()
                        })
                        check_and_create_alerts(user_id)
                        return result

                    # Fix 3: CSV mein nahi mila — OpenFDA ka data return karo
                    ingredients = res.get("active_ingredients", [])
                    composition = ", ".join(
                        [f"{i.get('name','')} ({i.get('strength','')})"
                         for i in ingredients]
                    ) if ingredients else "N/A"

                    medicine_collection.insert_one({
                        "user_id": user_id,
                        "medicine_name": drug_name,
                        "category": "N/A",
                        "composition": composition,
                        "side_effects": "N/A",
                        "manufacturer": res.get("labeler_name", "N/A"),
                        "timestamp": datetime.utcnow()
                    })
                    check_and_create_alerts(user_id)

                    return {
                        "name": drug_name,
                        "type": res.get("product_type", "N/A").title(),
                        "category": "N/A",
                        "composition": composition,
                        "uses": "N/A",
                        "side_effects": "N/A",
                        "manufacturer": res.get("labeler_name", "N/A"),
                        "available": True,
                        "trust_score": "N/A",
                        "alternatives": []
                    }

        raise HTTPException(
            status_code=404,
            detail="Barcode not found in OpenFDA. Try /medicine/search?name=<drug_name>"
        )

    except HTTPException:
        raise
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"OpenFDA connection error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process barcode: {str(e)}")