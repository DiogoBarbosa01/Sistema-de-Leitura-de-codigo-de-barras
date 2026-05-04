from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app_embalagem.models.base import Base


class Caixa(Base):
    __tablename__ = "caixas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo_caixa: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    arte: Mapped[str] = mapped_column(String(120), nullable=False)
    artigo: Mapped[str] = mapped_column(String(60), nullable=False)
    cor: Mapped[str] = mapped_column(String(40), nullable=False, default="-")
    emendas: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metros: Mapped[float] = mapped_column(Float, nullable=False)
    nome_funcionario: Mapped[str] = mapped_column(String(120), nullable=False, default="-")
    sigla_funcionario: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="criada", nullable=False)
    barcode_png: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    movimentacoes = relationship("Movimentacao", back_populates="caixa")
