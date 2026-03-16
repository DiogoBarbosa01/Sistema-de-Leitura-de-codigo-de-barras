from app_embalagem.database.connection import engine
from app_embalagem.models.base import Base
from app_embalagem.models.caixa import Caixa
from app_embalagem.models.funcionario import Funcionario
from app_embalagem.models.movimentacao import Movimentacao
from app_embalagem.models.usuario import Usuario


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Banco inicializado com sucesso.")
