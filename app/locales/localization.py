import json
import os


class Localization:
    _cache = {}
    _default_lang = "en"

    @classmethod
    def load_language(cls, lang: str):
        """Load the language file into memory."""
        file_path = f"app/locales/{lang}.json"
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                cls._cache[lang] = json.load(f)
        else:
            cls._cache[lang] = cls._cache.get(cls._default_lang, {})

    @classmethod
    def set_language(cls, lang: str):
        """Set the active language globally."""
        cls._default_lang = lang
        cls.load_language(lang)

    @classmethod
    def get(cls, key: str) -> str:
        """Get a localized message."""
        return cls._cache.get(cls._default_lang, {}).get(key, key)


def tr(key: str) -> str:
    """Helper function for translations."""
    return Localization.get(key)
