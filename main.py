import os
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

import db.models  # noqa: F401
from app_logging import configure_logging
from db.base import Base
from db.session import engine
from window import MainWindow


def _setup_argos_data_dir() -> None:
    """
    argostranslate/sentencepiece используют fopen() без поддержки Unicode
    на Windows, поэтому кириллица (или другие не-ASCII символы) в пути
    пользователя (C:\\Users\\Али\\...) ломает загрузку модели.
    Уводим данные argostranslate в фиксированный ASCII-путь,
    не зависящий от имени пользователя.
    """
    candidates = [
        Path(os.environ.get("PROGRAMDATA", "C:/ProgramData")) / "MarineParser",
        Path("C:/MarineParserData"),
    ]
    for data_dir in candidates:
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
            os.environ.setdefault("XDG_DATA_HOME", str(data_dir))
            return
        except OSError:
            continue
    base = Path(os.environ.get("PROGRAMDATA", "C:/ProgramData"))
    data_dir = base / "MarineParser"
    data_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("XDG_DATA_HOME", str(data_dir))


_setup_argos_data_dir()


def boot():
    configure_logging()
    Base.metadata.create_all(engine)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    boot()
