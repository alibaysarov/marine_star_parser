import os
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models  # noqa: F401
from .base import Base

BASE_DIR = Path(__file__).resolve().parent.parent


def _get_data_dir() -> Path:
    if not getattr(sys, "frozen", False):
        return BASE_DIR / "data"

    local_app_data = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    return local_app_data / "MarineParser"


DB_PATH = _get_data_dir() / "app.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(engine)
