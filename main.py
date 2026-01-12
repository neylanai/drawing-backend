import os
import json
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import google.generativeai as genai

app = FastAPI()


# ---------- Health / Env ----------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/env-check")
def env_check():
    key = os.getenv("GEMINI_API_KEY")
    return {"has_key": bool(key), "key_len": len(key or "")}


# ---------- Lesson ----------
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


# ---------- Analyze ----------
@app.post("/analyze")
async def analyze_drawing(request: Request):
    """
    Süper esnek endpoint - her türlü input kabul eder.
    Body boş bile olsa çalışır.
    """
    try:
        # Body'yi oku (boş olabilir)
        try:
            payload = await request.json()
        except Exception:
            payload = {}

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return JSONResponse(
                status_code=500, content={"error": "GEMINI_API_KEY missing on server"}
            )

        genai.configure(api_key=api_key)

        # ✅ Güncel model adı (Ocak 2026)
        model = genai.GenerativeModel("gemini-2.5-flash")

        # Payload'dan paths'i al veya tüm payload'ı kullan
        if isinstance(payload, dict):
            paths_data = payload.get("paths", payload) if payload else "boş çizim"
        else:
            paths_data = payload or "boş çizim"

        prompt = f"""
Sen bir iPad çizim uygulaması için çizim koçusun.
Kullanıcının çizimi (SVG path listesi):
{paths_data}

SADECE geçerli JSON döndür. Ekstra açıklama, markdown, backtick YOK.
Şu şemaya tam uy:
{{
  "score": 0-100,
  "feedback_text": "kısa, sakin, teşvik edici yorum",
  "tips": ["1-3 kısa ipucu"],
  "next_step": "bir sonraki küçük görev"
}}
"""

        resp = model.generate_content(prompt)
        text = getattr(resp, "text", "") or ""

        # Model bazen JSON'u ``` içinde döndürebilir. Temizleyelim:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json", "", 1).strip()

        # JSON parse etmeyi dene:
        try:
            data = json.loads(cleaned)
        except Exception:
            data = {
                "score": 70,
                "feedback_text": text.strip()[:800],
                "tips": ["Çizgiyi daha sabit hızla çekmeyi dene."],
                "next_step": "Aynı çizgiyi 3 kez daha çiz.",
            }

        return JSONResponse(status_code=200, content=data)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "type": e.__class__.__name__,
                "trace": traceback.format_exc()[-2000:],
            },
        )
