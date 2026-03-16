from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app_embalagem.models.base import Base


class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    caixa_id: Mapped[int] = mapped_column(ForeignKey("caixas.id"), nullable=False)
    funcionario_id: Mapped[int] = mapped_column(ForeignKey("funcionarios.id"), nullable=False)
    acao: Mapped[str] = mapped_column(String(40), nullable=False)
    data_hora: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)

    caixa = relationship("Caixa", back_populates="movimentacoes")
    funcionario = relationship("Funcionario", back_populates="movimentacoes")
