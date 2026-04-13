<div align="center">

# 🩺 MediMind — RAG-based Medical Chatbot

Context-aware medical Q&A over a curated knowledge base using FAISS vector search + Groq-hosted LLMs.

[![Streamlit App](https://img.shields.io/badge/Streamlit-Live%20Demo-FF4B4B?style=for-the-badge&logo=streamlit)](https://medimind-bot.streamlit.app)
[![API Docs](https://img.shields.io/badge/FastAPI-Render%20API-009688?style=for-the-badge&logo=fastapi)](https://ai-healtcare-22.onrender.com/docs)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)](https://python.org)

> Part of the **Ai_healthcare** platform — Branch: `rag-medical-bot`

</div>

---

## 📌 What It Does

User asks a medical question → FAISS retrieves relevant chunks from medical PDF knowledge base → Groq LLM generates a grounded answer → Response shown with source document references.

Instead of hallucinating, the LLM is **constrained by retrieved passages** from a curated medical encyclopedia — making answers factual and traceable.

**Two entry points:**
- 🖥️ **Streamlit UI** — Chat interface at `medimind-bot.streamlit.app`
- ⚡ **FastAPI endpoint** — REST API at `ai-healtcare-22.onrender.com`

---

## 🏗️ Architecture

```
PDF(s) ──► Text Splitter ──► Embeddings ──► FAISS Index
                                                  │
User Query ──► Retriever (top-k chunks) ──────────┘
                    │
              Prompt Assembly
              {context} + {question}
                    │
            LLM Generation (Groq / HuggingFace)
                    │
            Answer + Source Chunks
```

### Main Components

| File | Role |
|------|------|
| `create_memory_for_llm.py` | Builds FAISS index from PDFs |
| `connect_memory_with_llm.py` | CLI RAG query via HuggingFaceEndpoint |
| `medibot.py` | Streamlit chat UI using Groq + FAISS |
| `main.py` | FastAPI app — `/ask-pdf` REST endpoint |
| `vectorstore/db_faiss` | Persisted FAISS index |
| `data/` | PDF source documents (medical encyclopedia) |

---

## ✨ Key Features

- FAISS vector store for fast semantic retrieval
- SentenceTransformer embeddings (`all-MiniLM-L6-v2`)
- Groq-hosted **Llama 4 Maverick** as LLM backend
- HuggingFace **Mistral 7B Instruct** as CLI backend
- Modular prompt template — customizable tone/style
- Source document traceability — shows which chunks answered
- Streamlit resource cache for embeddings + vector store
- FastAPI `/ask-pdf` endpoint for programmatic access

---

## 🚀 Live Deployments

### 🖥️ Streamlit Chat UI
```
https://medimind-bot.streamlit.app
```
Open and start asking medical questions directly in the chat interface.

### ⚡ FastAPI REST API

```
https://ai-healtcare-22.onrender.com
```

**Swagger Docs:**
```
https://ai-healtcare-22.onrender.com/docs#/default/ask_pdf_ask_pdf_post
```

---

## 🚀 API Reference

### `POST /ask-pdf`

Ask a medical question — returns grounded answer with source references.

**Request Body:**
```json
{
  "query": "How is hypertension managed?"
}
```

**Response (200 OK):**
```json
{
  "answer": "Hypertension is managed through lifestyle modifications including reduced sodium intake, regular physical activity, and weight management. Pharmacological treatment includes ACE inhibitors, beta-blockers, and diuretics depending on severity.",
  "sources": [
    {
      "page": 142,
      "snippet": "...antihypertensive therapy should be initiated when blood pressure consistently exceeds 140/90 mmHg..."
    },
    {
      "page": 145,
      "snippet": "...lifestyle interventions remain the first-line approach for stage 1 hypertension..."
    }
  ]
}
```

**Example cURL:**
```bash
curl -X POST https://ai-healtcare-22.onrender.com/ask-pdf \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the symptoms of diabetes?"}'
```

---

## 🔐 Environment Variables

Create a `.env` file:
```env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxx
GROQ_API_KEY=groq_xxxxxxxxxxxxxxxxxxx
```

Optional:
```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
HUGGINGFACE_REPO_ID=mistralai/Mistral-7B-Instruct-v0.3
```

---

## ⚙️ Local Setup

### 1. Clone the branch
```bash
git clone -b rag-medical-bot https://github.com/Harsh28-raj/Ai_healthcare.git
cd Ai_healthcare
```

### 2. Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate        # Mac/Linux
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set environment variables
```bash
export HF_TOKEN=hf_...
export GROQ_API_KEY=groq_...
```

---

## 🗂️ Building the Vector Store

Run once before starting the app:
```bash
python create_memory_for_llm.py
```

This will:
1. Load PDFs from `data/`
2. Chunk text (chunk_size=1000, overlap=150)
3. Embed using `all-MiniLM-L6-v2`
4. Persist FAISS index to `vectorstore/db_faiss`

**Pipeline code:**
```python
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

loader = PyPDFLoader("data/The_GALE_ENCYCLOPEDIA_of_MEDICINE_SECOND.pdf")
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
chunks = splitter.split_documents(docs)
emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.from_documents(chunks, emb)
db.save_local("vectorstore/db_faiss")
```

---

## 💬 Running Locally

### Streamlit Chat UI
```bash
export GROQ_API_KEY=groq_...
streamlit run medibot.py
```
Open: `http://localhost:8501`

### FastAPI Server
```bash
uvicorn main:app --reload
```
Open: `http://localhost:8000/docs`

### CLI Version
```bash
export HF_TOKEN=hf_...
python connect_memory_with_llm.py
```

---

## 🔄 Switching Embedding Modes

`medibot.py` supports two modes:
```python
# Local model (default)
vectorstore = get_vectorstore()

# HuggingFace API mode (limited disk environments)
vectorstore = get_vectorstore_hf_api(os.environ["HF_TOKEN"])
```

---

## 🛠️ Prompt Customization

Modify `CUSTOM_PROMPT_TEMPLATE` in `medibot.py` or `connect_memory_with_llm.py`:
```python
CUSTOM_PROMPT_TEMPLATE = """
Use the following context to answer the question.
If you don't know the answer, say "I don't know" — do not guess.

Context: {context}
Question: {question}

Answer:
"""
```
Keep `{context}` and `{question}` variables intact.

---

## 🧪 Quick Sanity Test

```bash
python - <<'PY'
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
emb = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
db = FAISS.load_local('vectorstore/db_faiss', emb, allow_dangerous_deserialization=True)
print('Index loaded. Sample:\n', db.similarity_search('What is diabetes?', k=2))
PY
```

---

## 🐛 Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `FAISS file not found` | Vector store not built | Run `create_memory_for_llm.py` first |
| Empty / irrelevant answers | `k` too small or chunk mismatch | Increase `search_kwargs={'k':5}` or rebuild index |
| Hallucinations | LLM ignoring context | Tighten prompt, lower temperature |
| `HF_TOKEN not set` | Missing env var | Export token or add to `.env` |
| `GROQ_API_KEY not set` | Missing env var | Export key or add to `.env` |
| Render cold start delay | Free tier sleep | First request takes 30–50s |
| Virtualenv mismatch | Old `VIRTUAL_ENV` exported | `deactivate` → `source .venv/bin/activate` |

---

## 🧱 Roadmap / Extending

- Multi-PDF ingestion (glob over `data/*.pdf`)
- Streaming token output in Streamlit UI
- Hindi / multilingual query support
- OpenAI / Anthropic backend abstraction
- RAGAS evaluation for answer faithfulness
- Integration with main healthcare app as embedded bot

---

## ⚠️ Disclaimer

> This tool is for **educational and reference purposes only.**  
> It does **not** provide medical advice, diagnosis, or treatment recommendations.  
> Always consult a licensed healthcare professional for medical decisions.

---

## ✅ Quick Start Recap

```bash
python create_memory_for_llm.py       # build FAISS index (one time)
streamlit run medibot.py              # Streamlit UI (needs GROQ_API_KEY)
uvicorn main:app --reload             # FastAPI server
python connect_memory_with_llm.py     # CLI (needs HF_TOKEN)
```

---

## 🔗 Related Branches

| Branch | Feature |
|--------|---------|
| `disease-prediction-engine` | Symptom → Disease prediction |
| `drug-condition-api` | Drug condition API v1 |
| `drug-condition-api-v2` | Drug condition API v2 (20 conditions) |
| `food-api-final` | Food barcode → Nutri-Score |
| `food-health-api` | Daily food log → Health score |
| `medicine-barcode-api` | Medicine barcode scanner |
| `rag-medical-bot` | ← You are here |

---

## 👨‍💻 Author

**Harsh Raj** — [@Harsh28-raj](https://github.com/Harsh28-raj)  
2nd Year CS Student | AI/ML Developer  
Part of **Ai_healthcare** — an end-to-end AI health platform for Indian users.
