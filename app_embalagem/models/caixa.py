from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app_embalagem.models.base import Base


class Caixa(Base):
    __tablename__ = "caixas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo_caixa: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    arte: Mapped[str] = mapped_column(String(120), nullable=False)
    artigo: Mapped[str] = mapped_column(String(60), nullable=False)
    metros: Mapped[float] = mapped_column(Float, nullable=False)
    sigla_funcionario: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="criada", nullable=False)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    movimentacoes = relationship("Movimentacao", back_populates="caixa")
