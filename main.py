import os
import traceback

from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse

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
    return {
        "lessonId": "lesson_001",
        "title": "Calm Straight Lines",
        "steps": [
            {"stepId": "step_1", "targetPath": "M10 10 L300 10", "tolerance": 6},
            {"stepId": "step_2", "targetPath": "M10 30 L300 30", "tolerance": 6},
        ],
    }


def _get_model():
    """
    google.generativeai (v1beta) bazı ortamlarda model isimleri konusunda hassas.
    Önce flash dene, 404 vs olursa pro'ya düş.
    """
    # 1) En çok istenen
    try:
        return genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        # 2) Daha “garanti” alternatif
        return genai.GenerativeModel("gemini-1.5-pro")


@app.post("/analyze")
def analyze_drawing(data: dict = Body(...)):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return JSONResponse(
                status_code=500,
                content={"error": "GEMINI_API_KEY missing on server"},
            )

        genai.configure(api_key=api_key)

        model = _get_model()

        prompt = (
            "Kullanıcının çizimi:\n"
            f"{data}\n\n"
            "Çizimi sakin, net ve teşvik edici şekilde değerlendir.\n"
            "Kısa, net ve teşvik edici bir geri bildirim ver. Maddeler halinde yazabilirsin."
        )

        resp = model.generate_content(prompt)

        text = getattr(resp, "text", None)
        if not text:
            return JSONResponse(
                status_code=500,
                content={"error": "Empty response from Gemini", "raw": str(resp)},
            )

        return {"feedback": text}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "type": e.__class__.__name__,
                "trace": traceback.format_exc()[-2000:],
            },
        )
