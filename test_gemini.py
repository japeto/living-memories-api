import asyncio
from google import genai
from google.genai import types
from app.core.config import settings

async def main():
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say something in JSON",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    print("Type of response.text:", type(response.text))
    print("Value:", repr(response.text))

asyncio.run(main())
