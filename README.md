# 🩺 Disease Prediction Engine

> AI-powered symptom-to-disease prediction API — part of the **Ai_healthcare** platform.  
> Branch: `disease-prediction-engine`

---

## 📌 What It Does

User selects symptoms → Model predicts **Top 5 most likely diseases** with confidence scores → API returns ranked predictions with remedies.

Built on a **Neural Network** trained on a 773-class symptom-disease dataset with **85.6% accuracy**.

---

## 🗂️ Branch Structure

```
disease-prediction-engine/
│
├── main.py                  # FastAPI app — prediction endpoint
├── disease_rf_model.joblib  # Trained ML model (serialized)
├── symptoms_list.json       # List of all 377 valid symptoms
└── requirements.txt         # Python dependencies
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| ML Model | Keras Neural Network (joblib serialized) |
| Input Features | 377 binary symptom flags |
| Output Classes | 773 diseases |
| Deployment | Render (Free Tier) |
| Language | Python 3.10+ |

---

## 🧠 How The Model Works

```
User Input (symptoms list)
        ↓
Map symptoms → 377-dim binary vector
        ↓
Neural Network Inference
  Input(377) → Dense(1024) → Dense(1024) → Softmax(773)
        ↓
Top 5 predictions with confidence scores (Softmax probabilities)
        ↓
JSON Response
```

**Training Details:**
- Dataset: Kaggle Symptom-Disease dataset
- Classes: 773 diseases
- Input: 377 binary symptom features
- Accuracy: **85.6%**
- Early stopping applied

---

## 🚀 API Reference

### Base URL
```
https://your-app.onrender.com
```

### `POST /predict`

Predicts top diseases based on input symptoms.

**Request Body:**
```json
{
  "symptoms": [
    "fever",
    "headache",
    "vomiting"
  ]
}
```

**Response:**
```json
{
  "input_symptoms": [
    "fever",
    "headache",
    "vomiting"
  ],
  "predictions": [
    {
      "disease": "malaria",
      "confidence": 0.82
    },
    {
      "disease": "typhoid",
      "confidence": 0.11
    }
  ]
}
```

**Notes:**
- Symptoms must match entries in `symptoms_list.json`
- Returns top 5 predictions sorted by confidence (descending)
- Confidence values are Softmax probabilities (0.0 – 1.0)
- If confidence < 0.40 → app shows **"Consult a doctor"** warning

---

### `GET /symptoms`

Returns the full list of valid symptom strings.

**Response:**
```json
{
  "symptoms": ["fever", "headache", "vomiting", "...377 total"]
}
```

---

## 🛠️ Local Setup

### 1. Clone the branch
```bash
git clone -b disease-prediction-engine https://github.com/Harsh28-raj/Ai_healthcare.git
cd Ai_healthcare
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the server
```bash
uvicorn main:app --reload
```

### 5. Test it
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"symptoms": ["fever", "headache", "vomiting"]}'
```

---

## 📦 requirements.txt

```
fastapi
uvicorn
numpy==1.24.4
scikit-learn
joblib
pydantic
```

> ⚠️ NumPy version pinned to `1.24.4` — model was serialized with this version. Changing it will cause joblib load errors.

---

## ⚠️ Disclaimer

> This API is for **informational and educational purposes only**.  
> It does **not** provide medical diagnosis.  
> Always consult a qualified doctor for medical advice.  
> Low confidence predictions (< 0.40) are automatically flagged.

---

## 🔗 Related Branches

| Branch | Feature |
|--------|---------|
| `disease-prediction-engine` | ← You are here |
| `medicine-barcode-api` | Medicine barcode scanner |
| `food-barcode-api` | Food barcode + Nutri-Score |
| `daily-health-log` | Calorie & activity tracker |
| `rag-medical-bot` | AI chatbot (Roadmap) |

---

## 👨‍💻 Author

**Harsh Raj** — [@Harsh28-raj](https://github.com/Harsh28-raj)  
2nd Year CS Student | AI/ML Developer  
Part of **Ai_healthcare** — an end-to-end AI health platform for Indian users.
