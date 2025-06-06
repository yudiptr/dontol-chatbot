import os
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db import SessionLocal, engine
from models import Base
from schemas import ChatInput
from crud import get_all_docs
import requests

Base.metadata.create_all(bind=engine)
app = FastAPI()
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/chat")
def chat(input: ChatInput, db: Session = Depends(get_db)):
    # Ambil semua dokumen internal untuk jadi konteks
    docs = get_all_docs(db)
    context = "\n\n".join(f"{d.title}:\n{d.content}" for d in docs)

    # Gabungkan prompt dengan konteks
    full_prompt = f"""
Berikut adalah beberapa informasi internal perusahaan:\n\n{context}

Jawab pertanyaan berikut berdasarkan informasi di atas:
{input.message}
""".strip()

    # Kirim ke Ollama
    
    response = requests.post(
        OLLAMA_API_URL,
        json={"model": "llama3", "prompt": full_prompt},
        stream=True
    )

    full_response = ""

    if response.status_code != 200:
        return {"error": f"Ollama error: {response.status_code}"}

    for line in response.iter_lines():
        if line:
            line = line.decode("utf-8")
            if '"response":"' in line:
                part = line.split('"response":"')[1].split('"')[0]
                full_response += part

    return {"reply": full_response.strip()}
