import json
import random
import logging
from pathlib import Path

class Chatbot:
    def __init__(self, intents_path="intents/intents.json"):
        self.intents = self._load_intents(intents_path)
        self._setup_logger()

    def _setup_logger(self):
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _load_intents(self, path):
        with open(Path(__file__).parent.parent / path) as f:
            return json.load(f)

    def get_response(self, query):
        query = query.lower().strip()
        for intent in self.intents["intents"]:
            if any(p.lower() in query for p in intent["patterns"]):
                return {
                    "response": random.choice(intent["responses"]),
                    "tag": intent["tag"]
                }
        return {
            "response": "I can help with app settings and account issues",
            "tag": "unknown"
        }