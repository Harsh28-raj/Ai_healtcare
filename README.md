# 💊 Medicine Barcode Scanner API

> Indian medicine lookup API with barcode scan, search, and autocomplete — part of the **Ai_healthcare** platform.  
> Branch: `medicine-barcode-api`

---

## 📌 What It Does

Three-in-one medicine intelligence API:
1. **Barcode Scan** → Fetch complete medicine details from NDC/barcode
2. **Medicine Search** → Search by name → Get composition, side effects, manufacturer
3. **Autocomplete Suggest** → Type 3 letters → Get dropdown suggestions instantly

Built on **11,000+ Indian medicines dataset** with fuzzy matching + ML-based drug category prediction.

---

## 🗂️ Branch Structure

```
medicine-barcode-api/
│
├── data/
│   ├── medicines_11k.csv        # 11,000+ Indian medicines dataset
│   └── medicines_az.csv         # A-Z indexed medicines (fast lookup)
├── main.py                      # FastAPI app — all 3 endpoints
├── search.py                    # Fuzzy search logic
├── model.py                     # ML model loader & predictor
├── medicine_model.pkl           # Trained drug category classifier
├── requirements.txt             # Python dependencies
├── test_api.py                  # API test cases
├── test_api2.py                 # Extended test cases
├── test_fda.py                  # OpenFDA integration tests
├── test_results.txt             # Test output logs
├── test_results_ascii.txt       # ASCII test output
└── tests.txt                    # Manual test cases
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Indian Medicine DB | Kaggle — 11,000+ medicines CSV |
| External API | OpenFDA NDC API |
| Fuzzy Search | fuzzywuzzy library |
| ML Model | Passive Aggressive Classifier (medicine_model.pkl) |
| Autocomplete | Prefix-based fast search on medicines_az.csv |
| Deployment | Render (Free Tier) |
| Language | Python 3.10+ |

---

## 🧠 How It Works

```
                    ┌─────────────────────────────┐
                    │      User Action             │
                    └──────────┬──────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
   Scan Barcode          Type Medicine         Search Bar
          │                    │               (3+ letters)
          ▼                    ▼                    ▼
  /medicine/barcode    /medicine/search     /medicine/suggest
  ?code=XXXXX-XXX      ?name=dolo           ?q=dol
          │                    │                    │
          ▼                    │                    ▼
   OpenFDA NDC API             │            Prefix match on
   + local DB lookup           │            medicines_az.csv
          │                    │                    │
     404? ↓ yes                │                    ▼
   Ask user for name           │           Dropdown suggestions
          │                    │
          └────────────────────┘
                    │
                    ▼
          Fuzzy match on medicines_11k.csv
                    │
                    ▼
          ML model → Drug Category prediction
                    │
                    ▼
          JSON Response (name, composition,
          side effects, manufacturer, category)
```

---

## 🚀 API Reference

### Base URL
```
https://ai-healtcare-12.onrender.com
```

---

### 1️⃣ `GET /medicine/barcode`

Fetch medicine details by barcode/NDC code.

**Query Parameter:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | string | ✅ | Barcode or NDC code from medicine packaging |

**Example Request:**
```
GET https://ai-healtcare-12.onrender.com/medicine/barcode?code=68462-0283-01
```

**Response (200 OK):**
```json
{
  "barcode": "68462-0283-01",
  "name": "Dolo 650",
  "manufacturer": "Micro Labs Ltd",
  "composition": "Paracetamol 650mg",
  "category": "Analgesic / Antipyretic",
  "side_effects": ["Nausea", "Liver damage (overdose)", "Allergic reaction"],
  "source": "openfda"
}
```

**Response (404 — Barcode not found):**
```json
{
  "status": "not_found",
  "message": "Barcode not found. Please search by medicine name.",
  "fallback": "/medicine/search?name=<medicine_name>"
}
```

> ⚠️ On 404 → redirect user to search endpoint

---

### 2️⃣ `GET /medicine/search`

Search medicine by name — returns full details.

**Query Parameter:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ | Medicine name (partial or full) |

**Example Request:**
```
GET https://ai-healtcare-12.onrender.com/medicine/search?name=dolo
```

**Response (200 OK):**
```json
{
  "query": "dolo",
  "results": [
    {
      "name": "Dolo 650",
      "manufacturer": "Micro Labs Ltd",
      "composition": "Paracetamol 650mg",
      "category": "Analgesic / Antipyretic",
      "side_effects": ["Nausea", "Liver damage (overdose)", "Allergic reaction"],
      "type": "Tablet"
    },
    {
      "name": "Dolo 500",
      "manufacturer": "Micro Labs Ltd",
      "composition": "Paracetamol 500mg",
      "category": "Analgesic / Antipyretic",
      "side_effects": ["Nausea", "Rash"],
      "type": "Tablet"
    }
  ],
  "total": 2
}
```

---

### 3️⃣ `GET /medicine/suggest`

Autocomplete — returns suggestions as user types (for search bar dropdown).

**Query Parameter:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `q` | string | ✅ | Partial medicine name (min 2–3 characters) |

**Example Request:**
```
GET https://ai-healtcare-12.onrender.com/medicine/suggest?q=dol
```

**Response (200 OK):**
```json
{
  "query": "dol",
  "suggestions": [
    "Dolo 650",
    "Dolo 500",
    "Dolokind Plus",
    "Dolopar",
    "Dolonex DT"
  ]
}
```

> User selects suggestion → hits `/medicine/search?name=<selected>`

---

## 🌐 Web Team Integration Flow

```
User scans barcode
        ↓
GET /medicine/barcode?code=XXXXX-XXX
        ↓
Found? → Show details ✅
        ↓
404?   → Prompt user to type name
        ↓
GET /medicine/search?name=dolo → Show details ✅

────────────────────────────────

Search bar flow:
User types "dol"
        ↓
GET /medicine/suggest?q=dol
        ↓
Show dropdown suggestions
        ↓
User selects → GET /medicine/search?name=Dolo+650
        ↓
Show full medicine details ✅
```

---

## 🛠️ Local Setup

### 1. Clone the branch
```bash
git clone -b medicine-barcode-api https://github.com/Harsh28-raj/Ai_healthcare.git
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

### 5. Test endpoints
```bash
# Barcode
curl "http://localhost:8000/medicine/barcode?code=68462-0283-01"

# Search
curl "http://localhost:8000/medicine/search?name=dolo"

# Suggest
curl "http://localhost:8000/medicine/suggest?q=dol"
```

---

## 📦 requirements.txt

```
fastapi
uvicorn
pandas
fuzzywuzzy
python-Levenshtein
scikit-learn
joblib
requests
pydantic
```

---

## 📱 Flutter Integration

```dart
// Barcode scan
final barcode = await FlutterBarcodeScanner.scanBarcode(...);
final res = await http.get(
  Uri.parse('https://ai-healtcare-12.onrender.com/medicine/barcode?code=$barcode')
);
if (res.statusCode == 404) {
  // show name input dialog
}

// Search
final res = await http.get(
  Uri.parse('https://ai-healtcare-12.onrender.com/medicine/search?name=$medicineName')
);

// Autocomplete (on text change)
final res = await http.get(
  Uri.parse('https://ai-healtcare-12.onrender.com/medicine/suggest?q=$query')
);
// populate dropdown with suggestions
```

---

## 📊 Dataset Info

| Dataset | Details |
|---------|---------|
| `medicines_11k.csv` | 11,000+ Indian medicines with composition, manufacturer, side effects |
| `medicines_az.csv` | A-Z sorted index for fast autocomplete prefix lookup |
| Source | Kaggle Indian Medicines Dataset + OpenFDA |

---

## ⚠️ Disclaimer

> This API provides **medicine information for general awareness only.**  
> It does **not** recommend dosage or replace a doctor's prescription.  
> Always consult a qualified doctor or pharmacist before taking any medicine.

---

## 🔗 Related Branches

| Branch | Feature |
|--------|---------|
| `disease-prediction-engine` | Symptom → Disease prediction |
| `drug-condition-api` | Drug condition API v1 |
| `drug-condition-api-v2` | Drug condition API v2 (20 conditions) |
| `food-api-final` | Food barcode → Nutri-Score |
| `food-health-api` | Daily food log → Health score |
| `medicine-barcode-api` | ← You are here |

---

## 👨‍💻 Author

**Harsh Raj** — [@Harsh28-raj](https://github.com/Harsh28-raj)  
2nd Year CS Student | AI/ML Developer  
Part of **Ai_healthcare** — an end-to-end AI health platform for Indian users.

