import json
from pathlib import Path

from astrbot.api import logger


class I18nManager:
    """Internationalization manager for loading and querying locale strings."""

    def __init__(self, locales_dir: Path):
        self.locales_dir = locales_dir
        self.translations: dict[str, dict[str, str]] = {}
        self._load_locales()

    def _load_locales(self):
        """Load all locale JSON files from the locales directory."""
        if not self.locales_dir.exists():
            logger.warning(f"Locales directory not found: {self.locales_dir}")
            return
        for locale_file in self.locales_dir.glob("*.json"):
            locale_code = locale_file.stem
            try:
                with open(locale_file, encoding="utf-8") as f:
                    self.translations[locale_code] = json.load(f)
                logger.info(f"Loaded locale: {locale_code}")
            except Exception as e:
                logger.error(f"Failed to load locale {locale_code}: {e}")

    def get(self, key: str, locale: str = "zh_CN", **kwargs) -> str:
        """Get a translated string by key.

        Args:
            key: The translation key.
            locale: The locale code (e.g. "zh_CN", "en_US").
            **kwargs: Format parameters for the translation string.

        Returns:
            The translated string, or the key itself if not found.
        """
        if locale not in self.translations:
            locale = "zh_CN"
        text = self.translations.get(locale, {}).get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, IndexError, ValueError):
                return text
        return text

    def reload(self):
        """Reload all locale files."""
        self.translations.clear()
        self._load_locales()
