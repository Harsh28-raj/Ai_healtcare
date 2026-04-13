# 💊 Drug Condition API

> NLP-powered drug recommendation API based on patient reviews — part of the **Ai_healthcare** platform.  
> Branch: `drug-condition-api`

---

## 📌 What It Does

User inputs a **text review / symptom description** → Model predicts the **Top 4 most relevant drug conditions** → API returns ranked condition recommendations.

Built using a **Passive Aggressive Classifier** with **TF-IDF vectorization** trained on the UCI Drug Review Dataset.

> ⚠️ **Known Limitation:** This version predicts only from a fixed set of **4 conditions**. This limitation has been resolved in the next feature branch.

---

## 🗂️ Branch Structure

```
drug-condition-api/
│
├── data/
│   └── drugs_filtered.csv       # Filtered drug-review training data
├── model/
│   ├── model.pkl                # Trained Passive Aggressive Classifier
│   └── vectorizer.pkl           # TF-IDF vectorizer (fitted)
├── app.py                       # FastAPI app — prediction endpoint
├── utils.py                     # Helper functions (preprocessing etc.)
└── requirements.txt             # Python dependencies
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| ML Model | Passive Aggressive Classifier |
| Vectorizer | TF-IDF (sklearn) |
| Dataset | UCI Drug Review Dataset |
| Input Format | Raw string (patient review text) |
| Output | Top 4 predicted drug conditions |
| Deployment | Render (Free Tier) |
| Language | Python 3.10+ |

---

## 🧠 How The Model Works

```
User Input (free text review / symptom description)
        ↓
Text Preprocessing (utils.py)
  → lowercase, remove punctuation, stopwords
        ↓
TF-IDF Vectorization (vectorizer.pkl)
        ↓
Passive Aggressive Classifier Inference (model.pkl)
        ↓
Top 4 Conditions with confidence scores
        ↓
JSON Response
```

**Training Details:**
- Dataset: UCI Drug Review Dataset
- Model: Passive Aggressive Classifier
- Vectorizer: TF-IDF, max_features = 15,000
- Model size: ~1.52MB (optimized for Render free tier)
- Input: Raw string text
- Output: Top 4 drug conditions

---

## 🚀 API Reference

### Base URL
```
https://ai-healtcare-2.onrender.com
```

---

### `POST /recommend`

Predicts top drug conditions from a patient review string.

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
      "confidence": 0.78
    },
    {
      "condition": "Depression",
      "confidence": 0.12
    },
    {
      "condition": "Pain",
      "confidence": 0.06
    },
    {
      "condition": "Birth Control",
      "confidence": 0.04
    }
  ]
}
```

**Notes:**
- Input must be a **non-empty string**
- Returns exactly **Top 4 conditions** (model limitation in this version)
- Confidence values are classifier probability scores (0.0 – 1.0)
- This limitation is resolved in the next branch (`medicine-barcode-api`)

---

### `GET /health`

Check if API is live.

**Response:**
```json
{
  "status": "ok",
  "model": "drug-condition-classifier",
  "version": "1.0"
}
```

---

## 🛠️ Local Setup

### 1. Clone the branch
```bash
git clone -b drug-condition-api https://github.com/Harsh28-raj/Ai_healthcare.git
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
uvicorn app:app --reload
```

### 5. Test it
```bash
curl -X POST https://ai-healtcare-2.onrender.com/recommend \
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

## ⚠️ Known Limitations

| Limitation | Status |
|-----------|--------|
| Predicts only Top 4 conditions | ✅ Fixed in next branch |
| Input must be English text only | 🔜 Multilingual planned |
| No drug name recommendation, only condition | 🔜 Planned |

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
| `drug-condition-api` | ← You are here |
| `medicine-barcode-api` | Medicine barcode scanner (fixes limitations) |
| `food-barcode-api` | Food barcode + Nutri-Score |
| `daily-health-log` | Calorie & activity tracker |

---

## 👨‍💻 Author

**Harsh Raj** — [@Harsh28-raj](https://github.com/Harsh28-raj)  
2nd Year CS Student | AI/ML Developer  
Part of **Ai_healthcare** — an end-to-end AI health platform for Indian users.

