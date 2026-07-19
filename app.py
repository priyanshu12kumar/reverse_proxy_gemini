import logging
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import uvicorn

logger = logging.getLogger("proxy_server")

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str
    api_key : str
    model_name : str


@app.post("/generate")
def generate(req: PromptRequest) -> str | None :

    URL = f"https://generativelanguage.googleapis.com/v1beta/{req.model_name}:generateContent?key={req.api_key}"

    payload = {
        "contents": [
            {
                "parts": [{"text": req.prompt}]
            }
        ]
    }

    raw_data = ""

    try:

        response = requests.post(
            URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=20,
        )

        response.raise_for_status()
        raw_data = response.json()

        text = (
            raw_data["candidates"][0]
            ["content"]["parts"][0]
            ["text"]
        )

        return text

    except (KeyError, IndexError, TypeError):
        logger.error("Gemini response missing candidate text: %s", raw_data)
        return None

    except requests.Timeout:
        logger.error("Gemini request timed out")
        return None

    except requests.RequestException as exc:
        logger.error("Gemini request failed: %s", exc)
        return None
    
if __name__ == "__main__" :
    
    uvicorn.run(
        "app:app" ,
        host="0.0.0.0" ,
        port=8000 ,
        reload=True
    )