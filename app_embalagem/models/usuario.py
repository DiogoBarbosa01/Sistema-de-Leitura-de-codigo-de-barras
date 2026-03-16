from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app_embalagem.models.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    perfil: Mapped[str] = mapped_column(String(20), nullable=False, default="operador")
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
