import json
import os
from typing import Dict, List


class TextService:
    def __init__(self):
        self._texts = {}
        self._buttons = {}
        self._language_buttons = []
        self._admin_buttons = {}
        self._admin_actions = {}
        self._load_data()

    def _load_data(self):
        current_dir = os.path.dirname(__file__)
        texts_json_path = os.path.join(
            current_dir, "..", "..", "properties", "texts.json"
        )
        with open(texts_json_path, encoding="utf-8") as file:
            data = json.load(file)
            self._texts = data.get("texts", {})
            self._buttons = data.get("buttons", {})
            self._language_buttons = data.get("language_buttons", [])
            self._admin_buttons = data.get("admin_buttons", {})
            self._admin_actions = data.get("admin_actions", {})

    def get_text(self, key: str, language: str) -> str:
        return self._texts.get(language, {}).get(key, "")

    @property
    def texts(self) -> Dict:
        return self._texts

    @property
    def buttons(self) -> Dict:
        return self._buttons

    @property
    def admin_buttons(self) -> Dict:
        return self._admin_buttons

    @property
    def admin_actions(self) -> Dict:
        return self._admin_actions

    @property
    def language_buttons(self) -> List:
        return self._language_buttons


text_service = TextService()
