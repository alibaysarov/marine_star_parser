# workers/db_worker.py
from typing import Any, Callable
from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class WorkerSignals(QObject):
    finished = Signal(object)   # результат функции
    error = Signal(Exception)   # исключение, если случилось


class DbWorker(QRunnable):
    """
    Выполняет произвольную функцию (обычно — метод репозитория)
    в фоновом потоке и возвращает результат через сигнал.
    """

    def __init__(self, fn: Callable[..., Any], *args, **kwargs) -> None:
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:  # noqa: BLE001
            self.signals.error.emit(e)
        else:
            self.signals.finished.emit(result)