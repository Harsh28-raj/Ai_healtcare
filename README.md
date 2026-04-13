# 🍔 Food Health Score API

> Barcode-based food health scoring API — part of the **Ai_healthcare** platform.  
> Branch: `food-api-final`

---

## 📌 What It Does

User scans a **food product barcode** → API fetches product details → Calculates **health score** using Nutri-Score algorithm → Returns grade, category, and full nutritional breakdown.

Real example tested:
> **Britannia Tiger Krunch Chocochips** → Grade **C** → Category **Moderate**

---

## 🗂️ Branch Structure

```
food-api-final/
│
├── food_db.json             # Local food products database
├── main.py                  # FastAPI app — barcode prediction endpoint
└── requirements.txt         # Python dependencies
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Food Database | Local `food_db.json` + Open Food Facts API |
| Scoring Algorithm | Nutri-Score (rule-based) |
| Input | Barcode number (EAN/UPC) |
| Output | Product name, brand, grade, score, nutrients |
| Deployment | Render (Free Tier) |
| Language | Python 3.10+ |

---

## 🧠 How Health Score Is Calculated

```
Barcode Input
      ↓
Lookup food_db.json (local)
      ↓ (if not found)
Open Food Facts API fallback
      ↓
Nutri-Score Algorithm
  Negative points: sugars + fat + salt + energy_kcal
  Positive points: fiber + protein
      ↓
health_score_raw (0–100 scale)
      ↓
Final Grade Assignment:
  A → Excellent   (score ≥ 80)
  B → Good        (score 60–79)
  C → Moderate    (score 40–59)
  D → Poor        (score < 40)
```

**Real Example:**
| Field | Value |
|-------|-------|
| Product | Britannia Tiger Krunch Chocochips |
| Brand | Britannia |
| health_score_raw | 6.37 |
| final_grade | C |
| category | Moderate |
| energy_kcal | 487 |
| sugars | 28.3g |
| fat | 19.1g |
| fiber | 0g |
| salt | 0.445g |

---

## 🚀 API Reference

### Base URL
```
https://ai-healtcare-9.onrender.com
```

---

### `GET /predict_health_predict_barcode`

Fetches health score for a product by barcode.

**Query Parameter:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `barcode` | string | ✅ | EAN/UPC barcode number |

**Example Request:**
```
GET https://ai-healtcare-9.onrender.com/predict_health_predict_barcode?barcode=8901063155619
```

**Response (200 OK):**
```json
{
  "barcode": "8901063155619",
  "product_name": "Britannia Tiger Krunch Chocochips",
  "brand": "Britannia",
  "health_score_raw": 6.37,
  "final_grade": "C",
  "category": "Moderate",
  "input_nutrients": {
    "energy_kcal": 487,
    "sugars": 28.3,
    "fat": 19.1,
    "fiber": 0,
    "salt": 0.445
  }
}
```

**Grade Reference:**

| Grade | Category | Meaning |
|-------|----------|---------|
| A | Excellent | Very healthy choice |
| B | Good | Healthy choice |
| C | Moderate | Consume in moderation |
| D | Poor | Avoid or limit intake |

---

### `GET /health`

Check if API is live.

**Response:**
```json
{
  "status": "ok",
  "model": "food-health-score-api",
  "version": "1.0"
}
```

---

## 🛠️ Local Setup

### 1. Clone the branch
```bash
git clone -b food-api-final https://github.com/Harsh28-raj/Ai_healthcare.git
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
curl "http://localhost:8000/predict_health_predict_barcode?barcode=8901063155619"
```

---

## 📦 requirements.txt

```
fastapi
uvicorn
requests
pydantic
```

---

## 📱 Flutter Integration

```dart
final barcode = await FlutterBarcodeScanner.scanBarcode(...);

final response = await http.get(
  Uri.parse(
    'https://ai-healtcare-9.onrender.com/predict_health_predict_barcode?barcode=$barcode'
  ),
);

final data = jsonDecode(response.body);
// data['final_grade'] → show grade badge
// data['input_nutrients'] → show nutrition table
```

---

## ⚠️ Disclaimer

> This API provides **nutritional information and health scores** for general awareness only.  
> Scores are calculated using the Nutri-Score algorithm and may vary from official ratings.  
> Always check product labels for accurate nutritional information.

---

## 🔗 Related Branches

| Branch | Feature |
|--------|---------|
| `disease-prediction-engine` | Symptom → Disease prediction |
| `drug-condition-api` | Drug condition API v1 |
| `drug-condition-api-v2` | Drug condition API v2 (20 conditions) |
| `food-api-final` | ← You are here |
| `medicine-barcode-api` | Medicine barcode scanner |
| `daily-health-log` | Calorie & activity tracker |

---

## 👨‍💻 Author

**Harsh Raj** — [@Harsh28-raj](https://github.com/Harsh28-raj)  
2nd Year CS Student | AI/ML Developer  
Part of **Ai_healthcare** — an end-to-end AI health platform for Indian users.

