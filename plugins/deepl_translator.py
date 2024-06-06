# plugins/deepl_translator.py

import requests
import logging

DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"
DEEPL_API_KEY = "API"

def activate():
    print("DeepL Translator activated")
    logging.info("DeepL Translator activated")

def deactivate():
    print("DeepL Translator deactivated")
    logging.info("DeepL Translator deactivated")

def translate_text(text, target_lang="EN"):
    try:
        response = requests.post(DEEPL_API_URL, data={
            "auth_key": DEEPL_API_KEY,
            "text": text,
            "target_lang": target_lang
        })
        response.raise_for_status()
        result = response.json()
        return result["translations"][0]["text"]
    except requests.RequestException as e:
        logging.error(f"Error translating text: {e}")
        return None
