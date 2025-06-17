import os
import requests
import httpx
import asyncio
from fastapi import FastAPI, Depends, Form
from sqlalchemy.orm import Session
from db import SessionLocal, engine
from models import Base
from schemas import ChatInput
from crud import get_all_docs

# Setup database
Base.metadata.create_all(bind=engine)
app = FastAPI()

# Load env
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def build_prompt(user_message: str, docs: list):
    context = "\n\n".join(f"{d.title}:\n{d.content}" for d in docs)
    return f"""
Berikut adalah beberapa informasi internal perusahaan:\n\n{context}

Jawab pertanyaan berikut berdasarkan informasi di atas:
{user_message}
""".strip()

import json

def query_ollama(full_prompt: str):
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={"model": "llama3", "prompt": full_prompt},
            stream=True,
            timeout=60,
        )
    except Exception as e:
        return f"[ERROR] Gagal request Ollama: {e}"

    if response.status_code != 200:
        return f"[ERROR] Ollama error: {response.status_code}"

    full_response = ""
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            part = data.get("response", "")
            full_response += part
    return full_response.strip()


@app.post("/chat")
def chat(input: ChatInput, db: Session = Depends(get_db)):
    docs = get_all_docs(db)
    prompt = build_prompt(input.message, docs)
    reply = query_ollama(prompt)
    return {"reply": reply}


import threading

@app.post("/slack/chat")
def slack_chat(text: str = Form(...), response_url: str = Form(...)):
    threading.Thread(target=handle_slack_request, args=(text, response_url)).start()
    return "Baik, pertanyaan kamu sedang diproses. Mohon tunggu sebentar..."

def handle_slack_request(text: str, response_url: str):
    db = SessionLocal()
    try:
        docs = get_all_docs(db)
        prompt = build_prompt(text, docs)
        reply = query_ollama(prompt)
    finally:
        db.close()
        
    try:
        requests.post(response_url, json={"text": reply})
    except Exception as e:
        print(f"Gagal kirim Slack reply: {e}")

