# 🥗 Food Health Log API

> NLP-powered daily food intake analyzer with health scoring — part of the **Ai_healthcare** platform.  
> Branch: `food-health-api`

---

## 📌 What It Does

User types their daily food intake in **plain natural language** → API detects food items → Estimates **total calories** → Calculates **health score**, **activity level**, **risk flags**, and gives a **personalized recommendation**.

Real example tested:
> Input: `"i have eaten dal rice and 2 samosa 5 chicken"`  
> Output: 1342 kcal · Grade 70/100 · Risk: High Calorie, High Fat

---

## 🗂️ Branch Structure

```
food-health-api/
│
├── health_model.pkl         # Trained ML model (health scoring)
├── scaler.pkl               # Feature scaler (normalization)
├── main.py                  # FastAPI app — food log endpoint
└── requirements.txt         # Python dependencies
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| ML Model | Sklearn model (health_model.pkl) |
| Scaler | StandardScaler (scaler.pkl) |
| Food Detection | NLP-based item extraction from free text |
| Calorie DB | Indian food calorie database |
| Input Format | Plain text string |
| Output | Calories, health score, risk flags, recommendation |
| Deployment | Render (Free Tier) |
| Language | Python 3.10+ |

---

## 🧠 How It Works

```
User Input (natural language food description)
        ↓
NLP Food Item Extraction
  → "dal rice and 2 samosa 5 chicken"
  → ["dal parantha", "rice flakes", "potato samosa" ×2, "chicken sandwich" ×5]
        ↓
Calorie Lookup (Indian Food DB)
  → Per item calorie mapping
  → Quantity-aware calculation
        ↓
Feature Engineering
  → total_calories, fat_score, fiber_score, protein_score
        ↓
Scaler normalization (scaler.pkl)
        ↓
ML Model Inference (health_model.pkl)
  → health_score (0–100)
  → activity_level
        ↓
Rule Engine
  → Risk flags (High Calorie, High Fat, Low Fiber...)
  → Recommendation string
        ↓
JSON Response
```

---

## 🚀 API Reference

### Base URL
```
https://ai-healtcare-13.onrender.com
```

---

### `POST /log`

Analyzes daily food intake from plain text.

**Request Body:**
```json
{
  "text": "i have eaten dal rice and 2 samosa 5 chicken"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "detected_items": [
    "dal parantha/paratha",
    "rice flakes",
    "cheese and chilli sandwich",
    "potato samosa",
    "chicken sandwich"
  ],
  "estimated_calories": 1342,
  "activity_level": "Sedentary",
  "risk_flags": [
    "High Calorie",
    "High Fat"
  ],
  "health_score": 70,
  "recommendation": "Watch out for salt and fried items in your next meal."
}
```

**Risk Flags Reference:**

| Flag | Trigger Condition |
|------|-----------------|
| High Calorie | Total kcal exceeds daily threshold |
| High Fat | Fat content above recommended limit |
| Low Fiber | Fiber intake insufficient |
| High Sugar | Sugar content elevated |
| Low Protein | Protein below recommended intake |

**Activity Level Reference:**

| Level | Meaning |
|-------|---------|
| Sedentary | Very low physical activity detected |
| Lightly Active | Moderate food + some activity balance |
| Active | Good calorie-activity balance |

**Health Score Reference:**

| Score | Meaning |
|-------|---------|
| 80–100 | Excellent — keep it up |
| 60–79 | Good — minor improvements needed |
| 40–59 | Moderate — watch your diet |
| < 40 | Poor — consult a nutritionist |

---

### `GET /health`

Check if API is live.

**Response:**
```json
{
  "status": "ok",
  "model": "food-health-api",
  "version": "1.0"
}
```

---

## 🛠️ Local Setup

### 1. Clone the branch
```bash
git clone -b food-health-api https://github.com/Harsh28-raj/Ai_healthcare.git
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
curl -X POST http://localhost:8000/log \
  -H "Content-Type: application/json" \
  -d '{"text": "i have eaten dal rice and 2 samosa 5 chicken"}'
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
numpy
```

---

## 📱 Flutter Integration

```dart
final response = await http.post(
  Uri.parse('https://ai-healtcare-13.onrender.com/log'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    "text": userInputController.text
  }),
);

final data = jsonDecode(response.body);
// data['health_score']      → show circular progress
// data['risk_flags']        → show warning chips
// data['estimated_calories'] → show calorie counter
// data['recommendation']    → show tip card
```

---

## ⚠️ Disclaimer

> This API provides **estimated nutritional analysis** for general wellness awareness only.  
> Calorie estimates are approximate and based on standard Indian food portion sizes.  
> Always consult a certified nutritionist for personalized dietary advice.

---

## 🔗 Related Branches

| Branch | Feature |
|--------|---------|
| `disease-prediction-engine` | Symptom → Disease prediction |
| `drug-condition-api` | Drug condition API v1 |
| `drug-condition-api-v2` | Drug condition API v2 (20 conditions) |
| `food-api-final` | Food barcode → Nutri-Score |
| `food-health-api` | ← You are here |
| `medicine-barcode-api` | Medicine barcode scanner |

---

## 👨‍💻 Author

**Harsh Raj** — [@Harsh28-raj](https://github.com/Harsh28-raj)  
2nd Year CS Student | AI/ML Developer  
Part of **Ai_healthcare** — an end-to-end AI health platform for Indian users.
