import asyncio

import pdf_parser.translate as translate_module
from pdf_parser.translate import _argos_translate_batch, get_translated_results


def test_translate_batch_preserves_order_and_count(monkeypatch):
    inputs = ["OIL SEAL", "BALL BEARING", "GASKET"]

    async def fake_translate_batch(texts):
        return [f"Перевод {text}" for text in texts]

    monkeypatch.setattr(translate_module, "translate_batch_async", fake_translate_batch)
    results = get_translated_results(inputs)

    assert len(results) == len(inputs)
    assert results == [
        "Перевод OIL SEAL (OIL SEAL)",
        "Перевод BALL BEARING (BALL BEARING)",
        "Перевод GASKET (GASKET)",
    ]


def test_translate_batch_empty_list():
    assert get_translated_results([]) == []


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
    assert isinstance(results[0], str)
    assert results[0] != ""


def test_translate_batch_async_falls_back_on_googletrans_failure(monkeypatch):
    """
    Если googletrans падает, translate_batch_async должен без исключения
    вернуть результат через argostranslate.
    """

    class BrokenTranslator:
        async def __aenter__(self):
            raise RuntimeError("simulated googletrans failure")

        async def __aexit__(self, *args):
            pass

    monkeypatch.setattr(translate_module, "GoogleTranslator", lambda: BrokenTranslator())

    async def fake_fallback(texts):
        return [f"Перевод {text}" for text in texts]

    monkeypatch.setattr(translate_module, "_argos_translate_batch_nonblocking", fake_fallback)

    results = asyncio.run(translate_module.translate_batch_async(["OIL SEAL"]))
    assert len(results) == 1
    assert results == ["Перевод OIL SEAL"]
