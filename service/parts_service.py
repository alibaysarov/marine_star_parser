# services/parts_service.py

from itertools import batched

from PySide6.QtCore import QThreadPool

from db.session import SessionLocal
from repository import PartsRepository
from workers.db_worker import DbWorker


class PartsService:
    def __init__(self) -> None:
        self._pool = QThreadPool.globalInstance()

    @staticmethod
    def _get_all(
        search: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> list:
        # Эта функция будет выполнена в потоке DbWorker
        with SessionLocal() as session:
            repo = PartsRepository(session)

            return repo.get_all(
                search=search,
                page=page,
                per_page=per_page,
            )

    @staticmethod
    def _batch_upload(products: list[dict]):
        # Отдельная SQLite-сессия внутри фонового потока
        with SessionLocal() as session:
            repo = PartsRepository(session)
            
            return repo.batch_import(products)

    def upload_parts_async(
        self,
        products: list[dict],
        on_success,
        on_error=None,
    ) -> None:

        # Функция передаётся БЕЗ вызова ()
        # Аргумент products передаётся отдельно
        worker = DbWorker(
            self._batch_upload,
            products,
        )

        worker.signals.finished.connect(on_success)

        if on_error:
            worker.signals.error.connect(on_error)

        self._pool.start(worker)

    def load_parts_async(
        self,
        search: str | None = None,
        page: int = 1,
        per_page: int = 50,
        on_success=None,
        on_error=None,
    ) -> None:

        # Все аргументы будут переданы в:
        # _get_all(search, page, per_page)
        worker = DbWorker(
            self._get_all,
            search,
            page,
            per_page,
        )

        if on_success:
            worker.signals.finished.connect(on_success)

        if on_error:
            worker.signals.error.connect(on_error)

        self._pool.start(worker)