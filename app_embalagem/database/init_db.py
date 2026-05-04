from sqlalchemy import text

from app_embalagem.database.connection import engine
from app_embalagem.models.base import Base
from app_embalagem.models.caixa import Caixa
from app_embalagem.models.funcionario import Funcionario
from app_embalagem.models.movimentacao import Movimentacao
from app_embalagem.models.usuario import Usuario


def _adicionar_colunas_faltantes_caixas():
    comandos = [
        "ALTER TABLE caixas ADD COLUMN cor VARCHAR(40) NOT NULL DEFAULT '-'",
        "ALTER TABLE caixas ADD COLUMN emendas INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE caixas ADD COLUMN nome_funcionario VARCHAR(120) NOT NULL DEFAULT '-'",
        "ALTER TABLE caixas ADD COLUMN largura VARCHAR(10) NOT NULL DEFAULT '40'",
        "ALTER TABLE caixas ADD COLUMN barcode_png BYTEA",
    ]
    with engine.begin() as conn:
        for cmd in comandos:
            try:
                conn.execute(text(cmd))
            except Exception:
                # ignora quando a coluna já existe.
                pass


def init_db():
    Base.metadata.create_all(bind=engine)
    _adicionar_colunas_faltantes_caixas()


if __name__ == "__main__":
    init_db()
    print("Banco inicializado com sucesso.")
