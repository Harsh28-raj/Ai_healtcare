import os
import shutil
import uuid
from pathlib import Path
from collections import defaultdict
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI(title="MediMind API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = "temp_uploads"
Path(TEMP_DIR).mkdir(exist_ok=True)

session_store = defaultdict(list)

def ask_llm(messages: list) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=1024,
    )
    return response.choices[0].message.content

def clean_query(q: str) -> str:
    return q.lower().replace("i have", "").replace("tell me", "").strip()

def get_history_messages(session_id: str) -> list:
    history = session_store[session_id]
    messages = [{"role": "system", "content": "You are a calm and helpful medical assistant. Explain clearly. Suggest basic care first. Only recommend a doctor if severe or persistent."}]
    for msg in history[-10:]:
        role = "user" if msg["role"] == "human" else "assistant"
        messages.append({"role": role, "content": msg["content"]})
    return messages

def save_to_memory(session_id, q, a):
    session_store[session_id].append({"role": "human", "content": q})
    session_store[session_id].append({"role": "ai", "content": a})
    if len(session_store[session_id]) > 20:
        session_store[session_id] = session_store[session_id][-20:]

def extract_pdf_text(path: str) -> str:
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()

class QuestionRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

@app.get("/health")
def health():
    return {"status": "ok", "active_sessions": len(session_store)}

@app.post("/ask")
def ask(body: QuestionRequest):
    session_id = body.session_id or str(uuid.uuid4())
    cleaned = clean_query(body.question)

    red_flags = ["chest pain", "shortness of breath", "heart attack", "severe bleeding", "unconscious"]
    if any(word in cleaned for word in red_flags):
        return {
            "question": body.question,
            "answer": "⚠️ This may be serious. Please seek immediate medical help or call emergency services.",
            "session_id": session_id
        }

    messages = get_history_messages(session_id)
    messages.append({"role": "user", "content": body.question})
    answer = ask_llm(messages)
    save_to_memory(session_id, body.question, answer)

    return {"question": body.question, "answer": answer, "session_id": session_id}

@app.post("/ask-pdf")
async def ask_pdf(question: str, file: UploadFile = File(...), session_id: Optional[str] = None):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF supported")

    session_id = session_id or str(uuid.uuid4())
    temp_path = f"{TEMP_DIR}/{uuid.uuid4()}_{file.filename}"

    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        text = extract_pdf_text(temp_path)
        if not text:
            raise HTTPException(status_code=400, detail="No text found in PDF")

        context = text[:3000]
        messages = [
            {"role": "system", "content": "Answer based on the provided document context only."},
            {"role": "user", "content": f"Document:\n{context}\n\nQuestion: {question}"}
        ]
        answer = ask_llm(messages)
        save_to_memory(session_id, question, answer)

        return {"question": question, "answer": answer, "session_id": session_id}

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/prescription-schedule")
async def prescription_schedule(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF supported")

    temp_path = f"{TEMP_DIR}/{uuid.uuid4()}_{file.filename}"

    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        text = extract_pdf_text(temp_path)
        if not text:
            raise HTTPException(status_code=400, detail="No text found in prescription")

        prompt = f"""
You are a medical assistant. Extract medicines from this prescription and generate a daily schedule.

Prescription:
{text[:2000]}

Format:
MEDICINES FOUND:
- [Name] | [Dosage] | [Frequency]

DAILY SCHEDULE:
Morning (with breakfast): ...
Afternoon (with lunch): ...
Evening: ...
Night (before sleep): ...

NOTES: ...

Do not make up medicines. If unclear, say so.
"""
        schedule = ask_llm([{"role": "user", "content": prompt}])
        return {"schedule": schedule, "source": file.filename}

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.delete("/clear-memory/{session_id}")
def clear_memory(session_id: str):
    if session_id in session_store:
        del session_store[session_id]
    return {"session_id": session_id, "message": "Memory cleared"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)