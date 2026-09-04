import os
from pathlib import Path

base = Path(os.environ.get("PROGRAMDATA", "C:/ProgramData"))
data_dir = base / "MarineParser"
data_dir.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("XDG_DATA_HOME", str(data_dir))
