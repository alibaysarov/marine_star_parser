import asyncio
import os
import sys
from pathlib import Path

from googletrans import Translator

# Эти переменные должны быть заданы до импорта argostranslate: его settings
# вычисляет каталоги пакетов во время импорта модуля.
ARGOS_DATA_DIR = Path(os.environ.get("PROGRAMDATA", "C:/ProgramData")) / "MarineParser"
os.environ.setdefault("XDG_DATA_HOME", str(ARGOS_DATA_DIR))
os.environ.setdefault("ARGOS_PACKAGES_DIR", str(ARGOS_DATA_DIR / "argos-translate" / "packages"))

import argostranslate.package  # noqa: E402
import argostranslate.translate  # noqa: E402

from app_logging import logger  # noqa: E402

BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
MODEL_PATH = BUNDLE_DIR / "models" / "translate-en_ru.argosmodel"

_translation_ready = False


def install_model():
    global _translation_ready
    if _translation_ready:
        return
    installed_codes = {lang.code for lang in argostranslate.translate.get_installed_languages()}
    if "en" not in installed_codes or "ru" not in installed_codes:
        argostranslate.package.install_from_path(MODEL_PATH)
    _translation_ready = True


def _argos_translate_batch(texts: list[str]) -> dict[str, str]:
    """Блокирующий по своей природе fallback-перевод через argostranslate."""
    install_model()
    return {f"key_{t}": argostranslate.translate.translate(t, "en", "ru") for t in texts}


async def _argos_translate_batch_nonblocking(texts: list[str]) -> dict[str, str]:
    """Гоняем блокирующий argostranslate в отдельном потоке, чтобы не держать event loop."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _argos_translate_batch, texts)


async def translate_batch_async(texts: list[str]) -> dict[str, str]:
    """Переводит через Google Translate, используя Argos при ошибке сети."""
    if not texts:
        return {}
    try:
        async with Translator() as translator:
            results = await translator.translate(texts, src="en", dest="ru")

        logger.info("Переведено %d строк через Google Translate", len(texts))
        return {f"key_{result.origin}": result.text for result in results}

    except Exception:
        logger.exception("Google Translate недоступен, используется локальный перевод")
        return await _argos_translate_batch_nonblocking(texts)


# def get_translated_results(inputs: list[str]) -> list[str]:
#     """Синхронная обёртка над батч-переводом — вызывать из обычного (не async) кода."""
#     translated = asyncio.run(translate_batch_async(inputs))
#     return [f"{t} ({orig})" for t, orig in zip(translated, inputs)]


def get_translated_results(inputs: list[str]) -> dict[str]:
    """Синхронная обёртка над батч-переводом — вызывать из обычного (не async) кода."""
    translated = asyncio.run(translate_batch_async(inputs))
    return translated


def get_translated_result(input: str) -> str:
    """Перевод одной строки — обратная совместимость со старым API."""
    return get_translated_results([input])[0]
