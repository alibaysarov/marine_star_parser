import asyncio
import os
from pathlib import Path

import argostranslate.package
import argostranslate.translate
from googletrans import Translator as GoogleTranslator

# argostranslate использует Path.home() для data_dir, а C:\Users\Али
# содержит кириллицу, которая ломает низкоуровневый sentencepiece (fopen).
# Переопределяем через официальную переменную XDG_DATA_HOME на ASCII-путь.
os.environ.setdefault("XDG_DATA_HOME", "C:/argos_data")

MODEL_PATH = Path(__file__).parent.parent / "models" / "translate-en_ru.argosmodel"

_translation_ready = False


def install_model():
    global _translation_ready
    if _translation_ready:
        return
    installed_codes = {lang.code for lang in argostranslate.translate.get_installed_languages()}
    if "en" not in installed_codes or "ru" not in installed_codes:
        argostranslate.package.install_from_path(MODEL_PATH)
    _translation_ready = True


def _argos_translate_batch(texts: list[str]) -> list[str]:
    """Блокирующий по своей природе fallback-перевод через argostranslate."""
    install_model()
    return [argostranslate.translate.translate(t, "en", "ru") for t in texts]


async def _argos_translate_batch_nonblocking(texts: list[str]) -> list[str]:
    """Гоняем блокирующий argostranslate в отдельном потоке, чтобы не держать event loop."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _argos_translate_batch, texts)


async def translate_batch_async(texts: list[str]) -> list[str]:
    """
    Батч-перевод en->ru.
    Основной путь: googletrans, асинхронно, одним запросом на весь список.
    Фолбэк (неблокирующий): argostranslate, если googletrans упал.
    """
    if not texts:
        return []
    try:
        async with GoogleTranslator() as translator:
            results = await translator.translate(texts, src="en", dest="ru")
        return [r.text for r in results]
    except Exception:
        return await _argos_translate_batch_nonblocking(texts)


def get_translated_results(inputs: list[str]) -> list[str]:
    """Синхронная обёртка над батч-переводом — вызывать из обычного (не async) кода."""
    translated = asyncio.run(translate_batch_async(inputs))
    return [f"{t} ({orig})" for t, orig in zip(translated, inputs)]


def get_translated_result(input: str) -> str:
    """Перевод одной строки — обратная совместимость со старым API."""
    return get_translated_results([input])[0]
