import json
from pathlib import Path

from astrbot.api import logger


class I18nManager:
    """Load plugin translations and metadata.

    加载插件翻译文本和元数据。
    """

    def __init__(self, locales_path: str | Path | None = None):
        self._translations = {}
        self._metadata = {}
        self._fallback_lang = "zh-CN"
        self._locales_path = (
            Path(locales_path)
            if locales_path is not None
            else Path(__file__).parent / ".astrbot-plugin" / "i18n"
        )
        self._load_translations()

    def _load_translations(self):
        """Load all JSON translation files from the i18n directory.

        从 i18n 目录加载全部 JSON 翻译文件。
        """
        i18n_dir = self._locales_path
        if not i18n_dir.exists():
            logger.warning(f"I18n directory not found: {i18n_dir}")
            return

        for lang_file in i18n_dir.glob("*.json"):
            lang_code = lang_file.stem
            try:
                with lang_file.open(encoding="utf-8") as f:
                    data = json.load(f)
                    if "messages" in data:
                        self._translations[lang_code] = data["messages"]
                    if "metadata" in data:
                        self._metadata[lang_code] = data["metadata"]
                    logger.debug(f"Loaded translations and metadata for {lang_code}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in {lang_file}: {e}")
            except Exception as e:
                logger.warning(f"Failed to load translation file {lang_file}: {e}")

    def translate(self, key: str, locale: str = "zh_CN", **kwargs) -> str:
        """Translate a message key with fallback and placeholder formatting.

        翻译消息 key，并提供回退与占位符格式化。
        """
        lang_code = locale.replace("_", "-")
        lang_translations = self._translations.get(lang_code)

        if lang_translations and key in lang_translations:
            text = lang_translations[key]
        else:
            fallback_translations = self._translations.get(self._fallback_lang)
            if fallback_translations and key in fallback_translations:
                text = fallback_translations[key]
            else:
                text = key
                logger.debug(f"Translation not found for key: {key}, locale: {locale}")

        try:
            return text.format(**kwargs)
        except (KeyError, ValueError) as e:
            logger.debug(f"Failed to format translation '{text}': {e}")
            return text

    def get(self, key: str, locale: str = "zh_CN", **kwargs) -> str:
        """Return translated text for the given key.

        返回指定 key 的翻译文本。
        """
        return self.translate(key, locale, **kwargs)

    def get_metadata(self, key: str, locale: str = "zh_CN") -> str | None:
        """Get metadata value (display_name, short_desc, desc) for the given locale.

        获取指定语言下的元数据值（display_name、short_desc、desc）。

        Falls back to zh-CN if the key is not found in the requested locale.
        如果请求语言没有对应 key，则回退到 zh-CN。
        """
        lang_code = locale.replace("_", "-")
        lang_metadata = self._metadata.get(lang_code)

        if lang_metadata and key in lang_metadata:
            return lang_metadata[key]

        fallback_metadata = self._metadata.get(self._fallback_lang)
        if fallback_metadata and key in fallback_metadata:
            return fallback_metadata[key]

        logger.debug(f"Metadata not found for key: {key}, locale: {locale}")
        return None
