import json

texts = {}


def load_texts_from_json(file_path: str):
    global texts
    with open(file_path, encoding='utf-8') as file:
        data = json.load(file)
        buttons = data.get("buttons", {})
        language_buttons = data.get("language_buttons", [])
        texts = data.get("texts", {})

    return buttons, language_buttons


def get_text(key: str, language: str):
    return texts.get(language, {}).get(key, "")
