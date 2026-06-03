import json
import logging

from google import genai
from google.genai import types

from app.core.config import settings
from app.features.memories.schemas import GeminiEvaluationResult

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """
Eres un asistente experto en psicología geriátrica y análisis de lenguaje.
Analiza la siguiente transcripción de voz de un adulto mayor y extrae información estructurada.
Clasifica el tema (topic) en una de las siguientes opciones exactas:
- Familia
- Salud
- Lecturas
- Bienestar
- Cotidiano

Clasifica el estado de ánimo (mood) en una de las siguientes opciones exactas:
- Entusiasmado
- Alegre
- Relajado
- Tranquilo
- Nostálgico
- Triste
- Ansioso / Preocupado
- Frustrado / Enojado

Además, genera un título (title) corto que resuma la memoria, y si el usuario
menciona algo que deba recordar (una cita médica, comprar algo, llamar a alguien),
extráelo en reminder_text. Si no hay nada que recordar, déjalo nulo.

Devuelve la respuesta estrictamente en este formato JSON:
{{
  "topic": "...",
  "mood": "...",
  "title": "...",
  "reminder_text": "..." // o null
}}

Transcripción: {text}
"""


class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            logger.warning("GEMINI_API_KEY no está configurada.")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)

    async def evaluate_memory(self, text: str) -> GeminiEvaluationResult:
        """
        Evaluates the memory transcription using Gemini and returns a structured result.
        """
        if not self.client:
            # Fallback for local testing without API key
            return GeminiEvaluationResult(
                topic="Familia",
                mood="Tranquilo",
                title="Memoria sin evaluar",
                reminder_text=None,
            )

        prompt = PROMPT_TEMPLATE.format(text=text)

        try:
            # Note: We use the async client `client.aio`
            response = await self.client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            # Parse the JSON response
            raw_json = response.text
            # Sometimes the model wraps the response in ```json ... ``` blocks
            if raw_json.startswith("```json"):
                raw_json = raw_json[7:-3].strip()
            elif raw_json.startswith("```"):
                raw_json = raw_json[3:-3].strip()

            data = json.loads(raw_json)
            return GeminiEvaluationResult(**data)
        except Exception as e:
            logger.error(f"Error evaluating memory with Gemini: {e}")
            raise


def get_gemini_service() -> GeminiService:
    return GeminiService()
