import os
from fastapi import FastAPI, Body
import google.generativeai as genai

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/env-check")
def env_check():
    key = os.getenv("GEMINI_API_KEY")
    return {"has_key": bool(key), "key_len": len(key or "")}

@app.get("/lesson/daily")
def daily_lesson():
    # Basit sabit lesson (şimdilik)
    return {
        "lessonId": "lesson_001",
        "title": "Calm Straight Lines",
        "steps": [
            {"stepId": "step_1", "targetPath": "M10 10 L300 10", "tolerance": 6},
            {"stepId": "step_2", "targetPath": "M10 30 L300 30", "tolerance": 6},
        ],
    }

@app.post("/analyze")
def analyze_drawing(data: dict = Body(...)):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY missing on server"}

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-pro")

    prompt = f"""
Kullanıcının çizimi:
{data}

Çizimi sakin, net ve teşvik edici şekilde değerlendir.
"""
    response = model.generate_content(prompt)
    return {"feedback": response.text}
