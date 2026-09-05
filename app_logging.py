import logging
import os
import sys
import time
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

LOGGER_NAME = "marine_parser"
LOG_RETENTION_DAYS = 7


def get_log_path() -> Path:
    if getattr(sys, "frozen", False):
        base_dir = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base_dir / "MarineParser" / "app.log"
    return Path(__file__).resolve().parent / "logs" / "app.log"


def remove_old_logs(log_path: Path) -> None:
    cutoff = time.time() - LOG_RETENTION_DAYS * 24 * 60 * 60
    for candidate in log_path.parent.glob(f"{log_path.name}*"):
        try:
            if candidate.is_file() and candidate.stat().st_mtime < cutoff:
                candidate.unlink()
        except OSError:
            logging.getLogger(LOGGER_NAME).warning(
                "Не удалось удалить старый лог: %s", candidate, exc_info=True
            )


def configure_logging() -> Path:
    log_path = get_log_path()
    console_logging = os.environ.get("MARINE_PARSER_CONSOLE") == "1"
    handlers: list[logging.Handler]
    log_path.parent.mkdir(parents=True, exist_ok=True)
    remove_old_logs(log_path)
    if console_logging:
        handlers = [logging.StreamHandler()]
    else:
        handlers = [
            TimedRotatingFileHandler(
                log_path,
                when="midnight",
                interval=1,
                backupCount=LOG_RETENTION_DAYS,
                encoding="utf-8",
            )
        ]

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
        force=True,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.getLogger(LOGGER_NAME).critical(
            "Необработанная ошибка приложения", exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_exception
    logging.getLogger(LOGGER_NAME).info(
        "Приложение запущено; режим=%s",
        "терминал" if console_logging else f"файл {log_path}",
    )
    return log_path


logger = logging.getLogger(LOGGER_NAME)
