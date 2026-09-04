import asyncio
import pytest

from pdf_parser import get_translated_result
from pdf_parser.translate import (
    install_model,
    get_translated_results,
    translate_batch_async,
    _argos_translate_batch,
)


@pytest.fixture(autouse=True, scope="session")
def setup_translation_model():
    install_model()




def test_translate_batch_preserves_order_and_count():
    inputs = ["OIL SEAL", "BALL BEARING", "GASKET"]
    results = get_translated_results(inputs)

    assert len(results) == len(inputs)
    for original, result in zip(inputs, results):
        assert result.endswith(f"({original})")


def test_translate_batch_empty_list():
    assert get_translated_results([]) == []


def test_argos_fallback_translates_directly():
    """
    Проверяем сам fallback-путь (argostranslate) в изоляции от googletrans,
    чтобы убедиться, что он рабочий сам по себе, а не только как недостижимая ветка.
    """
    install_model()
    results = _argos_translate_batch(["OIL SEAL"])
    assert len(results) == 1
    assert isinstance(results[0], str)
    assert results[0] != ""


def test_translate_batch_async_falls_back_on_googletrans_failure(monkeypatch):
    """
    Если googletrans падает, translate_batch_async должен без исключения
    вернуть результат через argostranslate.
    """
    import pdf_parser.translate as translate_module

    class BrokenTranslator:
        async def __aenter__(self):
            raise RuntimeError("simulated googletrans failure")

        async def __aexit__(self, *args):
            pass

    monkeypatch.setattr(translate_module, "GoogleTranslator", lambda: BrokenTranslator())

    results = asyncio.run(translate_module.translate_batch_async(["OIL SEAL"]))
    assert len(results) == 1
    assert results[0] != ""