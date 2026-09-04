start:
	uv run python main.py
test:
	uv run pytest
# build:
    # pyinstaller main.py --add-data "models\translate-en_ru.argosmodel;models"

# # создать миграцию на основе изменений в моделях
# uv run alembic revision --autogenerate -m "init tables"

# применить миграции к базе
# uv run alembic upgrade head