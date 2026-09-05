import asyncio

import pdf_parser.translate as translate_module
from pdf_parser.translate import _argos_translate_batch, get_translated_results


def test_translate_batch_preserves_order_and_count(monkeypatch):
    inputs = ["OIL SEAL", "BALL BEARING", "GASKET"]

    async def fake_translate_batch(texts):
        return {f"key_{text}": f"Перевод {text}" for text in texts}

    monkeypatch.setattr(translate_module, "translate_batch_async", fake_translate_batch)
    results = get_translated_results(inputs)

    assert len(results) == len(inputs)
    assert results == {
        "key_OIL SEAL": "Перевод OIL SEAL",
        "key_BALL BEARING": "Перевод BALL BEARING",
        "key_GASKET": "Перевод GASKET",
    }


def test_translate_batch_empty_list():
    assert get_translated_results([]) == {}


def test_argos_fallback_translates_directly(monkeypatch):
    """
    Проверяем сам fallback-путь (argostranslate) в изоляции от googletrans,
    чтобы убедиться, что он рабочий сам по себе, а не только как недостижимая ветка.
    """
    translate_module._translation_ready = True
    monkeypatch.setattr(
        translate_module.argostranslate.translate,
        "translate",
        lambda text, source, target: f"Перевод {text}",
    )
    results = _argos_translate_batch(["OIL SEAL"])
    assert len(results) == 1
    assert isinstance(results["key_OIL SEAL"], str)
    assert results["key_OIL SEAL"] != ""


def test_translate_batch_async_falls_back_to_local_argos(monkeypatch):
    class BrokenTranslator:
        async def __aenter__(self):
            raise RuntimeError("simulated googletrans failure")

        async def __aexit__(self, *args):
            pass

    monkeypatch.setattr(translate_module, "GoogleTranslator", lambda: BrokenTranslator())

    async def fake_fallback(texts):
        return {f"key_{text}": f"Перевод {text}" for text in texts}

    monkeypatch.setattr(translate_module, "_argos_translate_batch_nonblocking", fake_fallback)

    results = asyncio.run(translate_module.translate_batch_async(["OIL SEAL"]))
    assert len(results) == 1
    assert results == {"key_OIL SEAL": "Перевод OIL SEAL"}
