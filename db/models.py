from sqlalchemy import String,Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class SparePart(Base):
    __tablename__ = "spare_parts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    sku: Mapped[str] = mapped_column(String(100),unique=True,index=True)
    part_id: Mapped[str] = mapped_column(String(100), unique=True)
    part_weight: Mapped[int] = mapped_column(Integer())