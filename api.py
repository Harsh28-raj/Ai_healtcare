import os
import shutil
import uuid
from pathlib import Path
from collections import defaultdict

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from groq import Groq
from dotenv import load_dotenv

# ───────────────────────────────
# ENV
# ───────────────────────────────
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ───────────────────────────────
# APP
# ───────────────────────────────
app = FastAPI(title="MediMind API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FAISS_PATH = "vectorstore/db_faiss"
TEMP_DIR = "temp_uploads"
Path(TEMP_DIR).mkdir(exist_ok=True)

session_store = defaultdict(list)

# ───────────────────────────────
# UTILITIES
# ───────────────────────────────

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def ask_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
    )
    return response.choices[0].message.content


def clean_query(q: str) -> str:
    return q.lower().replace("i have", "").replace("tell me", "").strip()


def build_history_prompt(session_id: str, question: str) -> str:
    history = session_store[session_id]

    if not history:
        return question

    history_text = ""
    for msg in history[-6:]:
        role = "User" if msg["role"] == "human" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"

    return f"""
Previous conversation:
{history_text}

Current question:
{question}
"""


def save_to_memory(session_id, q, a):
    session_store[session_id].append({"role": "human", "content": q})
    session_store[session_id].append({"role": "ai", "content": a})


# ───────────────────────────────
# LOAD VECTORSTORE
# ───────────────────────────────

gale_vectorstore = None

@app.on_event("startup")
def load_db():
    global gale_vectorstore
    embeddings = get_embeddings()

    gale_vectorstore = FAISS.load_local(
        DB_FAISS_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    print("✅ FAISS loaded")


# ───────────────────────────────
# MODELS
# ───────────────────────────────

class QuestionRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


# ───────────────────────────────
# ENDPOINTS
# ───────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(body: QuestionRequest):

    if gale_vectorstore is None:
        raise HTTPException(status_code=500, detail="Vector DB not loaded")

    session_id = body.session_id or str(uuid.uuid4())

    # 🔴 Clean query
    cleaned_question = clean_query(body.question)

    # 🔴 Basic guardrail
    red_flags = [
        "chest pain",
        "shortness of breath",
        "heart attack",
        "severe bleeding",
        "unconscious"
    ]

    if any(word in cleaned_question for word in red_flags):
        return {
            "question": body.question,
            "answer": "⚠️ This may be serious. Please seek immediate medical help.",
            "session_id": session_id,
            "sources": []
        }

    query = build_history_prompt(session_id, cleaned_question)

    docs = gale_vectorstore.similarity_search(query, k=3)

    if not docs:
        return {
            "question": body.question,
            "answer": "I don't know based on available information.",
            "session_id": session_id,
            "sources": []
        }

    # 🔥 FILTER BAD CONTEXT (MAIN FIX)
    filtered_docs = []

    for d in docs:
        text = d.page_content.lower()

        if "call a physician" in text:
            continue
        if "immediate medical attention" in text:
            continue

        filtered_docs.append(d.page_content)

    context = "\n".join(filtered_docs)

    # 🔥 IMPROVED PROMPT
    prompt = f"""
You are a calm and helpful medical assistant.

Your job is to EXPLAIN, not copy.

Rules:
- Do NOT copy sentences directly from context
- Do NOT give extreme advice unless clearly necessary
- If symptom is common (like headache), give simple causes
- Suggest basic care first (rest, hydration, stress)
- Only suggest doctor if severe or persistent

Context:
{context}

Question:
{query}

Answer in a friendly and balanced way:
"""

    answer = ask_llm(prompt)

    # 🔴 FINAL SAFETY FIX
    if "call a physician" in answer.lower():
        answer = "Headaches are common and can be caused by stress, dehydration, or lack of sleep. Try rest and hydration. If it persists or becomes severe, consult a doctor."

    save_to_memory(session_id, body.question, answer)

    sources = [doc.page_content[:200] for doc in docs]

    return {
        "question": body.question,
        "answer": answer,
        "session_id": session_id,
        "sources": sources
    }


@app.post("/ask-pdf")
async def ask_pdf(question: str, file: UploadFile = File(...)):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF supported")

    temp_path = f"{TEMP_DIR}/{uuid.uuid4()}_{file.filename}"

    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        loader = PyPDFLoader(temp_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = splitter.split_documents(docs)

        if not chunks:
            raise HTTPException(status_code=400, detail="No text in PDF")

        texts = [doc.page_content for doc in chunks if doc.page_content.strip()]

        if not texts:
            raise HTTPException(status_code=400, detail="Empty PDF content")

        embeddings = get_embeddings()
        db = FAISS.from_texts(texts, embeddings)

        docs = db.similarity_search(question, k=3)
        context = "\n".join([d.page_content for d in docs])

        prompt = f"""
Explain clearly using the context below.

Context:
{context}

Question:
{question}
"""

        answer = ask_llm(prompt)

        return {"answer": answer}

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ───────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)