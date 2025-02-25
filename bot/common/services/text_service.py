import json
import os
from typing import Dict, List


class TextService:
    _instance = None
    _texts: Dict = {}
    _buttons: Dict = {}
    _language_buttons: List = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TextService, cls).__new__(cls)
            cls._instance._load_data()

        return cls._instance

    def _load_data(self) -> None:
        current_dir = os.path.dirname(__file__)
        texts_json_path = os.path.join(current_dir, '..', '..', 'properties', 'texts.json')

        with open(texts_json_path, encoding='utf-8') as file:
            data = json.load(file)
            self._texts = data.get('texts', {})
            self._buttons = data.get('buttons', {})
            self._language_buttons = data.get('language_buttons', [])

    def get_text(self, key: str, language: str) -> str:
        return self._texts.get(language, {}).get(key, "")

    @property
    def texts(self) -> Dict:
        return self._texts

    @property
    def buttons(self) -> Dict:
        return self._buttons

    @property
    def language_buttons(self) -> List:
        return self._language_buttons


text_service = TextService()
