import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db.base import Base
from db.models import SparePart
from repository.parts_repository import PartsRepository


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db_session:
        yield db_session
    engine.dispose()


def seed_parts(session):
    session.add_all(
        [
            SparePart(name="Цепь", sku="CHAIN-01", part_id="P-001", part_weight=10),
            SparePart(name="Прокладка", sku="GASKET-02", part_id="P-002", part_weight=20),
            SparePart(name="Цепь приводная", sku="DRIVE-03", part_id="P-003", part_weight=30),
        ]
    )
    session.commit()


def test_get_all_is_sorted_descending_and_paginated(session):
    seed_parts(session)
    repository = PartsRepository(session)

    result = repository.get_all(page=1, per_page=2)

    assert [part.part_id for part in result] == ["P-003", "P-002"]


def test_get_all_searches_all_fields_case_insensitively(session):
    seed_parts(session)
    repository = PartsRepository(session)

    assert [part.part_id for part in repository.get_all(search="ЦЕПЬ")] == ["P-003", "P-001"]
    assert [part.part_id for part in repository.get_all(search="gasket")] == ["P-002"]
    assert [part.part_id for part in repository.get_all(search="p-001")] == ["P-001"]


def test_get_parts_by_part_ids_returns_names_and_weights(session):
    seed_parts(session)
    repository = PartsRepository(session)

    assert repository.get_parts_by_part_ids(["P-002", "P-404", "P-001"]) == {
        "P-001": ("Цепь", 10),
        "P-002": ("Прокладка", 20),
    }


def test_repository_crud_and_upsert(session):
    repository = PartsRepository(session)
    part = repository.add(
        SparePart(name="Старое имя", sku="SKU-1", part_id="PART-1", part_weight=1)
    )

    assert repository.get_by_id(part.id).name == "Старое имя"

    repository.batch_import(
        [{"name": "Новое имя", "sku": "SKU-1", "part_id": "PART-1", "part_weight": 5}]
    )
    updated = repository.get_by_id(part.id)
    assert updated.name == "Новое имя"
    assert updated.part_weight == 5

    repository.delete(part.id)
    assert repository.get_by_id(part.id) is None


def test_empty_batch_does_not_change_database(session):
    repository = PartsRepository(session)

    assert repository.batch_import([]) is None
    assert repository.get_all() == []
