import json

raw_json = """{
  "topic": "Familia y Amigos"
}"""
try:
    data = json.loads(raw_json)
    print("OK", data)
except Exception as e:
    print("Error:", repr(e))
