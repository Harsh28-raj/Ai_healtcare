# 💊 Drug Condition API — v2

> Upgraded NLP-powered drug recommendation API — part of the **Ai_healthcare** platform.  
> Branch: `drug-condition-api-v2`

---

## 📌 What It Does

User inputs a **text review / symptom description** → Model dynamically predicts **Top 4 conditions** from a pool of **20 conditions** → API returns ranked recommendations with confidence scores.

> ✅ **Upgrade from v1:** Previous version was hardcoded to only 4 fixed conditions. This version supports **20 conditions** with dynamic Top 4 selection — model picks the best 4 from 20 based on input.

---

## 🆚 v1 vs v2 Comparison

| Feature | v1 (`drug-condition-api`) | v2 (`drug-condition-api-v2`) |
|---------|--------------------------|------------------------------|
| Conditions supported | 4 (hardcoded) | 20 (dynamic) |
| Top K predictions | Fixed Top 4 | Dynamic Top 4 from 20 |
| Model size | ~1.52MB | ~1.5MB |
| Vectorizer | `vectorizer.pkl` | `tfidfvectorizer.pkl` |
| Model file | `model.pkl` | `passmodel.pkl` |
| Flexibility | ❌ Low | ✅ High |

---

## 🗂️ Branch Structure

```
drug-condition-api-v2/
│
├── model/
│   ├── passmodel.pkl            # Upgraded PAC model (20 conditions)
│   └── tfidfvectorizer.pkl      # Fitted TF-IDF vectorizer
├── main.py                      # FastAPI app — prediction endpoint
└── requirements.txt             # Python dependencies
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| ML Model | Passive Aggressive Classifier (upgraded) |
| Vectorizer | TF-IDF (sklearn) |
| Input Format | Raw string (patient review text) |
| Conditions Pool | 20 drug conditions |
| Output | Top 4 dynamically selected conditions |
| Model Size | ~1.5MB |
| Deployment | Render (Free Tier) |
| Language | Python 3.10+ |

---

## 🧠 How The Model Works

```
User Input (free text review / symptom description)
        ↓
Text Preprocessing
  → lowercase, remove punctuation, stopwords
        ↓
TF-IDF Vectorization (tfidfvectorizer.pkl)
        ↓
Passive Aggressive Classifier (passmodel.pkl)
  → Scores across 20 conditions
        ↓
Dynamic Top 4 selection (highest confidence from 20)
        ↓
JSON Response
```

**Model Details:**
- Algorithm: Passive Aggressive Classifier
- Conditions pool: **20 drug conditions**
- Output: **Top 4** dynamically picked from 20
- Model size: **~1.5MB** (lightweight, Render optimized)
- Vectorizer: TF-IDF, fitted on drug review corpus

---

## 🚀 API Reference

### Base URL
```
https://your-app-v2.onrender.com
```
> 🔗 Replace with your actual Render deployment URL

---

### `POST /recommend`

Predicts top 4 drug conditions dynamically from 20 possible conditions.

**Request Body:**
```json
{
  "review": "I have been suffering from severe anxiety and constant stress for months"
}
```

**Response:**
```json
{
  "input_review": "I have been suffering from severe anxiety and constant stress for months",
  "top_conditions": [
    {
      "condition": "Anxiety",
      "confidence": 0.76
    },
    {
      "condition": "Depression",
      "confidence": 0.13
    },
    {
      "condition": "Insomnia",
      "confidence": 0.07
    },
    {
      "condition": "ADHD",
      "confidence": 0.04
    }
  ]
}
```

**Notes:**
- Input must be a **non-empty string**
- Model scores input across **20 conditions**
- Returns **Top 4** with highest confidence — dynamically selected
- Confidence values sum to ~1.0 across all 20 conditions

---

### `GET /health`

Check if API is live.

**Response:**
```json
{
  "status": "ok",
  "model": "drug-condition-classifier-v2",
  "version": "2.0",
  "conditions_supported": 20
}
```

---

## 🛠️ Local Setup

### 1. Clone the branch
```bash
git clone -b drug-condition-api-v2 https://github.com/Harsh28-raj/Ai_healthcare.git
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
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"review": "I have been suffering from severe anxiety and stress"}'
```

---

## 📦 requirements.txt

```
fastapi
uvicorn
scikit-learn
joblib
pydantic
pandas
```

---

## ⚠️ Disclaimer

> This API is for **informational and educational purposes only.**  
> It does **not** recommend specific medicines or replace medical advice.  
> Always consult a qualified doctor before taking any medication.

---

## 🔗 Related Branches

| Branch | Feature |
|--------|---------|
| `disease-prediction-engine` | Symptom → Disease prediction |
| `drug-condition-api` | Drug condition API v1 (4 conditions) |
| `drug-condition-api-v2` | ← You are here (20 conditions) |
| `medicine-barcode-api` | Medicine barcode scanner |
| `food-barcode-api` | Food barcode + Nutri-Score |
| `daily-health-log` | Calorie & activity tracker |

---

## 👨‍💻 Author

**Harsh Raj** — [@Harsh28-raj](https://github.com/Harsh28-raj)  
2nd Year CS Student | AI/ML Developer  
Part of **Ai_healthcare** — an end-to-end AI health platform for Indian users.

