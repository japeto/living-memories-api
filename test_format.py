PROMPT_TEMPLATE = """
Devuelve la respuesta estrictamente en este formato JSON:
{
  "topic": "...",
  "mood": "..."
}
Transcripción: {text}
"""
try:
    prompt = PROMPT_TEMPLATE.format(text="Hola")
except Exception as e:
    print("Caught:", repr(e))
