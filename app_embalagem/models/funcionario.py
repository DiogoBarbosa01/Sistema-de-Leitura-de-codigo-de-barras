from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app_embalagem.models.base import Base


class Funcionario(Base):
    __tablename__ = "funcionarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    matricula: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    codigo_barras: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    movimentacoes = relationship("Movimentacao", back_populates="funcionario")
