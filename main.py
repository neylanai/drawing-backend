import os
import google.generativeai as genai
from fastapi import FastAPI
import os
import google.generativeai as genai

app = FastAPI()

# Gemini API key'i ortam değişkeninden al
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/lesson/daily")
def daily_lesson():
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = """
    Create a simple drawing lesson for an iPad drawing app.
    Focus on calm straight lines.
    Respond in JSON with:
    lessonId, title, steps (each step has stepId, targetPath, tolerance)
    """

    response = model.generate_content(prompt)

    return {
        "raw": response.text
    }

from fastapi import FastAPI



app = FastAPI()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("models/gemini-pro")


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/lesson/daily")
def daily_lesson():
    return {
        "lessonId": "lesson_001",
        "title": "Calm Straight Lines",
        "steps": [
            {"stepId": "step_1", "targetPath": "M10 10 L300 10", "tolerance": 6},
            {"stepId": "step_2", "targetPath": "M10 30 L300 30", "tolerance": 6}
        ]
    }
from fastapi import Body

@app.post("/analyze")
def analyze_drawing(data: dict = Body(...)):
    prompt = f"""
    Kullanıcının çizimi:
    {data}

    Çizimi sakin, net ve teşvik edici şekilde değerlendir.
    """

    response = model.generate_content(prompt)
    return {"feedback": response.text}


