start:
	set MARINE_PARSER_CONSOLE=1&& uv run python main.py
test:
	uv run pytest
build: build-windows
build-windows:
	uv run pyinstaller --noconfirm --clean --onefile --windowed --name MarineParser --distpath bin --workpath build/pyinstaller --specpath build --add-data "$(CURDIR)/models;models" --add-data "$(CURDIR)/assets;assets" --collect-all argostranslate main.py
build-installer: build-windows
	ISCC installer/MarineParser.iss
# build:
    # pyinstaller main.py --add-data "models\translate-en_ru.argosmodel;models"

# # создать миграцию на основе изменений в моделях
# uv run alembic revision --autogenerate -m "init tables"

# применить миграции к базе
# uv run alembic upgrade head