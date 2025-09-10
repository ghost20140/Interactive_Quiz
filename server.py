#!/usr/bin/env python3
from __future__ import annotations
import os, json, re
from typing import List, Dict
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# ----- Paths -----
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters")

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# ----- Keys (optional) -----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Ensure folders exist
os.makedirs(CHAPTERS_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)

SAFE_ID = re.compile(r"^[A-Za-z0-9._-]+$")  # sanitize chapter_id (allow dots/underscores/dashes)

# ---------- Helpers ----------
def list_chapter_ids() -> List[str]:
    """Return chapter ids derived from chapters/*.txt filenames."""
    ids = []
    for name in os.listdir(CHAPTERS_DIR):
        if name.lower().endswith(".txt"):
            ids.append(os.path.splitext(name)[0])
    return sorted(ids)

def chapter_title_from_id(ch_id: str) -> str:
    return re.sub(r"[_-]+", " ", ch_id).strip().title()

def read_chapter_text(chapter_id: str) -> str:
    if not SAFE_ID.match(chapter_id or ""):
        raise FileNotFoundError("Invalid chapter id")
    path = os.path.join(CHAPTERS_DIR, f"{chapter_id}.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def sample_questions_from_text(text: str, n: int = 5) -> List[Dict]:
    """Offline fallback—creates simple MCQs if no API key is set or API fails."""
    lines = [ln.strip("-• ").strip() for ln in (text or "").splitlines() if ln.strip()]
    facts = [ln for ln in lines if len(ln.split()) >= 4] or [
        "This is a placeholder fact about the chapter."
    ]
    out: List[Dict] = []
    for i in range(n):
        fact = facts[i % len(facts)]
        q = "Which statement best reflects the chapter content?"
        options = [
            fact,
            "An unrelated statement.",
            "A partially correct but misleading statement.",
            "A contradictory statement.",
        ]
        out.append(
            {
                "question": f"Q{i+1}: {q}",
                "options": options,
                "correct": 0,
                "explanation": "This option directly restates the accurate fact from the chapter.",
            }
        )
    return out

def parse_ai_json_block(text: str) -> List[Dict]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\[.*\]", text, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        raise

def generate_with_openai(chapter_content: str, num_questions: int) -> List[Dict]:
    if not OPENAI_API_KEY:
        raise RuntimeError("OpenAI key not set")
    prompt = f"""
You are an assessment writer.
Create {num_questions} multiple-choice questions (4 options each) based ONLY on the chapter text below.
Return JSON array only. Object schema:
{{"question": str, "options": [str,str,str,str], "correct": int, "explanation": str}}

Chapter:
\"\"\"{chapter_content}\"\"\""""
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 1500,
        },
        timeout=60,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"OpenAI error: {resp.text}")
    text = resp.json()["choices"][0]["message"]["content"]
    return parse_ai_json_block(text)

def generate_with_anthropic(chapter_content: str, num_questions: int) -> List[Dict]:
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("Anthropic key not set")
    prompt = f"""
Create {num_questions} multiple-choice questions (4 options) from the chapter.
Return ONLY a JSON array of objects: question, options[4], correct (index), explanation.

Chapter:
\"\"\"{chapter_content}\"\"\""""
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1500,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Anthropic error: {resp.text}")
    text = resp.json()["content"][0]["text"]
    return parse_ai_json_block(text)

# ---------- Routes ----------
@app.get("/")
def home():
    return render_template("index.html")

@app.get("/health")
def health():
    return jsonify(
        {
            "ok": True,
            "openai": bool(OPENAI_API_KEY),
            "anthropic": bool(ANTHROPIC_API_KEY),
            "chapters": list_chapter_ids(),
        }
    )

@app.get("/api/chapters")
def api_chapters():
    data = [{"id": ch_id, "title": chapter_title_from_id(ch_id)} for ch_id in list_chapter_ids()]
    return jsonify({"chapters": data})

@app.post("/api/generate-questions")
def api_generate_questions():
    payload = request.get_json(force=True) or {}
    chapter_id = (payload.get("chapter_id") or "").strip()
    num_questions = int(payload.get("num_questions") or 5)

    if not chapter_id:
        return jsonify({"success": False, "error": "chapter_id is required"}), 400

    try:
        chapter_text = read_chapter_text(chapter_id)

        # Try OpenAI → Anthropic → fallback
        try:
            if OPENAI_API_KEY:
                questions = generate_with_openai(chapter_text, num_questions)
            elif ANTHROPIC_API_KEY:
                questions = generate_with_anthropic(chapter_text, num_questions)
            else:
                questions = sample_questions_from_text(chapter_text, num_questions)
        except Exception:
            # Any LLM failure falls back to offline generation
            questions = sample_questions_from_text(chapter_text, num_questions)

        return jsonify({"success": True, "chapter_id": chapter_id, "questions": questions})
    except FileNotFoundError:
        return jsonify({"success": False, "error": "Chapter not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.get("/chapters/<path:filename>")
def serve_chapter(filename: str):
    # Optional: allow downloading raw chapter text
    return send_from_directory(CHAPTERS_DIR, filename, mimetype="text/plain")

if __name__ == "__main__":
    print("🚀 AI Quiz Server on http://localhost:8001")
    print("Tip: set OPENAI_API_KEY (no quotes): export OPENAI_API_KEY=sk-...")
    app.run(host="0.0.0.0", port=8001, debug=True)

