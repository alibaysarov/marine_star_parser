from itertools import batched

from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from db.models import SparePart
from sqlalchemy.dialects.sqlite import insert


class PartsRepository:
    def __init__(self,session:Session) -> None:
        self._session = session
    def get_all(
            self,
            search: str | None = None,
            page: int = 1,
            per_page: int = 50,
        ) -> list[SparePart]:
    
            # Защита от некорректных значений
            page = max(page, 1)
            per_page = max(per_page, 1)
    
            stmt = select(SparePart)
    
            # Если есть поисковый запрос
            if search:
                stmt = stmt.where(
                    SparePart.name.ilike(f"%{search}%")
                )
    
            # Пагинация
            offset = (page - 1) * per_page
    
            stmt = (
                stmt
                .order_by(SparePart.id)
                .offset(offset)
                .limit(per_page)
            )
    
            result = self._session.execute(stmt)
    
            return result.scalars().all()
        
    def get_by_id(self, part_id: int) -> SparePart | None:
        return self._session.get(SparePart, part_id)

    def add(self, part: SparePart) -> SparePart:
        self._session.add(part)
        self._session.commit()
        self._session.refresh(part)
        return part

    def batch_import(self, parts: list[dict]) -> None:
        """
        Принимает список словарей вида:
        {"name": str, "part_id": str, "part_weight": int}

        При конфликте по part_id обновляет name и part_weight.
        """
        if not parts:
            return

        chunks = [list(c) for c in batched(parts, 900)]
        smtmts = [insert(SparePart).values(c) for c in chunks]
        #stmt = insert(SparePart).values(parts)

        for stmt in smtmts:
            stmt = stmt.on_conflict_do_update(
                index_elements=["sku"],
                set_={
                    "name": stmt.excluded.name,
                    "part_weight": stmt.excluded.part_weight,
                },
            )
            self._session.execute(stmt)
        self._session.commit()
    
    def delete(self, part_id: int) -> None:
        part = self.get_by_id(part_id)
        if part is not None:
            self._session.delete(part)
            self._session.commit()
