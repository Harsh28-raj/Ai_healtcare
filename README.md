<div align="center">

# 🏥 Ai_healthcare

### An end-to-end AI-powered healthcare platform for Indian users

[![Web App](https://img.shields.io/badge/Web%20App-Live-00C853?style=for-the-badge&logo=vercel)](https://healhcare-ai.vercel.app)
[![Streamlit Bot](https://img.shields.io/badge/MediMind%20Bot-Live-FF4B4B?style=for-the-badge&logo=streamlit)](https://medimind-bot.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Deployed-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)

> Built by **Harsh Raj** — 2nd Year CS Student | AI/ML Developer

</div>

---

## 📌 What Is This?

**Ai_healthcare** is a multi-feature AI healthcare platform designed specifically for Indian users. It combines multiple ML models, NLP pipelines, and external APIs into one unified health intelligence system — covering disease prediction, food analysis, medicine intelligence, and a RAG-based medical chatbot.

Every feature is independently deployed as a **FastAPI microservice** on Render, consumed by a **Flutter mobile app** and a **React web frontend**.

---

## 🌐 Live Deployments

| Interface | Link |
|-----------|------|
| 🌐 Web Frontend | [healhcare-ai.vercel.app](https://healhcare-ai.vercel.app) |
| 🤖 MediMind Chatbot | [medimind-bot.streamlit.app](https://medimind-bot.streamlit.app) |

---

## 🗂️ Project Structure — Branches

Each feature lives in its own branch with an independent FastAPI backend:

```
Ai_healthcare/
│
├── main                      ← You are here (project overview)
├── disease-prediction-engine ← Symptom → Disease prediction
├── drug-condition-api        ← Drug condition classifier v1
├── drug-condition-api-v2     ← Drug condition classifier v2 (20 conditions)
├── food-api-final            ← Food barcode → Nutri-Score
├── food-health-api           ← Daily food log → Health score
├── medicine-barcode-api      ← Medicine barcode + search + autocomplete
└── medimind-rag-api          ← RAG medical chatbot (FAISS + Groq)
```

---

## 🚀 Features & API Endpoints

### 1. 🩺 Disease Prediction Engine
> Branch: `disease-prediction-engine`

Predicts **Top 5 diseases** from user-selected symptoms with confidence scores and remedy recommendations.

| Detail | Info |
|--------|------|
| Model | Keras Neural Network |
| Input | 377 binary symptom features |
| Output | Top 5 diseases + confidence scores |
| Accuracy | **85.6%** |
| Classes | 773 diseases |

**Endpoint:**
```
POST https://ai-healtcare.onrender.com/predict
Body: { "symptoms": ["fever", "headache", "vomiting"] }
```

---

### 2. 💊 Drug Condition Classifier v1
> Branch: `drug-condition-api`

Predicts **Top 4 drug conditions** from a patient's free-text review.

| Detail | Info |
|--------|------|
| Model | Passive Aggressive Classifier |
| Vectorizer | TF-IDF (15,000 features) |
| Input | Free text string |
| Output | Top 4 conditions (hardcoded pool) |

**Endpoint:**
```
POST https://ai-healtcare-2.onrender.com/recommend
Body: { "review": "I have severe anxiety and stress" }
```

---

### 3. 💊 Drug Condition Classifier v2
> Branch: `drug-condition-api-v2`

Upgraded version — dynamically predicts **Top 4 from a pool of 20 conditions**.

| Detail | Info |
|--------|------|
| Model | Passive Aggressive Classifier (upgraded) |
| Conditions Pool | 20 drug conditions |
| Model Size | ~1.5MB |
| Improvement | Dynamic Top 4 vs hardcoded v1 |

**Endpoint:**
```
POST /recommend
Body: { "review": "I have severe anxiety and stress" }
```

---

### 4. 🍔 Food Barcode Scanner
> Branch: `food-api-final`

Scan any food product barcode → Get **Nutri-Score grade** (A/B/C/D) + full nutritional breakdown.

| Detail | Info |
|--------|------|
| Scoring | Nutri-Score algorithm (rule-based) |
| Data Source | Open Food Facts API + local `food_db.json` |
| Input | EAN/UPC barcode number |
| Output | Grade A–D, calories, sugar, fat, fiber, salt |

**Endpoint:**
```
GET https://ai-healtcare-9.onrender.com/predict_health_predict_barcode?barcode=8901063155619
```

**Real Example — Britannia Tiger Krunch:**
```json
{
  "product_name": "Britannia Tiger Krunch Chocochips",
  "final_grade": "C",
  "category": "Moderate",
  "health_score_raw": 6.37,
  "input_nutrients": { "energy_kcal": 487, "sugars": 28.3, "fat": 19.1 }
}
```

---

### 5. 🥗 Daily Food Health Log
> Branch: `food-health-api`

User types daily food intake in **plain natural language** → API detects items → Returns calories, health score, risk flags, and personalized recommendation.

| Detail | Info |
|--------|------|
| Model | Sklearn ML model + StandardScaler |
| Food DB | Indian food calorie database |
| Input | Natural language string |
| Output | Calories, health score (0–100), risk flags, recommendation |

**Endpoint:**
```
POST https://ai-healtcare-13.onrender.com/log
Body: { "text": "i have eaten dal rice and 2 samosa 5 chicken" }
```

**Real Example Output:**
```json
{
  "estimated_calories": 1342,
  "health_score": 70,
  "risk_flags": ["High Calorie", "High Fat"],
  "recommendation": "Watch out for salt and fried items in your next meal."
}
```

---

### 6. 💉 Medicine Barcode Scanner
> Branch: `medicine-barcode-api`

Three-in-one medicine intelligence — barcode scan, name search, and autocomplete suggestions. Built on 11,000+ Indian medicines dataset.

| Detail | Info |
|--------|------|
| Dataset | 11,000+ Indian medicines (Kaggle) |
| Fuzzy Search | fuzzywuzzy library |
| ML Model | Passive Aggressive Classifier (drug category) |
| External API | OpenFDA NDC API |

**Endpoints:**
```
GET https://ai-healtcare-12.onrender.com/medicine/barcode?code=XXXXX-XXX
GET https://ai-healtcare-12.onrender.com/medicine/search?name=dolo
GET https://ai-healtcare-12.onrender.com/medicine/suggest?q=dol
```

---

### 7. 🤖 MediMind — RAG Medical Chatbot
> Branch: `medimind-rag-api`

Context-aware medical Q&A using **FAISS vector search + Groq LLM**. Answers grounded in a curated medical encyclopedia — no hallucinations.

| Detail | Info |
|--------|------|
| Vector Store | FAISS |
| Embeddings | `all-MiniLM-L6-v2` (SentenceTransformer) |
| LLM | Groq — Llama 4 Maverick |
| CLI Backend | HuggingFace — Mistral 7B Instruct |
| Knowledge Base | Gale Encyclopedia of Medicine (PDF) |
| Streamlit UI | [medimind-bot.streamlit.app](https://medimind-bot.streamlit.app) |

**Endpoint:**
```
POST https://ai-healtcare-22.onrender.com/ask-pdf
Body: { "query": "How is hypertension managed?" }
```

---

## 🧠 ML Models Summary

| Model | Algorithm | Task | Accuracy |
|-------|-----------|------|----------|
| Disease Predictor | Keras Neural Network | 773-class disease classification | **85.6%** |
| Drug Condition v1 | Passive Aggressive Classifier | 4-class condition prediction | — |
| Drug Condition v2 | Passive Aggressive Classifier | 20-class condition prediction | — |
| Medicine Categorizer | Passive Aggressive Classifier | Drug category prediction | — |
| Food Health Scorer | Sklearn + StandardScaler | Health score from food intake | — |
| Nutri-Score | Rule-based formula | Food grade A–D from nutrients | — |
| RAG Pipeline | FAISS + Groq LLM | Medical Q&A with retrieval | — |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   USER INTERFACES                    │
│  Flutter Mobile App    │    React Web (Vercel)       │
│  Streamlit Chatbot     │    Swagger API Docs         │
└────────────────────────┬────────────────────────────┘
                         │ HTTP / REST
┌────────────────────────▼────────────────────────────┐
│              FastAPI MICROSERVICES (Render)          │
│                                                      │
│  /predict      /recommend    /log    /ask-pdf        │
│  /medicine/barcode    /medicine/search               │
│  /medicine/suggest    /barcode (food)                │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│                   ML / AI LAYER                      │
│  Keras NN  │  PAC Models  │  FAISS  │  Groq LLM     │
│  Sklearn   │  Fuzzy Match │  TF-IDF │  HuggingFace  │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│                   DATA LAYER                         │
│  Kaggle Indian Medicines (11k)  │  UCI Drug Reviews  │
│  USDA FoodData  │  OpenFDA API  │  Open Food Facts   │
│  Symptom-Disease Dataset (773)  │  Medical PDFs      │
└─────────────────────────────────────────────────────┘
```

---

## ⚙️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| Mobile Frontend | Flutter (Dart) |
| Web Frontend | React, Vercel |
| Backend | FastAPI, Python 3.10+ |
| Deep Learning | TensorFlow / Keras |
| ML | Scikit-learn, joblib |
| NLP | TF-IDF, fuzzywuzzy, LangChain |
| Vector Search | FAISS |
| LLM | Groq (Llama 4 Maverick), HuggingFace (Mistral 7B) |
| Embeddings | SentenceTransformers (`all-MiniLM-L6-v2`) |
| Deployment | Render (APIs), Streamlit Cloud, Vercel |
| Training | Google Colab |

---

## ⚠️ Disclaimer

> All APIs and features in this platform are for **educational and wellness awareness purposes only.**  
> This platform does **not** provide medical diagnosis, prescriptions, or treatment recommendations.  
> Always consult a qualified doctor or licensed healthcare professional for medical decisions.

---

## 👨‍💻 Author

**Harsh Raj** — [@Harsh28-raj](https://github.com/Harsh28-raj)  
2nd Year CS Student | AI/ML Developer  
Machine Learning Centre of Excellence (MLCOE)

---

<div align="center">
Built with ❤️ for Indian healthcare using open-source AI
</div>
