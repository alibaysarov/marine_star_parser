start:
	set MARINE_PARSER_CONSOLE=1&& uv run python main.py
test:
	uv run pytest
build: build-windows
prepare-ssl:
	uv run python -c "from pathlib import Path; import shutil, sys; source = Path(sys.base_prefix) / 'DLLs'; target = Path('build/ssl'); target.mkdir(parents=True, exist_ok=True); [shutil.copy2(source / name, target / name) for name in ('_ssl.pyd', 'libcrypto-3-x64.dll', 'libssl-3-x64.dll')]"
build-windows: prepare-ssl
	uv run pyinstaller --noconfirm --clean --onefile --windowed --name MarineParser --icon "$(CURDIR)/assets/logo.ico" --distpath bin --workpath build/pyinstaller --specpath build --add-binary "$(CURDIR)/build/ssl/_ssl.pyd;." --add-binary "$(CURDIR)/build/ssl/libcrypto-3-x64.dll;." --add-binary "$(CURDIR)/build/ssl/libssl-3-x64.dll;." --add-data "$(CURDIR)/models;models" --add-data "$(CURDIR)/assets;assets" --collect-all argostranslate main.py
build-installer: build-windows
	ISCC installer/MarineParser.iss
# build:
    # pyinstaller main.py --add-data "models\translate-en_ru.argosmodel;models"

# # создать миграцию на основе изменений в моделях
# uv run alembic revision --autogenerate -m "init tables"

# применить миграции к базе
# uv run alembic upgrade head