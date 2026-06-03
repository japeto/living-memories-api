import json

class MockResult:
    def __init__(self, **kwargs):
        pass

# Simulate KeyError internally
try:
    data = {"hello": "world"}
    # what if someone does data['\n  "topic"']?
    x = data['\n  "topic"']
except Exception as e:
    print(repr(e))
