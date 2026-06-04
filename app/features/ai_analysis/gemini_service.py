import json
import logging
import zoneinfo
from datetime import datetime

from google import genai
from google.genai import types

from app.core.config import settings
from app.features.memories.schemas import GeminiEvaluationResult

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """
Eres un asistente experto en psicología geriátrica y análisis de lenguaje.
La fecha y hora local actuales del usuario son: {current_time} (Zona horaria: {time_zone})
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

Además, genera un título (title) corto que resuma la memoria. Si el usuario
menciona cosas que deba recordar (citas médicas, comprar cosas, llamar a alguien),
extráelas como una lista de recordatorios. Si no hay nada que recordar, devuelve una lista vacía.

IMPORTANTE PARA LOS RECORDATORIOS:
- Si el usuario no especifica una hora concreta (ej: "mañana"), asume que es un evento de todo
  el día y usa una hora por defecto como las 08:00 de la mañana.
- El campo due_date DEBE usar estrictamente el formato ISO 8601 con el offset de la zona horaria
  del usuario (YYYY-MM-DDTHH:MM:SS±HH:MM), sin usar la Z al final.

Devuelve la respuesta estrictamente en este formato JSON:
{{
  "topic": "...",
  "mood": "...",
  "title": "...",
  "reminders": [
    {{
      "title": "...",
      "due_date": "YYYY-MM-DDTHH:MM:SS±HH:MM",
      "description": "..."
    }}
  ]
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

    async def evaluate_memory(self, text: str, time_zone: str = "UTC") -> GeminiEvaluationResult:
        """
        Evaluates the memory transcription using Gemini and returns a structured result.
        """
        if not self.client:
            # Fallback for local testing without API key
            return GeminiEvaluationResult(
                topic="Familia",
                mood="Tranquilo",
                title="Memoria sin evaluar",
                reminders=[],
            )

        try:
            user_tz = zoneinfo.ZoneInfo(time_zone)
        except Exception:
            user_tz = zoneinfo.ZoneInfo("UTC")

        current_time = datetime.now(user_tz).isoformat()
        prompt = PROMPT_TEMPLATE.format(text=text, current_time=current_time, time_zone=time_zone)

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
            result = GeminiEvaluationResult(**data)

            for reminder in result.reminders:
                if reminder.due_date.tzinfo is None:
                    reminder.due_date = reminder.due_date.replace(tzinfo=user_tz)

            return result
        except Exception as e:
            logger.error(f"Error evaluating memory with Gemini: {e}")
            raise


def get_gemini_service() -> GeminiService:
    return GeminiService()
