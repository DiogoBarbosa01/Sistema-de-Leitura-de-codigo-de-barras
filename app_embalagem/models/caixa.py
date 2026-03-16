from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app_embalagem.models.base import Base


class Caixa(Base):
    __tablename__ = "caixas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo_caixa: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    produto: Mapped[str] = mapped_column(String(120), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="criada", nullable=False)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    movimentacoes = relationship("Movimentacao", back_populates="caixa")
